# ================================
# src/api/endpoints/reels.py - Extended Reels API Endpoints
# ================================

"""
Reels API endpoint'leri - Tracking, Analytics ve Feed sistemi ile genişletilmiş
Orijinal mockup endpoint'leri + yeni tracking fonksiyonları
"""

from fastapi import APIRouter, Query, HTTPException, Depends, Header
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime, date
import hashlib

# Original imports
from ...services.content import content_service
from ...services.processing import processing_service
from ...models.news import NewsResponse, Article
from ...models.base import BaseResponse

# New tracking imports
from ...services.reels_analytics import reels_analytics
from ...models.reels_tracking import (
    TrackViewRequest, TrackViewResponse, UserReelStats, 
    DailyProgress, ReelFeedItem, TrendPeriod, ViewStatus
)

# Router
router = APIRouter(prefix="/api/reels", tags=["reels"])

# ============ REQUEST/RESPONSE MODELS ============

class ReelTrackingRequest(BaseModel):
    """Reel tracking request - frontend'den gelecek"""
    reel_id: str = Field(..., description="İzlenen reel ID'si")
    duration_ms: int = Field(..., ge=0, description="İzleme süresi (milisaniye)")
    completed: bool = Field(default=False, description="Tamamen izlendi mi (3sn+)")
    category: Optional[str] = Field(None, description="Reel kategorisi")
    session_id: Optional[str] = Field(None, description="Frontend session ID")

class MarkSeenRequest(BaseModel):
    """Mark reels as seen request"""
    reel_ids: List[str] = Field(..., description="Görüldü olarak işaretlenecek reel ID'leri")

class UserProgressResponse(BaseModel):
    """Günlük progress response"""
    success: bool = True
    date: str
    progress_percentage: float = Field(..., description="İlerleme yüzdesi")
    total_published_today: int = Field(..., description="Bugün yayınlanan toplam")
    watched_today: int = Field(..., description="Bugün izlenen")
    category_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
class UserStatsResponse(BaseModel):
    """Kullanıcı istatistikleri response"""
    success: bool = True
    user_id: str
    total_reels_watched: int
    total_screen_time_ms: int
    total_screen_time_hours: float
    completion_rate: float
    favorite_categories: List[str]
    last_activity: Optional[str] = None
    current_streak_days: int = 0
    avg_daily_reels: float = 0.0

class FeedResponse(BaseModel):
    """Feed response model"""
    success: bool = True
    reels: List[ReelFeedItem]
    total_count: int
    trending_count: int
    recent_count: int
    user_watched_count: int

# ============ UTILITY FUNCTIONS ============

def get_user_id_from_header(user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """Header'dan user ID al, yoksa default ver"""
    return user_id or "anonymous_user"

# ============ TRACKING ENDPOINTS ============

@router.post("/track-view", response_model=TrackViewResponse)
async def track_reel_view(
    request: ReelTrackingRequest,
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Reel izleme kaydı oluştur
    
    **Frontend'den her reel izlendiğinde çağrılacak**
    
    - **reel_id**: İzlenen reel ID'si  
    - **duration_ms**: Kaç milisaniye izlendi
    - **completed**: 3 saniyeden fazla izlendiyse true
    - **category**: Reel kategorisi
    """
    try:
        # TrackViewRequest'e çevir
        track_request = TrackViewRequest(
            reel_id=request.reel_id,
            duration_ms=request.duration_ms,
            completed=request.completed,
            category=request.category,
            session_id=request.session_id
        )
        
        # Analytics servisine gönder
        response = await reels_analytics.track_reel_view(user_id, track_request)
        
        if response.success:
            return response
        else:
            raise HTTPException(status_code=400, detail=response.message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Track view error: {str(e)}")

@router.get("/user/{user_id}/watched")
async def get_user_watched_reels(
    user_id: str,
    limit: int = Query(50, ge=1, le=200, description="Kaç reel döndürülecek"),
    category: Optional[str] = Query(None, description="Kategori filtresi")
):
    """
    Kullanıcının izlediği reels listesi
    
    - **user_id**: Kullanıcı ID'si
    - **limit**: Döndürülecek reel sayısı
    - **category**: Kategori filtresi (opsiyonel)
    """
    try:
        watched_reels = await reels_analytics.get_user_watched_reels(user_id, limit)
        
        # Category filter
        if category:
            watched_reels = [reel for reel in watched_reels if reel.get("category") == category]
        
        # Duration'ları saniyeye çevir
        for reel in watched_reels:
            reel["duration_seconds"] = reel["duration_ms"] / 1000.0
            reel["meaningful_view"] = reel["duration_ms"] >= 3000
        
        return {
            "success": True,
            "user_id": user_id,
            "watched_reels": watched_reels,
            "total_count": len(watched_reels),
            "filter_applied": category
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get watched reels error: {str(e)}")

@router.get("/user/{user_id}/daily-progress", response_model=UserProgressResponse)
async def get_user_daily_progress(
    user_id: str,
    target_date: Optional[str] = Query(None, description="Hedef tarih (YYYY-MM-DD), default bugün")
):
    """
    Kullanıcının günlük progress bilgisi
    
    **O gün yayınlanan haberlerin %kaçını izlediği**
    
    - **user_id**: Kullanıcı ID'si
    - **target_date**: Hedef tarih, default bugün
    """
    try:
        # Date parsing
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            parsed_date = date.today()
        
        # Progress al
        progress = await reels_analytics.get_user_daily_progress(user_id, parsed_date)
        
        # Category breakdown oluştur
        category_breakdown = {}
        for category, data in progress.category_progress.items():
            published = data.get("published", 0)
            watched = data.get("watched", 0)
            percentage = (watched / published * 100) if published > 0 else 0.0
            
            category_breakdown[category] = {
                "published": published,
                "watched": watched,
                "percentage": round(percentage, 1)
            }
        
        return UserProgressResponse(
            date=parsed_date.isoformat(),
            progress_percentage=round(progress.progress_percentage, 1),
            total_published_today=progress.total_published_today,
            watched_today=progress.watched_today,
            category_breakdown=category_breakdown
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily progress error: {str(e)}")

@router.get("/user/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: str):
    """
    Kullanıcının genel reel istatistikleri
    
    - **user_id**: Kullanıcı ID'si
    
    **Dönen bilgiler:**
    - Toplam izlenen reel sayısı
    - Toplam ekran süresi  
    - Tamamlama oranı
    - Favori kategoriler
    - Son aktivite zamanı
    """
    try:
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        return UserStatsResponse(
            user_id=user_id,
            total_reels_watched=user_stats.total_reels_watched,
            total_screen_time_ms=user_stats.total_screen_time_ms,
            total_screen_time_hours=round(user_stats.get_total_screen_time_hours(), 2),
            completion_rate=round(user_stats.completion_rate * 100, 1),  # Yüzde olarak
            favorite_categories=user_stats.favorite_categories,
            last_activity=user_stats.last_reel_viewed_at.isoformat() if user_stats.last_reel_viewed_at else None,
            current_streak_days=user_stats.current_streak_days,
            avg_daily_reels=round(user_stats.avg_daily_reels, 1)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User stats error: {str(e)}")

# ============ FEED & DISCOVERY ENDPOINTS ============

@router.get("/feed", response_model=FeedResponse)
async def get_user_feed(
    limit: int = Query(20, ge=1, le=50, description="Feed'de kaç reel gösterilecek"),
    user_id: str = Depends(get_user_id_from_header),
    include_watched: bool = Query(True, description="İzlenmiş reels dahil edilsin mi")
):
    """
    Kullanıcı için kişiselleştirilmiş reel feed'i
    
    **Trending + Recent karışımı, izlenmiş flagları ile**
    
    - **limit**: Feed boyutu
    - **include_watched**: İzlenmiş reels dahil et (ama flag ile işaretle)
    """
    try:
        # Feed'i oluştur
        feed_items = await reels_analytics.generate_user_feed(user_id, limit)
        
        # İzlenmiş reels'i filtrele (eğer istenmiyorsa)
        if not include_watched:
            feed_items = [item for item in feed_items if not item.is_watched]
        
        # İstatistikler
        trending_count = sum(1 for item in feed_items if item.is_trending)
        recent_count = len(feed_items) - trending_count
        watched_count = sum(1 for item in feed_items if item.is_watched)
        
        return FeedResponse(
            reels=feed_items,
            total_count=len(feed_items),
            trending_count=trending_count,
            recent_count=recent_count,
            user_watched_count=watched_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feed generation error: {str(e)}")

@router.get("/trending")
async def get_trending_reels(
    period: TrendPeriod = Query(TrendPeriod.DAILY, description="Trend periyodu"),
    limit: int = Query(20, ge=1, le=50, description="Trending reel sayısı"),
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Ekran süresine göre trend olan reels
    
    - **period**: Trend hesaplama periyodu (hourly, daily, weekly)
    - **limit**: Kaç trend reel döndürülecek
    """
    try:
        trending_reels = await reels_analytics.get_trending_reels(period, limit)
        
        # Kullanıcının izlediği reels'i işaretle
        watched_reel_ids = await reels_analytics._get_user_watched_reel_ids(user_id)
        for reel in trending_reels:
            reel.is_watched = reel.reel_id in watched_reel_ids
        
        return {
            "success": True,
            "trending_reels": trending_reels,
            "period": period,
            "total_count": len(trending_reels),
            "calculated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending reels error: {str(e)}")

@router.get("/latest-published")
async def get_latest_published_reel():
    """
    En son yayınlanan reel
    
    **Sistem genelinde en son yayınlanan haber**
    """
    try:
        latest_reel = await reels_analytics.get_latest_published_reel()
        
        if latest_reel:
            return {
                "success": True,
                "latest_reel": latest_reel,
                "message": "Latest published reel found"
            }
        else:
            return {
                "success": False,
                "message": "No published reels found",
                "latest_reel": None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Latest reel error: {str(e)}")

# ============ ANALYTICS ENDPOINTS ============

@router.get("/analytics/{reel_id}")
async def get_reel_analytics(reel_id: str):
    """
    Belirli bir reel'in analytics bilgileri
    
    - **reel_id**: Reel ID'si
    
    **Admin/moderator için reel performans bilgileri**
    """
    try:
        reel_analytics_data = await reels_analytics.get_reel_analytics(reel_id)
        
        if reel_analytics_data:
            # Engagement score hesapla
            engagement_score = reel_analytics_data.get_engagement_score()
            
            return {
                "success": True,
                "reel_id": reel_id,
                "analytics": reel_analytics_data.dict(),
                "engagement_score": round(engagement_score, 2),
                "performance_level": "high" if engagement_score > 7 else "medium" if engagement_score > 4 else "low"
            }
        else:
            raise HTTPException(status_code=404, detail="Reel analytics not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reel analytics error: {str(e)}")

@router.get("/analytics/overview")
async def get_analytics_overview(
    period_days: int = Query(7, ge=1, le=30, description="Kaç günlük analiz")
):
    """
    Genel sistem analytics özeti
    
    - **period_days**: Analiz periyodu (gün)
    
    **Sistem geneli istatistikler**
    """
    try:
        # Basit overview - geliştirilecek
        trending_reels = await reels_analytics.get_trending_reels(TrendPeriod.DAILY, 10)
        latest_reel = await reels_analytics.get_latest_published_reel()
        
        return {
            "success": True,
            "period_days": period_days,
            "overview": {
                "top_trending_count": len(trending_reels),
                "latest_reel_published": latest_reel.get("published_at") if latest_reel else None,
                "total_categories": len(set(reel.category for reel in trending_reels)),
                "avg_trend_score": round(sum(reel.recommendation_score for reel in trending_reels) / len(trending_reels), 2) if trending_reels else 0
            },
            "top_trending": trending_reels[:5]  # Top 5
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics overview error: {str(e)}")

# ============ UTILITY ENDPOINTS ============

@router.post("/mark-seen")
async def mark_reel_as_seen(
    request: MarkSeenRequest,
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Reel'leri 'görüldü' olarak işaretle
    
    **Kullanıcı scroll yaparken arka planda çağrılabilir**
    
    - **reel_ids**: İşaretlenecek reel ID'leri (request body'de)
    """
    try:
        marked_count = 0
        
        for reel_id in request.reel_ids:
            # Kısa süre (100ms) ile "seen" kaydı oluştur
            track_request = TrackViewRequest(
                reel_id=reel_id,
                duration_ms=100,  # Çok kısa süre
                completed=False,
                category=None
            )
            
            response = await reels_analytics.track_reel_view(user_id, track_request)
            if response.success:
                marked_count += 1
        
        return {
            "success": True,
            "message": f"Marked {marked_count}/{len(request.reel_ids)} reels as seen",
            "marked_count": marked_count,
            "total_requested": len(request.reel_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mark seen error: {str(e)}")

@router.get("/user/{user_id}/session-summary")
async def get_user_session_summary(
    user_id: str,
    session_id: Optional[str] = Query(None, description="Session ID (opsiyonel)")
):
    """
    Kullanıcının session özetini al
    
    - **user_id**: Kullanıcı ID'si
    - **session_id**: Session ID (opsiyonel)
    
    **Kullanıcı uygulamadan çıkarken gösterilebilir**
    """
    try:
        # Bugünkü stats al
        today_progress = await reels_analytics.get_user_daily_progress(user_id)
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        # Session summary
        session_summary = {
            "session_date": date.today().isoformat(),
            "reels_watched_today": today_progress.watched_today,
            "progress_percentage": round(today_progress.progress_percentage, 1),
            "total_screen_time_today_minutes": round((user_stats.total_screen_time_ms / (1000 * 60)), 1),
            "completion_rate": round(user_stats.completion_rate * 100, 1),
            "favorite_category": user_stats.favorite_categories[0] if user_stats.favorite_categories else None,
            "total_reels_all_time": user_stats.total_reels_watched
        }
        
        # Achievements check (basit)
        achievements = []
        if today_progress.progress_percentage >= 50:
            achievements.append("Daily Explorer - %50+ progress")
        if user_stats.completion_rate > 0.8:
            achievements.append("Focused Viewer - %80+ completion")
        
        return {
            "success": True,
            "user_id": user_id,
            "session_summary": session_summary,
            "achievements": achievements,
            "message": "Have a great day! 🎬"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session summary error: {str(e)}")

# ============ ORIGINAL MOCKUP ENDPOINTS (Preserved) ============

@router.get("/mockup/scraped-news")
async def get_scraped_news_mockup(
    count: int = Query(3, ge=1, le=10, description="Number of news items"),
    category: Optional[str] = Query(None, description="Category filter")
):
    """
    **[ORIGINAL MOCKUP ENDPOINT]**
    Web scraping'den gelmiş gibi detaylı haber verisi
    """
    try:
        # Mockup data (basit simülasyon)
        mockup_news = [
            {
                "title": "Sample News 1",
                "summary": "This is a sample news summary",
                "category": category or "guncel",
                "published_date": datetime.now().isoformat()
            }
        ] * count
        
        return {
            "success": True,
            "message": f"Retrieved {count} scraped news items",
            "news_items": mockup_news,
            "total_count": count,
            "scraping_info": {
                "scraping_time": datetime.now().isoformat(),
                "source": "aa.com.tr",
                "quality": "high",
                "errors": 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraped news error: {str(e)}")

@router.get("/mockup/generate-reels")
async def generate_reels_from_scraped_mockup(
    count: int = Query(3, ge=1, le=10, description="Number of reels to generate"),
    voice: str = Query("alloy", description="TTS voice"),
    category: Optional[str] = Query(None, description="Category filter")
):
    """
    **[ORIGINAL MOCKUP ENDPOINT]**
    Scraped news'dan reel generate et (mockup)
    """
    try:
        # Mockup reel generation
        reels = []
        for i in range(count):
            reel = {
                "id": f"mockup_reel_{i}",
                "title": f"Mockup Reel {i+1}",
                "category": category or "guncel",
                "voice_used": voice,
                "duration_seconds": 30 + i * 10,
                "estimated_cost": 0.001 * (i + 1)
            }
            reels.append(reel)
        
        total_cost = sum(reel["estimated_cost"] for reel in reels)
        total_duration = sum(reel["duration_seconds"] for reel in reels)
        
        return {
            "success": True,
            "message": f"Generated {len(reels)} reels from scraped news",
            "reels": reels,
            "summary": {
                "total_reels": len(reels),
                "total_characters": count * 500,  # Estimated
                "total_estimated_cost": round(total_cost, 6),
                "total_duration_seconds": total_duration,
                "average_duration": round(total_duration / len(reels), 1),
                "voice_used": voice
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reel generation error: {str(e)}")

# ============ API DOCUMENTATION HELPER ============

@router.get("/endpoints")
async def list_reel_endpoints():
    """
    Reels API endpoint'lerinin listesi
    
    **Geliştirici referansı için**
    """
    endpoints = {
        "tracking": [
            "POST /api/reels/track-view - Reel izleme kaydı",
            "GET /api/reels/user/{id}/watched - İzlenen reels",
            "POST /api/reels/mark-seen - Reels'i görüldü işaretle"
        ],
        "analytics": [
            "GET /api/reels/user/{id}/daily-progress - Günlük progress",
            "GET /api/reels/user/{id}/stats - Kullanıcı istatistikleri", 
            "GET /api/reels/analytics/{reel_id} - Reel analytics",
            "GET /api/reels/analytics/overview - Sistem overview"
        ],
        "feed": [
            "GET /api/reels/feed - Kişiselleştirilmiş feed",
            "GET /api/reels/trending - Trend reels",
            "GET /api/reels/latest-published - En son reel"
        ],
        "utility": [
            "GET /api/reels/user/{id}/session-summary - Session özeti",
            "GET /api/reels/endpoints - Bu endpoint listesi"
        ],
        "mockup": [
            "GET /api/reels/mockup/scraped-news - Test verisi",
            "GET /api/reels/mockup/generate-reels - Test reel generation"
        ]
    }
    
    return {
        "success": True,
        "message": "Reels API endpoints",
        "total_endpoints": sum(len(group) for group in endpoints.values()),
        "endpoints": endpoints,
        "base_url": "/api/reels",
        "authentication": "X-User-ID header recommended"
    }