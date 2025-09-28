# ================================
# src/models/reels_tracking.py - Reels Tracking Models
# ================================

"""
Reels izleme, kullanıcı aktivitesi ve progress tracking modelleri
Basit ve genişletilebilir yapı
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from enum import Enum

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
    
    def is_meaningful_view(self) -> bool:
        """Anlamlı bir izleme mi (3sn+ için True)"""
        return self.duration_ms >= 3000
    
    def get_duration_seconds(self) -> float:
        """İzleme süresini saniye olarak döndür"""
        return self.duration_ms / 1000.0

class UserDailyStats(BaseModel):
    """Kullanıcının günlük istatistikleri"""
    user_id: str
    stats_date: date = Field(default_factory=date.today)
    
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
    
    # Averages
    avg_daily_reels: float = Field(default=0.0, description="Günlük ortalama reel")
    avg_daily_screen_time_ms: float = Field(default=0.0, description="Günlük ortalama ekran süresi")
    avg_reel_duration_ms: float = Field(default=0.0, description="Ortalama reel izleme süresi")
    
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

# ============ REEL ANALYTICS MODELS ============

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
        
        # Completion rate (40%) + Average duration (30%) + Views (30%)
        completion_score = self.completion_rate * 4.0
        duration_score = min(self.avg_view_duration_ms / 30000, 1.0) * 3.0  # 30sn max
        view_score = min(self.total_views / 100, 1.0) * 3.0  # 100 view max
        
        return completion_score + duration_score + view_score

# ============ PROGRESS TRACKING MODELS ============

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

# ============ FEED & TRENDING MODELS ============

class ReelFeedItem(BaseModel):
    """Feed'deki bir reel item'i"""
    reel_id: str
    title: str
    category: str
    published_at: datetime
    
    # User-specific flags
    is_watched: bool = Field(default=False, description="Kullanıcı tarafından izlendi mi")
    is_trending: bool = Field(default=False, description="Trend mi")
    
    # Analytics info
    trend_rank: Optional[int] = Field(None, description="Trend sıralaması")
    total_views: int = Field(default=0, description="Toplam görüntülenme")
    total_screen_time_ms: int = Field(default=0, description="Toplam ekran süresi")
    
    # Recommendation score
    recommendation_score: float = Field(default=0.0, description="Öneri puanı")

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

class TrackViewResponse(BaseModel):
    """Reel izleme kaydı response'u"""
    success: bool = Field(default=True)
    message: str = Field(default="View tracked successfully")
    
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
    
# ============ EXPORTS ============

__all__ = [
    # Enums
    "ViewStatus",
    "TrendPeriod",
    
    # Core models
    "ReelView", 
    "UserDailyStats",
    "UserReelStats",
    "ReelAnalytics",
    "DailyProgress",
    
    # Feed models
    "ReelFeedItem",
    "TrendingReels",
    
    # Request/Response
    "TrackViewRequest",
    "TrackViewResponse",
    
    # Utilities
    "TimeRange",
    "StatsFilter"
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