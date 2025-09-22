"""
RSS Reader Service
AA Ajansı RSS feed'ini güvenli şekilde parse eden servis
"""

import feedparser
import requests
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import time
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

from models.news_models import RSSNewsItem


class RSSReader:
    """AA Ajansı RSS feed okuyucu sınıfı"""
        
    def __init__(self, 
                 default_category: str = "guncel",
                 timeout: int = 30,
                 max_retries: int = 3,
                 user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"):
        
        self.default_category = default_category
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        
        # AA Ajansı RSS URL template
        self.rss_base_url = "https://www.aa.com.tr/tr/rss/default?cat={}"
        
        # Desteklenen kategoriler (AA'dan doğrulanmış)
        self.valid_categories = {
            'guncel', 'ekonomi', 'spor', 'kultur', 'dunya', 'politika', 
            'teknoloji', 'bilim-teknoloji', 'saglik', 'egitim', 'yasam', 
            'analiz', 'portre', 'futbol', 'basketbol', 'dunyadan-spor'
        }
        
        # Kategori açıklamaları
        self.category_descriptions = {
            'guncel': 'Güncel Haberler',
            'ekonomi': 'Ekonomi Haberleri',
            'spor': 'Spor Haberleri',
            'kultur': 'Kültür Haberleri',
            'dunya': 'Dünya Haberleri',
            'politika': 'Politika Haberleri',
            'teknoloji': 'Teknoloji Haberleri',
            'bilim-teknoloji': 'Bilim ve Teknoloji',
            'saglik': 'Sağlık Haberleri',
            'egitim': 'Eğitim Haberleri',
            'yasam': 'Yaşam Haberleri',
            'analiz': 'Analiz Yazıları',
            'portre': 'Portre Haberleri',
            'futbol': 'Futbol Haberleri',
            'basketbol': 'Basketbol Haberleri',
            'dunyadan-spor': 'Dünyadan Spor'
        }
        
        # Varsayılan RSS URL
        self.rss_url = self._get_category_url(default_category)
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
    
    def _get_category_url(self, category: str) -> str:
        """Kategori için RSS URL oluştur"""
        if category not in self.valid_categories:
            self.logger.warning(f"Geçersiz kategori '{category}', 'guncel' kullanılıyor")
            category = 'guncel'
        
        return self.rss_base_url.format(category)
    
    def _is_valid_category(self, category: str) -> bool:
        """Kategori geçerliliğini kontrol et"""
        return category.lower() in self.valid_categories
    
    def fetch_rss_content(self) -> Optional[str]:
        """RSS içeriğini çek"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"RSS feed çekiliyor (deneme {attempt + 1}/{self.max_retries}): {self.rss_url}")
                
                response = self.session.get(
                    self.rss_url, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # Content-Type kontrolü
                content_type = response.headers.get('content-type', '').lower()
                if 'xml' not in content_type and 'rss' not in content_type:
                    self.logger.warning(f"Beklenmeyen content-type: {content_type}")
                
                # Encoding kontrolü
                response.encoding = response.apparent_encoding or 'utf-8'
                
                content = response.text
                
                if not content or len(content) < 100:
                    raise ValueError("RSS içeriği çok kısa veya boş")
                
                # XML geçerliliği kontrolü
                try:
                    ET.fromstring(content.encode('utf-8'))
                except ET.ParseError as e:
                    self.logger.error(f"Geçersiz XML formatı: {e}")
                    continue
                
                self.logger.info(f"RSS başarıyla çekildi. İçerik boyutu: {len(content)} karakter")
                return content
                
            except requests.exceptions.Timeout:
                self.logger.error(f"Timeout hatası (deneme {attempt + 1})")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Bağlantı hatası (deneme {attempt + 1})")
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP hatası: {e.response.status_code} (deneme {attempt + 1})")
            except Exception as e:
                self.logger.error(f"Beklenmeyen hata: {e} (deneme {attempt + 1})")
            
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 2
                self.logger.info(f"{wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
        
        self.logger.error("RSS içeriği çekilemedi. Tüm denemeler başarısız")
        return None
    
    def parse_rss_feed(self, content: str) -> Optional[feedparser.FeedParserDict]:
        """RSS içeriğini parse et"""
        try:
            self.logger.info("RSS içeriği parse ediliyor...")
            
            # feedparser ile parse et
            feed = feedparser.parse(content)
            
            if feed.bozo:
                self.logger.warning(f"RSS parse hatası: {feed.bozo_exception}")
                # Hata olsa bile devam etmeyi dene
            
            if not hasattr(feed, 'entries') or not feed.entries:
                self.logger.error("RSS'de haber girdisi bulunamadı")
                return None
            
            self.logger.info(f"RSS başarıyla parse edildi. {len(feed.entries)} haber bulundu")
            
            # Feed bilgilerini logla
            if hasattr(feed, 'feed'):
                feed_info = feed.feed
                self.logger.info(f"Feed başlığı: {getattr(feed_info, 'title', 'Bilinmiyor')}")
                self.logger.info(f"Feed açıklaması: {getattr(feed_info, 'description', 'Bilinmiyor')}")
            
            return feed
            
        except Exception as e:
            self.logger.error(f"RSS parse hatası: {e}")
            return None
    
    def extract_news_item(self, entry: feedparser.FeedParserDict) -> Optional[RSSNewsItem]:
        """Tek bir RSS entry'sinden NewsItem çıkar"""
        try:
            # Güvenli attribute alma fonksiyonu
            def safe_get(obj, attr, default=""):
                try:
                    value = getattr(obj, attr, default)
                    return str(value) if value else default
                except:
                    return default
            
            # Temel alanları çıkar
            title = safe_get(entry, 'title')
            link = safe_get(entry, 'link')
            summary = safe_get(entry, 'summary')
            
            # Alternatif alanları dene
            if not summary:
                summary = safe_get(entry, 'description')
            
            # Tarih bilgisi
            published = safe_get(entry, 'published')
            if not published:
                published = safe_get(entry, 'pubDate')
            
            # Yazar bilgisi
            author = safe_get(entry, 'author')
            if not author:
                author = safe_get(entry, 'dc_creator')
            
            # GUID
            guid = safe_get(entry, 'guid')
            if not guid:
                guid = safe_get(entry, 'id')
            
            # Kategori
            category = ""
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].get('term', '') if entry.tags[0] else ""
            
            # Minimum gereksinimler kontrolü
            if not title or not link:
                self.logger.warning(f"Eksik veri: title='{title}', link='{link}'")
                return None
            
            news_item = RSSNewsItem(
                title=title,
                link=link,
                summary=summary,
                published=published,
                guid=guid,
                author=author,
                category=category,
                description=summary  # description alanını da doldur
            )
            
            # Veri doğrulama
            if not news_item.is_valid():
                self.logger.warning(f"Geçersiz haber verisi: {news_item.title}")
                return None
            
            return news_item
            
        except Exception as e:
            self.logger.error(f"Haber çıkarma hatası: {e}")
            return None
    
    def get_news_items(self, limit: Optional[int] = None) -> List[RSSNewsItem]:
        """RSS'den haber listesi al"""
        try:
            # RSS içeriğini çek
            content = self.fetch_rss_content()
            if not content:
                return []
            
            # Parse et
            feed = self.parse_rss_feed(content)
            if not feed:
                return []
            
            # Haberleri çıkar
            news_items = []
            entries = feed.entries
            
            if limit:
                entries = entries[:limit]
            
            for i, entry in enumerate(entries):
                try:
                    news_item = self.extract_news_item(entry)
                    if news_item:
                        news_items.append(news_item)
                        self.logger.debug(f"Haber {i+1} başarıyla çıkarıldı: {news_item.title[:50]}...")
                    else:
                        self.logger.debug(f"Haber {i+1} çıkarılamadı")
                        
                except Exception as e:
                    self.logger.error(f"Haber {i+1} işleme hatası: {e}")
                    continue
            
            self.logger.info(f"Toplam {len(news_items)} haber başarıyla çıkarıldı")
            return news_items
            
        except Exception as e:
            self.logger.error(f"Haber listesi alma hatası: {e}")
            return []
    
    def get_latest_news(self, count: int = 10) -> List[RSSNewsItem]:
        """En son haberleri al"""
        self.logger.info(f"Son {count} haber çekiliyor...")
        return self.get_news_items(limit=count)
    
    def get_news_by_category(self, category: str, count: int = 10) -> List[RSSNewsItem]:
        """Kategoriye göre haber al"""
        if not self._is_valid_category(category):
            self.logger.error(f"Desteklenmeyen kategori: {category}")
            self.logger.info(f"Desteklenen kategoriler: {', '.join(sorted(self.valid_categories))}")
            return []
        
        # Geçici olarak URL'i değiştir
        original_url = self.rss_url
        self.rss_url = self._get_category_url(category)
        
        try:
            self.logger.info(f"'{category}' kategorisinden {count} haber çekiliyor...")
            news_items = self.get_news_items(limit=count)
            
            # Kategori bilgisini her habere ekle
            for item in news_items:
                item.category = category
            
            return news_items
        finally:
            # URL'i geri al
            self.rss_url = original_url
    
    def get_available_categories(self) -> List[str]:
        """Mevcut kategorilerin listesini döndür"""
        return sorted(list(self.valid_categories))
    
    def get_category_info(self) -> Dict[str, str]:
        """Kategori bilgilerini döndür"""
        return self.category_descriptions.copy()
    
    def add_custom_category(self, category: str, description: str = None) -> bool:
        """Özel kategori ekle (test için)"""
        try:
            # URL'i test et
            test_url = self._get_category_url(category)
            response = self.session.get(test_url, timeout=10)
            
            if response.status_code == 200:
                self.valid_categories.add(category)
                if description:
                    self.category_descriptions[category] = description
                self.logger.info(f"Yeni kategori eklendi: {category}")
                return True
            else:
                self.logger.error(f"Kategori '{category}' mevcut değil (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            self.logger.error(f"Kategori test hatası: {e}")
            return False
    
    def get_news_from_multiple_categories(self, categories: List[str], count_per_category: int = 5) -> Dict[str, List[RSSNewsItem]]:
        """Birden fazla kategoriden haber çek"""
        results = {}
        
        for category in categories:
            if self._is_valid_category(category):
                try:
                    news_items = self.get_news_by_category(category, count_per_category)
                    results[category] = news_items
                    self.logger.info(f"'{category}' kategorisinden {len(news_items)} haber çekildi")
                except Exception as e:
                    self.logger.error(f"'{category}' kategorisi çekilemedi: {e}")
                    results[category] = []
            else:
                self.logger.warning(f"Geçersiz kategori: {category}")
                results[category] = []
        
        return results
    
    def search_in_category(self, category: str, keyword: str, count: int = 10) -> List[RSSNewsItem]:
        """Belirli kategoride anahtar kelime ara"""
        news_items = self.get_news_by_category(category, count * 3)  # Daha fazla çek, filtrele
        
        keyword_lower = keyword.lower()
        filtered_items = []
        
        for item in news_items:
            if (keyword_lower in item.title.lower() or 
                keyword_lower in item.summary.lower()):
                filtered_items.append(item)
                
                if len(filtered_items) >= count:
                    break
        
        self.logger.info(f"'{category}' kategorisinde '{keyword}' araması: {len(filtered_items)} sonuç")
        return filtered_items
    
    def test_connection(self) -> Dict[str, Any]:
        """RSS bağlantısını test et"""
        start_time = time.time()
        
        result = {
            'success': False,
            'response_time': 0,
            'feed_title': '',
            'news_count': 0,
            'errors': []
        }
        
        try:
            content = self.fetch_rss_content()
            if not content:
                result['errors'].append('RSS içeriği çekilemedi')
                return result
            
            feed = self.parse_rss_feed(content)
            if not feed:
                result['errors'].append('RSS parse edilemedi')
                return result
            
            result['success'] = True
            result['response_time'] = round(time.time() - start_time, 2)
            result['feed_title'] = getattr(feed.feed, 'title', 'Bilinmiyor')
            result['news_count'] = len(feed.entries)
            
            self.logger.info(f"RSS bağlantı testi başarılı: {result}")
            
        except Exception as e:
            result['errors'].append(str(e))
            self.logger.error(f"RSS bağlantı testi hatası: {e}")
        
        return result
    
    def get_feed_info(self) -> Dict[str, Any]:
        """RSS feed bilgilerini al"""
        try:
            content = self.fetch_rss_content()
            if not content:
                return {}
            
            feed = self.parse_rss_feed(content)
            if not feed or not hasattr(feed, 'feed'):
                return {}
            
            feed_info = feed.feed
            
            return {
                'title': getattr(feed_info, 'title', ''),
                'description': getattr(feed_info, 'description', ''),
                'link': getattr(feed_info, 'link', ''),
                'language': getattr(feed_info, 'language', ''),
                'last_updated': getattr(feed_info, 'updated', ''),
                'total_entries': len(feed.entries) if hasattr(feed, 'entries') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Feed bilgisi alma hatası: {e}")
            return {}


# Test ve örnek kullanım
if __name__ == "__main__":
    # Logging seviyesini ayarla
    logging.basicConfig(level=logging.INFO)
    
    # RSS reader oluştur
    reader = RSSReader(default_category="guncel")
    
    # Kategori bilgilerini göster
    print("Mevcut Kategoriler:")
    categories = reader.get_category_info()
    for key, name in categories.items():
        print(f"  {key}: {name}")
    
    print("\n" + "="*50)
    
    # Bağlantı testi
    print("RSS Bağlantı Testi:")
    test_result = reader.test_connection()
    print(f"Başarılı: {test_result['success']}")
    print(f"Yanıt süresi: {test_result['response_time']} saniye")
    print(f"Haber sayısı: {test_result['news_count']}")
    
    if test_result['errors']:
        print(f"Hatalar: {test_result['errors']}")
    
    print("\n" + "="*50)
    
    # Son haberleri çek (varsayılan kategori)
    print("Son 3 Haber (Güncel):")
    news_items = reader.get_latest_news(3)
    
    for i, item in enumerate(news_items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Kategori: {item.category}")
        print(f"   Link: {item.link}")
        print(f"   Özet: {item.summary[:100]}...")
        print(f"   Karakter: {item.get_character_count()}")
    
    print("\n" + "="*50)
    
    # Farklı kategori testi
    print("Ekonomi Haberleri (2 adet):")
    ekonomi_haberleri = reader.get_news_by_category("ekonomi", 2)
    
    for i, item in enumerate(ekonomi_haberleri, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Kategori: {item.category}")
        print(f"   Özet: {item.summary[:80]}...")
    
    print("\n" + "="*50)
    
    # Multiple kategori testi
    print("Birden Fazla Kategoriden Haber:")
    multi_categories = ["guncel", "spor", "teknoloji"]
    multi_results = reader.get_news_from_multiple_categories(multi_categories, 2)
    
    for category, items in multi_results.items():
        print(f"\n{category.upper()} ({len(items)} haber):")
        for item in items[:1]:  # Sadece ilkini göster
            print(f"  - {item.title[:60]}...")
    
    print(f"\nToplam işlem tamamlandı!")