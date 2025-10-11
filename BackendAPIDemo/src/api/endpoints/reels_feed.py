# backend/src/api/endpoints/reels_feed.py

"""
Reels Feed Endpoints - JWT Auth entegrasyonu ile
Feed, trending, latest endpoint'leri
"""

from fastapi import APIRouter, Query, HTTPException, Depends, Header
from typing import Optional

from ...services.feed_generator import feed_generator
from ...services.reels_analytics import reels_analytics
from ...models.reels_tracking import FeedResponse, TrendPeriod
from ...services.auth_service import auth_service
router = APIRouter(prefix="/api/reels", tags=["reels-feed"])


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


# ============ FEED ENDPOINTS ============

@router.get("/feed", response_model=FeedResponse)
async def get_personalized_feed(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50, description="Kaç reel döndürülecek"),
    cursor: Optional[str] = Query(None, description="Pagination için cursor (reel_id)")
):
    """
    Instagram-style personalized feed (JWT Auth)
    
    **Ana feed endpoint - kullanıcıya özel reel listesi döndürür**
    
    Algoritma:
    - %30 Trending (son 24 saatte popüler)
    - %50 Personalized (kullanıcı tercihlerine göre)
    - %20 Fresh/Exploration (yeni keşif)
    
    Cursor-based pagination ile infinite scroll desteği
    """
    try:
        feed_response = await feed_generator.generate_feed(
            user_id=user_id,
            limit=limit,
            cursor=cursor
        )
        
        return feed_response
        
    except Exception as e:
        print(f"❌ Feed generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Feed generation failed: {str(e)}")

@router.get("/trending")
async def get_trending_reels(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(10, ge=1, le=50, description="Kaç reel döndürülecek"),
    period: TrendPeriod = Query(TrendPeriod.DAILY, description="Trend periyodu")
):
    """
    Trend reels listesi (JWT Auth)
    
    **En çok izlenen/engagement alan reels**
    
    - HOURLY: Son 1 saatin trendleri
    - DAILY: Bugünün trendleri
    - WEEKLY: Bu haftanın trendleri
    """
    try:
        trending_reels = await reels_analytics.get_trending_reels(
            limit=limit,
            period=period
        )
        
        # Kullanıcının izlediklerini işaretle
        watched_ids = await reels_analytics._get_user_watched_reel_ids(user_id)
        for reel in trending_reels:
            reel.is_watched = reel.id in watched_ids
        
        return {
            "success": True,
            "reels": trending_reels,
            "total_count": len(trending_reels),
            "period": period.value
        }
        
    except Exception as e:
        print(f"❌ Get trending reels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    


@router.get("/latest-published")
async def get_latest_published_reel(
    user_id: str = Depends(get_current_user_id)
):
    """
    En son yayınlanan reel (JWT Auth)
    
    **Debug ve monitoring için kullanışlı**
    """
    try:
        latest_reel = await reels_analytics.get_latest_published_reel()
        
        if not latest_reel:
            return {
                "success": False,
                "message": "No published reels found"
            }
        
        # Kullanıcının izleyip izlemediğini kontrol et
        watched_ids = await reels_analytics._get_user_watched_reel_ids(user_id)
        latest_reel.is_watched = latest_reel.id in watched_ids
        
        return {
            "success": True,
            "reel": latest_reel,
            "message": "Latest reel found"
        }
        
    except Exception as e:
        print(f"❌ Get latest reel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
# backend/src/api/endpoints/reels_feed.py
# 🎯 CATEGORY FEED ENDPOINT - Dosyanın SONUNA EKLE (router tanımından sonra)

@router.get("/category/{category_id}")
async def get_reels_by_category(
    category_id: str,
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50, description="Sayfa başına reel"),
    cursor: Optional[str] = Query(None, description="Pagination cursor")
):
    """
    🎯 Kategoriye özel reels feed (JWT Auth)
    
    **Instagram-style category feed**
    
    Args:
        - category_id: Kategori slug (guncel, ekonomi, spor, etc)
        - limit: Sayfa başına reel sayısı
        - cursor: Pagination için son reel_id
    
    Returns:
        - Kategoriye ait reels
        - Pagination bilgisi
        - Kategori metadata
    """
    try:
        from ...services.category_feed_service import category_feed_service
        
        print(f"📥 Category feed: {category_id} (user: {user_id})")
        
        result = await category_feed_service.get_category_feed(
            user_id=user_id,
            category=category_id,
            limit=limit,
            cursor=cursor
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=result.get('message', 'Category not found')
            )
        
        print(f"✅ Returning {len(result['reels'])} reels")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Category feed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))