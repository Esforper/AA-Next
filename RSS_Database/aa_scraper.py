import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from typing import Dict, List, Optional
import re

""" 
pip install requests beautifulsoup4
"""

class AANewsScraper:
    def __init__(self, input_file: str = 'aa_news_data.json', output_file: str = 'aa_news_scraped.json'):
        self.input_file = input_file
        self.output_file = output_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.scraped_data = []
        
    def load_rss_data(self) -> Dict:
        """RSS verilerini JSON dosyasından yükle"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Hata: {self.input_file} dosyası bulunamadı!")
            return {}
        except json.JSONDecodeError:
            print(f"Hata: {self.input_file} geçerli bir JSON dosyası değil!")
            return {}
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Tek bir haber makalesini scrape et"""
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_data = {
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Haber başlığı
            title_elem = soup.find('h1', class_='detay-baslik') or soup.find('h1')
            article_data['full_title'] = title_elem.get_text(strip=True) if title_elem else None
            
            # Haber özeti/spot
            summary_elem = soup.find('div', class_='detay-spot') or soup.find('p', class_='lead')
            article_data['summary'] = summary_elem.get_text(strip=True) if summary_elem else None
            
            # Haber içeriği - tüm paragraflar
            content_div = soup.find('div', class_='detay-icerik') or soup.find('article')
            if content_div:
                paragraphs = content_div.find_all('p')
                # article_data['content'] = ' '.join([p.get_text(strip=True) for p in paragraphs])
                article_data['paragraphs'] = [p.get_text(strip=True) for p in paragraphs]
            else:
                article_data['content'] = None
                article_data['paragraphs'] = []
            
            # Etiketler (tags)
            tags = []
            tag_container = soup.find('div', class_='detay-etiketler') or soup.find('div', class_='tags')
            if tag_container:
                tag_links = tag_container.find_all('a')
                tags = [tag.get_text(strip=True) for tag in tag_links]
            article_data['tags'] = tags
            
            # Hashtag'ler - içerikten çıkar
            hashtags = []
            if article_data.get('content'):
                hashtags = re.findall(r'#\w+', article_data['content'])
            article_data['hashtags'] = list(set(hashtags))
            
            # Meta açıklama
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            article_data['meta_description'] = meta_desc.get('content') if meta_desc else None
            
            # Meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                keywords = meta_keywords.get('content', '').split(',')
                article_data['keywords'] = [k.strip() for k in keywords if k.strip()]
            else:
                article_data['keywords'] = []
            
            # Yazar bilgisi
            author_elem = soup.find('div', class_='detay-yazar') or soup.find('span', class_='author')
            article_data['author'] = author_elem.get_text(strip=True) if author_elem else None
            
            # Yayın tarihi (sayfadan)
            date_elem = soup.find('div', class_='detay-tarih') or soup.find('time')
            article_data['published_date'] = date_elem.get_text(strip=True) if date_elem else None
            
            # Kategori
            category_elem = soup.find('div', class_='detay-kategori') or soup.find('a', class_='category')
            article_data['category_full'] = category_elem.get_text(strip=True) if category_elem else None
            
            # İlgili haberler
            related_news = []
            related_container = soup.find('div', class_='ilgili-haberler') or soup.find('div', class_='related')
            if related_container:
                related_links = related_container.find_all('a')
                related_news = [
                    {
                        'title': link.get_text(strip=True),
                        'url': link.get('href')
                    } for link in related_links if link.get('href')
                ]
            article_data['related_news'] = related_news
            
            # Görseller
            images = []
            img_tags = soup.find_all('img', class_='detay-resim') or soup.find_all('img', class_='article-image')
            for img in img_tags:
                if img.get('src'):
                    images.append({
                        'src': img.get('src'),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            article_data['images'] = images
            
            # Video varsa
            video_elem = soup.find('video') or soup.find('iframe', class_='video')
            article_data['has_video'] = video_elem is not None
            if video_elem:
                article_data['video_url'] = video_elem.get('src', '')
            
            # Toplam kelime sayısı
            if article_data.get('content'):
                article_data['word_count'] = len(article_data['content'].split())
            
            return article_data
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP Hatası ({url}): {e}")
            return None
        except Exception as e:
            print(f"Genel Hata ({url}): {e}")
            return None
    
    def save_single_item(self, item: Dict):
        """Tek bir veriyi hemen JSON dosyasına kaydet"""
        try:
            # Mevcut dosyayı oku
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []
            
            # Yeni veriyi ekle
            existing_data.append(item)
            
            # Dosyaya yaz
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
    
    def scrape_all(self, delay: float = 1.0):
        """Tüm RSS verilerini scrape et ve anında kaydet"""
        rss_data = self.load_rss_data()
        
        if not rss_data:
            print("RSS verisi bulunamadı!")
            return
        
        total = len(rss_data)
        print(f"\nToplam {total} haber bulundu. Scraping başlıyor...\n")
        
        success_count = 0
        
        for idx, (guid, news_item) in enumerate(rss_data.items(), 1):
            print(f"[{idx}/{total}] İşleniyor...")
            
            # RSS verisini kopyala
            combined_data = news_item.copy()
            
            # Web scraping yap
            scraped = self.scrape_article(news_item['link'])
            
            if scraped:
                # Scraped verileri ekle
                combined_data['scraped_content'] = scraped
                combined_data['scraping_success'] = True
                success_count += 1
                print(f"  ✓ Başarılı! JSON'a kaydediliyor...")
            else:
                combined_data['scraping_success'] = False
                combined_data['scraped_content'] = None
                print(f"  ✗ Başarısız!")
            
            # Hemen JSON dosyasına kaydet
            self.save_single_item(combined_data)
            self.scraped_data.append(combined_data)
            
            # Rate limiting
            if idx < total:
                time.sleep(delay)
        
        print(f"\n✓ Scraping tamamlandı! Başarılı: {success_count}/{total}")
    
    def save_to_json(self):
        """Özet istatistikleri göster"""
        try:
            # İstatistikler
            success_count = sum(1 for item in self.scraped_data if item.get('scraping_success'))
            print(f"\n{'='*60}")
            print(f"İstatistikler:")
            print(f"  - Toplam haber: {len(self.scraped_data)}")
            print(f"  - Başarılı: {success_count}")
            print(f"  - Başarısız: {len(self.scraped_data) - success_count}")
            print(f"  - Dosya: {self.output_file}")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"İstatistik hatası: {e}")
    
    def run(self, delay: float = 1.0):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 60)
        print("AA News Web Scraper")
        print("=" * 60)
        
        start_time = time.time()
        
        self.scrape_all(delay=delay)
        self.save_to_json()
        
        elapsed = time.time() - start_time
        print(f"\nToplam süre: {elapsed:.2f} saniye")
        print("=" * 60)


if __name__ == "__main__":
    # Scraper'ı başlat
    scraper = AANewsScraper(
        input_file='aa_news_data.json',
        output_file='aa_news_scraped.json'
    )
    
    # Çalıştır (1 saniye bekleme ile)
    scraper.run(delay=1.0)