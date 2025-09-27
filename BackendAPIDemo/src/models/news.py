# ================================
# src/models/news.py
# ================================

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
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
    # Yeni kategori eklemek için buraya ekle

class Article(BaseModel):
    """Universal article model - tüm news provider'lar için"""
    id: str
    title: str
    content: str
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
    
    # Metadata
    tags: List[str] = []
    source: Optional[str] = None
    language: str = "tr"
    status: ArticleStatus = ArticleStatus.PUBLISHED
    
    # Processing info
    character_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    sentiment_score: Optional[float] = None  # -1 to 1
    
    # Extensible metadata
    metadata: Dict[str, Any] = {}
    
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
            # İlk 500 karakter
            parts.append(self.content[:500])
        return "\n\n".join(parts)
    
    def calculate_reading_time(self) -> int:
        """Calculate reading time in minutes (avg 200 words/min)"""
        word_count = len(self.content.split())
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