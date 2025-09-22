"""
Web Scraper Service
AA Ajansı haber detay sayfalarından içerik çekme servisi
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, List
import logging
import time
from urllib.parse import urljoin, urlparse
import re

from models.news_models import ScrapedNewsContent


class AANewsScraper:
    """AA Ajansı web scraper sınıfı"""
    
    def __init__(self, delay: float = 1.0, timeout: int = 20):
        self.delay = delay
        self.timeout = timeout
        self.base_url = "https://www.aa.com.tr"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        self.logger = logging.getLogger(__name__)
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Sayfayı çek ve parse et"""
        try:
            self.logger.debug(f"Sayfa çekiliyor: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            self.logger.error(f"Sayfa çekme hatası ({url}): {e}")
            return None
    
    def _extract_article_content(self, soup: BeautifulSoup) -> str:
        """Makale içeriğini çıkar"""
        content_selectors = [
            'div.detay-icerik',
            'div.article-content',
            'div.news-content',
            'div.content'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Reklamları ve gereksiz elementleri temizle
                for tag in content_div.find_all(['script', 'style', 'nav', 'aside', 'footer']):
                    tag.decompose()
                
                # Paragrafları topla
                paragraphs = []
                for p in content_div.find_all(['p', 'h3', 'h4']):
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        paragraphs.append(text)
                
                return '\n\n'.join(paragraphs)
        
        return ""
    
    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Meta verileri çıkar - tüm mevcut bilgiler"""
        metadata = {}
        
        # Başlık
        title_tag = soup.find('h1') or soup.find('title')
        metadata['title'] = title_tag.get_text().strip() if title_tag else ""
        
        # Yazar ve konum bilgisi
        author_selectors = [
            'span[style*="float:left"]',
            '.author',
            '.byline'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author_text = author_elem.get_text().strip()
                metadata['author'] = author_text.replace('|', '').strip()
                break
        else:
            metadata['author'] = ""
        
        # Konum bilgisi (h6 tag)
        location_elem = soup.find('h6')
        metadata['location'] = location_elem.get_text().strip() if location_elem else ""
        
        # Tarih bilgileri - yayın ve güncelleme
        date_elem = soup.select_one('.tarih, .date, .publish-date')
        if date_elem:
            date_text = date_elem.get_text().strip()
            metadata['publish_date'] = date_text
            
            # Güncelleme tarihini ayır
            if 'Güncelleme' in date_text:
                parts = date_text.split('Güncelleme')
                metadata['update_date'] = parts[1].strip().replace(':', '').strip() if len(parts) > 1 else ""
            else:
                metadata['update_date'] = ""
        else:
            metadata['publish_date'] = ""
            metadata['update_date'] = ""
        
        # Meta tags - SEO ve social media
        metadata.update(self._extract_meta_tags(soup))
        
        # Ana görsel ve alt text
        main_img = soup.select_one('img.detay-buyukFoto, .main-image img, .article-image img')
        if main_img and main_img.get('src'):
            metadata['main_image_url'] = urljoin(self.base_url, main_img['src'])
            metadata['main_image_alt'] = main_img.get('alt', '')
        else:
            metadata['main_image_url'] = ""
            metadata['main_image_alt'] = ""
        
        # Tüm görseller ve alt textleri
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', '')
            if src and not src.startswith('data:'):
                full_url = urljoin(self.base_url, src)
                if full_url not in [img_data['url'] for img_data in images]:
                    images.append({
                        'url': full_url,
                        'alt': alt,
                        'width': img.get('width'),
                        'height': img.get('height')
                    })
        
        metadata['images_detailed'] = images
        metadata['image_urls'] = [img['url'] for img in images]  # Backward compatibility
        
        # Etiketler/konular
        tags = []
        tag_links = soup.select('.detay-paylas a.btn-outline-secondary, .tags a')
        for link in tag_links:
            tag_text = link.get_text().strip()
            if tag_text:
                tags.append(tag_text)
        
        metadata['tags'] = tags
        
        # Kategori
        category_elem = soup.select_one('.detay-news-category a, .category a')
        metadata['category'] = category_elem.get_text().strip() if category_elem else ""
        
        # Paylaşım linkleri
        metadata['sharing_urls'] = self._extract_sharing_urls(soup)
        
        # Benzer haberler
        metadata['related_articles'] = self._extract_related_articles(soup)
        
        # Fotoğraf editör bilgileri
        photo_credit = soup.select_one('.detay-foto-editor a, .photo-credit')
        metadata['photo_credit'] = photo_credit.get_text().strip() if photo_credit else ""
        
        return metadata
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict:
        """SEO ve social media meta taglarını çıkar"""
        meta_data = {}
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_data['meta_description'] = meta_desc.get('content', '') if meta_desc else ""
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        meta_data['meta_keywords'] = meta_keywords.get('content', '') if meta_keywords else ""
        
        # Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        meta_data['og_title'] = og_title.get('content', '') if og_title else ""
        
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        meta_data['og_description'] = og_desc.get('content', '') if og_desc else ""
        
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        meta_data['og_image'] = og_image.get('content', '') if og_image else ""
        
        og_url = soup.find('meta', attrs={'property': 'og:url'})
        meta_data['og_url'] = og_url.get('content', '') if og_url else ""
        
        # Twitter tags
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        meta_data['twitter_title'] = twitter_title.get('content', '') if twitter_title else ""
        
        twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
        meta_data['twitter_description'] = twitter_desc.get('content', '') if twitter_desc else ""
        
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image:src'})
        meta_data['twitter_image'] = twitter_image.get('content', '') if twitter_image else ""
        
        return meta_data
    
    def _extract_sharing_urls(self, soup: BeautifulSoup) -> dict:
        """Sosyal medya paylaşım linklerini çıkar"""
        sharing = {}
        
        # WhatsApp
        whatsapp_btn = soup.find('a', {'id': 'whatsapp'})
        if whatsapp_btn:
            sharing['whatsapp_text'] = whatsapp_btn.get('data-text', '')
            sharing['whatsapp_url'] = whatsapp_btn.get('data-link', '')
        
        # BIP
        bip_btn = soup.find('a', {'id': 'bip'})
        if bip_btn:
            sharing['bip_text'] = bip_btn.get('data-text', '')
            sharing['bip_url'] = bip_btn.get('data-link', '')
        
        # Facebook
        fb_btn = soup.find('a', class_='facebook')
        if fb_btn:
            sharing['facebook_url'] = fb_btn.get('href', '')
        
        # Twitter
        twitter_btn = soup.find('a', class_='twitter')
        if twitter_btn:
            sharing['twitter_url'] = twitter_btn.get('href', '')
        
        # LinkedIn
        linkedin_btn = soup.find('a', class_='linkedin')
        if linkedin_btn:
            sharing['linkedin_url'] = linkedin_btn.get('href', '')
        
        return sharing
    
    def _extract_related_articles(self, soup: BeautifulSoup) -> List[dict]:
        """Benzer haberleri çıkar"""
        related = []
        
        # Benzer haberler bölümü
        related_section = soup.select_one('.detay-benzerHaberler, .related-articles')
        if related_section:
            links = related_section.find_all('a')
            for link in links:
                href = link.get('href')
                if href and '/tr/' in href:
                    title = link.get_text().strip()
                    img = link.find('img')
                    
                    if title and len(title) > 10:  # Minimum title length
                        related_item = {
                            'title': title,
                            'url': urljoin(self.base_url, href),
                            'image_url': urljoin(self.base_url, img['src']) if img and img.get('src') else ""
                        }
                        related.append(related_item)
        
        return related[:5]  # Maximum 5 benzer haber
    
    def scrape_article(self, url: str) -> Optional[ScrapedNewsContent]:
        """Tek makaleyi scrape et - tüm verilerle"""
        if not self._is_aa_url(url):
            self.logger.warning(f"AA URL değil: {url}")
            return None
        
        soup = self._fetch_page(url)
        if not soup:
            return None
        
        try:
            # İçerik çıkar
            article_text = self._extract_article_content(soup)
            
            # Metadata çıkar
            metadata = self._extract_metadata(soup)
            
            scraped_content = ScrapedNewsContent(
                url=url,
                full_content=article_text,
                article_text=article_text,
                location=metadata.get('location', ''),
                author=metadata.get('author', ''),
                publish_date=metadata.get('publish_date', ''),
                update_date=metadata.get('update_date', ''),
                main_image_url=metadata.get('main_image_url', ''),
                main_image_alt=metadata.get('main_image_alt', ''),
                image_urls=metadata.get('image_urls', []),
                images_detailed=metadata.get('images_detailed', []),
                tags=metadata.get('tags', []),
                category=metadata.get('category', ''),
                meta_description=metadata.get('meta_description', ''),
                meta_keywords=metadata.get('meta_keywords', ''),
                og_title=metadata.get('og_title', ''),
                og_description=metadata.get('og_description', ''),
                og_image=metadata.get('og_image', ''),
                og_url=metadata.get('og_url', ''),
                twitter_title=metadata.get('twitter_title', ''),
                twitter_description=metadata.get('twitter_description', ''),
                twitter_image=metadata.get('twitter_image', ''),
                sharing_urls=metadata.get('sharing_urls', {}),
                related_articles=metadata.get('related_articles', []),
                photo_credit=metadata.get('photo_credit', '')
            )
            
            self.logger.info(f"Scraping başarılı: {scraped_content.get_character_count()} karakter")
            return scraped_content
            
        except Exception as e:
            self.logger.error(f"Scraping hatası: {e}")
            return None
    
    def scrape_multiple_articles(self, urls: List[str]) -> List[Optional[ScrapedNewsContent]]:
        """Birden fazla makaleyi scrape et"""
        results = []
        
        for i, url in enumerate(urls):
            self.logger.info(f"Scraping {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_article(url)
            results.append(result)
            
            # Rate limiting
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        successful_count = sum(1 for r in results if r is not None)
        self.logger.info(f"Scraping tamamlandı: {successful_count}/{len(urls)} başarılı")
        
        return results
    
    def _is_aa_url(self, url: str) -> bool:
        """AA URL kontrolü"""
        try:
            parsed = urlparse(url)
            return 'aa.com.tr' in parsed.netloc
        except:
            return False


# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = AANewsScraper()
    
    # Test URL'i
    test_url = "https://www.aa.com.tr/tr/guncel/test-haber/123456"
    
    print(f"Test URL scraping: {test_url}")
    result = scraper.scrape_article(test_url)
    
    if result:
        print(f"Başarılı! {result.get_character_count()} karakter çekildi")
        print(f"Yazar: {result.author}")
        print(f"Konum: {result.location}")
        print(f"Görsel sayısı: {len(result.image_urls)}")
    else:
        print("Scraping başarısız")