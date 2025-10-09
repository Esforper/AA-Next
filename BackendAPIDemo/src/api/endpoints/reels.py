# ================================
# src/api/endpoints/reels.py - Updated Reels API Endpoints
# ================================

"""
Reels API endpoint'leri - Yeni ReelsAnalyticsService ve ReelFeedItem modelleriyle güncellenmiş
Instagram-style pagination ve feed sistemi ile
"""
from ...services.feed_generator import feed_generator
from ...services.user_preference import preference_engine
from ...services.incremental_nlp import incremental_nlp
from ...models.reels_tracking import (
    TrackDetailViewRequest,
    DetailViewEvent,
    EmojiType
)
from fastapi import APIRouter, Query, HTTPException, Depends, Header
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime, date
import hashlib

# Analytics service - Updated
from ...services.reels_analytics import reels_analytics
from ...models.reels_tracking import (
    TrackViewRequest, TrackViewResponse, UserReelStats, 
    DailyProgress, ReelFeedItem, TrendPeriod, ViewStatus,
    FeedResponse, FeedPagination, FeedMetadata, ReelStatus
)

# Original imports (still needed)
from ...services.content import content_service
from ...services.processing import processing_service
from ...models.news import NewsResponse, Article
from ...models.base import BaseResponse

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

class BulkReelCreationRequest(BaseModel):
    """Toplu reel oluşturma request'i"""
    category: str = Field(default="guncel", description="Haber kategorisi")
    count: int = Field(default=10, ge=1, le=50, description="Oluşturulacak reel sayısı")
    voice: str = Field(default="alloy", description="TTS ses modeli")
    min_chars: int = Field(default=300, description="Minimum karakter sayısı")
    enable_scraping: bool = Field(default=True, description="Web scraping aktif et")

# ayrıntılı tracking request

class TrackDetailViewRequest(BaseModel):
    """Detay görüntüleme tracking request'i"""
    reel_id: str = Field(..., description="Görüntülenen reel ID")
    read_duration_ms: int = Field(..., ge=0, description="Okuma süresi")
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Scroll derinliği")
    shared_from_detail: bool = Field(default=False, description="Detaydan paylaştı mı")
    session_id: Optional[str] = None



# ============ UTILITY FUNCTIONS ============

def get_user_id_from_header(user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """Header'dan user ID al, yoksa default ver"""
    return user_id or "anonymous_user"

# ============ CORE TRACKING ENDPOINTS ============
@router.post("/track-view")
async def track_view(
    request: TrackViewRequest,
    user_id: str = Header(..., alias="X-User-ID")
):
    """
    Reel izleme kaydı oluştur (UPDATED: Emoji support)
    
    Frontend'den her reel izlendiğinde çağrılır.
    
    New features:
    - Emoji reaction tracking
    - Paused count, replayed, shared, saved signals
    """
    try:
        # Reel'in var olup olmadığını kontrol et
        reel = await reels_analytics.get_reel_by_id(request.reel_id)
        if not reel:
            raise HTTPException(status_code=404, detail=f"Reel not found: {request.reel_id}")
        
        # ReelView oluştur (with new fields)
        from ...models.reels_tracking import ReelView, ViewStatus
        
        view = ReelView(
            user_id=user_id,
            reel_id=request.reel_id,
            duration_ms=request.duration_ms,
            status=ViewStatus.COMPLETED if request.completed else ViewStatus.PARTIAL,
            category=request.category or reel.news_data.category,
            session_id=request.session_id,
            
            # NEW: Emoji reaction
            emoji_reaction=request.emoji_reaction,
            emoji_timestamp=datetime.now() if request.emoji_reaction else None,
            
            # NEW: Extra signals
            paused_count=request.paused_count or 0,
            replayed=request.replayed or False,
            shared=request.shared or False,
            saved=request.saved or False
        )
        
        # Track view
        response = await reels_analytics.track_reel_view(user_id, request)
        
        # NEW: Preference engine güncelle
        await preference_engine.update_from_view(user_id, reel, view)
        
        # User stats al
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        # Response oluştur
        return TrackViewResponse(
            success=True,
            message="View tracked successfully",
            view_id=response.get("view_id"),
            meaningful_view=view.is_meaningful_view(),
            engagement_score=view.get_engagement_score(),
            personalization_level=user_stats.get_personalization_level(),
            total_interactions=user_stats.total_reels_watched,
            daily_progress_updated=response.get("daily_progress_updated", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Track view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    
    🆕 Yeni kullanıcılar için boş progress döndürür (500 hatası vermez)
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
        
        # 🆕 Eğer progress None dönerse, boş progress oluştur
        if progress is None:
            return UserProgressResponse(
                date=parsed_date.isoformat(),
                progress_percentage=0.0,
                total_published_today=0,
                watched_today=0,
                category_breakdown={}
            )
        
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
        # 🆕 Hata durumunda da boş progress döndür (500 hatası yerine)
        print(f"⚠️ Daily progress error for {user_id}: {e}")
        return UserProgressResponse(
            date=parsed_date.isoformat() if 'parsed_date' in locals() else date.today().isoformat(),
            progress_percentage=0.0,
            total_published_today=0,
            watched_today=0,
            category_breakdown={}
        )
        
        
        
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
    
    🆕 Yeni kullanıcılar için boş liste döndürür (500 hatası vermez)
    """
    try:
        watched_reels = await reels_analytics.get_user_watched_reels(user_id, limit)
        
        # 🆕 Eğer None dönerse boş liste kullan
        if watched_reels is None:
            watched_reels = []
        
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
        # 🆕 Hata durumunda da boş liste döndür
        print(f"⚠️ Get watched reels error for {user_id}: {e}")
        return {
            "success": True,
            "user_id": user_id,
            "watched_reels": [],
            "total_count": 0,
            "filter_applied": category,
            "error_message": "Could not load watched reels"
        }


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
    
    🆕 Yeni kullanıcılar için boş stats döndürür (500 hatası vermez)
    """
    try:
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        # 🆕 Eğer stats None dönerse, boş stats oluştur
        if user_stats is None:
            return UserStatsResponse(
                user_id=user_id,
                total_reels_watched=0,
                total_screen_time_ms=0,
                total_screen_time_hours=0.0,
                completion_rate=0.0,
                favorite_categories=[],
                last_activity=None,
                current_streak_days=0,
                avg_daily_reels=0.0
            )
        
        return UserStatsResponse(
            user_id=user_id,
            total_reels_watched=user_stats.total_reels_watched,
            total_screen_time_ms=user_stats.total_screen_time_ms,
            total_screen_time_hours=round(user_stats.get_total_screen_time_hours(), 2),
            completion_rate=round(user_stats.completion_rate * 100, 1),
            favorite_categories=user_stats.favorite_categories,
            last_activity=user_stats.last_reel_viewed_at.isoformat() if user_stats.last_reel_viewed_at else None,
            current_streak_days=user_stats.current_streak_days,
            avg_daily_reels=round(user_stats.avg_daily_reels, 1)
        )
        
    except Exception as e:
        # 🆕 Hata durumunda da boş stats döndür (500 hatası yerine)
        print(f"⚠️ User stats error for {user_id}: {e}")
        return UserStatsResponse(
            user_id=user_id,
            total_reels_watched=0,
            total_screen_time_ms=0,
            total_screen_time_hours=0.0,
            completion_rate=0.0,
            favorite_categories=[],
            last_activity=None,
            current_streak_days=0,
            avg_daily_reels=0.0
        )

# ============ MAIN FEED ENDPOINTS (Instagram-style) ============
@router.get("/feed")
async def get_feed(
    limit: int = Query(20, ge=1, le=50, description="Kaç reel döndürsün"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    user_id: str = Header(..., alias="X-User-ID")
):
    """
    Kullanıcıya özel personalized feed (COMPLETELY REWRITTEN)
    
    Instagram-style adaptive algorithm:
    - Cold start (0-10 interactions): %70 trending + %30 fresh
    - Warm (10-50 interactions): Rule-based preference
    - Hot (50+ interactions): NLP-powered similarity
    
    Query params:
    - limit: Kaç reel (1-50)
    - cursor: Pagination için
    
    Headers:
    - X-User-ID: Kullanıcı ID (required)
    """
    try:
        # Feed generator kullan
        feed_response = await feed_generator.generate_feed(
            user_id=user_id,
            limit=limit,
            cursor=cursor
        )
        
        return feed_response
        
    except Exception as e:
        print(f"Feed generation error: {e}")
        
        # Fallback: En yeni haberler
        all_reels = await reels_analytics.get_all_published_reels()
        sorted_reels = sorted(all_reels, key=lambda r: r.published_at, reverse=True)
        
        return FeedResponse(
            success=False,
            reels=sorted_reels[:limit],
            pagination=FeedPagination(
                current_page=1,
                has_next=False,
                total_available=len(sorted_reels)
            ),
            feed_metadata=FeedMetadata(
                algorithm_version="fallback",
                personalization_level="none"
            )
        )


@router.get("/user/{user_id}/preference-stats")
async def get_user_preference_stats(user_id: str):
    """
    Kullanıcının tercih istatistikleri (NEW ENDPOINT)
    
    Debug ve analytics için kullanılır.
    
    Returns:
    - Personalization level (cold/warm/hot)
    - Top categories
    - Top keywords
    - Total interactions
    """
    try:
        stats = preference_engine.get_user_stats(user_id)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/system/nlp-stats")
async def get_nlp_stats():
    """
    NLP engine istatistikleri (NEW ENDPOINT)
    
    Debug için: Model fitted mi, corpus boyutu vb.
    """
    try:
        stats = incremental_nlp.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            reel.is_watched = reel.id in watched_reel_ids
        
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

# ============ REEL MANAGEMENT ENDPOINTS ============

@router.get("/{reel_id}")
async def get_reel_by_id(
    reel_id: str,
    user_id: str = Depends(get_user_id_from_header)
):
    """
    Belirli bir reel'in detaylarını al
    
    - **reel_id**: Reel ID'si
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
        raise HTTPException(status_code=500, detail=f"Get reel error: {str(e)}")
@router.post("/bulk-create")
async def bulk_create_reels(request: BulkReelCreationRequest):
    """
    Toplu reel oluşturma (RSS → TTS → Reel → NLP Corpus)
    
    **UPDATED: NLP corpus integration**
    
    Pipeline:
    1. RSS'den haberler al
    2. Filtreleme (min_chars)
    3. TTS dönüşümü
    4. Reel oluştur
    5. NLP corpus'a ekle (NEW)
    6. Keyword extraction (NEW)
    
    Args:
    - **category**: Haber kategorisi
    - **count**: Oluşturulacak reel sayısı
    - **voice**: TTS ses modeli
    - **min_chars**: Minimum karakter sayısı
    - **enable_scraping**: Scraping aktif mi
    
    Returns:
    - Summary with NLP stats
    """
    try:
        # 1. RSS'den haberler al
        news_response = await content_service.get_latest_news(
            count=request.count * 2,  # Filtreleme için fazla al
            category=request.category,
            enable_scraping=request.enable_scraping
        )
        
        if not news_response.success:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch news: {news_response.message}"
            )
        
        # 2. Filtreleme
        filtered_articles = [
            article for article in news_response.articles
            if len(article.content) >= request.min_chars
        ][:request.count]
        
        if not filtered_articles:
            raise HTTPException(
                status_code=404, 
                detail="No articles found matching criteria"
            )
        
        # 3. TTS işlemi + Reel oluştur
        processed_count = 0
        failed_count = 0
        created_reels = []
        nlp_added_count = 0
        
        for article in filtered_articles:
            try:
                # TTS işlemi (simulated - production'da processing_service kullan)
                tts_content = article.to_tts_content()
                
                # Simulated TTS response
                estimated_cost = (len(tts_content) / 1_000_000) * 0.015
                duration_seconds = max(15, len(tts_content.split()) // 150 * 60)
                audio_filename = f"reel_{hashlib.md5(article.url.encode()).hexdigest()[:12]}.mp3"
                audio_url = f"/audio/{audio_filename}"
                file_size_mb = duration_seconds * 0.5
                
                # 4. Reel oluştur
                reel = await reels_analytics.create_reel_from_article(
                    article=article,
                    audio_url=audio_url,
                    duration_seconds=duration_seconds,
                    file_size_mb=file_size_mb,
                    voice_used=request.voice,
                    estimated_cost=estimated_cost
                )
                
                processed_count += 1
                created_reels.append(reel)
                print(f"✅ Reel created: {reel.id} - {reel.news_data.title[:50]}...")
                
                # 🆕 5. NLP corpus'a ekle
                try:
                    # Corpus text: title + summary
                    corpus_text = f"{reel.news_data.title} {reel.news_data.summary}"
                    
                    # Metadata
                    metadata = {
                        "category": reel.news_data.category,
                        "keywords": reel.news_data.keywords,
                        "published_at": reel.published_at.isoformat()
                    }
                    
                    # NLP'ye ekle
                    await incremental_nlp.add_news_to_corpus(
                        reel_id=reel.id,
                        text=corpus_text,
                        metadata=metadata
                    )
                    
                    nlp_added_count += 1
                    
                    # 🆕 6. Keyword extraction (eğer haber keywords'ü yoksa)
                    if not reel.news_data.keywords:
                        extracted_keywords = incremental_nlp.extract_keywords(
                            text=corpus_text,
                            top_n=10
                        )
                        # Keywords'ü güncelle (optional - reel object'e ekleyebilirsin)
                        print(f"   Extracted keywords: {extracted_keywords[:5]}")
                    
                except Exception as nlp_error:
                    print(f"⚠️ NLP corpus add failed for {reel.id}: {nlp_error}")
                    # NLP hatası reel oluşumunu engellemez, devam et
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to create reel for {article.title}: {e}")
                continue
        
        # 🆕 NLP stats
        nlp_stats = incremental_nlp.get_stats()
        
        return {
            "success": True,
            "message": f"Bulk reel creation completed with NLP integration",
            "summary": {
                "requested_count": request.count,
                "articles_found": len(filtered_articles),
                "reels_created": processed_count,
                "failed": failed_count,
                "success_rate": round((processed_count / len(filtered_articles)) * 100, 1) if filtered_articles else 0,
                "category": request.category,
                "voice_used": request.voice
            },
            "nlp_integration": {
                "corpus_added": nlp_added_count,
                "nlp_fitted": nlp_stats["is_fitted"],
                "corpus_size": nlp_stats["corpus_size"],
                "vocab_size": nlp_stats["vocab_size"],
                "next_refit_in": nlp_stats["next_refit_in"]
            },
            "created_reels": [
                {
                    "id": r.id,
                    "title": r.news_data.title,
                    "category": r.news_data.category,
                    "duration_seconds": r.duration_seconds,
                    "audio_url": r.audio_url
                }
                for r in created_reels[:5]  # İlk 5 reel'i göster
            ] if created_reels else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Bulk creation error: {str(e)}"
        )
# ============ ANALYTICS ENDPOINTS ============

@router.get("/analytics/{reel_id}")
async def get_reel_analytics(reel_id: str):
    """
    Belirli bir reel'in analytics bilgileri
    
    - **reel_id**: Reel ID'si
    
    **Admin/moderator için reel performans bilgileri**
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
        overview = await reels_analytics.get_analytics_overview(period_days)
        
        return {
            "success": True,
            "analytics_overview": overview
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
    
    🆕 Yeni kullanıcılar için boş summary döndürür (500 hatası vermez)
    """
    try:
        # Bugünkü stats al
        today_progress = await reels_analytics.get_user_daily_progress(user_id)
        user_stats = await reels_analytics.get_user_stats(user_id)
        
        # 🆕 None check
        if today_progress is None or user_stats is None:
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
                "message": "Welcome! Start watching to see your progress 🎬"
            }
        
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
        
        # Achievements check
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
        # 🆕 Hata durumunda da varsayılan response döndür
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

# ============ SYSTEM STATUS ENDPOINTS ============

@router.get("/system/status")
async def get_reel_system_status():
    """
    Reel sisteminin durumu
    
    **Sistem sağlık kontrolü ve istatistikleri**
    """
    try:
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
        raise HTTPException(status_code=500, detail=f"System status error: {str(e)}")

# ============ API DOCUMENTATION HELPER ============
@router.post("/track-detail-view")
async def track_detail_view(
    request: TrackDetailViewRequest,
    user_id: str = Header(..., alias="X-User-ID")
):
    """
    Haber detayı okuma tracking (NEW ENDPOINT)
    
    Kullanıcı "Detayları Oku" butonuna tıklayıp tam haberi okuduğunda çağrılır.
    
    Bu çok güçlü bir sinyal! Detay okuma = merak + ilgi
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
        
        # Analytics'e kaydet (detail view count güncelle)
        await reels_analytics.track_detail_view(user_id, detail_event)
        
        # CRITICAL: Preference engine'e EKSTRA boost ver
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
        print(f"Track detail view error: {e}")
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
        "management": [
            "GET /api/reels/{reel_id} - Reel detayı",
            "POST /api/reels/bulk-create - Toplu reel oluştur",
            "GET /api/reels/system/status - Sistem durumu"
        ],
        "utility": [
            "GET /api/reels/user/{id}/session-summary - Session özeti",
            "GET /api/reels/endpoints - Bu endpoint listesi"
        ]
    }
    
    return {
        "success": True,
        "message": "Updated Reels API endpoints",
        "total_endpoints": sum(len(group) for group in endpoints.values()),
        "endpoints": endpoints,
        "base_url": "/api/reels",
        "authentication": "X-User-ID header recommended",
        "pagination": "Cursor-based for main feed",
        "new_features": [
            "Instagram-style feed algorithm",
            "Real ReelFeedItem with NewsData",
            "Cursor-based pagination",
            "Bulk reel creation",
            "Enhanced analytics"
        ]
    }
    
    
    
"""  

Instagram-style Ana Feed:
httpGET /api/reels/feed?limit=20&cursor=reel_123

Cursor-based pagination
FeedResponse yapısı (pagination + metadata)
Algoritma: %30 trending, %50 personalized, %20 fresh

2. Yeni ReelFeedItem Desteği:

Tam haber verisi (NewsData)
Audio bilgileri (url, duration, file_size)
TTS maliyeti tracking
Reel durumu (draft/published/archived)

3. Bulk Reel Creation:
httpPOST /api/reels/bulk-create
{
  "category": "guncel",
  "count": 10,
  "voice": "alloy"
}

RSS → TTS → Reel pipeline
Toplu işlem with success rate

4. Enhanced Analytics:

Detaylı performance report (/analytics/{reel_id})
Sistem overview with hourly breakdown
User session summary with achievements

5. Real Data Integration:

Mockup temizliği - gerçek ReelsAnalyticsService kullanımı
Article → ReelFeedItem dönüşümü
Gerçek tracking sistemi

🎯 Ana API Akışı:
Frontend için:

Ana Feed: GET /feed - Ana sayfa
İzleme: POST /track-view - Her reel için
Progress: GET /user/{id}/daily-progress - Dashboard

"""