# ================================
# src/providers/news_aa.py - Süper Basit!
# ================================

"""
AA News Provider - Basit ve Hızlı
Mevcut kodunun basitleştirilmiş hali
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from datetime import datetime

from ..models.news import Article
from . import register_provider

# Basit session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})


def filter_aa_images(soup, base_url: str):
    """AA.com.tr'ye özel minimal görsel filtreleme"""
    images = []
    main_image = None
    
    # AA.com.tr için base domain
    AA_DOMAIN = 'https://www.aa.com.tr'
    AA_CDN = 'https://cdnuploads.aa.com.tr'
    
    def normalize_url(src):
        """URL'i normalize et"""
        if not src:
            return None
            
        # Zaten tam URL ise direkt döndür
        if src.startswith('http://') or src.startswith('https://'):
            return src
            
        # // ile başlıyorsa https: ekle
        if src.startswith('//'):
            return 'https:' + src
            
        # / ile başlıyorsa (relative path)
        if src.startswith('/'):
            # /uploads/ ile başlayanlar CDN'den gelir
            if src.startswith('/uploads/'):
                return AA_CDN + src
            # Diğerleri ana domainden
            else:
                return AA_DOMAIN + src
        
        return None
    
    # 1. Ana görseli bul (detay-buyukFoto)
    main_img = soup.select_one('img.detay-buyukFoto, img[class*="detay-buyuk"]')
    if main_img and main_img.get('src'):
        src = normalize_url(main_img.get('src'))
        if src:
            main_image = src
            images.append(src)
    
    # 2. İçerik görsellerini bul (detay-icerik içinde)
    content_div = soup.select_one('div.detay-icerik')
    if content_div:
        for img in content_div.find_all('img'):
            src = normalize_url(img.get('src'))
            
            if src and src != main_image:
                # AA'nın uploads klasöründen gelenleri tercih et
                if any(keyword in src.lower() for keyword in ['/uploads/', 'cdnuploads.aa.com.tr', '/thumbs_']):
                    images.append(src)
    
    # 3. Eğer hiç görsel yoksa eski yöntemi dene
    if not images:
        for img in soup.find_all('img'):
            src = normalize_url(img.get('src'))
            if src:
                # İstenmeyen pattern'leri filtrele
                if not any(pattern in src.lower() for pattern in ['logo', 'icon', 'button', 'social', 'facebook', 'twitter', 'instagram']):
                    images.append(src)
    
    return list(set(images))  # Duplicate'ları çıkar

async def get_latest_news(count: int = 10, category: str = "guncel", **kwargs) -> List[Article]:
    """
    AA'dan son haberleri çek
    Basit implementation - mevcut kodunu buraya kopyala
    """
    try:
        # RSS çek
        rss_url = f"https://www.aa.com.tr/tr/rss/default?cat={category}"
        response = session.get(rss_url, timeout=30)
        feed = feedparser.parse(response.content)
        
        articles = []
        for entry in feed.entries[:count]:
            # Basit parse
            article = Article(
                id=f"aa_{hash(entry.link)}",
                title=entry.title,
                content=getattr(entry, 'summary', ''),
                summary=getattr(entry, 'summary', ''),
                url=entry.link,
                category=category,
                source="aa",
                published_at=datetime.now()  # Basit tarih
            )
            
            # Web scraping istiyorsa (opsiyonel)
            if kwargs.get('enable_scraping', False):
                scraped = await scrape_article(entry.link)
                if scraped:
                    article.content = scraped.get('content', article.content)
                    article.author = scraped.get('author')
                    article.images = scraped.get('images', [])
            
            articles.append(article)
        
        print(f"✅ AA News: {len(articles)} articles from {category}")
        return articles
        
    except Exception as e:
        print(f"❌ AA News error: {e}")
        return []

async def scrape_article(url: str) -> Dict:
    """
    Basit web scraping - İyileştirilmiş görsel filtreleme ile
    """
    try:
        response = session.get(url, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basit content extraction
        content_div = soup.select_one('div.detay-icerik')
        content = ""
        if content_div:
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 20:
                    paragraphs.append(text)
            content = '\n\n'.join(paragraphs)
        
        # Basit author extraction  
        author = None
        author_elem = soup.select_one('span[style*="float:left"]')
        if author_elem:
            author = author_elem.get_text().strip()
        
        # İyileştirilmiş görsel filtreleme
        images = filter_aa_images(soup, url)
        
        return {
            'content': content,
            'author': author,
            'images': images
        }
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return {}

# Provider'ı kaydet
register_provider("news_aa", {
    "get_latest_news": get_latest_news,
    "scrape_article": scrape_article
})