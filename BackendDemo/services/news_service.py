"""
News Service
RSS ve Web Scraper'ı birleştiren ana haber servisi
"""

from typing import List, Optional, Dict, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from models.news_models import RSSNewsItem, ScrapedNewsContent, CompleteNewsArticle
from services.rss_reader import RSSReader
from services.web_scraper import AANewsScraper


class NewsService:
    """Ana haber servisi - RSS + Web Scraping birleşimi"""
    
    def __init__(self, 
                 default_category: str = "guncel",
                 scraping_delay: float = 1.5,
                 max_workers: int = 3,
                 enable_scraping: bool = True):
        
        self.enable_scraping = enable_scraping
        self.max_workers = max_workers
        
        # Servisleri başlat
        self.rss_reader = RSSReader(default_category=default_category)
        self.web_scraper = AANewsScraper(delay=scraping_delay) if enable_scraping else None
        
        self.logger = logging.getLogger(__name__)
    
    def get_latest_news(self, 
                       count: int = 10, 
                       category: str = None,
                       enable_scraping: bool = None) -> List[CompleteNewsArticle]:
        """Son haberleri RSS + scraping ile al"""
        
        # Scraping ayarı
        scraping_enabled = enable_scraping if enable_scraping is not None else self.enable_scraping
        
        # RSS'den haberleri çek
        if category:
            rss_items = self.rss_reader.get_news_by_category(category, count)
        else:
            rss_items = self.rss_reader.get_latest_news(count)
        
        if not rss_items:
            self.logger.warning("RSS'den haber çekilemedi")
            return []
        
        self.logger.info(f"{len(rss_items)} haber RSS'den çekildi")
        
        # Complete news article'ları oluştur
        complete_articles = []
        for rss_item in rss_items:
            article = CompleteNewsArticle(rss_data=rss_item)
            complete_articles.append(article)
        
        # Scraping yapılacaksa
        if scraping_enabled and self.web_scraper:
            self._enrich_articles_with_scraping(complete_articles)
        
        return complete_articles
    
    def get_news_by_categories(self, 
                              categories: List[str], 
                              count_per_category: int = 5,
                              enable_scraping: bool = None) -> Dict[str, List[CompleteNewsArticle]]:
        """Birden fazla kategoriden haber al"""
        
        scraping_enabled = enable_scraping if enable_scraping is not None else self.enable_scraping
        results = {}
        
        # Her kategori için RSS çek
        rss_results = self.rss_reader.get_news_from_multiple_categories(
            categories, count_per_category
        )
        
        # Complete articles oluştur
        for category, rss_items in rss_results.items():
            complete_articles = []
            for rss_item in rss_items:
                article = CompleteNewsArticle(rss_data=rss_item)
                complete_articles.append(article)
            
            results[category] = complete_articles
        
        # Scraping yapılacaksa tüm articlelar için
        if scraping_enabled and self.web_scraper:
            all_articles = []
            for articles in results.values():
                all_articles.extend(articles)
            
            self._enrich_articles_with_scraping(all_articles)
        
        return results
    
    def get_single_article(self, url: str, with_scraping: bool = True) -> Optional[CompleteNewsArticle]:
        """Tek bir makaleyi URL'den al"""
        
        if not with_scraping or not self.web_scraper:
            # Sadece RSS verisini dene (url match)
            self.logger.warning("Scraping kapalı - sadece URL bilgisi")
            rss_item = RSSNewsItem(link=url, title="URL'den makale")
            return CompleteNewsArticle(rss_data=rss_item)
        
        # Scraping ile tam veri al
        scraped_content = self.web_scraper.scrape_article(url)
        
        if scraped_content:
            # RSS benzeri veri oluştur
            rss_item = RSSNewsItem(
                title=scraped_content.og_title or "Scraped Article",
                link=url,
                summary=scraped_content.meta_description or scraped_content.og_description,
                author=scraped_content.author,
                category=scraped_content.category
            )
            
            article = CompleteNewsArticle(
                rss_data=rss_item,
                scraped_data=scraped_content,
                scraping_attempted=True,
                scraping_successful=True
            )
            
            return article
        
        return None
    
    def _enrich_articles_with_scraping(self, articles: List[CompleteNewsArticle]) -> None:
        """Makaleleri scraping ile zenginleştir"""
        
        if not self.web_scraper:
            self.logger.warning("Web scraper mevcut değil")
            return
        
        self.logger.info(f"{len(articles)} makale için scraping başlatılıyor...")
        start_time = time.time()
        
        # URL'leri topla
        urls = [article.rss_data.link for article in articles]
        
        if self.max_workers == 1:
            # Sıralı işlem
            scraped_results = self.web_scraper.scrape_multiple_articles(urls)
        else:
            # Paralel işlem
            scraped_results = self._scrape_parallel(urls)
        
        # Sonuçları birleştir
        successful_count = 0
        for article, scraped_content in zip(articles, scraped_results):
            article.scraping_attempted = True
            
            if scraped_content:
                article.scraped_data = scraped_content
                article.scraping_successful = True
                successful_count += 1
            else:
                article.scraping_successful = False
                article.scraping_error = "Scraping başarısız"
        
        elapsed_time = time.time() - start_time
        self.logger.info(
            f"Scraping tamamlandı: {successful_count}/{len(articles)} başarılı "
            f"({elapsed_time:.1f}s)"
        )
    
    def _scrape_parallel(self, urls: List[str]) -> List[Optional[ScrapedNewsContent]]:
        """Paralel scraping"""
        results = [None] * len(urls)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Future'ları başlat
            future_to_index = {
                executor.submit(self.web_scraper.scrape_article, url): i 
                for i, url in enumerate(urls)
            }
            
            # Sonuçları topla
            for future in future_to_index:
                index = future_to_index[future]
                try:
                    result = future.result(timeout=30)
                    results[index] = result
                except Exception as e:
                    self.logger.error(f"Paralel scraping hatası (index {index}): {e}")
        
        return results
    
    def filter_articles(self, 
                       articles: List[CompleteNewsArticle],
                       min_chars: int = 100,
                       max_chars: int = 10000,
                       require_scraping: bool = False,
                       keywords: List[str] = None) -> List[CompleteNewsArticle]:
        """Makaleleri filtrele"""
        
        filtered = []
        
        for article in articles:
            # Karakter sayısı kontrolü
            char_count = article.get_character_count()
            if not (min_chars <= char_count <= max_chars):
                continue
            
            # Scraping zorunluluğu
            if require_scraping and not article.scraping_successful:
                continue
            
            # Anahtar kelime kontrolü
            if keywords:
                content = article.get_content_for_tts().lower()
                if not any(keyword.lower() in content for keyword in keywords):
                    continue
            
            filtered.append(article)
        
        self.logger.info(f"Filtreleme: {len(filtered)}/{len(articles)} makale kaldı")
        return filtered
    
    def get_articles_summary(self, articles: List[CompleteNewsArticle]) -> Dict[str, Any]:
        """Makale listesi özeti"""
        
        total_count = len(articles)
        scraped_count = sum(1 for a in articles if a.scraping_successful)
        complete_count = sum(1 for a in articles if a.is_complete())
        
        total_chars = sum(a.get_character_count() for a in articles)
        avg_chars = total_chars / total_count if total_count > 0 else 0
        
        categories = {}
        for article in articles:
            cat = article.rss_data.category or 'unknown'
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_articles': total_count,
            'scraped_successfully': scraped_count,
            'complete_articles': complete_count,
            'total_characters': total_chars,
            'average_characters': int(avg_chars),
            'categories': categories,
            'scraping_success_rate': f"{(scraped_count/total_count*100):.1f}%" if total_count > 0 else "0%"
        }
    
    def search_articles(self, 
                       query: str, 
                       category: str = None,
                       count: int = 20) -> List[CompleteNewsArticle]:
        """Haber ara (RSS içinde)"""
        
        if category:
            articles = self.get_latest_news(count * 2, category, enable_scraping=False)
        else:
            articles = self.get_latest_news(count * 2, enable_scraping=False)
        
        # Filtrele
        query_lower = query.lower()
        filtered = []
        
        for article in articles:
            content = f"{article.rss_data.title} {article.rss_data.summary}".lower()
            if query_lower in content:
                filtered.append(article)
                if len(filtered) >= count:
                    break
        
        # Bulunanları scraping ile zenginleştir
        if filtered and self.enable_scraping:
            self._enrich_articles_with_scraping(filtered)
        
        return filtered


# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # News service oluştur
    news_service = NewsService(enable_scraping=True, max_workers=2)
    
    print("=== NEWS SERVICE TEST ===")
    
    # Son 3 haber al
    print("\n1. Son 3 haber (güncel kategori):")
    articles = news_service.get_latest_news(count=3)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get_title()}")
        print(f"   Scraping: {'✓' if article.scraping_successful else '✗'}")
        print(f"   Karakter: {article.get_character_count()}")
        print(f"   Tam: {'✓' if article.is_complete() else '✗'}")
    
    # Özet bilgiler
    summary = news_service.get_articles_summary(articles)
    print(f"\n=== ÖZET ===")
    print(f"Toplam: {summary['total_articles']}")
    print(f"Scraping başarı: {summary['scraping_success_rate']}")
    print(f"Ortalama karakter: {summary['average_characters']}")