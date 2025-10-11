# backend/src/api/endpoints/categories.py
# 🎯 Category API Endpoints

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from ...services.category_feed_service import category_feed_service
from ..utils.auth_utils import get_current_user_id

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("/list")
async def get_categories_list():
    """
    📋 Tüm kategorileri listele
    
    Returns:
        - Kategori listesi (name, icon, color, reel count)
    """
    try:
        result = await category_feed_service.get_all_categories()
        return result
        
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/{category_id}")
async def get_category_feed(
    category_id: str,
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=50, description="Sayfa başına reel sayısı"),
    cursor: Optional[str] = Query(None, description="Pagination cursor (reel_id)")
):
    """
    🎯 Kategoriye özel feed getir
    
    Args:
        - category_id: Kategori slug (guncel, ekonomi, spor, etc)
        - limit: Sayfa başına reel sayısı (default: 20)
        - cursor: Pagination için son reel_id
    
    Returns:
        - Kategoriye ait reels feed
        - Pagination bilgisi
        - Kategori metadata
    """
    try:
        print(f"📥 Category feed request: {category_id} (user: {user_id})")
        
        result = await category_feed_service.get_category_feed(
            user_id=user_id,
            category=category_id,
            limit=limit,
            cursor=cursor
        )
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('message'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting category feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{category_id}")
async def get_category_stats(
    category_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    📊 Kategori istatistikleri
    
    Returns:
        - Toplam reel sayısı
        - Son 24 saatteki yeni reels
        - Kullanıcının bu kategorideki izleme oranı
    """
    try:
        from ...services.reels_analytics import reels_analytics_service
        
        # Kategorideki tüm reels
        all_reels = await reels_analytics_service.get_reels_by_category(category_id)
        
        # Son 24 saatteki reels
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_reels = [r for r in all_reels if r.published_at > yesterday]
        
        return {
            'success': True,
            'category_id': category_id,
            'total_reels': len(all_reels),
            'recent_reels_24h': len(recent_reels),
            'has_content': len(all_reels) > 0
        }
        
    except Exception as e:
        print(f"❌ Error getting category stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))