# ================================
# src/services/reels_analytics.py - Reels Analytics Service
# ================================

"""
Reels Analytics Service - Tracking, Statistics ve Feed Management
In-memory implementation (production'da database kullanılacak)
"""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import hashlib

from ..models.reels_tracking import (
    ReelView, UserReelStats, UserDailyStats, DailyProgress,
    ReelAnalytics, ReelFeedItem, TrendingReels, TrendPeriod,
    TrackViewRequest, TrackViewResponse, ViewStatus
)

class ReelsAnalyticsService:
    """Reels analytics ve tracking servisi"""
    
    def __init__(self):
        # In-memory storage (production'da database olacak)
        self.view_storage: Dict[str, List[ReelView]] = defaultdict(list)  # user_id -> views
        self.user_stats: Dict[str, UserReelStats] = {}  # user_id -> stats
        self.daily_progress: Dict[str, Dict[str, DailyProgress]] = defaultdict(dict)  # user_id -> date -> progress
        self.reel_analytics: Dict[str, ReelAnalytics] = {}  # reel_id -> analytics
        
        # Cache for performance
        self._trending_cache: Optional[TrendingReels] = None
        self._cache_expiry: Optional[datetime] = None
        
        print("✅ Reels Analytics Service initialized (in-memory)")
    
    # ============ CORE TRACKING METHODS ============
    
    async def track_reel_view(self, user_id: str, request: TrackViewRequest) -> TrackViewResponse:
        """
        Reel izleme kaydı oluştur ve tüm istatistikleri güncelle
        """
        try:
            # ReelView oluştur
            view = ReelView(
                reel_id=request.reel_id,
                user_id=user_id,
                viewed_at=datetime.now(),
                duration_ms=request.duration_ms,
                status=ViewStatus.COMPLETED if request.completed else ViewStatus.PARTIAL,
                completed=request.completed,
                category=request.category,
                session_id=request.session_id
            )
            
            # View'ı kaydet
            self.view_storage[user_id].append(view)
            
            # Kullanıcı istatistiklerini güncelle
            await self._update_user_stats(user_id, view)
            
            # Günlük progress'i güncelle
            await self._update_daily_progress(user_id, view)
            
            # Reel analytics'i güncelle
            await self._update_reel_analytics(request.reel_id, view)
            
            # Trending cache'i invalidate et
            self._invalidate_trending_cache()
            
            # Response oluştur
            view_id = f"{user_id}_{request.reel_id}_{int(datetime.now().timestamp())}"
            meaningful_view = view.is_meaningful_view()
            
            return TrackViewResponse(
                success=True,
                message="View tracked successfully",
                view_id=view_id,
                meaningful_view=meaningful_view,
                daily_progress_updated=True
            )
            
        except Exception as e:
            print(f"❌ Track view error: {e}")
            return TrackViewResponse(
                success=False,
                message=f"Failed to track view: {str(e)}"
            )
    
    async def get_user_watched_reels(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Kullanıcının izlediği reels listesi
        """
        try:
            user_views = self.view_storage.get(user_id, [])
            
            # Son izlenen reels'i al (unique reel_id'ler)
            seen_reels = set()
            watched_reels = []
            
            for view in reversed(user_views):  # En yeniden başla
                if view.reel_id not in seen_reels and len(watched_reels) < limit:
                    seen_reels.add(view.reel_id)
                    
                    watched_reels.append({
                        "reel_id": view.reel_id,
                        "viewed_at": view.viewed_at.isoformat(),
                        "duration_ms": view.duration_ms,
                        "completed": view.completed,
                        "category": view.category,
                        "status": view.status
                    })
            
            return watched_reels
            
        except Exception as e:
            print(f"❌ Get watched reels error: {e}")
            return []
    
    async def get_user_daily_progress(self, user_id: str, target_date: date = None) -> DailyProgress:
        """
        Kullanıcının günlük progress'ini al
        """
        if target_date is None:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        
        # Mevcut progress'i al veya oluştur
        if date_str not in self.daily_progress[user_id]:
            self.daily_progress[user_id][date_str] = DailyProgress(
                user_id=user_id,
                progress_date=target_date,
                total_published_today=await self._get_published_count_for_date(target_date),
                watched_today=0
            )
        
        progress = self.daily_progress[user_id][date_str]
        
        # Progress'i yeniden hesapla
        progress.calculate_progress()
        
        return progress
    
    async def get_user_stats(self, user_id: str) -> UserReelStats:
        """
        Kullanıcının genel istatistiklerini al
        """
        if user_id not in self.user_stats:
            # Yeni kullanıcı için boş stats oluştur
            self.user_stats[user_id] = UserReelStats(user_id=user_id)
        
        return self.user_stats[user_id]
    
    # ============ FEED & TRENDING METHODS ============
    
    async def generate_user_feed(self, user_id: str, limit: int = 20) -> List[ReelFeedItem]:
        """
        Kullanıcı için kişiselleştirilmiş feed oluştur
        """
        try:
            # Trending reels al
            trending = await self.get_trending_reels(TrendPeriod.DAILY, limit // 2)
            
            # Recent reels simülasyonu (gerçek implementation'da database'den gelecek)
            recent_reels = await self._get_recent_reels(limit // 2)
            
            # Kullanıcının izlediği reels
            watched_reel_ids = await self._get_user_watched_reel_ids(user_id)
            
            # Feed'i birleştir
            feed_items = []
            
            # Trending'leri ekle
            for reel in trending:
                reel.is_watched = reel.reel_id in watched_reel_ids
                reel.is_trending = True
                feed_items.append(reel)
            
            # Recent'leri ekle
            for reel in recent_reels:
                if reel.reel_id not in [f.reel_id for f in feed_items]:  # Duplicate check
                    reel.is_watched = reel.reel_id in watched_reel_ids
                    reel.is_trending = False
                    feed_items.append(reel)
            
            return feed_items[:limit]
            
        except Exception as e:
            print(f"❌ Generate feed error: {e}")
            return []
    
    async def get_trending_reels(self, period: TrendPeriod, limit: int = 20) -> List[ReelFeedItem]:
        """
        Trending reels'i al (cache'li)
        """
        try:
            # Cache kontrolü
            if (self._trending_cache and self._cache_expiry and 
                datetime.now() < self._cache_expiry and 
                self._trending_cache.period == period):
                return self._trending_cache.get_top_trending(limit)
            
            # Trending'i hesapla
            trending_reels = await self._calculate_trending_reels(period, limit * 2)
            
            # Cache'e kaydet
            self._trending_cache = TrendingReels(
                period=period,
                trending_reels=trending_reels,
                total_reels_analyzed=len(self.reel_analytics)
            )
            self._cache_expiry = datetime.now() + timedelta(minutes=15)  # 15 dakika cache
            
            return trending_reels[:limit]
            
        except Exception as e:
            print(f"❌ Get trending reels error: {e}")
            return []
    
    async def get_latest_published_reel(self) -> Optional[Dict[str, Any]]:
        """
        En son yayınlanan reel'i al
        """
        try:
            # Simulated data (gerçek implementation'da database'den gelecek)
            return {
                "reel_id": "latest_001",
                "title": "Son Dakika: Önemli Gelişme",
                "category": "guncel",
                "published_at": datetime.now().isoformat(),
                "total_views": 0
            }
            
        except Exception as e:
            print(f"❌ Get latest reel error: {e}")
            return None
    
    async def get_reel_analytics(self, reel_id: str) -> Optional[ReelAnalytics]:
        """
        Belirli bir reel'in analytics'ini al
        """
        return self.reel_analytics.get(reel_id)
    
    # ============ PRIVATE HELPER METHODS ============
    
    async def _update_user_stats(self, user_id: str, view: ReelView):
        """Kullanıcı istatistiklerini güncelle"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserReelStats(user_id=user_id)
        
        stats = self.user_stats[user_id]
        
        # Basic stats güncelle
        stats.total_reels_watched += 1
        stats.total_screen_time_ms += view.duration_ms
        stats.last_reel_viewed_at = view.viewed_at
        stats.last_viewed_reel_id = view.reel_id
        
        # Completion rate hesapla
        user_views = self.view_storage[user_id]
        completed_views = sum(1 for v in user_views if v.completed)
        stats.completion_rate = completed_views / len(user_views) if user_views else 0
        
        # Favorite categories güncelle
        if view.category:
            category_counts = Counter(v.category for v in user_views if v.category)
            stats.favorite_categories = [cat for cat, _ in category_counts.most_common(3)]
        
        # Average hesaplamaları
        if stats.total_days_active > 0:
            stats.avg_daily_reels = stats.total_reels_watched / stats.total_days_active
            stats.avg_daily_screen_time_ms = stats.total_screen_time_ms / stats.total_days_active
        
        if user_views:
            stats.avg_reel_duration_ms = sum(v.duration_ms for v in user_views) / len(user_views)
    
    async def _update_daily_progress(self, user_id: str, view: ReelView):
        """Günlük progress'i güncelle"""
        today = date.today()
        date_str = today.isoformat()
        
        if date_str not in self.daily_progress[user_id]:
            self.daily_progress[user_id][date_str] = DailyProgress(
                user_id=user_id,
                progress_date=today,
                total_published_today=await self._get_published_count_for_date(today)
            )
        
        progress = self.daily_progress[user_id][date_str]
        
        # Watched count güncelle (sadece meaningful view'lar için)
        if view.is_meaningful_view():
            progress.watched_today += 1
        
        # Category progress güncelle
        if view.category:
            if view.category not in progress.category_progress:
                progress.category_progress[view.category] = {"published": 5, "watched": 0}  # Simulated
            
            if view.is_meaningful_view():
                progress.category_progress[view.category]["watched"] += 1
        
        # First/last activity güncelle
        if not progress.first_view_today:
            progress.first_view_today = view.viewed_at
        progress.last_view_today = view.viewed_at
        
        # Progress yüzdesini hesapla
        progress.calculate_progress()
    
    async def _update_reel_analytics(self, reel_id: str, view: ReelView):
        """Reel analytics'i güncelle"""
        if reel_id not in self.reel_analytics:
            self.reel_analytics[reel_id] = ReelAnalytics(
                reel_id=reel_id,
                published_at=datetime.now(),
                category=view.category
            )
        
        analytics = self.reel_analytics[reel_id]
        
        # Basic metrics güncelle
        analytics.total_views += 1
        analytics.total_screen_time_ms += view.duration_ms
        
        # Unique viewers (basit implementation)
        analytics.unique_viewers = analytics.total_views  # Simulated
        
        # Completion rate hesapla
        if view.completed:
            # Basit completion rate hesaplama
            analytics.completion_rate = min(1.0, analytics.completion_rate + 0.1)
        
        # Average duration güncelle
        analytics.avg_view_duration_ms = analytics.total_screen_time_ms / analytics.total_views
        
        # Trend score hesapla (basit algoritma)
        recency_factor = max(0, 10 - (datetime.now() - analytics.published_at).hours)
        engagement_factor = min(10, analytics.total_views / 10)
        analytics.trend_score = (recency_factor + engagement_factor) / 2
        
        # Hourly/daily views güncelle
        if (datetime.now() - analytics.published_at).total_seconds() < 3600:  # Son 1 saat
            analytics.hourly_views += 1
        if (datetime.now() - analytics.published_at).total_seconds() < 86400:  # Son 24 saat
            analytics.daily_views += 1
    
    async def _get_published_count_for_date(self, target_date: date) -> int:
        """Belirli bir tarihte yayınlanan haber sayısı (simulated)"""
        # Simulated data - gerçek implementation'da database'den gelecek
        return 15  # Günde ortalama 15 haber
    
    async def _get_recent_reels(self, limit: int) -> List[ReelFeedItem]:
        """Recent reels'i al (simulated)"""
        recent_reels = []
        
        for i in range(limit):
            reel = ReelFeedItem(
                reel_id=f"recent_{i}",
                title=f"Recent News {i+1}",
                category="guncel",
                published_at=datetime.now() - timedelta(hours=i),
                total_views=10 - i
            )
            recent_reels.append(reel)
        
        return recent_reels
    
    async def _get_user_watched_reel_ids(self, user_id: str) -> Set[str]:
        """Kullanıcının izlediği reel ID'lerini al"""
        user_views = self.view_storage.get(user_id, [])
        return {view.reel_id for view in user_views if view.is_meaningful_view()}
    
    async def _calculate_trending_reels(self, period: TrendPeriod, limit: int) -> List[ReelFeedItem]:
        """Trending reels'i hesapla"""
        trending_reels = []
        
        # Reel analytics'lerini trend score'a göre sırala
        sorted_reels = sorted(
            self.reel_analytics.values(),
            key=lambda x: x.trend_score,
            reverse=True
        )
        
        for analytics in sorted_reels[:limit]:
            reel = ReelFeedItem(
                reel_id=analytics.reel_id,
                title=f"Trending: {analytics.reel_id}",
                category=analytics.category or "guncel",
                published_at=analytics.published_at,
                total_views=analytics.total_views,
                is_trending=True,
                trend_rank=len(trending_reels) + 1,
                recommendation_score=analytics.trend_score
            )
            trending_reels.append(reel)
        
        return trending_reels
    
    def _invalidate_trending_cache(self):
        """Trending cache'i temizle"""
        self._trending_cache = None
        self._cache_expiry = None

# Global instance
reels_analytics = ReelsAnalyticsService()
    

"""

Core Tracking:

track_reel_view(): Reel izleme kaydı + tüm istatistikleri güncelle
get_user_watched_reels(): Kullanıcının izlediği reels listesi
get_user_daily_progress(): Günlük progress (%kaç haber izlendi)
get_user_stats(): Genel kullanıcı istatistikleri

Trending & Feed:

get_trending_reels(): Ekran süresi bazlı trending (cache'li)
get_latest_published_reel(): En son yayınlanan reel
generate_user_feed(): Kişiselleştirilmiş feed (trending + recent + watched flags)

Analytics:

get_reel_analytics(): Reel'in kendi analytics bilgileri
Otomatik trend score hesaplama (view recency + engagement)
Real-time istatistik güncelleme




# Reel izleme kaydı
response = await reels_analytics.track_reel_view("user123", TrackViewRequest(
    reel_id="aa_567", 
    duration_ms=45000, 
    completed=True
))

# Günlük progress
progress = await reels_analytics.get_user_daily_progress("user123")
print(f"Bugün %{progress.progress_percentage} tamamlandı")

# Feed oluştur
feed = await reels_analytics.generate_user_feed("user123", limit=20)

"""