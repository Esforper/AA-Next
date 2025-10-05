# ================================
# src/providers/news_aa.py
# ================================

"""
AA News Provider - aa_scraper mantığı ile geliştirilmiş
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
from datetime import datetime

from ..models.news import Article
from . import register_provider

# Session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# AA.com.tr domains
AA_DOMAIN = 'https://www.aa.com.tr'
AA_CDN = 'https://cdnuploads.aa.com.tr'


def normalize_url(src: str) -> str:
    """URL normalize et"""
    if not src:
        return None
    if src.startswith('http://') or src.startswith('https://'):
        return src
    if src.startswith('//'):
        return 'https:' + src
    if src.startswith('/'):
        return AA_CDN + src if src.startswith('/uploads/') else AA_DOMAIN + src
    return None


def filter_aa_images(soup, base_url: str) -> List[str]:
    """AA görselleri filtrele"""
    images = []
    main_image = None
    
    # Ana görsel
    main_img = soup.select_one('img.detay-buyukFoto, img[class*="detay-buyuk"]')
    if main_img and main_img.get('src'):
        src = normalize_url(main_img.get('src'))
        if src:
            main_image = src
            images.append(src)
    
    # İçerik görselleri
    content_div = soup.select_one('div.detay-icerik')
    if content_div:
        for img in content_div.find_all('img'):
            src = normalize_url(img.get('src'))
            if src and src != main_image:
                if any(k in src.lower() for k in ['/uploads/', 'cdnuploads.aa.com.tr', '/thumbs_']):
                    images.append(src)
    
    # Fallback: Tüm görselleri tara
    if not images:
        for img in soup.find_all('img'):
            src = normalize_url(img.get('src'))
            if src:
                if not any(p in src.lower() for p in ['logo', 'icon', 'button', 'social', 'facebook', 'twitter', 'instagram']):
                    images.append(src)
    
    return list(set(images))


async def get_latest_news(count: int = 10, category: str = "guncel", **kwargs) -> List[Article]:
    """AA'dan son haberleri çek"""
    try:
        rss_url = f"https://www.aa.com.tr/tr/rss/default?cat={category}"
        response = session.get(rss_url, timeout=30)
        feed = feedparser.parse(response.content)
        
        articles = []
        for entry in feed.entries[:count]:
            article = Article(
                id=f"aa_{hash(entry.link)}",
                title=entry.title,
                content=getattr(entry, 'summary', ''),  # RSS'den gelen özet
                summary=getattr(entry, 'summary', ''),
                url=entry.link,
                category=category,
                source="aa",
                published_at=datetime.now()
            )
            
            # Scraping istenmişse
            if kwargs.get('enable_scraping', False):
                scraped = await scrape_article(entry.link)
                if scraped:
                    # ✅ content artık List[str] olarak dönüyor
                    article.content = scraped.get('paragraphs', scraped.get('content', article.content))
                    article.author = scraped.get('author')
                    article.images = scraped.get('images', [])
                    article.tags = scraped.get('tags', [])
                    article.keywords = scraped.get('keywords', [])
                    article.hashtags = scraped.get('hashtags', [])
                    article.meta_description = scraped.get('meta_description')
            
            articles.append(article)
        
        print(f"✅ AA News: {len(articles)} articles from {category}")
        return articles
        
    except Exception as e:
        print(f"❌ AA News error: {e}")
        return []


async def scrape_article(url: str) -> Dict:
    """
    ✅ aa_scraper mantığı ile geliştirilmiş web scraping
    """
    try:
        response = session.get(url, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        scraped_data = {}
        
        # Başlık
        title_elem = soup.find('h1', class_='detay-baslik') or soup.find('h1')
        scraped_data['title'] = title_elem.get_text(strip=True) if title_elem else None
        
        # Özet/Spot
        summary_elem = soup.find('div', class_='detay-spot') or soup.find('p', class_='lead')
        scraped_data['summary'] = summary_elem.get_text(strip=True) if summary_elem else None
        
        # ✅ İçerik - Paragraflar (aa_scraper mantığı)
        content_div = soup.find('div', class_='detay-icerik') or soup.find('article')
        if content_div:
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 20:  # Minimum uzunluk kontrolü
                    paragraphs.append(text)
            
            scraped_data['paragraphs'] = paragraphs  # ✅ List[str]
            scraped_data['content'] = ' '.join(paragraphs)  # Fallback str
        else:
            scraped_data['paragraphs'] = []
            scraped_data['content'] = ""
        
        # ✅ Tags (aa_scraper mantığı)
        tags = []
        tag_container = soup.find('div', class_='detay-etiketler') or soup.find('div', class_='tags')
        if tag_container:
            tag_links = tag_container.find_all('a')
            tags = [tag.get_text(strip=True) for tag in tag_links]
        scraped_data['tags'] = tags
        
        # ✅ Hashtags (aa_scraper mantığı)
        hashtags = []
        if scraped_data.get('content'):
            hashtags = re.findall(r'#\w+', scraped_data['content'])
        scraped_data['hashtags'] = list(set(hashtags))
        
        # ✅ Meta description (aa_scraper mantığı)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        scraped_data['meta_description'] = meta_desc.get('content') if meta_desc else None
        
        # ✅ Meta keywords (aa_scraper mantığı)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '').split(',')
            scraped_data['keywords'] = [k.strip() for k in keywords if k.strip()]
        else:
            scraped_data['keywords'] = []
        
        # Yazar
        author_elem = soup.find('div', class_='detay-yazar') or soup.find('span', class_='author') or soup.select_one('span[style*="float:left"]')
        scraped_data['author'] = author_elem.get_text(strip=True) if author_elem else None
        
        # Location
        location_elem = soup.find('span', class_='location') or soup.find('div', class_='detay-konum')
        scraped_data['location'] = location_elem.get_text(strip=True) if location_elem else None
        
        # Görseller (geliştirilmiş filtreleme)
        scraped_data['images'] = filter_aa_images(soup, url)
        
        return scraped_data
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return {}


# Provider kaydet
register_provider("news_aa", {
    "get_latest_news": get_latest_news,
    "scrape_article": scrape_article
})