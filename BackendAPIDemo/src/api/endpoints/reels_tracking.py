# backend/src/api/endpoints/reels_tracking.py

"""
Reels Tracking Endpoints - JWT Auth entegrasyonu ile
Track view ve track detail view endpoint'leri
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime

from ...services.reels_analytics import reels_analytics
from ...services.user_preference import preference_engine
from ...models.reels_tracking import (
    TrackViewRequest,
    TrackViewResponse,
    TrackDetailViewRequest,
    DetailViewEvent,
    ReelView,
    ViewStatus
)

router = APIRouter(prefix="/api/reels", tags=["reels-tracking"])


# ============ AUTH HELPER ============

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """JWT token'dan user ID çıkar"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.split(" ")[1]
    
    try:
        from ...auth import verify_token
        payload = verify_token(token)
        return payload.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ============ TRACKING ENDPOINTS ============

@router.post("/track-view", response_model=TrackViewResponse)
async def track_view(
    request: TrackViewRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Reel izleme kaydı oluştur (JWT Auth)
    
    **Frontend her reel izlendiğinde çağırır**
    
    - Emoji reaction tracking
    - Pause count, replay, share, save tracking
    - Engagement score hesaplama
    - User preference güncelleme
    """
    try:
        # Reel kontrolü
        reel = await reels_analytics.get_reel_by_id(request.reel_id)
        if not reel:
            raise HTTPException(status_code=404, detail=f"Reel not found: {request.reel_id}")
        
        # ReelView oluştur
        view = ReelView(
            user_id=user_id,
            reel_id=request.reel_id,
            duration_ms=request.duration_ms,
            status=ViewStatus.COMPLETED if request.completed else ViewStatus.PARTIAL,
            category=request.category or reel.news_data.category,
            session_id=request.session_id,
            
            # Emoji reaction
            emoji_reaction=request.emoji_reaction,
            emoji_timestamp=datetime.now() if request.emoji_reaction else None,
            
            # Extra signals
            paused_count=request.paused_count or 0,
            replayed=request.replayed or False,
            shared=request.shared or False,
            saved=request.saved or False,
        )
        
        # Analytics'e kaydet
        response = await reels_analytics.track_reel_view(user_id, request)
        
        # User stats al
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        return TrackViewResponse(
            success=True,
            message="View tracked successfully",
            view_id=response.view_id,
            meaningful_view=view.is_meaningful_view(),
            engagement_score=view.get_engagement_score(),
            personalization_level=user_stats.get_personalization_level(),
            total_interactions=user_stats.total_reels_watched,
            daily_progress_updated=response.daily_progress_updated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Track view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track-detail-view")
async def track_detail_view(
    request: TrackDetailViewRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Haber detayı okuma tracking (JWT Auth)
    
    **Kullanıcı "Detayları Oku" butonuna tıklayıp tam haberi okuduğunda çağrılır**
    
    Bu çok güçlü bir sinyal! Detay okuma = merak + ilgi
    
    - Read duration tracking
    - Scroll depth tracking
    - Share/save from detail tracking
    - Preference engine boost
    """
    try:
        # Reel kontrolü
        reel = await reels_analytics.get_reel_by_id(request.reel_id)
        if not reel:
            raise HTTPException(status_code=404, detail=f"Reel not found: {request.reel_id}")
        
        # DetailViewEvent oluştur
        detail_event = DetailViewEvent(
            user_id=user_id,
            reel_id=request.reel_id,
            read_duration_ms=request.read_duration_ms,
            scroll_depth=request.scroll_depth,
            shared_from_detail=request.shared_from_detail,
            saved_from_detail=request.saved_from_detail,
            session_id=request.session_id
        )
        
        # Analytics'e kaydet
        await reels_analytics.track_detail_view(user_id, detail_event)
        
        # Preference engine'e EKSTRA boost ver
        engagement_score = detail_event.get_detail_engagement_score()
        await preference_engine.boost_from_detail_view(
            user_id=user_id,
            reel=reel,
            engagement_score=engagement_score
        )
        
        return {
            "success": True,
            "message": "Detail view tracked successfully",
            "meaningful_read": detail_event.is_meaningful_read(),
            "engagement_score": engagement_score,
            "boost_applied": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Track detail view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))