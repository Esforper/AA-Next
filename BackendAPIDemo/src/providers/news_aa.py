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
    Basit web scraping
    Mevcut scraping kodunu buraya kopyala
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
        
        # Basit images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and 'http' in src:
                images.append(src)
        
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
