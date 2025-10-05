# ================================
# src/models/news.py
# ================================

from pydantic import BaseModel, Field, HttpUrl, computed_field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from .base import BaseResponse

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class NewsCategory(str, Enum):
    GUNCEL = "guncel"
    EKONOMI = "ekonomi"
    SPOR = "spor"
    TEKNOLOJI = "teknoloji"
    KULTUR = "kultur"
    DUNYA = "dunya"

class Article(BaseModel):
    """Universal article model - tüm news provider'lar için"""
    id: str
    title: str
    
    # ✅ UPDATED: content artık str veya List[str] olabilir
    content: Union[str, List[str]]  
    
    summary: Optional[str] = None
    url: HttpUrl
    category: str
    
    # Optional fields
    author: Optional[str] = None
    location: Optional[str] = None
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Media
    images: List[str] = []
    main_image: Optional[str] = None
    videos: List[str] = []
    
    # ✅ UPDATED: aa_scraper'dan gelen yeni alanlar
    tags: List[str] = []
    keywords: List[str] = Field(default_factory=list, description="Meta keywords + content'ten çıkarılan kelimeler")
    hashtags: List[str] = Field(default_factory=list, description="Content'ten çıkarılan hashtag'ler")
    meta_description: Optional[str] = Field(None, description="SEO meta açıklama")
    
    source: Optional[str] = None
    language: str = "tr"
    status: ArticleStatus = ArticleStatus.PUBLISHED
    
    # Processing info
    character_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    sentiment_score: Optional[float] = None
    
    # Extensible metadata
    metadata: Dict[str, Any] = {}
    
    # ✅ COMPUTED PROPERTY: Geriye dönük uyumluluk için
    @computed_field
    @property
    def content_text(self) -> str:
        """
        Content'i her zaman str olarak döndür
        Eski kodlarla uyumluluk için
        """
        if isinstance(self.content, list):
            return '\n\n'.join(self.content)
        return self.content
    
    # ✅ COMPUTED PROPERTY: Paragraf listesi
    @computed_field
    @property
    def content_paragraphs(self) -> List[str]:
        """
        Content'i her zaman List[str] olarak döndür
        """
        if isinstance(self.content, list):
            return self.content
        # Eğer str ise, çift newline'a göre split et
        return [p.strip() for p in self.content.split('\n\n') if p.strip()]
    
    def to_tts_content(self) -> str:
        """Convert article to TTS-optimized content"""
        parts = []
        if self.title:
            parts.append(f"Başlık: {self.title}")
        if self.author and self.location:
            parts.append(f"{self.author}, {self.location}")
        if self.summary:
            parts.append(f"Özet: {self.summary}")
        elif self.content:
            # İlk 500 karakter (content_text kullan)
            parts.append(self.content_text[:500])
        return "\n\n".join(parts)
    
    def calculate_reading_time(self) -> int:
        """Calculate reading time in minutes (avg 200 words/min)"""
        word_count = len(self.content_text.split())
        return max(1, round(word_count / 200))

class NewsFilter(BaseModel):
    """News filtering options"""
    category: Optional[str] = None
    author: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_chars: Optional[int] = None
    max_chars: Optional[int] = None
    keywords: Optional[List[str]] = None

class NewsResponse(BaseResponse):
    """News API response"""
    articles: List[Article]
    total_count: int
    category: Optional[str] = None
    provider: Optional[str] = None
    filters_applied: Optional[NewsFilter] = None