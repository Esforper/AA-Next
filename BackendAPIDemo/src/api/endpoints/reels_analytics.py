# backend/src/api/endpoints/reels_analytics.py

"""
Reels Analytics Endpoints
Analytics ve raporlama endpoint'leri
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ...services.reels_analytics import reels_analytics

router = APIRouter(prefix="/api/reels", tags=["reels-analytics"])


# ============ ANALYTICS ENDPOINTS ============

@router.get("/analytics/{reel_id}")
async def get_reel_analytics(reel_id: str):
    """
    Belirli bir reel'in analytics bilgileri
    
    **Admin/moderator için reel performans bilgileri**
    
    - View count
    - Completion rate
    - Average watch duration
    - Engagement metrics
    """
    try:
        # Detaylı performans raporu al
        performance_report = await reels_analytics.get_reel_performance_report(reel_id)
        
        if "error" in performance_report:
            raise HTTPException(status_code=404, detail=performance_report["error"])
        
        return {
            "success": True,
            "reel_id": reel_id,
            "performance_report": performance_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Reel analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/overview")
async def get_analytics_overview(
    period_days: int = Query(7, ge=1, le=30, description="Kaç günlük analiz")
):
    """
    Genel sistem analytics özeti
    
    **Sistem geneli istatistikler**
    
    - Total views
    - Total reels
    - Active users
    - Category breakdown
    - Hourly breakdown
    """
    try:
        overview = await reels_analytics.get_analytics_overview(period_days)
        
        return {
            "success": True,
            "analytics_overview": overview
        }
        
    except Exception as e:
        print(f"❌ Analytics overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status")
async def get_reel_system_status():
    """
    Reel sisteminin durumu
    
    **Sistem sağlık kontrolü ve istatistikleri**
    
    - System health
    - Total published reels
    - Today's stats
    - Active users
    - Last published reel
    """
    try:
        from datetime import datetime
        
        # Sistem istatistikleri al
        all_reels = await reels_analytics.get_all_published_reels()
        overview = await reels_analytics.get_analytics_overview(1)  # Son 24 saat
        
        status = {
            "system_health": "healthy",
            "total_published_reels": len(all_reels),
            "reels_today": overview.get("overview", {}).get("recent_reels", 0),
            "total_views_today": overview.get("overview", {}).get("total_views", 0),
            "active_users": overview.get("user_stats", {}).get("active_users", 0),
            "last_reel_published": None
        }
        
        # Son reel bilgisi
        latest_reel = await reels_analytics.get_latest_published_reel()
        if latest_reel:
            status["last_reel_published"] = latest_reel.published_at.isoformat()
        
        return {
            "success": True,
            "system_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))