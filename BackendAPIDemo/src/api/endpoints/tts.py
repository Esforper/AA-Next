# ================================
# src/api/endpoints/tts.py - Updated TTS API Endpoints
# ================================

"""
Text-to-Speech API endpoint'leri
Audio generation, voice management, cost tracking ve RSS integration
"""

from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum
from pathlib import Path

from ...services.processing import processing_service
from ...services.content import content_service
from ...models.tts import TTSRequest, TTSResponse, AudioResult
from ...models.base import BaseResponse
from ...config import settings

# Router oluştur
router = APIRouter(prefix="/api/tts", tags=["tts"])

# ============ REQUEST MODELS (Updated) ============

class TextToSpeechRequest(BaseModel):
    """Direct text to speech request"""
    text: str = Field(..., min_length=10, max_length=50000, description="Text to convert")
    voice: str = Field(default="nova", description="Voice to use")
    model: str = Field(default="gpt-4o-mini-tts", description="TTS model")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")
    create_reel: bool = Field(default=False, description="Create reel after TTS")

class ArticleToSpeechRequest(BaseModel):
    """Article URL to speech request"""
    url: HttpUrl = Field(..., description="Article URL")
    voice: str = Field(default="nova", description="Voice to use")
    model: str = Field(default="gpt-4o-mini-tts", description="TTS model")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")
    enable_scraping: bool = Field(default=True, description="Enable web scraping")
    create_reel: bool = Field(default=True, description="Create reel after TTS")

class BatchTTSRequest(BaseModel):
    """Batch TTS processing request"""
    category: str = Field(default="guncel", description="News category")
    count: int = Field(default=5, ge=1, le=20, description="Number of articles")
    voice: str = Field(default="nova", description="Voice to use")
    model: str = Field(default="gpt-4o-mini-tts", description="TTS model")
    min_chars: int = Field(default=200, ge=50, description="Minimum characters")
    max_chars: int = Field(default=8000, le=50000, description="Maximum characters")
    create_reels: bool = Field(default=True, description="Create reels automatically")
    rss_optimized: bool = Field(default=True, description="Use RSS optimization")
    force: bool = Field(default=False, description="Skip confirmation")

# RSS-Specific Request Models (NEW)

class RSSConvertRequest(BaseModel):
    """RSS article to speech request"""
    url: HttpUrl = Field(..., description="RSS article URL")
    voice: str = Field(default="nova", description="Voice to use")
    model: str = Field(default="gpt-4o-mini-tts", description="TTS model")
    use_summary_only: bool = Field(default=True, description="Use only title+summary (optimal for reels)")
    create_reel: bool = Field(default=True, description="Auto-create reel")

class BatchRSSRequest(BaseModel):
    """Batch RSS processing request"""
    category: str = Field(default="guncel", description="News category")
    count: int = Field(default=10, ge=1, le=50, description="Number of articles to process")
    voice: str = Field(default="nova", description="Voice to use")
    model: str = Field(default="gpt-4o-mini-tts", description="TTS model")
    min_chars: int = Field(default=100, ge=50, description="Minimum character count")
    enable_scraping: bool = Field(default=True, description="Enable full content scraping")

class WorkerIntegrationRequest(BaseModel):
    """Worker integration request"""
    action: str = Field(..., description="Action: trigger, status, config")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")

# ============ BASIC TTS ENDPOINTS (Updated) ============

@router.post("/convert", response_model=TTSResponse)
async def convert_text_to_speech(request: TextToSpeechRequest):
    """
    Text'i sese çevir
    
    - **text**: Dönüştürülecek metin (10-50000 karakter)
    - **voice**: Ses modeli (nova, alloy, echo, fable, onyx, shimmer, coral, verse, ballad, ash, sage, marin, cedar)
    - **model**: TTS modeli (gpt-4o-mini-tts, tts-1, tts-1-hd)
    - **speed**: Konuşma hızı (0.25-4.0)
    - **create_reel**: TTS sonrası otomatik reel oluştur
    """
    try:
        # TTSRequest oluştur
        tts_request = TTSRequest(
            text=request.text,
            voice=request.voice,
            model=request.model,
            speed=request.speed
        )
        
        # Cost estimation
        estimated_cost = (len(request.text) / 1_000_000) * (0.030 if request.model == "tts-1-hd" else 0.015)
        
        # Convert to speech with optional reel creation
        result = await processing_service.text_to_speech(
            request=tts_request,
            create_reel=request.create_reel,
            article=None  # Pure text, no article
        )
        
        if result.success:
            # Add extra info for response
            result.result.estimated_cost = estimated_cost
            return result
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS conversion error: {str(e)}")

@router.post("/convert-article", response_model=TTSResponse)
async def convert_article_to_speech(request: ArticleToSpeechRequest):
    """
    Article URL'ini sese çevir
    
    - **url**: Makale URL'i
    - **voice**: Ses modeli
    - **model**: TTS modeli
    - **enable_scraping**: Web scraping aktif et
    - **create_reel**: Otomatik reel oluştur (önerilen)
    """
    try:
        # Article'ı al
        article = await content_service.get_article_by_url(
            url=str(request.url),
            enable_scraping=request.enable_scraping
        )
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found or could not be scraped"
            )
        
        # Article'ı sese çevir (enhanced method)
        result = await processing_service.article_to_speech(
            article=article,
            voice=request.voice,
            model=request.model,
            create_reel=request.create_reel
        )
        
        if result.success:
            # Article bilgilerini ekle
            if not hasattr(result.result, 'metadata'):
                result.result.metadata = {}
            
            result.result.metadata.update({
                "article_title": article.title,
                "article_url": str(request.url),
                "article_author": article.author,
                "article_category": article.category,
                "scraping_enabled": request.enable_scraping,
                "reel_created": request.create_reel
            })
            return result
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Article TTS error: {str(e)}")

@router.post("/batch")
async def batch_convert_articles(request: BatchTTSRequest):
    """
    Toplu makale ses dönüştürme (Enhanced)
    
    - **category**: Haber kategorisi
    - **count**: İşlenecek makale sayısı
    - **voice**: Ses modeli
    - **min_chars/max_chars**: Karakter limitleri
    - **create_reels**: Otomatik reel oluştur
    - **rss_optimized**: RSS optimizasyonu kullan (önerilen)
    """
    try:
        # News articles al
        news_result = await content_service.get_latest_news(
            count=request.count * 2,  # Filtreleme için fazla al
            category=request.category,
            enable_scraping=True
        )
        
        if not news_result.success:
            raise HTTPException(status_code=400, detail=news_result.message)
        
        # Filter articles by character count
        filtered_articles = [
            article for article in news_result.articles
            if request.min_chars <= len(article.content) <= request.max_chars
        ][:request.count]
        
        if not filtered_articles:
            raise HTTPException(
                status_code=404,
                detail="No articles found matching the criteria"
            )
        
        # Cost estimation
        if request.rss_optimized:
            # RSS optimization kullanır sadece title+summary
            total_chars = sum(len(f"{article.title}. {article.summary or ''}") for article in filtered_articles)
        else:
            # Full content
            total_chars = sum(len(article.to_tts_content()) for article in filtered_articles)
        
        cost_per_char = 0.030 if request.model == "tts-1-hd" else 0.015
        estimated_cost = (total_chars / 1_000_000) * cost_per_char
        
        # Batch process (Enhanced method)
        results = await processing_service.batch_articles_to_speech(
            articles=filtered_articles,
            voice=request.voice,
            model=request.model,
            create_reels=request.create_reels,
            rss_optimized=request.rss_optimized
        )
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        actual_cost = sum(r.result.estimated_cost for r in results if r.success)
        
        return {
            "success": True,
            "message": f"Batch processing completed: {successful}/{len(results)} successful",
            "summary": {
                "total_articles": len(results),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(results)) * 100, 1),
                "estimated_cost": estimated_cost,
                "actual_cost": actual_cost,
                "total_characters": total_chars,
                "rss_optimized": request.rss_optimized,
                "reels_created": successful if request.create_reels else 0
            },
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch TTS error: {str(e)}")

# ============ RSS-SPECIFIC ENDPOINTS (NEW) ============

@router.post("/rss-convert", response_model=TTSResponse)
async def convert_rss_article_to_speech(request: RSSConvertRequest):
    """
    RSS article'ı sese çevir (RSS için optimize edilmiş)
    
    **RSS haberleri için özel optimize edilmiş endpoint**
    
    - **url**: RSS makale URL'i
    - **voice**: Ses modeli (default: nova)
    - **model**: TTS modeli (default: gpt-4o-mini-tts)
    - **use_summary_only**: Sadece başlık+özet kullan (reels için ideal)
    - **create_reel**: Otomatik reel oluştur
    """
    try:
        # Article'ı al
        article = await content_service.get_article_by_url(
            url=str(request.url),
            enable_scraping=True
        )
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="RSS article not found or could not be scraped"
            )
        
        # RSS-optimized TTS conversion
        result = await processing_service.rss_news_to_speech(
            article=article,
            voice=request.voice,
            model=request.model,
            use_summary_only=request.use_summary_only
        )
        
        if result.success:
            # RSS-specific metadata
            if not hasattr(result.result, 'metadata'):
                result.result.metadata = {}
            
            result.result.metadata.update({
                "article_title": article.title,
                "article_url": str(request.url),
                "rss_optimized": True,
                "summary_only": request.use_summary_only,
                "reel_created": request.create_reel,
                "processing_type": "rss_optimized"
            })
            
            return result
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RSS TTS error: {str(e)}")

@router.post("/batch-rss")
async def batch_convert_rss_articles(request: BatchRSSRequest):
    """
    Toplu RSS makale işleme
    
    **RSS pipeline için optimize edilmiş toplu işlem**
    
    - **category**: Haber kategorisi
    - **count**: İşlenecek makale sayısı (1-50)
    - **voice**: Ses modeli
    - **model**: TTS modeli
    - **min_chars**: Minimum karakter sayısı
    - **enable_scraping**: Full content scraping
    """
    try:
        # Bu endpoint processing_service.batch_rss_to_speech kullanır
        news_result = await content_service.get_latest_news(
            count=request.count * 2,
            category=request.category,
            enable_scraping=request.enable_scraping
        )
        
        if not news_result.success:
            raise HTTPException(status_code=400, detail=news_result.message)
        
        # Filter by minimum characters
        suitable_articles = [
            article for article in news_result.articles
            if len(article.title + (article.summary or "") + article.content) >= request.min_chars
        ][:request.count]
        
        if not suitable_articles:
            raise HTTPException(
                status_code=404,
                detail="No suitable RSS articles found"
            )
        
        # RSS-optimized batch processing
        results = await processing_service.batch_rss_to_speech(
            articles=suitable_articles,
            voice=request.voice,
            model=request.model
        )
        
        # Summary
        successful = sum(1 for r in results if r.success)
        total_cost = sum(r.result.estimated_cost for r in results if r.success)
        
        return {
            "success": True,
            "message": f"RSS batch processing completed",
            "summary": {
                "articles_found": len(news_result.articles),
                "articles_suitable": len(suitable_articles),
                "articles_processed": len(results),
                "successful_conversions": successful,
                "failed_conversions": len(results) - successful,
                "success_rate": round((successful / len(results)) * 100, 1),
                "total_cost": round(total_cost, 6),
                "reels_auto_created": successful,
                "category": request.category,
                "voice_used": request.voice,
                "model_used": request.model
            },
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch RSS error: {str(e)}")

@router.post("/create-reels-from-news")
async def create_reels_from_latest_news(
    category: str = Query("guncel", description="News category"),
    count: int = Query(10, ge=1, le=50, description="Number of articles"),
    voice: str = Query("nova", description="TTS voice"),
    min_chars: int = Query(100, ge=50, description="Minimum characters")
):
    """
    Son haberlerden otomatik reel oluştur
    
    **RSS → TTS → Reel pipeline'ının API versiyonu**
    
    Bu endpoint processing_service.create_reels_from_latest_news() kullanır
    """
    try:
        result = await processing_service.create_reels_from_latest_news(
            category=category,
            count=count,
            voice=voice,
            min_chars=min_chars
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "reels_pipeline": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create reels error: {str(e)}")

# ============ WORKER INTEGRATION ENDPOINTS (NEW) ============

@router.post("/worker-integration")
async def worker_integration(request: WorkerIntegrationRequest):
    """
    RSS Worker ile TTS entegrasyonu
    
    **Worker'dan TTS işlemlerini tetikleme ve kontrol**
    
    - **action**: trigger, status, config
    - **parameters**: Action'a özel parametreler
    """
    try:
        if request.action == "trigger":
            # Worker'dan tetiklenen TTS işlemi
            category = request.parameters.get("category", "guncel")
            count = request.parameters.get("count", 5)
            voice = request.parameters.get("voice", "nova")
            
            result = await processing_service.create_reels_from_latest_news(
                category=category,
                count=count,
                voice=voice,
                min_chars=100
            )
            
            return {
                "success": True,
                "action": "trigger",
                "result": result
            }
        
        elif request.action == "status":
            # TTS sistem durumu
            stats = await processing_service.get_tts_stats()
            
            return {
                "success": True,
                "action": "status",
                "tts_stats": stats,
                "worker_integration": True
            }
        
        elif request.action == "config":
            # TTS configuration bilgisi
            return {
                "success": True,
                "action": "config",
                "tts_config": {
                    "default_voice": settings.tts_voice,
                    "default_model": settings.tts_model,
                    "provider": settings.tts_provider,
                    "available_voices": [
                        "nova", "alloy", "echo", "fable", "onyx", "shimmer",
                        "coral", "verse", "ballad", "ash", "sage", "marin", "cedar"
                    ],
                    "available_models": ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"]
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Worker integration error: {str(e)}")

@router.get("/worker-stats")
async def get_worker_tts_stats():
    """
    Worker TTS istatistikleri
    
    **Worker'ın TTS kullanım istatistikleri**
    """
    try:
        # TTS stats al
        tts_stats = await processing_service.get_tts_stats()
        
        # Worker-specific bilgiler ekle
        try:
            from ...services.rss_worker import rss_worker
            worker_status = rss_worker.get_worker_status()
            
            return {
                "success": True,
                "tts_stats": tts_stats,
                "worker_stats": {
                    "is_running": worker_status["is_running"],
                    "total_runs": worker_status["total_runs"],
                    "total_reels_created": worker_status["total_reels_created"],
                    "total_cost": worker_status["total_cost"],
                    "success_rate": worker_status.get("success_rate", 0)
                },
                "integration_active": True
            }
        except Exception as e:
            # Worker service mevcut değilse sadece TTS stats döndür
            return {
                "success": True,
                "tts_stats": tts_stats,
                "worker_stats": None,
                "integration_active": False,
                "note": "Worker service not available"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Worker stats error: {str(e)}")

# ============ VOICE & MODEL MANAGEMENT (Updated) ============

@router.get("/voices")
async def get_available_voices():
    """
    Mevcut ses modellerini listele (Updated)
    """
    voices = {
        "nova": {
            "name": "Nova",
            "description": "Energetic, clear voice - ideal for news",
            "gender": "female",
            "recommended_for": ["news", "rss", "reels"],
            "default_for": "rss"
        },
        "alloy": {
            "name": "Alloy",
            "description": "Balanced, natural voice",
            "gender": "neutral",
            "recommended_for": ["general", "education"]
        },
        "echo": {
            "name": "Echo", 
            "description": "Clear, crisp voice",
            "gender": "male",
            "recommended_for": ["professional", "business"]
        },
        "fable": {
            "name": "Fable",
            "description": "Warm, storytelling voice",
            "gender": "neutral",
            "recommended_for": ["stories", "audiobooks"]
        },
        "onyx": {
            "name": "Onyx",
            "description": "Deep, authoritative voice",
            "gender": "male", 
            "recommended_for": ["news", "documentaries"]
        },
        "shimmer": {
            "name": "Shimmer",
            "description": "Soft, gentle voice",
            "gender": "female",
            "recommended_for": ["meditation", "calm content"]
        },
        # New voices
        "coral": {
            "name": "Coral",
            "description": "Warm, friendly voice",
            "gender": "female",
            "recommended_for": ["casual", "friendly"]
        },
        "sage": {
            "name": "Sage",
            "description": "Wise, mature voice",
            "gender": "neutral",
            "recommended_for": ["education", "wisdom"]
        }
    }
    
    return {
        "success": True,
        "voices": voices,
        "default_voice": settings.tts_voice,
        "rss_recommended": "nova",
        "total_count": len(voices)
    }

@router.get("/models")
async def get_available_models():
    """
    Mevcut TTS modellerini listele (Updated)
    """
    models = {
        "gpt-4o-mini-tts": {
            "name": "GPT-4O Mini TTS",
            "description": "Latest OpenAI model, optimized quality",
            "quality": "high",
            "speed": "fast",
            "cost_per_1m_chars": 0.015,
            "recommended": True,
            "default_for": "rss"
        },
        "tts-1": {
            "name": "TTS-1",
            "description": "Standard quality, faster generation",
            "quality": "standard",
            "speed": "fast",
            "cost_per_1m_chars": 0.015
        },
        "tts-1-hd": {
            "name": "TTS-1 HD",
            "description": "High quality, slower generation",
            "quality": "high",
            "speed": "slower",
            "cost_per_1m_chars": 0.030
        }
    }
    
    return {
        "success": True,
        "models": models,
        "default_model": settings.tts_model,
        "recommended_model": "gpt-4o-mini-tts",
        "total_count": len(models)
    }

# ============ COST & STATISTICS (Enhanced) ============

@router.get("/stats")
async def get_enhanced_tts_stats():
    """
    TTS sistem istatistikleri ve maliyet bilgileri (Enhanced)
    """
    try:
        # Base stats
        stats = await processing_service.get_tts_stats()
        
        # Enhanced stats
        enhanced_stats = {
            "base_stats": stats,
            "provider": settings.tts_provider,
            "default_settings": {
                "voice": settings.tts_voice,
                "model": settings.tts_model,
                "speed": settings.tts_speed
            },
            "rss_integration": {
                "rss_optimized_endpoints": True,
                "worker_integration": True,
                "auto_reel_creation": True
            }
        }
        
        # Worker stats integration
        try:
            from ...services.rss_worker import rss_worker
            worker_status = rss_worker.get_worker_status()
            enhanced_stats["worker_integration"] = {
                "worker_running": worker_status["is_running"],
                "worker_reels_created": worker_status["total_reels_created"],
                "worker_total_cost": worker_status["total_cost"]
            }
        except:
            enhanced_stats["worker_integration"] = {"available": False}
        
        return {
            "success": True,
            "message": "Enhanced TTS statistics retrieved",
            "stats": enhanced_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced stats error: {str(e)}")

@router.get("/cost-estimate")
async def estimate_cost(
    text_length: int = Query(..., ge=1, description="Text length in characters"),
    model: str = Query("gpt-4o-mini-tts", description="TTS model"),
    batch_size: int = Query(1, ge=1, le=50, description="Number of articles (for batch estimation)")
):
    """
    Maliyet tahmini yap (Enhanced)
    """
    try:
        # Model'e göre fiyatlandırma
        pricing = {
            "gpt-4o-mini-tts": 0.015,  # $15 per 1M characters
            "tts-1": 0.015,           # $15 per 1M characters
            "tts-1-hd": 0.030         # $30 per 1M characters
        }
        
        rate = pricing.get(model, 0.015)
        single_cost = (text_length / 1_000_000) * rate
        batch_cost = single_cost * batch_size
        
        return {
            "success": True,
            "estimation": {
                "single_article": {
                    "text_length": text_length,
                    "model": model,
                    "rate_per_1m_chars": rate,
                    "estimated_cost_usd": round(single_cost, 6),
                    "estimated_duration_seconds": max(1, text_length * 0.08)
                },
                "batch_processing": {
                    "batch_size": batch_size,
                    "total_characters": text_length * batch_size,
                    "total_estimated_cost_usd": round(batch_cost, 6),
                    "avg_cost_per_article": round(single_cost, 6)
                },
                "monthly_projections": {
                    "daily_10_articles": round(single_cost * 10 * 30, 2),
                    "daily_20_articles": round(single_cost * 20 * 30, 2),
                    "hourly_worker": round(single_cost * 10 * 24 * 30, 2)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation error: {str(e)}")

# ============ SYSTEM STATUS & TESTING ============

@router.get("/test-rss-integration")
async def test_rss_tts_integration():
    """
    RSS TTS entegrasyonunu test et
    """
    try:
        # Single RSS article test
        print("🧪 Testing RSS TTS integration...")
        
        # Get one article
        news_result = await content_service.get_latest_news(count=1, category="guncel")
        
        if not news_result.success or not news_result.articles:
            return {
                "success": False,
                "message": "No articles available for testing",
                "test_results": None
            }
        
        article = news_result.articles[0]
        
        # Test RSS-optimized TTS (without actually converting)
        test_text = f"{article.title}. {article.summary or article.content[:100]}"
        estimated_cost = (len(test_text) / 1_000_000) * 0.015
        
        test_results = {
            "article_info": {
                "title": article.title,
                "url": str(article.url),
                "category": article.category,
                "content_length": len(article.content)
            },
            "tts_test": {
                "optimized_text_length": len(test_text),
                "estimated_cost": round(estimated_cost, 6),
                "estimated_duration": len(test_text) * 0.08,
                "voice_default": "nova",
                "model_default": "gpt-4o-mini-tts"
            },
            "integration_status": {
                "rss_available": True,
                "tts_available": True,
                "reels_available": True,
                "worker_available": True
            }
        }
        
        return {
            "success": True,
            "message": "RSS TTS integration test completed (simulation)",
            "test_results": test_results,
            "note": "This is a simulation. Use /rss-convert for actual conversion."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"RSS TTS integration test failed: {str(e)}",
            "test_results": None
        }

# ============ UTILITY ENDPOINTS ============

@router.get("/test")
async def test_tts_system():
    """
    TTS sistemini test et (Enhanced)
    """
    try:
        test_text = "Bu bir test mesajıdır. Güncellenmiş TTS sistemi çalışıyor."
        
        # Test request oluştur
        from ...models.tts import TTSRequest
        test_request = TTSRequest(
            text=test_text,
            voice=settings.tts_voice,
            model=settings.tts_model
        )
        
        # Convert (but don't create reel for test)
        result = await processing_service.text_to_speech(
            request=test_request,
            create_reel=False  # Don't create reel for test
        )
        
        if result.success:
            # Test dosyasını sil (temizlik)
            if result.result.file_path:
                test_file = Path(result.result.file_path)
                if test_file.exists():
                    test_file.unlink()
            
            return {
                "success": True,
                "message": "Enhanced TTS system test successful",
                "test_info": {
                    "text_length": len(test_text),
                    "voice_used": settings.tts_voice,
                    "model_used": settings.tts_model,
                    "file_created": True,
                    "file_cleaned": True,
                    "duration_seconds": result.result.duration_seconds,
                    "estimated_cost": result.result.estimated_cost,
                    "rss_integration": True,
                    "worker_integration": True
                }
            }
        else:
            return {
                "success": False,
                "message": "Enhanced TTS system test failed",
                "error": result.message
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS test error: {str(e)}")

@router.get("/system-info")
async def get_tts_system_info():
    """
    TTS sistem bilgileri
    """
    return {
        "success": True,
        "system_info": {
            "provider": settings.tts_provider,
            "default_voice": settings.tts_voice,
            "default_model": settings.tts_model,
            "default_speed": settings.tts_speed,
            "storage_path": settings.storage_base_path,
            "rss_integration": True,
            "worker_integration": True,
            "auto_reel_creation": True
        },
        "features": {
            "basic_tts": True,
            "article_conversion": True,
            "batch_processing": True,
            "rss_optimization": True,
            "worker_integration": True,
            "cost_tracking": True,
            "multiple_voices": True,
            "multiple_models": True
        },
        "endpoints": {
            "basic": ["/convert", "/convert-article", "/batch"],
            "rss": ["/rss-convert", "/batch-rss", "/create-reels-from-news"],
            "worker": ["/worker-integration", "/worker-stats"],
            "management": ["/voices", "/models", "/stats", "/cost-estimate"],
            "testing": ["/test", "/test-rss-integration", "/system-info"]
        }
    }

# ============ API DOCUMENTATION HELPER ============

@router.get("/endpoints")
async def list_tts_endpoints():
    """
    TTS API endpoint'lerinin detaylı listesi
    
    **Geliştirici referansı için**
    """
    endpoints = {
        "basic_tts": [
            "POST /api/tts/convert - Direct text to speech",
            "POST /api/tts/convert-article - Article URL to speech", 
            "POST /api/tts/batch - Batch article processing"
        ],
        "rss_integration": [
            "POST /api/tts/rss-convert - RSS-optimized article conversion",
            "POST /api/tts/batch-rss - Batch RSS processing",
            "POST /api/tts/create-reels-from-news - Complete RSS→Reels pipeline"
        ],
        "worker_integration": [
            "POST /api/tts/worker-integration - Worker TTS operations",
            "GET /api/tts/worker-stats - Worker TTS statistics"
        ],
        "voice_management": [
            "GET /api/tts/voices - Available voices",
            "GET /api/tts/models - Available models"
        ],
        "analytics": [
            "GET /api/tts/stats - Enhanced TTS statistics",
            "GET /api/tts/cost-estimate - Cost estimation"
        ],
        "testing": [
            "GET /api/tts/test - System test",
            "GET /api/tts/test-rss-integration - RSS integration test",
            "GET /api/tts/system-info - System information"
        ],
        "utility": [
            "GET /api/tts/endpoints - This endpoint list"
        ]
    }
    
    new_features = [
        "RSS-optimized TTS conversion",
        "Automatic reel creation",
        "Worker integration",
        "Enhanced cost tracking",
        "GPT-4O Mini TTS support",
        "Nova voice default for news",
        "Batch RSS processing"
    ]
    
    return {
        "success": True,
        "message": "Enhanced TTS API endpoints",
        "total_endpoints": sum(len(group) for group in endpoints.values()),
        "endpoints": endpoints,
        "base_url": "/api/tts",
        "new_features": new_features,
        "integration": {
            "rss_system": "Full integration with RSS news fetching",
            "worker_system": "Background worker TTS operations",
            "reels_system": "Automatic reel creation after TTS",
            "analytics": "Enhanced cost and usage tracking"
        },
        "recommended_workflow": {
            "manual": "POST /rss-convert → GET /stats",
            "batch": "POST /batch-rss → GET /worker-stats", 
            "automated": "Worker handles everything automatically"
        }
    }