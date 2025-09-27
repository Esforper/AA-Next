# ================================
# src/api/content.py - News & Content Endpoints
# ================================

"""
Content API - News, Articles, Search endpoints
"""

from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional, List
from pydantic import BaseModel

from ..services.content import content_service
from ..models.news import NewsResponse, NewsFilter
from ..models.base import BaseResponse

router = APIRouter(prefix="/api/news", tags=["news"])

# Request models
class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    count: int = 20

class FilterRequest(BaseModel):
    category: Optional[str] = None
    author: Optional[str] = None
    min_chars: Optional[int] = None
    max_chars: Optional[int] = None
    keywords: Optional[List[str]] = None

# ============ NEWS ENDPOINTS ============

@router.get("/latest", response_model=NewsResponse)
async def get_latest_news(
    count: int = Query(10, ge=1, le=50, description="Number of articles to fetch"),
    category: Optional[str] = Query(None, description="News category"),
    enable_scraping: Optional[bool] = Query(None, description="Enable web scraping for full content")
):
    """
    Son haberleri al
    
    - **count**: Haber sayısı (1-50)
    - **category**: Kategori (guncel, ekonomi, spor vb)
    - **enable_scraping**: Web scraping aktif et/kapat
    """
    try:
        result = await content_service.get_latest_news(
            count=count,
            category=category,
            enable_scraping=enable_scraping
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """Mevcut kategorileri listele"""
    categories = {
        "guncel": "Güncel Haberler",
        "ekonomi": "Ekonomi",
        "spor": "Spor", 
        "teknoloji": "Teknoloji",
        "kultur": "Kültür",
        "dunya": "Dünya",
        "politika": "Politika",
        "saglik": "Sağlık",
        "egitim": "Eğitim"
        # Yeni kategori eklemek için buraya ekle
    }
    
    return {
        "success": True,
        "categories": list(categories.keys()),
        "descriptions": categories
    }

@router.get("/category/{category}")
async def get_news_by_category(
    category: str = Path(..., description="News category"),
    count: int = Query(10, ge=1, le=50)
):
    """Kategoriye göre haber al"""
    result = await content_service.get_latest_news(
        count=count,
        category=category
    )
    
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    
    return result

@router.post("/search")
async def search_news(request: SearchRequest):
    """
    Haber ara
    
    Body:
    - **query**: Arama terimi
    - **category**: Kategori filtresi (opsiyonel)
    - **count**: Sonuç sayısı
    """
    result = await content_service.search_news(
        query=request.query,
        category=request.category,
        count=request.count
    )
    return result

@router.get("/search")
async def search_news_get(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    count: int = Query(20, ge=1, le=100, description="Number of results")
):
    """Haber ara (GET version)"""
    result = await content_service.search_news(
        query=q,
        category=category,
        count=count
    )
    return result

@router.get("/article")
async def get_article_by_url(
    url: str = Query(..., description="Article URL"),
    enable_scraping: bool = Query(True, description="Enable web scraping")
):
    """URL'den makale al"""
    article = await content_service.get_article_by_url(
        url=url,
        enable_scraping=enable_scraping
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or could not be scraped")
    
    return {
        "success": True,
        "article": article
    }

@router.get("/trending")
async def get_trending_topics(
    count: int = Query(10, ge=1, le=50, description="Number of trending topics")
):
    """Trend olan konuları al"""
    topics = await content_service.get_trending_topics(count=count)
    
    return {
        "success": True,
        "trending_topics": topics,
        "count": len(topics)
    }

# ============ AGENDA ENDPOINTS (Özel) ============

@router.get("/agenda/ready")
async def get_ready_agenda(
    limit: int = Query(15, ge=1, le=50, description="Number of agenda items")
):
    """
    Hazır gündem haberlerini al (TTS dahil)
    Mevcut agenda_cache dosyalarından okur
    """
    try:
        from pathlib import Path
        import json
        from datetime import datetime, timedelta
        
        # Agenda cache dizini
        agenda_dir = Path("agenda_cache")
        if not agenda_dir.exists():
            return {
                "success": False,
                "error": "no_agenda_cache",
                "message": "Agenda cache bulunamadı",
                "reels": []
            }
        
        # Son 24 saat içindeki dosyaları bul
        cutoff_time = datetime.now() - timedelta(hours=24)
        agenda_files = []
        
        for file_path in agenda_dir.glob("agenda_data_*.json"):
            try:
                # Dosya adından tarihi çıkar
                date_str = file_path.stem.split('_')[-2] + '_' + file_path.stem.split('_')[-1]
                file_time = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if file_time > cutoff_time:
                    agenda_files.append((file_time, file_path))
            except:
                continue
        
        if not agenda_files:
            return {
                "success": False,
                "error": "no_recent_agenda",
                "message": "Son 24 saatte oluşturulan gündem bulunamadı",
                "reels": []
            }
        
        # En yeni dosyayı al
        latest_file = max(agenda_files, key=lambda x: x[0])[1]
        
        # JSON'u oku
        with open(latest_file, 'r', encoding='utf-8') as f:
            agenda_data = json.load(f)
        
        agenda_items = agenda_data.get('agenda_items', [])[:limit]
        
        return {
            "success": True,
            "message": f"{len(agenda_items)} gündem haberi hazır",
            "reels": agenda_items,
            "total_available": len(agenda_data.get('agenda_items', [])),
            "last_updated": agenda_data.get('timestamp'),
            "processing_info": {
                "total_cost": agenda_data.get('total_cost'),
                "processing_time": agenda_data.get('processing_time')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agenda read error: {str(e)}")