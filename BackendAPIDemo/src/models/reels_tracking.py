# ================================
# src/models/reels_tracking.py - COMPLETE FILE
# ================================

"""
Reels izleme, kullanıcı aktivitesi ve progress tracking modelleri
✅ UPDATED: NewsData.full_content → Union[str, List[str]]
"""

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional, Dict, Any, Tuple, Union
from datetime import datetime, date
from enum import Enum
import uuid

# ============ ENUMS ============

class ViewStatus(str, Enum):
    """Reel izleme durumu"""
    STARTED = "started"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PARTIAL = "partial"

class TrendPeriod(str, Enum):
    """Trend hesaplama periyodu"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

class ReelStatus(str, Enum):
    """Reel durumu"""
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"

class EmojiType(str, Enum):
    """Emoji türleri - tüm emojiler aynı ağırlıkta"""
    HEART = "❤️"
    LIKE = "👍"
    FIRE = "🔥"
    STAR = "⭐"
    CLAP = "👏"
    LOVE = "😍"
    THINKING = "🤔"
    WOW = "😮"

# ============ NEWS DATA MODEL ============

class NewsData(BaseModel):
    """
    ✅ UPDATED: Reel'deki haber verisi
    """
    title: str
    summary: str
    
    # ✅ UPDATED: full_content artık Union[str, List[str]]
    full_content: Union[str, List[str]] = Field(
        default_factory=list,
        description="Paragraflar listesi veya string"
    )
    
    url: str
    
    # Metadata
    category: str
    author: Optional[str] = None
    location: Optional[str] = None
    published_date: str
    
    # Media
    main_image: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    
    # SEO & Tags
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list, description="Haber anahtar kelimeleri")
    
    # Metrics
    estimated_reading_time: int = Field(default=3, description="Tahmini okuma süresi (dakika)")
    source: str = Field(default="aa", description="Kaynak")
    word_count: int = Field(default=0)
    character_count: int = Field(default=0)
    content_language: str = Field(default="tr")
    
    # ✅ COMPUTED PROPERTIES: Geriye dönük uyumluluk
    @computed_field
    @property
    def full_content_text(self) -> str:
        """full_content'i her zaman str olarak döndür"""
        if isinstance(self.full_content, list):
            return '\n\n'.join(self.full_content)
        return self.full_content or ""
    
    @computed_field
    @property
    def full_content_paragraphs(self) -> List[str]:
        """full_content'i her zaman List[str] olarak döndür"""
        if isinstance(self.full_content, list):
            return self.full_content
        if isinstance(self.full_content, str):
            return [p.strip() for p in self.full_content.split('\n\n') if p.strip()]
        return []

# ============ CORE TRACKING MODELS ============

class ReelView(BaseModel):
    """Tek bir reel izleme kaydı"""
    reel_id: str = Field(..., description="İzlenen reel ID'si")
    user_id: str = Field(..., description="İzleyen kullanıcı ID'si")
    
    # Timing info
    viewed_at: datetime = Field(default_factory=datetime.now, description="İzlenme zamanı")
    duration_ms: int = Field(..., ge=0, description="İzleme süresi (milisaniye)")
    
    # View details
    status: ViewStatus = Field(default=ViewStatus.PARTIAL, description="İzleme durumu")
    completed: bool = Field(default=False, description="Tamamen izlendi mi (3sn+)")
    
    # Context info
    category: Optional[str] = Field(None, description="Haber kategorisi")
    source: Optional[str] = Field(default="aa", description="Haber kaynağı")
    
    # Technical details
    session_id: Optional[str] = Field(None, description="Kullanıcı session ID'si")
    device_type: Optional[str] = Field(None, description="Cihaz türü (web/mobile)")
    
    # Emoji reaction tracking
    emoji_reaction: Optional[EmojiType] = Field(None, description="Emoji tepkisi")
    emoji_timestamp: Optional[datetime] = Field(None, description="Emoji atılma zamanı")

    # Detail view tracking
    detail_viewed: bool = Field(default=False, description="Detayları görüntüledi mi")
    detail_duration_ms: int = Field(default=0, ge=0, description="Detayda geçirilen süre (ms)")
    detail_scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Detay scroll derinliği")
    detail_opened_at: Optional[datetime] = Field(None, description="Detay açılma zamanı")
    detail_closed_at: Optional[datetime] = Field(None, description="Detay kapanma zamanı")

    # Extended engagement signals
    paused_count: int = Field(default=0, ge=0, description="Duraklama sayısı")
    replayed: bool = Field(default=False, description="Tekrar oynat tıklandı mı")
    shared: bool = Field(default=False, description="Paylaşıldı mı")
    saved: bool = Field(default=False, description="Kaydedildi mi")

    def is_meaningful_view(self) -> bool:
        """Anlamlı izleme mi"""
        has_minimum_watch = self.duration_ms >= 3000
        has_emoji = self.emoji_reaction is not None
        has_detail_view = self.detail_viewed and self.detail_duration_ms >= 5000
        return has_minimum_watch or has_emoji or has_detail_view

    def get_engagement_score(self) -> float:
        """Engagement skoru hesapla (0.0 - 1.5)"""
        score = 0.0
        
        # Audio izleme skoru (max 0.7)
        if self.status == ViewStatus.COMPLETED:
            audio_score = 0.7
        elif self.duration_ms >= 30000:
            audio_score = 0.6
        elif self.duration_ms >= 15000:
            audio_score = 0.4
        elif self.duration_ms >= 5000:
            audio_score = 0.2
        else:
            audio_score = 0.1
        
        score += audio_score
        
        # Emoji reaction bonus (+0.9)
        if self.emoji_reaction is not None:
            score += 0.9
        
        # Detail view bonus (max +0.6)
        if self.detail_viewed:
            if self.detail_duration_ms >= 60000:
                detail_score = 0.6
            elif self.detail_duration_ms >= 30000:
                detail_score = 0.5
            elif self.detail_duration_ms >= 15000:
                detail_score = 0.4
            elif self.detail_duration_ms >= 5000:
                detail_score = 0.2
            else:
                detail_score = 0.1
            
            if self.detail_scroll_depth >= 0.8:
                detail_score += 0.1
            elif self.detail_scroll_depth >= 0.5:
                detail_score += 0.05
            
            score += detail_score
        
        # Extra engagement signals (max +0.3)
        if self.replayed:
            score += 0.1
        if self.shared:
            score += 0.15
        if self.saved:
            score += 0.1
        if self.paused_count > 0:
            score += min(0.05 * self.paused_count, 0.1)
        
        return min(score, 1.5)

    def get_preference_weight(self) -> float:
        """Preference engine için ağırlık (0.0 - 1.0)"""
        engagement = self.get_engagement_score()
        return min(engagement / 1.5, 1.0)
    
    def get_duration_seconds(self) -> float:
        """İzleme süresini saniye olarak döndür"""
        return self.duration_ms / 1000.0

class UserDailyStats(BaseModel):
    """Kullanıcının günlük istatistikleri"""
    user_id: str
    stats_date: date = Field(default_factory=date.today)
    
    # Emoji & Detail stats
    total_emoji_reactions: int = Field(default=0, description="Toplam emoji sayısı")
    emoji_breakdown: Dict[str, int] = Field(default_factory=dict, description="Emoji dağılımı")
    detail_views: int = Field(default=0, description="Detay görüntüleme sayısı")
    meaningful_detail_reads: int = Field(default=0, description="Anlamlı detay okuma sayısı")
    
    # View counts
    total_reels_watched: int = Field(default=0, description="Toplam izlenen reel sayısı")
    completed_reels: int = Field(default=0, description="Tamamen izlenen reel sayısı") 
    skipped_reels: int = Field(default=0, description="Atlanan reel sayısı")
    
    # Time tracking
    total_screen_time_ms: int = Field(default=0, description="Toplam ekran süresi")
    avg_view_duration_ms: float = Field(default=0.0, description="Ortalama izleme süresi")
    
    # Categories
    categories_watched: List[str] = Field(default_factory=list, description="İzlenen kategoriler")
    most_watched_category: Optional[str] = Field(default=None, description="En çok izlenen kategori")
    
    # Session info  
    first_activity: Optional[datetime] = Field(default=None, description="İlk aktivite zamanı")
    last_activity: Optional[datetime] = Field(default=None, description="Son aktivite zamanı")
    session_count: int = Field(default=0, description="Günlük session sayısı")

class UserReelStats(BaseModel):
    """Kullanıcının genel reel istatistikleri"""
    user_id: str
    
    # Overall stats
    total_reels_watched: int = Field(default=0, description="Toplam izlenen reel")
    total_screen_time_ms: int = Field(default=0, description="Toplam ekran süresi")
    total_days_active: int = Field(default=0, description="Aktif gün sayısı")
    
    # Emoji & Detail stats
    total_emoji_reactions: int = Field(default=0, description="Toplam emoji sayısı")
    total_detail_views: int = Field(default=0, description="Toplam detay görüntüleme")
    detail_view_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Detay okuma oranı")
    
    # Averages
    avg_daily_reels: float = Field(default=0.0, description="Günlük ortalama reel")
    avg_daily_screen_time_ms: float = Field(default=0.0, description="Günlük ortalama ekran süresi")
    avg_reel_duration_ms: float = Field(default=0.0, description="Ortalama reel izleme süresi")
    avg_engagement_score: float = Field(default=0.0, description="Ortalama engagement skoru")
    
    # Engagement
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Tamamlama oranı")
    emoji_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Emoji atma oranı")
    favorite_categories: List[str] = Field(default_factory=list, description="Favori kategoriler")
    
    # Recent activity
    last_reel_viewed_at: Optional[datetime] = Field(None, description="Son reel izleme zamanı")
    last_viewed_reel_id: Optional[str] = Field(None, description="Son izlenen reel ID")
    current_streak_days: int = Field(default=0, description="Güncel seri (gün)")
    
    # Daily breakdown
    daily_stats: Dict[str, UserDailyStats] = Field(default_factory=dict, description="Günlük detaylar")
    
    def get_total_screen_time_hours(self) -> float:
        """Toplam ekran süresini saat olarak döndür"""
        return self.total_screen_time_ms / (1000 * 60 * 60)
    
    def get_personalization_level(self) -> str:
        """Kullanıcının personalization seviyesi"""
        if self.total_reels_watched < 10:
            return "cold"
        elif self.total_reels_watched < 50:
            return "warm"
        else:
            return "hot"

class ReelAnalytics(BaseModel):
    """Bir reel'in analitik verileri"""
    reel_id: str
    
    # View metrics
    total_views: int = Field(default=0, description="Toplam görüntülenme")
    unique_viewers: int = Field(default=0, description="Benzersiz izleyici sayısı")
    total_screen_time_ms: int = Field(default=0, description="Toplam izlenme süresi")
    
    # Engagement metrics
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Tamamlama oranı")
    avg_view_duration_ms: float = Field(default=0.0, description="Ortalama izleme süresi")
    skip_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Atlama oranı")
    
    # Trending metrics
    trend_score: float = Field(default=0.0, description="Trend puanı (0-10)")
    hourly_views: int = Field(default=0, description="Son 1 saatteki görüntülenme")
    daily_views: int = Field(default=0, description="Son 24 saatteki görüntülenme")
    
    # Emoji & Detail metrics
    total_emoji_reactions: int = Field(default=0, description="Toplam emoji sayısı")
    emoji_breakdown: Dict[str, int] = Field(default_factory=dict, description="Emoji dağılımı")
    emoji_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Emoji atma oranı")
    detail_view_count: int = Field(default=0, description="Detay görüntüleme sayısı")
    detail_view_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Detay okuma oranı")
    avg_detail_duration_ms: float = Field(default=0.0, description="Ortalama detay okuma süresi")
    
    # Metadata
    published_at: datetime = Field(..., description="Yayınlanma zamanı")
    first_viewed_at: Optional[datetime] = Field(None, description="İlk izlenme zamanı")
    peak_view_hour: Optional[int] = Field(None, description="En çok izlenen saat")
    
    # Categories & context
    category: Optional[str] = Field(None, description="Kategori")
    tags: List[str] = Field(default_factory=list, description="Etiketler")
    
    def get_engagement_score(self) -> float:
        """Engagement skoru hesapla (0-10)"""
        if self.total_views == 0:
            return 0.0
        
        completion_score = self.completion_rate * 3.0
        duration_score = min(self.avg_view_duration_ms / 30000, 1.0) * 2.0
        view_score = min(self.total_views / 100, 1.0) * 2.0
        emoji_score = self.emoji_rate * 1.5
        detail_score = self.detail_view_rate * 1.5
        
        total_score = completion_score + duration_score + view_score + emoji_score + detail_score
        return round(total_score, 2)

class DailyProgress(BaseModel):
    """Kullanıcının günlük progress takibi"""
    user_id: str
    progress_date: date = Field(default_factory=date.today)
    
    # Daily news stats
    total_published_today: int = Field(default=0, description="Bugün yayınlanan toplam")
    watched_today: int = Field(default=0, description="Bugün izlenen")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="İlerleme %")
    
    # Category breakdown
    category_progress: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Kategori bazlı progress"
    )
    
    # Timestamps
    first_view_today: Optional[datetime] = None
    last_view_today: Optional[datetime] = None
    
    def calculate_progress(self) -> float:
        """Progress yüzdesini hesapla"""
        if self.total_published_today == 0:
            self.progress_percentage = 0.0
        else:
            self.progress_percentage = (self.watched_today / self.total_published_today) * 100.0
        return self.progress_percentage
    
    def get_category_progress(self, category: str) -> float:
        """Kategori progress yüzdesi"""
        if category not in self.category_progress:
            return 0.0
        cat_data = self.category_progress[category]
        if cat_data.get("published", 0) == 0:
            return 0.0
        return (cat_data.get("watched", 0) / cat_data["published"]) * 100.0

# ============ FEED & REEL MODELS ============

class ReelFeedItem(BaseModel):
    """Feed'deki bir reel item'i"""
    id: str = Field(..., description="Reel unique ID")
    
    # News data
    news_data: NewsData = Field(..., description="Haber verisi")
    
    # TTS & Audio
    tts_content: str = Field(..., description="TTS için kullanılan metin")
    voice_used: str = Field(default="alloy")
    model_used: str = Field(default="tts-1")
    
    # Audio files
    audio_url: str = Field(..., description="Ses dosyası URL'i")
    duration_seconds: int = Field(..., description="Ses süresi")
    file_size_mb: float = Field(default=0.0)
    
    # Publishing info
    status: ReelStatus = Field(default=ReelStatus.PUBLISHED)
    published_at: datetime = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Analytics
    total_views: int = Field(default=0)
    total_screen_time_ms: int = Field(default=0)
    completion_rate: float = Field(default=0.0)
    trend_score: float = Field(default=0.0)
    
    # User-specific flags
    is_watched: bool = Field(default=False)
    is_trending: bool = Field(default=False)
    is_fresh: bool = Field(default=False)
    is_recommended: bool = Field(default=False)
    
    # Recommendation metadata
    recommendation_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recommendation_reason: Optional[str] = None
    feed_reason: str = Field(default="algorithmic")
    trend_rank: Optional[int] = None
    
    # Processing metadata
    character_count: int = Field(default=0)
    estimated_cost: float = Field(default=0.0)
    processing_time_seconds: float = Field(default=0.0)
    
    # Thumbnail
    thumbnail_url: Optional[str] = None
    
    def is_recent(self, hours: int = 3) -> bool:
        """Son X saat içinde yayınlandı mı"""
        from datetime import timedelta
        return datetime.now() - self.published_at < timedelta(hours=hours)
    
    def get_engagement_rate(self) -> float:
        """Engagement oranı hesapla"""
        if self.total_views == 0:
            return 0.0
        return (self.total_screen_time_ms / 1000) / (self.duration_seconds * self.total_views)

class TrendingReels(BaseModel):
    """Trend olan reels listesi"""
    period: TrendPeriod = Field(default=TrendPeriod.DAILY)
    calculated_at: datetime = Field(default_factory=datetime.now)
    trending_reels: List[ReelFeedItem] = Field(default_factory=list)
    total_reels_analyzed: int = Field(default=0)
    trending_threshold: float = Field(default=5.0)
    
    def get_top_trending(self, count: int = 10) -> List[ReelFeedItem]:
        """En trend olan N reel"""
        return self.trending_reels[:count]

# ============ REQUEST/RESPONSE MODELS ============

class TrackViewRequest(BaseModel):
    """Reel izleme kaydı request"""
    reel_id: str = Field(..., description="İzlenen reel ID")
    duration_ms: int = Field(..., ge=0, description="İzleme süresi (ms)")
    completed: bool = Field(default=False, description="Tamamen izlendi mi")
    category: Optional[str] = None
    session_id: Optional[str] = None
    emoji_reaction: Optional[EmojiType] = None
    paused_count: Optional[int] = Field(0, description="Duraklama sayısı")
    replayed: Optional[bool] = Field(False, description="Tekrar oynat")
    shared: Optional[bool] = Field(False, description="Paylaşıldı mı")
    saved: Optional[bool] = Field(False, description="Kaydedildi mi")

class TrackDetailViewRequest(BaseModel):
    """Detay görüntüleme tracking request"""
    reel_id: str = Field(..., description="Görüntülenen reel ID")
    read_duration_ms: int = Field(..., ge=0, description="Okuma süresi")
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0)
    shared_from_detail: bool = Field(default=False)
    saved_from_detail: bool = Field(default=False)
    session_id: Optional[str] = None

class TrackViewResponse(BaseModel):
    """Reel izleme kaydı response"""
    success: bool = Field(default=True)
    message: str = Field(default="View tracked successfully")
    engagement_score: float = Field(default=0.0)
    personalization_level: str = Field(default="cold")
    total_interactions: int = Field(default=0)
    view_id: Optional[str] = None
    meaningful_view: bool = Field(default=False)
    daily_progress_updated: bool = Field(default=False)
    new_achievement: Optional[str] = None

# ============ PAGINATION & FEED MODELS ============

class FeedPagination(BaseModel):
    """Feed pagination bilgisi"""
    current_page: int = Field(default=1)
    has_next: bool = Field(default=False)
    has_previous: bool = Field(default=False)
    next_cursor: Optional[str] = None
    total_available: int = Field(default=0)

class FeedMetadata(BaseModel):
    """Feed algoritma metadata"""
    trending_count: int = Field(default=0)
    personalized_count: int = Field(default=0)
    fresh_count: int = Field(default=0)
    algorithm_version: str = Field(default="v1.0")
    exploration_count: int = Field(default=0)
    personalization_level: str = Field(default="cold")

class FeedResponse(BaseModel):
    """Instagram-style feed response"""
    success: bool = Field(default=True)
    reels: List[ReelFeedItem] = Field(..., description="Reel listesi")
    pagination: FeedPagination = Field(...)
    feed_metadata: FeedMetadata = Field(...)
    generated_at: datetime = Field(default_factory=datetime.now)

class DetailViewEvent(BaseModel):
    """Haber detayı görüntüleme event'i"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="Kullanıcı ID")
    reel_id: str = Field(..., description="Reel ID")
    read_duration_ms: int = Field(..., ge=0)
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0)
    returned_to_feed: bool = Field(default=True)
    shared_from_detail: bool = Field(default=False)
    saved_from_detail: bool = Field(default=False)
    opened_at: datetime = Field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def is_meaningful_read(self) -> bool:
        """Anlamlı okuma mı (10+ saniye ve %30+ scroll)"""
        return self.read_duration_ms >= 10000 and self.scroll_depth >= 0.3
    
    def get_detail_engagement_score(self) -> float:
        """Detay okuma engagement skoru (0.0 - 1.0)"""
        time_score = min(self.read_duration_ms / 60000, 1.0)
        scroll_score = self.scroll_depth
        base_score = 0.6 * time_score + 0.4 * scroll_score
        
        bonus = 0.0
        if self.shared_from_detail:
            bonus += 0.2
        if self.saved_from_detail:
            bonus += 0.15
        
        return min(base_score + bonus, 1.0)

# ============ UTILITY MODELS ============

class TimeRange(BaseModel):
    """Zaman aralığı filtresi"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    def get_date_range(self) -> Tuple[date, date]:
        """Tarih aralığını tuple olarak döndür"""
        end_dt = self.end_date or date.today()
        start_dt = self.start_date or end_dt
        return start_dt, end_dt

class StatsFilter(BaseModel):
    """İstatistik filtreleme modeli"""
    user_id: Optional[str] = None
    category: Optional[str] = None
    time_range: Optional[TimeRange] = None
    min_duration_ms: Optional[int] = None

# ============ EXPORTS ============

__all__ = [
    # Enums
    "ViewStatus",
    "TrendPeriod", 
    "ReelStatus",
    "EmojiType",
    
    # Core models
    "ReelView", 
    "UserDailyStats",
    "UserReelStats",
    "ReelAnalytics",
    "DailyProgress",
    "NewsData",
    "DetailViewEvent",
    
    # Feed models
    "ReelFeedItem",
    "TrendingReels",
    "FeedResponse",
    "FeedPagination", 
    "FeedMetadata",
    
    # Request/Response
    "TrackViewRequest",
    "TrackViewResponse",
    "TrackDetailViewRequest",
    
    # Utilities
    "TimeRange",
    "StatsFilter",
]