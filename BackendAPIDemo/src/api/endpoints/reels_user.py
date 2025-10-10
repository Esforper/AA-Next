# backend/src/api/endpoints/reels_user.py

"""
Reels User Endpoints - JWT Auth entegrasyonu ile
Kullanıcı özel endpoint'leri (stats, progress, watched, session)
"""

from fastapi import APIRouter, Query, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime, date

from ...services.reels_analytics import reels_analytics
from ...models.reels_tracking import UserProgressResponse, UserStatsResponse
from ...services.auth_service import auth_service
router = APIRouter(prefix="/api/reels", tags=["reels-user"])


# ============ AUTH HELPER ============

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """JWT token'dan user ID çıkar"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    
    try:
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ============ USER ENDPOINTS ============

@router.get("/user/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcı istatistikleri (JWT Auth)
    
    **Kullanıcının genel istatistikleri**
    
    - Toplam izlenen reel sayısı
    - Toplam ekran süresi
    - Completion rate (tamamlama oranı)
    - Favori kategoriler
    - Streak bilgisi
    """
    try:
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        return UserStatsResponse(
            success=True,
            user_id=user_id,
            total_reels_watched=user_stats.total_reels_watched,
            total_screen_time_ms=user_stats.total_screen_time_ms,
            total_screen_time_hours=user_stats.total_screen_time_ms / 3_600_000,
            completion_rate=user_stats.completion_rate,
            favorite_categories=user_stats.favorite_categories,
            last_activity=user_stats.last_activity.isoformat() if user_stats.last_activity else None,
            current_streak_days=user_stats.current_streak_days,
            avg_daily_reels=user_stats.avg_daily_reels
        )
        
    except Exception as e:
        print(f"❌ Get user stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/daily-progress", response_model=UserProgressResponse)
async def get_user_daily_progress(
    user_id: str = Depends(get_current_user_id),
    target_date: Optional[str] = Query(None, description="Hedef tarih (YYYY-MM-DD), default bugün")
):
    """
    Kullanıcının günlük progress bilgisi (JWT Auth)
    
    **O gün yayınlanan haberlerin %kaçını izlediği**
    
    - Progress percentage
    - Kategori bazında breakdown
    - Bugün izlenen vs yayınlanan
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
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get daily progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/watched")
async def get_user_watched_reels(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=200, description="Kaç reel döndürülecek"),
    category: Optional[str] = Query(None, description="Kategori filtresi")
):
    """
    Kullanıcının izlediği reels listesi (JWT Auth)
    
    **İzleme geçmişi**
    
    - Son izlenen reels
    - Kategori filtresi ile
    """
    try:
        watched_reels = await reels_analytics.get_user_watched_reels(user_id, limit)
        
        # Category filter
        if category:
            watched_reels = [reel for reel in watched_reels if reel.get("category") == category]
        
        return {
            "success": True,
            "user_id": user_id,
            "watched_reels": watched_reels,
            "total_count": len(watched_reels),
            "filter_applied": category
        }
        
    except Exception as e:
        print(f"❌ Get watched reels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/session-summary")
async def get_user_session_summary(
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcı session özeti (JWT Auth)
    
    **Günlük özet ve achievement'lar**
    
    - Bugün izlenen reel sayısı
    - Progress yüzdesi
    - Toplam ekran süresi
    - Completion rate
    - Favori kategori
    - Achievement'lar
    """
    try:
        # Bugünkü progress
        progress = await reels_analytics.get_user_daily_progress(user_id, date.today())
        
        # User stats
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        # Achievement kontrolü (basit - daha sonra genişletilebilir)
        achievements = []
        
        if user_stats.total_reels_watched >= 10:
            achievements.append("🎯 İlk 10 haber")
        
        if user_stats.current_streak_days >= 3:
            achievements.append(f"🔥 {user_stats.current_streak_days} gün streak")
        
        if progress.progress_percentage >= 50:
            achievements.append("⭐ Bugün %50+")
        
        return {
            "success": True,
            "user_id": user_id,
            "session_summary": {
                "session_date": date.today().isoformat(),
                "reels_watched_today": progress.watched_today,
                "progress_percentage": progress.progress_percentage,
                "total_screen_time_today_minutes": user_stats.total_screen_time_ms / 60_000,
                "completion_rate": user_stats.completion_rate,
                "favorite_category": user_stats.favorite_categories[0] if user_stats.favorite_categories else None,
                "total_reels_all_time": user_stats.total_reels_watched
            },
            "achievements": achievements,
            "message": "Welcome back! 🎬"
        }
        
    except Exception as e:
        print(f"⚠️ Session summary error for {user_id}: {e}")
        return {
            "success": True,
            "user_id": user_id,
            "session_summary": {
                "session_date": date.today().isoformat(),
                "reels_watched_today": 0,
                "progress_percentage": 0.0,
                "total_screen_time_today_minutes": 0.0,
                "completion_rate": 0.0,
                "favorite_category": None,
                "total_reels_all_time": 0
            },
            "achievements": [],
            "message": "Welcome back! 🎬"
        }