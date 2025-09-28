# ================================
# src/api/endpoints/news.py - News API Endpoints
# ================================

"""
News ve Content API endpoint'leri
Temiz, basit ve genişletilebilir yapı
"""

from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

from ...services.content import content_service
from ...models.news import NewsResponse, Article
from ...models.base import BaseResponse

# Router oluştur
router = APIRouter(prefix="/api/news", tags=["news"])

# ============ REQUEST MODELS ============

class SearchRequest(BaseModel):
    """News search request"""
    query: str
    category: Optional[str] = None
    count: int = 20

class FilterRequest(BaseModel):
    """News filter request"""
    category: Optional[str] = None
    author: Optional[str] = None
    min_chars: Optional[int] = None
    max_chars: Optional[int] = None
    keywords: Optional[List[str]] = None

class ArticleRequest(BaseModel):
    """Single article request"""
    url: HttpUrl
    enable_scraping: bool = True

# ============ BASIC NEWS ENDPOINTS ============

@router.get("/latest", response_model=NewsResponse)
async def get_latest_news(
    count: int = Query(10, ge=1, le=50, description="Number of articles to fetch"),
    category: Optional[str] = Query(None, description="News category (guncel, ekonomi, spor, vb.)"),
    enable_scraping: Optional[bool] = Query(None, description="Enable web scraping for full content")
):
    """
    Son haberleri al
    
    - **count**: Haber sayısı (1-50 arası)
    - **category**: Kategori filtresi (opsiyonel)
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
        raise HTTPException(status_code=500, detail=f"News fetch error: {str(e)}")

@router.get("/categories")
async def get_news_categories():
    """
    Mevcut haber kategorilerini listele
    """
    categories = {
        "guncel": "Güncel Haberler",
        "ekonomi": "Ekonomi",
        "spor": "Spor",
        "teknoloji": "Teknoloji",
        "kultur": "Kültür",
        "dunya": "Dünya",
        "politika": "Politika",
        "saglik": "Sağlık",
        "egitim": "Eğitim",
        "cevre": "Çevre"
    }
    
    return {
        "success": True,
        "categories": list(categories.keys()),
        "descriptions": categories,
        "total_count": len(categories)
    }

@router.get("/category/{category}")
async def get_news_by_category(
    category: str = Path(..., description="News category"),
    count: int = Query(10, ge=1, le=50, description="Number of articles")
):
    """
    Belirli kategoriden haber al
    
    - **category**: Kategori adı (categories endpoint'inden al)
    - **count**: Haber sayısı
    """
    try:
        result = await content_service.get_latest_news(
            count=count,
            category=category
        )
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category news error: {str(e)}")

# ============ SEARCH ENDPOINTS ============

@router.post("/search")
async def search_news_post(request: SearchRequest):
    """
    Haber ara (POST method)
    
    Request body:
    - **query**: Arama terimi
    - **category**: Kategori filtresi (opsiyonel)
    - **count**: Sonuç sayısı
    """
    try:
        result = await content_service.search_news(
            query=request.query,
            category=request.category,
            count=request.count
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/search")
async def search_news_get(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    count: int = Query(20, ge=1, le=100, description="Number of results")
):
    """
    Haber ara (GET method)
    
    - **q**: Arama terimi
    - **category**: Kategori filtresi
    - **count**: Sonuç sayısı
    """
    try:
        result = await content_service.search_news(
            query=q,
            category=category,
            count=count
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# ============ SINGLE ARTICLE ENDPOINTS ============

@router.get("/article")
async def get_article_by_url(
    url: str = Query(..., description="Article URL"),
    enable_scraping: bool = Query(True, description="Enable web scraping")
):
    """
    URL'den tek makale al
    
    - **url**: Makale URL'i
    - **enable_scraping**: Web scraping aktif et
    """
    try:
        article = await content_service.get_article_by_url(
            url=url,
            enable_scraping=enable_scraping
        )
        
        if not article:
            raise HTTPException(
                status_code=404, 
                detail="Article not found or could not be scraped"
            )
        
        return {
            "success": True,
            "message": "Article retrieved successfully",
            "article": article
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Article fetch error: {str(e)}")

@router.post("/article")
async def get_article_by_url_post(request: ArticleRequest):
    """
    URL'den tek makale al (POST method)
    """
    try:
        article = await content_service.get_article_by_url(
            url=str(request.url),
            enable_scraping=request.enable_scraping
        )
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found or could not be scraped"
            )
        
        return {
            "success": True,
            "message": "Article retrieved successfully", 
            "article": article
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Article fetch error: {str(e)}")

# ============ TRENDING & ANALYTICS ============

@router.get("/trending")
async def get_trending_topics(
    count: int = Query(10, ge=1, le=50, description="Number of trending topics")
):
    """
    Trend olan konuları al
    
    - **count**: Trend konu sayısı
    """
    try:
        topics = await content_service.get_trending_topics(count=count)
        
        return {
            "success": True,
            "message": f"Retrieved {len(topics)} trending topics",
            "trending_topics": topics,
            "count": len(topics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending topics error: {str(e)}")

# ============ SPECIAL ENDPOINTS ============

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
        
        # Agenda cache dizini kontrol et
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
                parts = file_path.stem.split('_')
                if len(parts) >= 4:
                    date_str = f"{parts[-2]}_{parts[-1]}"
                    file_time = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                    
                    if file_time > cutoff_time:
                        agenda_files.append((file_time, file_path))
            except (ValueError, IndexError):
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

# ============ UTILITY ENDPOINTS ============
from datetime import datetime
@router.get("/stats")
async def get_news_stats():
    """
    News sistemi istatistikleri
    """
    try:
        # Basit istatistikler - geliştirilecek
        return {
            "success": True,
            "stats": {
                "provider": "aa",
                "available_categories": 10,
                "last_update": datetime.now().isoformat(),
                "status": "active"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")