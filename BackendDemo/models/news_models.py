"""
Haber veri modelleri
RSS ve web scraping verilerini tutmak için kullanılan data class'lar
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


@dataclass
class RSSNewsItem:
    """RSS'den gelen temel haber verisi"""
    title: str = ""
    link: str = ""
    summary: str = ""
    published: str = ""
    guid: str = ""
    author: str = ""
    category: str = ""
    
    # RSS'de bulunabilecek ek alanlar
    description: str = ""
    pub_date: str = ""
    
    def __post_init__(self):
        """Veri temizleme işlemleri"""
        self.title = self._clean_text(self.title)
        self.summary = self._clean_text(self.summary)
        self.description = self._clean_text(self.description)
        
    def _clean_text(self, text: str) -> str:
        """HTML etiketlerini ve fazla boşlukları temizle"""
        if not text:
            return ""
        
        # HTML etiketlerini kaldır
        text = re.sub(r'<[^>]+>', '', text)
        
        # HTML entity'lerini decode et
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def get_character_count(self) -> int:
        """TTS için toplam karakter sayısını hesapla"""
        total_text = f"{self.title} {self.summary}"
        return len(total_text.strip())
    
    def is_valid(self) -> bool:
        """Verinin geçerli olup olmadığını kontrol et"""
        return bool(self.title and self.link)


@dataclass 
class ScrapedNewsContent:
    """Web scraping ile elde edilen detaylı haber içeriği"""
    url: str = ""
    full_content: str = ""
    article_text: str = ""
    location: str = ""
    author: str = ""
    publish_date: str = ""
    update_date: str = ""
    main_image_url: str = ""
    main_image_alt: str = ""
    image_urls: List[str] = field(default_factory=list)
    images_detailed: List[Dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: str = ""
    
    # Meta data
    meta_description: str = ""
    meta_keywords: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    og_url: str = ""
    twitter_title: str = ""
    twitter_description: str = ""
    twitter_image: str = ""
    
    # Sosyal medya paylaşım bilgileri
    sharing_urls: Dict[str, str] = field(default_factory=dict)
    
    # Benzer haberler
    related_articles: List[Dict] = field(default_factory=list)
    
    # Fotoğraf editör bilgisi
    photo_credit: str = ""
    
    def __post_init__(self):
        """Veri temizleme işlemleri"""
        self.full_content = self._clean_article_text(self.full_content)
        self.article_text = self._clean_article_text(self.article_text)
        self.location = self._clean_text(self.location)
        self.author = self._clean_text(self.author)
        
    def _clean_text(self, text: str) -> str:
        """Basit metin temizleme"""
        if not text:
            return ""
        
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _clean_article_text(self, text: str) -> str:
        """Makale metnini temizle"""
        if not text:
            return ""
        
        # HTML etiketlerini kaldır
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fazla boşlukları ve satır başlarını düzelt
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # URL'leri kaldır (opsiyonel)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        return text.strip()
    
    def get_character_count(self) -> int:
        """Makale karakter sayısını hesapla"""
        return len(self.article_text)
    
    def has_sufficient_content(self, min_chars: int = 100) -> bool:
        """Yeterli içerik olup olmadığını kontrol et"""
        return self.get_character_count() >= min_chars


@dataclass
class CompleteNewsArticle:
    """RSS + Web scraping birleştirilmiş tam haber verisi"""
    
    # RSS verisi
    rss_data: RSSNewsItem
    
    # Scraping verisi  
    scraped_data: Optional[ScrapedNewsContent] = None
    
    # İşleme durumu
    scraping_attempted: bool = False
    scraping_successful: bool = False
    scraping_error: Optional[str] = None
    
    # Timestamp
    processed_at: datetime = field(default_factory=datetime.now)
    
    def get_title(self) -> str:
        """En iyi başlığı döndür"""
        if self.scraped_data and self.scraped_data.article_text:
            return self.rss_data.title
        return self.rss_data.title
    
    def get_content_for_tts(self) -> str:
        """TTS için optimize edilmiş içerik"""
        parts = []
        
        # Başlık
        title = self.get_title()
        if title:
            parts.append(f"Başlık: {title}")
        
        # Yazar ve konum bilgisi
        author = ""
        location = ""
        
        if self.scraped_data:
            author = self.scraped_data.author
            location = self.scraped_data.location
        
        if not author:
            author = self.rss_data.author
            
        if author and location:
            parts.append(f"{author}, {location}")
        elif location:
            parts.append(f"Konum: {location}")
        elif author:
            parts.append(f"Yazar: {author}")
        
        # Ana içerik
        main_content = ""
        if self.scraped_data and self.scraped_data.article_text:
            main_content = self.scraped_data.article_text
        elif self.rss_data.summary:
            main_content = self.rss_data.summary
        elif self.rss_data.description:
            main_content = self.rss_data.description
        
        if main_content:
            parts.append(main_content)
        
        return "\n\n".join(parts)
    
    def get_character_count(self) -> int:
        """TTS için toplam karakter sayısı"""
        return len(self.get_content_for_tts())
    
    def get_summary(self) -> str:
        """Özet bilgi döndür"""
        if self.scraped_data and self.scraped_data.article_text:
            # İlk paragrafı özet olarak kullan
            content = self.scraped_data.article_text
            first_paragraph = content.split('\n\n')[0]
            if len(first_paragraph) > 200:
                return first_paragraph[:200] + "..."
            return first_paragraph
        
        return self.rss_data.summary or self.rss_data.description
    
    def get_main_image_url(self) -> Optional[str]:
        """Ana görsel URL'i döndür"""
        if self.scraped_data and self.scraped_data.main_image_url:
            return self.scraped_data.main_image_url
        return None
    
    def get_all_image_urls(self) -> List[str]:
        """Tüm görsel URL'lerini döndür"""
        if self.scraped_data and self.scraped_data.image_urls:
            return self.scraped_data.image_urls
        return []
    
    def get_tags(self) -> List[str]:
        """Etiketleri döndür"""
        if self.scraped_data and self.scraped_data.tags:
            return self.scraped_data.tags
        return []
    
    def is_complete(self) -> bool:
        """Verinin tam olup olmadığını kontrol et"""
        return (
            self.rss_data.is_valid() and 
            self.scraping_successful and 
            self.scraped_data is not None and
            self.scraped_data.has_sufficient_content()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatına çevir (API response için)"""
        return {
            "title": self.get_title(),
            "url": self.rss_data.link,
            "summary": self.get_summary(),
            "content": self.get_content_for_tts(),
            "character_count": self.get_character_count(),
            "author": self.scraped_data.author if self.scraped_data else self.rss_data.author,
            "location": self.scraped_data.location if self.scraped_data else "",
            "published": self.rss_data.published,
            "category": self.scraped_data.category if self.scraped_data else self.rss_data.category,
            "main_image_url": self.get_main_image_url(),
            "image_urls": self.get_all_image_urls(),
            "tags": self.get_tags(),
            "scraping_successful": self.scraping_successful,
            "is_complete": self.is_complete(),
            "processed_at": self.processed_at.isoformat()
        }


@dataclass
class TTSRequest:
    """TTS isteği için veri modeli"""
    text: str
    voice: str = "alloy"
    model: str = "tts-1"
    speed: float = 1.0
    response_format: str = "mp3"
    
    def get_character_count(self) -> int:
        """Karakter sayısını döndür"""
        return len(self.text)
    
    def estimate_cost(self, pricing_per_1m_chars: float = 0.015) -> float:
        """Tahmini maliyeti hesapla (USD)"""
        char_count = self.get_character_count()
        return (char_count / 1_000_000) * pricing_per_1m_chars


@dataclass
class TTSResponse:
    """TTS yanıtı için veri modeli"""
    success: bool
    audio_file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    character_count: int = 0
    estimated_cost: float = 0.0
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatına çevir"""
        return {
            "success": self.success,
            "audio_file_path": self.audio_file_path,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "character_count": self.character_count,
            "estimated_cost": self.estimated_cost,
            "error_message": self.error_message,
            "processing_time_seconds": self.processing_time_seconds
        }