# ================================
# src/models/reels_tracking.py - Updated ReelFeedItem Model
# ================================

"""
Reels izleme, kullanıcı aktivitesi ve progress tracking modelleri
Mockup data yapısına uygun olarak güncellendi
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from enum import Enum
import uuid  # ← EKLE
# ============ ENUMS ============

class ViewStatus(str, Enum):
    """Reel izleme durumu"""
    STARTED = "started"          # İzlemeye başlandı
    COMPLETED = "completed"      # Tamamen izlendi (3sn+)
    SKIPPED = "skipped"         # Atlandı
    PARTIAL = "partial"         # Kısmen izlendi

class TrendPeriod(str, Enum):
    """Trend hesaplama periyodu"""
    HOURLY = "hourly"           # Son 1 saat
    DAILY = "daily"             # Son 24 saat  
    WEEKLY = "weekly"           # Son 7 gün

class ReelStatus(str, Enum):
    """Reel durumu - mockup'a uygun"""
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    FAILED = "failed"


# YENİ EKLE:
class EmojiType(str, Enum):
    """
    Emoji türleri - TÜM EMOJİLER AYNI AĞIRLIKTA (+0.9)
    Kullanıcı emoji attıysa → haberi beğendi demektir
    """
    HEART = "❤️"           # Kalp
    LIKE = "👍"            # Beğen
    FIRE = "🔥"            # Ateş
    STAR = "⭐"            # Yıldız
    CLAP = "👏"            # Alkış
    LOVE = "😍"            # Aşık
    THINKING = "🤔"        # Düşünüyor
    WOW = "😮"             # Şaşırdı
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
    
    
    # 🆕 NEW: Emoji reaction tracking
    emoji_reaction: Optional[EmojiType] = Field(None, description="Emoji tepkisi")
    emoji_timestamp: Optional[datetime] = Field(None, description="Emoji atılma zamanı")

    # 🆕 NEW: Detail view tracking
    detail_viewed: bool = Field(default=False, description="Detayları görüntüledi mi")
    detail_duration_ms: int = Field(default=0, ge=0, description="Detayda geçirilen süre (ms)")
    detail_scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Detay scroll derinliği")
    detail_opened_at: Optional[datetime] = Field(None, description="Detay açılma zamanı")
    detail_closed_at: Optional[datetime] = Field(None, description="Detay kapanma zamanı")

    # 🆕 NEW: Extended engagement signals
    paused_count: int = Field(default=0, ge=0, description="Duraklama sayısı")
    replayed: bool = Field(default=False, description="Tekrar oynat tıklandı mı")
    shared: bool = Field(default=False, description="Paylaşıldı mı")
    saved: bool = Field(default=False, description="Kaydedildi mi")

    def is_meaningful_view(self) -> bool:
        """
        Anlamlı izleme mi? (3+ saniye veya emoji/detail view var)
        
        Anlamlı izleme kriterleri:
        - 3+ saniye izledi
        - VEYA emoji attı (ilgi gösterdi)
        - VEYA detay okudu (merak etti)
        """
        has_minimum_watch = self.duration_ms >= 3000
        has_emoji = self.emoji_reaction is not None
        has_detail_view = self.detail_viewed and self.detail_duration_ms >= 5000  # 5+ saniye detay
        
        return has_minimum_watch or has_emoji or has_detail_view

    def get_engagement_score(self) -> float:
        """
        Engagement skoru hesapla (0.0 - 1.5 arası)
        
        Skorlama sistemi:
        - Audio izleme: 0.0 - 0.7
        - Emoji reaction: +0.9 (tüm emojiler aynı)
        - Detail view: +0.0 - 0.6 (süreye göre)
        - Extra signals: +0.1 - 0.3
        
        Maksimum skor: 1.5 (mükemmel engagement)
        """
        score = 0.0
        
        # 1. Audio izleme skoru (max 0.7)
        if self.status == ViewStatus.COMPLETED:
            audio_score = 0.7
        elif self.duration_ms >= 30000:  # 30+ saniye
            audio_score = 0.6
        elif self.duration_ms >= 15000:  # 15+ saniye
            audio_score = 0.4
        elif self.duration_ms >= 5000:   # 5+ saniye
            audio_score = 0.2
        else:
            audio_score = 0.1  # Hemen skip etti
        
        score += audio_score
        
        # 2. Emoji reaction bonus (TÜM EMOJİLER +0.9)
        if self.emoji_reaction is not None:
            score += 0.9
        
        # 3. Detail view bonus (max +0.6)
        if self.detail_viewed:
            # Detayda geçirilen süreye göre
            if self.detail_duration_ms >= 60000:  # 60+ saniye
                detail_score = 0.6
            elif self.detail_duration_ms >= 30000:  # 30+ saniye
                detail_score = 0.5
            elif self.detail_duration_ms >= 15000:  # 15+ saniye
                detail_score = 0.4
            elif self.detail_duration_ms >= 5000:   # 5+ saniye
                detail_score = 0.2
            else:
                detail_score = 0.1
            
            # Scroll depth bonusu
            if self.detail_scroll_depth >= 0.8:  # %80+ scroll
                detail_score += 0.1
            elif self.detail_scroll_depth >= 0.5:  # %50+ scroll
                detail_score += 0.05
            
            score += detail_score
        
        # 4. Extra engagement signals (max +0.3)
        if self.replayed:
            score += 0.1  # Tekrar izledi → önemli
        if self.shared:
            score += 0.15  # Paylaştı → çok önemli
        if self.saved:
            score += 0.1   # Kaydetti → ileride okumak istiyor
        if self.paused_count > 0:
            score += min(0.05 * self.paused_count, 0.1)  # Duraklattı → dikkatli dinliyor
        
        return min(score, 1.5)  # Max 1.5

    def get_preference_weight(self) -> float:
        """
        Preference engine için ağırlık (0.0 - 1.0 normalleştirilmiş)
        
        Bu değer kullanıcı tercih skorlarını güncellerken kullanılır
        """
        engagement = self.get_engagement_score()
        # 1.5 üzerinden normalize et
        return min(engagement / 1.5, 1.0)    
    
    
    def get_duration_seconds(self) -> float:
        """İzleme süresini saniye olarak döndür"""
        return self.duration_ms / 1000.0

class UserDailyStats(BaseModel):
    """Kullanıcının günlük istatistikleri"""
    user_id: str
    stats_date: date = Field(default_factory=date.today)
    
    # 🆕 NEW: Emoji & Detail stats
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
    
    # 🆕 NEW: Emoji & Detail stats
    total_emoji_reactions: int = Field(default=0, description="Toplam emoji sayısı")
    total_detail_views: int = Field(default=0, description="Toplam detay görüntüleme")
    detail_view_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Detay okuma oranı")
    
    # Averages
    avg_daily_reels: float = Field(default=0.0, description="Günlük ortalama reel")
    avg_daily_screen_time_ms: float = Field(default=0.0, description="Günlük ortalama ekran süresi")
    avg_reel_duration_ms: float = Field(default=0.0, description="Ortalama reel izleme süresi")
    # Mevcut averages'a ekle:
    avg_engagement_score: float = Field(default=0.0, description="Ortalama engagement skoru")
    
    
    # Engagement
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Tamamlama oranı")
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
    
    

    # YENİ METOD EKLE:
    def get_personalization_level(self) -> str:
        """
        Kullanıcının personalization seviyesi
        
        - cold: 0-10 etkileşim (trending feed)
        - warm: 10-50 etkileşim (rule-based)
        - hot: 50+ etkileşim (NLP-powered)
        """
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
    
    # 🆕 NEW: Emoji & Detail metrics
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
        """
        Engagement skoru hesapla (0-10)
        
        Faktörler:
        - Completion rate (30%)
        - Average duration (20%)
        - View count (20%)
        - Emoji rate (15%)
        - Detail view rate (15%)
        """
        if self.total_views == 0:
            return 0.0
        
        # Completion rate (30%) → 0-3 puan
        completion_score = self.completion_rate * 3.0
        
        # Duration (20%) → 0-2 puan (30sn max)
        duration_score = min(self.avg_view_duration_ms / 30000, 1.0) * 2.0
        
        # View count (20%) → 0-2 puan (100 view max)
        view_score = min(self.total_views / 100, 1.0) * 2.0
        
        # Emoji rate (15%) → 0-1.5 puan
        emoji_score = self.emoji_rate * 1.5
        
        # Detail view rate (15%) → 0-1.5 puan
        detail_score = self.detail_view_rate * 1.5
        
        total_score = (
            completion_score + 
            duration_score + 
            view_score + 
            emoji_score + 
            detail_score
        )
        
        return round(total_score, 2)        

class DailyProgress(BaseModel):
    """Kullanıcının günlük progress takibi"""
    user_id: str
    progress_date: date = Field(default_factory=date.today)
    
    # Daily news stats
    total_published_today: int = Field(default=0, description="O gün yayınlanan toplam haber")
    watched_today: int = Field(default=0, description="O gün izlenen haber sayısı")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="İlerleme yüzdesi")
    
    # Category breakdown
    category_progress: Dict[str, Dict[str, int]] = Field(
        default_factory=dict, 
        description="Kategori bazlı progress {category: {published: X, watched: Y}}"
    )
    
    # Timestamps
    first_view_today: Optional[datetime] = Field(None, description="İlk izleme zamanı")
    last_view_today: Optional[datetime] = Field(None, description="Son izleme zamanı")
    
    def calculate_progress(self) -> float:
        """Progress yüzdesini hesapla ve güncelle"""
        if self.total_published_today == 0:
            self.progress_percentage = 0.0
        else:
            self.progress_percentage = (self.watched_today / self.total_published_today) * 100.0
        
        return self.progress_percentage
    
    def get_category_progress(self, category: str) -> float:
        """Belirli bir kategorinin progress yüzdesini al"""
        if category not in self.category_progress:
            return 0.0
        
        cat_data = self.category_progress[category]
        if cat_data.get("published", 0) == 0:
            return 0.0
        
        return (cat_data.get("watched", 0) / cat_data["published"]) * 100.0

# ============ NEWS DATA MODEL (Mockup'tan uyarlandı) ============

class NewsData(BaseModel):
    """Reel'deki haber verisi - mockup'taki ScrapedNewsItem'a benzer"""
    title: str
    summary: str
    full_content: List[str] = Field(default_factory=list, description="Paragraflar listesi")  # ✅
    url: str
    
    # Metadata
    category: str
    author: Optional[str] = None
    location: Optional[str] = None
    published_date: str
    # scraped_date: str
    
    # Media
    main_image: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    
    # SEO & Tags
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list, description="Haber anahtar kelimeleri - NLP için kritik")
    
    # meta_description: Optional[str] = None
    
       # Metrics
    estimated_reading_time: int = Field(default=3, description="Tahmini okuma süresi (dakika)")
    source: str = Field(default="aa", description="Kaynak")
    
    # Metrics
    word_count: int
    character_count: int
    
    # Technical
    # scraping_quality: str = "high"  # high, medium, low
    content_language: str = "tr"

# ============ FEED & REEL MODELS (Updated to match Mockup) ============

class ReelFeedItem(BaseModel):
    """Feed'deki bir reel item'i - mockup yapısına uygun"""
    
    # Core identifiers
    id: str = Field(..., description="Reel unique ID")
    
    # News data (full news content)
    news_data: NewsData = Field(..., description="Haber verisi")
    
    # TTS & Audio info (mockup'tan)
    tts_content: str = Field(..., description="TTS için kullanılan metin")
    voice_used: str = Field(default="alloy", description="Kullanılan ses")
    model_used: str = Field(default="tts-1", description="Kullanılan TTS model")
    
    # Audio files
    audio_url: str = Field(..., description="Ses dosyası URL'i")
    duration_seconds: int = Field(..., description="Ses süresi (saniye)")
    file_size_mb: float = Field(default=0.0, description="Dosya boyutu (MB)")
    
    # Publishing info
    status: ReelStatus = Field(default=ReelStatus.PUBLISHED, description="Reel durumu")
    published_at: datetime = Field(..., description="Yayınlanma zamanı")
    created_at: datetime = Field(default_factory=datetime.now, description="Oluşturulma zamanı")
    
    # Analytics & Engagement
    total_views: int = Field(default=0, description="Toplam görüntülenme")
    total_screen_time_ms: int = Field(default=0, description="Toplam ekran süresi")
    completion_rate: float = Field(default=0.0, description="Tamamlama oranı")
    trend_score: float = Field(default=0.0, description="Trend puanı")
    
    # User-specific flags
    is_watched: bool = Field(default=False, description="Kullanıcı tarafından izlendi mi")
    is_trending: bool = Field(default=False, description="Trend mi")
    is_fresh: bool = Field(default=False, description="Yeni mi (son 3 saat)")
    
    # 🆕 NEW: Personalization metadata
    is_recommended: bool = Field(default=False, description="Kullanıcıya özel öneri mi")
    recommendation_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Öneri skoru")
    recommendation_reason: Optional[str] = Field(None, description="Öneri nedeni")
    

    feed_reason: str = Field(default="algorithmic", description="Feed'de olma sebebi")
    trend_rank: Optional[int] = Field(None, description="Trend sıralaması")
    
    # Cost tracking (mockup'tan)
    character_count: int = Field(default=0, description="TTS karakter sayısı")
    estimated_cost: float = Field(default=0.0, description="Tahmini maliyet")
    processing_time_seconds: float = Field(default=0.0, description="İşlem süresi")
    
    # Thumbnail (gelecekte eklenecek)
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL'i")
    
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
    
    # Trending list
    trending_reels: List[ReelFeedItem] = Field(default_factory=list)
    
    # Metadata
    total_reels_analyzed: int = Field(default=0, description="Analiz edilen toplam reel")
    trending_threshold: float = Field(default=5.0, description="Trend olma eşiği")
    
    def get_top_trending(self, count: int = 10) -> List[ReelFeedItem]:
        """En trend olan N reel'i al"""
        return self.trending_reels[:count]

# ============ REQUEST/RESPONSE MODELS ============

class TrackViewRequest(BaseModel):
    """Reel izleme kaydı request'i"""
    reel_id: str = Field(..., description="İzlenen reel ID")
    duration_ms: int = Field(..., ge=0, description="İzleme süresi (ms)")
    completed: bool = Field(default=False, description="Tamamen izlendi mi")
    category: Optional[str] = Field(None, description="Reel kategorisi")
    session_id: Optional[str] = Field(None, description="Session ID")
    emoji_reaction: Optional[EmojiType] = Field(None, description="Emoji tepkisi")

    # 🆕 NEW: Optional extra signals
    paused_count: Optional[int] = Field(0, description="Duraklama sayısı")
    replayed: Optional[bool] = Field(False, description="Tekrar oynat")
    shared: Optional[bool] = Field(False, description="Paylaşıldı mı")
    saved: Optional[bool] = Field(False, description="Kaydedildi mi")

class TrackDetailViewRequest(BaseModel):
    """Detay görüntüleme tracking request'i"""
    reel_id: str = Field(..., description="Görüntülenen reel ID")
    read_duration_ms: int = Field(..., ge=0, description="Okuma süresi")
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Scroll derinliği")
    shared_from_detail: bool = Field(default=False, description="Detaydan paylaştı mı")
    saved_from_detail: bool = Field(default=False, description="Detaydan kaydetti mi")
    session_id: Optional[str] = None

class TrackViewResponse(BaseModel):
    """Reel izleme kaydı response'u"""
    success: bool = Field(default=True)
    message: str = Field(default="View tracked successfully")

    engagement_score: float = Field(default=0.0, description="Engagement skoru")

    # 🆕 NEW: Personalization level
    personalization_level: str = Field(default="cold", description="cold/warm/hot")
    total_interactions: int = Field(default=0, description="Toplam etkileşim sayısı")


    # View info
    view_id: Optional[str] = Field(None, description="View kaydının ID'si")
    meaningful_view: bool = Field(default=False, description="Anlamlı izleme mi")
    
    # User stats update
    daily_progress_updated: bool = Field(default=False)
    new_achievement: Optional[str] = Field(None, description="Yeni başarım varsa")

# ============ UTILITY MODELS ============

class TimeRange(BaseModel):
    """Zaman aralığı filtresi"""
    start_date: Optional[date] = Field(None, description="Başlangıç tarihi")
    end_date: Optional[date] = Field(None, description="Bitiş tarihi")
    
    def get_date_range(self) -> Tuple[date, date]:
        """Tarih aralığını tuple olarak döndür"""
        end_dt = self.end_date or date.today()
        start_dt = self.start_date or end_dt
        return start_dt, end_dt

class StatsFilter(BaseModel):
    """İstatistik filtreleme modeli"""
    user_id: Optional[str] = Field(None, description="Kullanıcı filtresi")
    category: Optional[str] = Field(None, description="Kategori filtresi")
    time_range: Optional[TimeRange] = Field(None, description="Zaman aralığı")
    min_duration_ms: Optional[int] = Field(None, description="Minimum izleme süresi")

# ============ PAGINATION MODELS (Instagram-style) ============

class FeedPagination(BaseModel):
    """Feed pagination bilgisi"""
    current_page: int = Field(default=1, description="Mevcut sayfa")
    has_next: bool = Field(default=False, description="Sonraki sayfa var mı")
    has_previous: bool = Field(default=False, description="Önceki sayfa var mı")
    next_cursor: Optional[str] = Field(None, description="Sonraki sayfa cursor'u")
    total_available: int = Field(default=0, description="Toplam mevcut reel sayısı")

class FeedMetadata(BaseModel):
    """Feed algoritma metadata'sı"""
    trending_count: int = Field(default=0, description="Trending reel sayısı")
    personalized_count: int = Field(default=0, description="Kişiselleştirilmiş reel sayısı")
    fresh_count: int = Field(default=0, description="Yeni reel sayısı")
    algorithm_version: str = Field(default="v1.0", description="Algoritma versiyonu")
    exploration_count: int = Field(default=0, description="Keşfet reelleri")
    personalization_level: str = Field(default="cold", description="Personalization seviyesi")

class FeedResponse(BaseModel):
    """Instagram-style feed response"""
    success: bool = Field(default=True)
    reels: List[ReelFeedItem] = Field(..., description="Reel listesi")
    pagination: FeedPagination = Field(..., description="Sayfalama bilgisi")
    feed_metadata: FeedMetadata = Field(..., description="Feed metadata'sı")
    generated_at: datetime = Field(default_factory=datetime.now, description="Oluşturulma zamanı")





# ==================== KULLANICIYA ÖZEL REELS VERİLERİ ÇEKMEK İÇİN ====================
class DetailViewEvent(BaseModel):
    """
    Haber detayı görüntüleme event'i
    
    Kullanıcı "Detayları Oku" butonuna tıklayınca oluşturulur
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="Kullanıcı ID")
    reel_id: str = Field(..., description="Reel ID")
    
    # Reading behavior
    read_duration_ms: int = Field(..., ge=0, description="Okuma süresi (ms)")
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Scroll derinliği")
    
    # Actions
    returned_to_feed: bool = Field(default=True, description="Feed'e geri döndü mü")
    shared_from_detail: bool = Field(default=False, description="Detaydan paylaştı mı")
    saved_from_detail: bool = Field(default=False, description="Detaydan kaydetti mi")
    
    # Timestamps
    opened_at: datetime = Field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    
    # Session
    session_id: Optional[str] = None
    
    def is_meaningful_read(self) -> bool:
        """
        Anlamlı okuma mı?
        
        Kriterler:
        - 10+ saniye okudu
        - VE %30+ scroll yaptı
        """
        return (
            self.read_duration_ms >= 10000 and 
            self.scroll_depth >= 0.3
        )
    
    def get_detail_engagement_score(self) -> float:
        """
        Detay okuma engagement skoru (0.0 - 1.0)
        
        Bu skor kullanıcı profilini güncellerken EKSTRA boost için kullanılır
        """
        # Süre skoru (max 60sn = 1.0)
        time_score = min(self.read_duration_ms / 60000, 1.0)
        
        # Scroll depth skoru
        scroll_score = self.scroll_depth
        
        # Ağırlıklı ortalama (süre daha önemli)
        base_score = 0.6 * time_score + 0.4 * scroll_score
        
        # Bonuslar
        bonus = 0.0
        if self.shared_from_detail:
            bonus += 0.2  # Detaydan paylaştı → çok önemli!
        if self.saved_from_detail:
            bonus += 0.15  # Kaydetti → ileride tekrar okumak istiyor
        
        return min(base_score + bonus, 1.0)









# ============ EXPORTS ============
__all__ = [
    # Enums
    "ViewStatus",
    "TrendPeriod", 
    "ReelStatus",
    "EmojiType",  # ← YENİ
    
    # Core models
    "ReelView", 
    "UserDailyStats",
    "UserReelStats",
    "ReelAnalytics",
    "DailyProgress",
    "NewsData",
    "DetailViewEvent",  # ← YENİ
    
    # Feed models
    "ReelFeedItem",
    "TrendingReels",
    "FeedResponse",
    "FeedPagination", 
    "FeedMetadata",
    
    # Request/Response
    "TrackViewRequest",
    "TrackViewResponse",
    "TrackDetailViewRequest",  # ← YENİ
    
    # Utilities
    "TimeRange",
    "StatsFilter",
    
    "DetailViewEvent",
    "TrackDetailViewRequest",
    "EmojiType",
]
"""
    Core Tracking:

ReelView: Tek bir reel izleme kaydı (süre, durum, kategori vs)
UserDailyStats: Günlük kullanıcı istatistikleri
UserReelStats: Genel kullanıcı özet istatistikleri
ReelAnalytics: Reel'in kendi analytics verileri

Progress & Feed:

DailyProgress: Günlük progress takibi (%kaç haber izlendi)
ReelFeedItem: Feed'deki her item (trend flag, izlenmiş flag vs)
TrendingReels: Trending listesi yönetimi

Utility:

TrackViewRequest/Response: API request/response modelleri
TimeRange, StatsFilter: Filtreleme için

🚀 Öne Çıkan Özellikler

Anlamlı izleme kontrolü: 3sn+ için is_meaningful_view()
Engagement score: Analytics için otomatik hesaplama
Progress calculation: Günlük %progress otomatik hesabı
Trend scoring: 0-10 arası trend puanı
Category breakdown: Kategori bazlı detaylı analiz
    
    
"""