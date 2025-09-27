# ================================
# src/services/content.py - Content Management
# ================================

"""
Content Service - News, Articles, Media yönetimi
Provider'ları kullanarak business logic sağlar
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.news import Article, NewsResponse, NewsFilter
from ..models.base import BaseResponse
from ..providers import get_provider
from ..config import settings

class ContentService:
    """Content management service"""
    
    def __init__(self):
        self.news_provider_name = f"news_{settings.news_provider}"
        
    async def get_latest_news(self, 
                             count: int = 10, 
                             category: str = None, 
                             enable_scraping: bool = None) -> NewsResponse:
        """
        Son haberleri al
        Provider'dan haberleri çekip business logic uygula
        """
        try:
            # Provider'ı al
            provider = get_provider(self.news_provider_name)
            if not provider:
                return NewsResponse(
                    success=False,
                    message=f"News provider '{self.news_provider_name}' not found",
                    articles=[],
                    total_count=0
                )
            
            # Category default
            category = category or settings.news_default_category
            
            # Scraping default
            if enable_scraping is None:
                enable_scraping = settings.news_scraping_enabled
            
            # Provider'dan haberleri al
            articles = await provider["get_latest_news"](
                count=count,
                category=category,
                enable_scraping=enable_scraping
            )
            
            # Business logic: filtering, sorting etc.
            filtered_articles = self._apply_business_rules(articles)
            
            return NewsResponse(
                success=True,
                message=f"Retrieved {len(filtered_articles)} articles",
                articles=filtered_articles,
                total_count=len(filtered_articles),
                category=category,
                provider=settings.news_provider
            )
            
        except Exception as e:
            print(f"❌ Content service error: {e}")
            return NewsResponse(
                success=False,
                message=str(e),
                articles=[],
                total_count=0
            )
    
    async def get_article_by_url(self, url: str, enable_scraping: bool = True) -> Optional[Article]:
        """Tek makale al"""
        try:
            provider = get_provider(self.news_provider_name)
            if not provider or "scrape_article" not in provider:
                return None
            
            # Provider'dan makaleyi al
            scraped_data = await provider["scrape_article"](url)
            if not scraped_data:
                return None
            
            # Article oluştur
            article = Article(
                id=f"url_{hash(url)}",
                title=scraped_data.get('title', 'Article from URL'),
                content=scraped_data.get('content', ''),
                url=url,
                category='unknown',
                author=scraped_data.get('author'),
                images=scraped_data.get('images', []),
                source=settings.news_provider,
                published_at=datetime.now()
            )
            
            return article
            
        except Exception as e:
            print(f"❌ Get article error: {e}")
            return None
    
    async def search_news(self, query: str, category: str = None, count: int = 20) -> NewsResponse:
        """Haber ara"""
        try:
            # Önce haberleri al
            all_articles = await self.get_latest_news(
                count=count * 2,  # Filtreleme için fazla al
                category=category,
                enable_scraping=False  # Arama için scraping'e gerek yok
            )
            
            if not all_articles.success:
                return all_articles
            
            # Basit text search
            query_lower = query.lower()
            filtered = []
            
            for article in all_articles.articles:
                if (query_lower in article.title.lower() or 
                    query_lower in (article.summary or "").lower() or
                    query_lower in (article.content or "").lower()):
                    filtered.append(article)
                    if len(filtered) >= count:
                        break
            
            return NewsResponse(
                success=True,
                message=f"Found {len(filtered)} articles for '{query}'",
                articles=filtered,
                total_count=len(filtered),
                category=category,
                provider=settings.news_provider
            )
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return NewsResponse(
                success=False,
                message=str(e),
                articles=[],
                total_count=0
            )
    
    async def filter_articles(self, 
                             articles: List[Article], 
                             filters: NewsFilter) -> List[Article]:
        """Makale filtreleme"""
        filtered = articles
        
        # Category filter
        if filters.category:
            filtered = [a for a in filtered if a.category == filters.category]
        
        # Author filter
        if filters.author:
            filtered = [a for a in filtered if a.author and filters.author.lower() in a.author.lower()]
        
        # Character count filter
        if filters.min_chars:
            filtered = [a for a in filtered if len(a.content) >= filters.min_chars]
        if filters.max_chars:
            filtered = [a for a in filtered if len(a.content) <= filters.max_chars]
        
        # Keywords filter
        if filters.keywords:
            keyword_filtered = []
            for article in filtered:
                content_lower = f"{article.title} {article.content}".lower()
                if any(keyword.lower() in content_lower for keyword in filters.keywords):
                    keyword_filtered.append(article)
            filtered = keyword_filtered
        
        # Date filter (basit)
        if filters.date_from:
            filtered = [a for a in filtered if a.published_at and a.published_at >= filters.date_from]
        if filters.date_to:
            filtered = [a for a in filtered if a.published_at and a.published_at <= filters.date_to]
        
        return filtered
    
    def _apply_business_rules(self, articles: List[Article]) -> List[Article]:
        """Business rules uygula"""
        # 1. Duplicate removal (basit URL check)
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if str(article.url) not in seen_urls:
                seen_urls.add(str(article.url))
                unique_articles.append(article)
        
        # 2. Quality filter (çok kısa olanları çıkar)
        quality_articles = [a for a in unique_articles if len(a.title) > 10]
        
        # 3. Sort by published date (if available)
        try:
            quality_articles.sort(key=lambda x: x.published_at or datetime.min, reverse=True)
        except:
            pass  # Sorting failed, no problem
        
        return quality_articles
    
    async def get_trending_topics(self, count: int = 10) -> List[str]:
        """Trend olan konular (basit implementation)"""
        try:
            # Son haberleri al
            news_response = await self.get_latest_news(count=50, enable_scraping=False)
            if not news_response.success:
                return []
            
            # Tag'leri topla
            all_tags = []
            for article in news_response.articles:
                all_tags.extend(article.tags)
            
            # Tag frequency count (basit)
            tag_count = {}
            for tag in all_tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
            
            # En popüler tag'leri döndür
            trending = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
            return [tag for tag, count in trending[:count]]
            
        except Exception as e:
            print(f"❌ Trending topics error: {e}")
            return []

# Global instance
content_service = ContentService()