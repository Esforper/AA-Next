# backend/src/api/endpoints/reels_management.py

"""
Reels Management Endpoints
Admin/management endpoint'leri (bulk-create, mark-seen, get-by-id)
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from pydantic import BaseModel, Field

from ...services.reels_analytics import reels_analytics
from ...services.content import content_service
from ...services.processing import processing_service
from ...models.reels_tracking import TrackViewRequest
from ...services.auth_service import auth_service
router = APIRouter(prefix="/api/reels", tags=["reels-management"])


# ============ REQUEST MODELS ============

class MarkSeenRequest(BaseModel):
    """Mark reels as seen request"""
    reel_ids: List[str] = Field(..., description="Görüldü olarak işaretlenecek reel ID'leri")


class BulkReelCreationRequest(BaseModel):
    """Toplu reel oluşturma request'i"""
    category: str = Field(default="guncel", description="Haber kategorisi")
    count: int = Field(default=10, ge=1, le=50, description="Oluşturulacak reel sayısı")
    voice: str = Field(default="alloy", description="TTS ses modeli")
    min_chars: int = Field(default=300, description="Minimum karakter sayısı")
    enable_scraping: bool = Field(default=True, description="Web scraping aktif et")


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


# ============ MANAGEMENT ENDPOINTS ============

@router.get("/{reel_id}")
async def get_reel_by_id(
    reel_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Belirli bir reel'in detaylarını al (JWT Auth)
    
    **Reel detay bilgileri**
    """
    try:
        reel = await reels_analytics.get_reel_by_id(reel_id)
        
        if not reel:
            raise HTTPException(status_code=404, detail="Reel not found")
        
        # Kullanıcının bu reel'i izleyip izlemediğini kontrol et
        watched_reel_ids = await reels_analytics._get_user_watched_reel_ids(user_id)
        reel.is_watched = reel_id in watched_reel_ids
        
        return {
            "success": True,
            "reel": reel,
            "message": "Reel found successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get reel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-seen")
async def mark_reel_as_seen(
    request: MarkSeenRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Reel'leri 'görüldü' olarak işaretle (JWT Auth)
    
    **Kullanıcı scroll yaparken arka planda çağrılabilir**
    """
    try:
        marked_count = 0
        
        for reel_id in request.reel_ids:
            # Kısa süre (100ms) ile "seen" kaydı oluştur
            track_request = TrackViewRequest(
                reel_id=reel_id,
                duration_ms=100,
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
        print(f"❌ Mark seen error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-create")
async def bulk_create_reels(request: BulkReelCreationRequest):
    """
    Toplu reel oluşturma (RSS → TTS → Reel)
    
    **Admin endpoint - toplu reel üretimi**
    
    Pipeline:
    1. RSS'den haberler al
    2. Filtreleme (min_chars)
    3. TTS dönüşümü
    4. Reel oluştur
    5. NLP corpus'a ekle
    """
    try:
        # Processing service ile reel oluştur
        result = await processing_service.create_reels_from_latest_news(
            category=request.category,
            count=request.count,
            voice=request.voice,
            min_chars=request.min_chars,
            enable_scraping=request.enable_scraping
        )
        
        return {
            "success": True,
            "message": f"Bulk reel creation completed",
            "summary": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bulk creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/endpoints")
async def list_reel_endpoints():
    """
    Reels API endpoint'lerinin listesi
    
    **Geliştirici referansı için**
    """
    endpoints = {
        "core_feed": [
            "GET /api/reels/feed - Instagram-style ana feed (cursor pagination)",
            "GET /api/reels/trending - Trend reels",
            "GET /api/reels/latest-published - En son reel"
        ],
        "tracking": [
            "POST /api/reels/track-view - Reel izleme kaydı (JWT Auth)",
            "POST /api/reels/track-detail-view - Detay okuma kaydı (JWT Auth)"
        ],
        "user": [
            "GET /api/reels/user/stats - Kullanıcı istatistikleri (JWT Auth)",
            "GET /api/reels/user/daily-progress - Günlük progress (JWT Auth)",
            "GET /api/reels/user/watched - İzlenen reels (JWT Auth)",
            "GET /api/reels/user/session-summary - Session özeti (JWT Auth)"
        ],
        "analytics": [
            "GET /api/reels/analytics/{reel_id} - Reel analytics",
            "GET /api/reels/analytics/overview - Sistem overview",
            "GET /api/reels/system/status - Sistem durumu"
        ],
        "management": [
            "GET /api/reels/{reel_id} - Reel detayı (JWT Auth)",
            "POST /api/reels/bulk-create - Toplu reel oluştur",
            "POST /api/reels/mark-seen - Reels'i görüldü işaretle (JWT Auth)"
        ]
    }
    
    return {
        "success": True,
        "message": "Reels API endpoints (JWT Auth integrated)",
        "total_endpoints": sum(len(group) for group in endpoints.values()),
        "endpoints": endpoints,
        "base_url": "/api/reels",
        "authentication": "JWT Bearer token required for most endpoints"
    }