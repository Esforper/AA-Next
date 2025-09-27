# ================================
# src/api/endpoints/tts.py - TTS API Endpoints
# ================================

"""
Text-to-Speech API endpoint'leri
Audio generation, voice management ve cost tracking
"""

from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from pathlib import Path

from ...services.processing import processing_service
from ...services.content import content_service
from ...models.tts import TTSRequest, TTSResponse, AudioResult
from ...models.base import BaseResponse
from ...config import settings

# Router oluştur
router = APIRouter(prefix="/api/tts", tags=["tts"])

# ============ REQUEST MODELS ============

class TextToSpeechRequest(BaseModel):
    """Direct text to speech request"""
    text: str = Field(..., min_length=10, max_length=50000, description="Text to convert")
    voice: str = Field(default="alloy", description="Voice to use")
    model: str = Field(default="tts-1", description="TTS model")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")

class ArticleToSpeechRequest(BaseModel):
    """Article URL to speech request"""
    url: HttpUrl = Field(..., description="Article URL")
    voice: str = Field(default="alloy", description="Voice to use")
    model: str = Field(default="tts-1", description="TTS model")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")
    enable_scraping: bool = Field(default=True, description="Enable web scraping")

class BatchTTSRequest(BaseModel):
    """Batch TTS processing request"""
    category: str = Field(default="guncel", description="News category")
    count: int = Field(default=5, ge=1, le=20, description="Number of articles")
    voice: str = Field(default="alloy", description="Voice to use")
    model: str = Field(default="tts-1", description="TTS model")
    min_chars: int = Field(default=200, ge=50, description="Minimum characters")
    max_chars: int = Field(default=8000, le=50000, description="Maximum characters")
    force: bool = Field(default=False, description="Skip confirmation")

# ============ BASIC TTS ENDPOINTS ============

@router.post("/convert", response_model=TTSResponse)
async def convert_text_to_speech(request: TextToSpeechRequest):
    """
    Text'i sese çevir
    
    - **text**: Dönüştürülecek metin (10-50000 karakter)
    - **voice**: Ses modeli (alloy, echo, fable, onyx, nova, shimmer)
    - **model**: TTS modeli (tts-1, tts-1-hd)
    - **speed**: Konuşma hızı (0.25-4.0)
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
        estimated_cost = (len(request.text) / 1_000_000) * 0.015
        
        # Convert to speech
        result = await processing_service.text_to_speech(tts_request)
        
        if result.success:
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
        
        # Article'ı sese çevir
        result = await processing_service.article_to_speech(
            article=article,
            voice=request.voice,
            model=request.model
        )
        
        if result.success:
            # Article bilgilerini ekle
            result.result.metadata = {
                "article_title": article.title,
                "article_url": str(request.url),
                "article_author": article.author,
                "article_category": article.category
            }
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
    Toplu makale ses dönüştürme
    
    - **category**: Haber kategorisi
    - **count**: İşlenecek makale sayısı
    - **voice**: Ses modeli
    - **min_chars/max_chars**: Karakter limitleri
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
        total_chars = sum(len(article.to_tts_content()) for article in filtered_articles)
        estimated_cost = (total_chars / 1_000_000) * 0.015
        
        # Batch process
        results = await processing_service.batch_articles_to_speech(
            articles=filtered_articles,
            voice=request.voice,
            model=request.model
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
                "total_characters": total_chars
            },
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch TTS error: {str(e)}")

# ============ VOICE & MODEL MANAGEMENT ============

@router.get("/voices")
async def get_available_voices():
    """
    Mevcut ses modellerini listele
    """
    voices = {
        "alloy": {
            "name": "Alloy",
            "description": "Balanced, natural voice",
            "gender": "neutral",
            "recommended_for": ["general", "news", "education"]
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
        "nova": {
            "name": "Nova",
            "description": "Energetic, youthful voice",
            "gender": "female",
            "recommended_for": ["podcasts", "casual"]
        },
        "shimmer": {
            "name": "Shimmer",
            "description": "Soft, gentle voice",
            "gender": "female",
            "recommended_for": ["meditation", "calm content"]
        }
    }
    
    return {
        "success": True,
        "voices": voices,
        "default_voice": settings.tts_voice,
        "total_count": len(voices)
    }

@router.get("/models")
async def get_available_models():
    """
    Mevcut TTS modellerini listele
    """
    models = {
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
        "total_count": len(models)
    }

# ============ AUDIO FILE MANAGEMENT ============

@router.get("/files")
async def list_audio_files(
    limit: int = Query(50, ge=1, le=200, description="Number of files to list"),
    format: str = Query("json", description="Response format (json, simple)")
):
    """
    Oluşturulan ses dosyalarını listele
    """
    try:
        files = await processing_service.list_audio_files()
        
        # Limit uygula
        limited_files = files[:limit]
        
        if format == "simple":
            # Simple format - sadece filename ve download URL
            simple_files = [
                {
                    "filename": f["filename"],
                    "download_url": f["download_url"],
                    "size_mb": f["size_mb"]
                }
                for f in limited_files
            ]
            return {
                "success": True,
                "files": simple_files,
                "total_shown": len(simple_files),
                "total_available": len(files)
            }
        else:
            # Full format
            return {
                "success": True,
                "files": limited_files,
                "total_shown": len(limited_files),
                "total_available": len(files),
                "storage_info": {
                    "total_size_mb": sum(f["size_mb"] for f in files),
                    "storage_path": settings.storage_base_path
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File list error: {str(e)}")

# ============ COST & STATISTICS ============

@router.get("/stats")
async def get_tts_stats():
    """
    TTS sistem istatistikleri ve maliyet bilgileri
    """
    try:
        stats = await processing_service.get_tts_stats()
        
        return {
            "success": True,
            "message": "TTS statistics retrieved",
            "stats": stats,
            "provider": settings.tts_provider,
            "default_settings": {
                "voice": settings.tts_voice,
                "model": settings.tts_model,
                "speed": settings.tts_speed
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@router.get("/cost-estimate")
async def estimate_cost(
    text_length: int = Query(..., ge=1, description="Text length in characters"),
    model: str = Query("tts-1", description="TTS model")
):
    """
    Maliyet tahmini yap
    """
    try:
        # Model'e göre fiyatlandırma
        pricing = {
            "tts-1": 0.015,      # $15 per 1M characters
            "tts-1-hd": 0.030    # $30 per 1M characters
        }
        
        rate = pricing.get(model, 0.015)
        estimated_cost = (text_length / 1_000_000) * rate
        
        return {
            "success": True,
            "estimation": {
                "text_length": text_length,
                "model": model,
                "rate_per_1m_chars": rate,
                "estimated_cost_usd": round(estimated_cost, 6),
                "estimated_duration_seconds": max(1, text_length * 0.08)  # Rough estimate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cost estimation error: {str(e)}")

# ============ UTILITY ENDPOINTS ============

@router.get("/test")
async def test_tts_system():
    """
    TTS sistemini test et
    """
    try:
        test_text = "Bu bir test mesajıdır. TTS sistemi çalışıyor."
        
        # Test request oluştur
        test_request = TTSRequest(
            text=test_text,
            voice=settings.tts_voice,
            model=settings.tts_model
        )
        
        # Convert
        result = await processing_service.text_to_speech(test_request)
        
        if result.success:
            # Test dosyasını sil (temizlik)
            test_file = Path(result.result.file_path)
            if test_file.exists():
                test_file.unlink()
            
            return {
                "success": True,
                "message": "TTS system test successful",
                "test_info": {
                    "text_length": len(test_text),
                    "voice_used": settings.tts_voice,
                    "model_used": settings.tts_model,
                    "file_created": True,
                    "file_cleaned": True
                }
            }
        else:
            return {
                "success": False,
                "message": "TTS system test failed",
                "error": result.message
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS test error: {str(e)}")