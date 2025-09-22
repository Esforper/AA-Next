"""
News API Main
FastAPI ile local ağ üzerinde çalışan haber-TTS API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import socket
from pathlib import Path
import uvicorn

from models.news_models import TTSRequest
from services.news_service import NewsService
from services.tts_service import TTSService
from utils.config import get_app_config

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App config
app_config = get_app_config()

# FastAPI app
app = FastAPI(
    title="AA News TTS API",
    description="Anadolu Ajansı haberlerini çeken ve TTS'e dönüştüren API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Local network için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local network için
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - Ses dosyaları için
app.mount("/audio", StaticFiles(directory=app_config.output_dir), name="audio")

# Services
news_service = NewsService(
    default_category=app_config.default_category,
    scraping_delay=app_config.scraping_delay,
    max_workers=app_config.scraping_max_workers,
    enable_scraping=app_config.enable_scraping
)

tts_service = TTSService()


# Pydantic models
class NewsRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=50)
    category: Optional[str] = None
    enable_scraping: bool = True
    min_chars: int = Field(default=100, ge=50)
    max_chars: int = Field(default=10000, ge=100)


class TTSCreateRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    voice: str = Field(default="alloy", pattern="^(alloy|echo|fable|onyx|nova|shimmer)$")
    model: str = Field(default="tts-1", pattern="^(tts-1|tts-1-hd)$")
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class ArticleTTSRequest(BaseModel):
    url: str = Field(..., min_length=10)
    voice: Optional[str] = None
    model: Optional[str] = None


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AA News TTS API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "news": "/api/news/",
            "tts": "/api/tts/",
            "audio": "/audio/",
            "health": "/health"
        }
    }


# Health check
@app.get("/health")
async def health_check():
    """Sistem sağlığını kontrol et"""
    try:
        # RSS test
        rss_test = news_service.rss_reader.test_connection()
        
        # TTS stats
        tts_stats = tts_service.get_cost_statistics()
        
        return {
            "status": "healthy",
            "timestamp": tts_stats.get('total_requests', 0),
            "services": {
                "rss": rss_test.get('success', False),
                "tts": True,
                "scraping": app_config.enable_scraping
            },
            "stats": {
                "total_tts_requests": tts_stats.get('total_requests', 0),
                "total_cost": tts_stats.get('total_cost', 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


# News endpoints
@app.get("/api/news/latest")
async def get_latest_news(
    count: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    enable_scraping: bool = Query(True),
    min_chars: int = Query(100, ge=50),
    max_chars: int = Query(10000, ge=100)
):
    """Son haberleri al"""
    try:
        articles = news_service.get_latest_news(
            count=count,
            category=category,
            enable_scraping=enable_scraping
        )
        
        if not articles:
            raise HTTPException(status_code=404, detail="Haber bulunamadı")
        
        # Filtrele
        filtered_articles = news_service.filter_articles(
            articles, min_chars, max_chars
        )
        
        # Response oluştur
        result = {
            "success": True,
            "total_found": len(articles),
            "filtered_count": len(filtered_articles),
            "articles": [article.to_dict() for article in filtered_articles],
            "summary": news_service.get_articles_summary(filtered_articles)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Latest news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/categories")
async def get_available_categories():
    """Mevcut kategorileri listele"""
    categories = news_service.rss_reader.get_available_categories()
    category_info = news_service.rss_reader.get_category_info()
    
    return {
        "success": True,
        "categories": categories,
        "descriptions": category_info
    }


@app.get("/api/news/category/{category}")
async def get_news_by_category(
    category: str,
    count: int = Query(10, ge=1, le=50),
    enable_scraping: bool = Query(True)
):
    """Kategoriye göre haber al"""
    try:
        articles = news_service.get_latest_news(
            count=count,
            category=category,
            enable_scraping=enable_scraping
        )
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"'{category}' kategorisinde haber bulunamadı")
        
        return {
            "success": True,
            "category": category,
            "count": len(articles),
            "articles": [article.to_dict() for article in articles],
            "summary": news_service.get_articles_summary(articles)
        }
        
    except Exception as e:
        logger.error(f"Category news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/search")
async def search_news(
    q: str = Query(..., min_length=2),
    category: Optional[str] = Query(None),
    count: int = Query(20, ge=1, le=100)
):
    """Haber ara"""
    try:
        articles = news_service.search_articles(
            query=q,
            category=category,
            count=count
        )
        
        return {
            "success": True,
            "query": q,
            "category": category,
            "found": len(articles),
            "articles": [article.to_dict() for article in articles]
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# TTS endpoints
@app.post("/api/tts/convert")
async def convert_text_to_speech(request: TTSCreateRequest, background_tasks: BackgroundTasks):
    """Metni sese dönüştür"""
    try:
        tts_request = TTSRequest(
            text=request.text,
            voice=request.voice,
            model=request.model,
            speed=request.speed
        )
        
        logger.info(f"TTS dönüştürme başlatıldı: {len(request.text)} karakter")
        
        response = tts_service.text_to_speech(tts_request)
        
        if response.success:
            # Dosya URL'i oluştur
            filename = Path(response.audio_file_path).name
            audio_url = f"/audio/{filename}"
            
            return {
                "success": True,
                "message": "TTS başarılı",
                "audio_url": audio_url,
                "filename": filename,
                "file_size_bytes": response.file_size_bytes,
                "character_count": response.character_count,
                "estimated_cost": response.estimated_cost,
                "processing_time": response.processing_time_seconds,
                "voice": request.voice,
                "model": request.model
            }
        else:
            raise HTTPException(status_code=400, detail=response.error_message)
            
    except Exception as e:
        logger.error(f"TTS convert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts/article")
async def convert_article_to_speech(request: ArticleTTSRequest):
    """Haber makalesini sese dönüştür"""
    try:
        # Makaleyi al
        article = news_service.get_single_article(request.url, with_scraping=True)
        
        if not article:
            raise HTTPException(status_code=404, detail="Makale çekilemedi")
        
        # TTS'e dönüştür
        response = tts_service.convert_article_to_speech(
            article=article,
            voice=request.voice,
            model=request.model
        )
        
        if response.success:
            filename = Path(response.audio_file_path).name
            audio_url = f"/audio/{filename}"
            
            return {
                "success": True,
                "article": article.to_dict(),
                "audio_url": audio_url,
                "filename": filename,
                "file_size_bytes": response.file_size_bytes,
                "character_count": response.character_count,
                "estimated_cost": response.estimated_cost,
                "processing_time": response.processing_time_seconds
            }
        else:
            raise HTTPException(status_code=400, detail=response.error_message)
            
    except Exception as e:
        logger.error(f"Article TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tts/stats")
async def get_tts_statistics():
    """TTS istatistiklerini al"""
    try:
        stats = tts_service.get_cost_statistics()
        audio_files = tts_service.list_audio_files()
        
        return {
            "success": True,
            "statistics": stats,
            "audio_files_count": len(audio_files),
            "recent_files": audio_files[:5]  # Son 5 dosya
        }
        
    except Exception as e:
        logger.error(f"TTS stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio/list")
async def list_audio_files():
    """Ses dosyalarını listele"""
    try:
        files = tts_service.list_audio_files()
        
        # URL'leri ekle
        for file_info in files:
            file_info['download_url'] = f"/audio/{file_info['filename']}"
        
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"Audio list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio/download/{filename}")
async def download_audio_file(filename: str):
    """Ses dosyasını indir"""
    try:
        file_path = Path(app_config.output_dir) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        logger.error(f"Audio download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple RSS + TTS endpoints  
@app.get("/api/simple-news/{category}")
async def get_simple_news(
    category: str,
    count: int = Query(10, ge=1, le=50),
    voice: str = Query("alloy"),
    generate_audio: bool = Query(True)
):
    """RSS haberleri + TTS ses oluşturma"""
    try:
        from services.rss_reader import RSSReader
        
        rss_reader = RSSReader(default_category=category)
        
        # RSS'den haberleri al
        if category == "mix":
            # Karışık kategoriler
            categories = ["guncel", "ekonomi", "spor", "teknoloji"]
            all_items = []
            
            for cat in categories:
                items = rss_reader.get_news_by_category(cat, count//len(categories) + 1)
                all_items.extend(items)
            
            import random
            random.shuffle(all_items)
            news_items = all_items[:count]
        else:
            # Tek kategori
            news_items = rss_reader.get_news_by_category(category, count)
        
        if not news_items:
            raise HTTPException(status_code=404, detail=f"'{category}' kategorisinde haber bulunamadı")
        
        # TTS için hazırla
        simple_news = []
        for i, item in enumerate(news_items):
            # TTS metni oluştur
            tts_text = f"Başlık: {item.title}"
            if item.summary:
                tts_text += f"\n\nÖzet: {item.summary}"
            
            audio_url = f"/audio/mock_{i}.mp3"  # Default mock
            
            # Gerçek TTS oluştur
            if generate_audio and tts_service:
                try:
                    from models.news_models import TTSRequest
                    
                    tts_request = TTSRequest(
                        text=tts_text,
                        voice=voice,
                        model="tts-1",
                        speed=1.0
                    )
                    
                    logger.info(f"TTS oluşturuluyor: {item.title[:50]}...")
                    tts_response = tts_service.text_to_speech(tts_request)
                    
                    if tts_response.success:
                        filename = Path(tts_response.audio_file_path).name
                        audio_url = f"/audio/{filename}"
                        logger.info(f"TTS başarılı: {filename}")
                    else:
                        logger.warning(f"TTS başarısız: {tts_response.error_message}")
                        
                except Exception as e:
                    logger.error(f"TTS hatası: {e}")
            
            # Cümlelere böl (subtitle için)
            sentences = []
            if item.title:
                sentences.append(f"Başlık: {item.title}")
            if item.summary:
                sentences.append(f"Özet: {item.summary}")
            
            # Subtitle timing
            subtitles = []
            current_time = 0
            for sentence in sentences:
                duration = max(3, len(sentence.split()) * 0.5)  # Kelime sayısına göre süre
                subtitles.append({
                    "start": round(current_time, 1),
                    "end": round(current_time + duration, 1),
                    "text": sentence
                })
                current_time += duration + 0.5
            
            simple_item = {
                "id": item.guid or f"news_{i}",
                "title": item.title,
                "summary": item.summary or item.description or "",
                "content": tts_text,  # TTS için kullanılan tam metin
                "category": category,
                "published": item.published,
                "url": item.link,
                "author": item.author,
                "character_count": len(tts_text),
                "images": [
                    f"https://picsum.photos/400/600?random={i + 1}",
                    f"https://picsum.photos/400/600?random={i + 10}"
                ],
                "main_image": f"https://picsum.photos/400/600?random={i + 1}",
                "audio_url": audio_url,
                "subtitles": subtitles,
                "estimated_duration": int(current_time),
                "tags": [category, "haber"],
                "location": "Türkiye"
            }
            simple_news.append(simple_item)
        
        return {
            "success": True,
            "category": category,
            "count": len(simple_news),
            "reels": simple_news,
            "audio_generated": generate_audio
        }
        
    except Exception as e:
        logger.error(f"Simple news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_endpoint():
    """Basit test endpoint"""
    return {
        "success": True,
        "message": "API çalışıyor",
        "timestamp": "2025-09-20",
        "status": "OK"
    }
async def get_news_reels(
    category: str,
    count: int = Query(10, ge=1, le=20),
    voice: str = Query("alloy"),
    model: str = Query("tts-1")
):
    """Instagram reels tarzı haber formatı"""
    try:
        # Kategori haberlerini al
        articles = news_service.get_latest_news(
            count=count,
            category=category,
            enable_scraping=True
        )
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"'{category}' kategorisinde haber bulunamadı")
        
        # Reels için uygun olanları filtrele
        suitable_articles = news_service.filter_articles(
            articles, 
            min_chars=300, 
            max_chars=2000,  # Reels için optimal uzunluk
            require_scraping=True
        )
        
        if not suitable_articles:
            raise HTTPException(status_code=404, detail="Reels için uygun haber bulunamadı")
        
        reels_data = []
        
        for article in suitable_articles:
            # TTS oluştur
            tts_response = tts_service.convert_article_to_speech(
                article=article,
                voice=voice,
                model=model
            )
            
            if tts_response.success:
                filename = Path(tts_response.audio_file_path).name
                
                # Metni cümlelere böl
                sentences = _split_into_sentences(article.get_content_for_tts())
                
                # Subtitle timing hesapla (tahmini)
                subtitles = _generate_subtitle_timing(sentences)
                
                reel_item = {
                    "id": article.rss_data.guid or f"reel_{len(reels_data)}",
                    "title": article.get_title(),
                    "content": article.get_content_for_tts(),
                    "summary": article.get_summary(),
                    "category": category,
                    "images": article.get_all_image_urls(),
                    "main_image": article.get_main_image_url(),
                    "audio_url": f"/audio/{filename}",
                    "audio_filename": filename,
                    "character_count": article.get_character_count(),
                    "estimated_duration": len(sentences) * 3,  # Tahmini 3 saniye/cümle
                    "subtitles": subtitles,
                    "tags": article.get_tags(),
                    "author": article.scraped_data.author if article.scraped_data else "",
                    "location": article.scraped_data.location if article.scraped_data else "",
                    "published": article.rss_data.published
                }
                
                reels_data.append(reel_item)
        
        return {
            "success": True,
            "category": category,
            "count": len(reels_data),
            "reels": reels_data
        }
        
    except Exception as e:
        logger.error(f"Reels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))







# Bu kodu api/main.py dosyasına ekle

import json
from datetime import datetime, timedelta
import os

# Yeni endpoint - Hazır gündem verilerini döner
@app.get("/api/agenda/ready")
async def get_ready_agenda(
    limit: int = Query(15, ge=1, le=50)
):
    """Önceden hazırlanmış gündem haberlerini döner (TTS dahil)"""
    try:
        # Gündem verilerini kaydettiğimiz dizin
        agenda_dir = Path("agenda_cache")
        agenda_dir.mkdir(exist_ok=True)
        
        # Son 24 saat içinde oluşturulan agenda dosyalarını ara
        cutoff_time = datetime.now() - timedelta(hours=24)
        agenda_files = []
        
        for file_path in agenda_dir.glob("agenda_data_*.json"):
            try:
                # Dosya adından tarihi çıkar: agenda_data_20250920_183045.json
                date_str = file_path.stem.split('_')[-2] + '_' + file_path.stem.split('_')[-1]
                file_time = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if file_time > cutoff_time:
                    agenda_files.append((file_time, file_path))
            except:
                continue
        
        if not agenda_files:
            # Güncel agenda bulunamadı
            return {
                "success": False,
                "error": "ready_agenda_not_found",
                "message": "Güncel gündem bulunamadı. Lütfen güncelleme yapın.",
                "reels": [],
                "last_updated": None,
                "update_command": "python main.py update-agenda --force"
            }
        
        # En yeni dosyayı al
        latest_file = max(agenda_files, key=lambda x: x[0])[1]
        
        # JSON dosyasını oku
        with open(latest_file, 'r', encoding='utf-8') as f:
            agenda_data = json.load(f)
        
        # Agenda items'ı al
        agenda_items = agenda_data.get('agenda_items', [])
        
        if not agenda_items:
            return {
                "success": False,
                "error": "empty_agenda",
                "message": "Gündem boş",
                "reels": []
            }
        
        # Limit uygula
        limited_items = agenda_items[:limit]
        
        # Her item için ses dosyası kontrolü
        validated_items = []
        
        for item in limited_items:
            # Ses dosyası var mı kontrol et
            audio_filename = item.get('audio_filename', '')
            if audio_filename:
                audio_path = Path(app_config.output_dir) / audio_filename
                
                if audio_path.exists():
                    # Ses dosyası mevcut, item'ı ekle
                    validated_items.append(item)
                else:
                    # Ses dosyası bulunamadı, logla ama item'ı yine de ekle (sessiz)
                    logger.warning(f"Ses dosyası bulunamadı: {audio_filename}")
                    item['audio_url'] = ""  # Ses URL'ini boşalt
                    item['has_audio'] = False
                    validated_items.append(item)
            else:
                # Ses dosyası bilgisi yok
                item['has_audio'] = False
                validated_items.append(item)
        
        # Response
        return {
            "success": True,
            "message": f"{len(validated_items)} gündem haberi hazır",
            "reels": validated_items,
            "total_available": len(agenda_items),
            "returned_count": len(validated_items),
            "last_updated": agenda_data.get('timestamp'),
            "processing_info": {
                "total_items": agenda_data.get('total_items'),
                "total_cost": agenda_data.get('total_cost'),
                "processing_time": agenda_data.get('processing_time')
            },
            "audio_status": {
                "with_audio": sum(1 for item in validated_items if item.get('audio_url')),
                "without_audio": sum(1 for item in validated_items if not item.get('audio_url'))
            }
        }
        
    except Exception as e:
        logger.error(f"Ready agenda error: {e}")
        return {
            "success": False,
            "error": "internal_error",
            "message": str(e),
            "reels": []
        }


@app.get("/api/agenda/status")
async def get_agenda_status():
    """Gündem durumunu kontrol et"""
    try:
        agenda_dir = Path("agenda_cache")
        
        if not agenda_dir.exists():
            return {
                "status": "no_agenda",
                "message": "Henüz gündem oluşturulmamış",
                "last_update": None,
                "files_count": 0
            }
        
        # Agenda dosyalarını listele
        agenda_files = list(agenda_dir.glob("agenda_data_*.json"))
        
        if not agenda_files:
            return {
                "status": "no_agenda", 
                "message": "Gündem dosyası bulunamadı",
                "last_update": None,
                "files_count": 0
            }
        
        # En yeni dosyayı bul
        newest_file = None
        newest_time = None
        
        for file_path in agenda_files:
            try:
                date_str = file_path.stem.split('_')[-2] + '_' + file_path.stem.split('_')[-1]
                file_time = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if newest_time is None or file_time > newest_time:
                    newest_time = file_time
                    newest_file = file_path
            except:
                continue
        
        if not newest_file:
            return {
                "status": "invalid_files",
                "message": "Geçerli gündem dosyası bulunamadı", 
                "files_count": len(agenda_files)
            }
        
        # Dosya yaşını kontrol et
        age_hours = (datetime.now() - newest_time).total_seconds() / 3600
        
        if age_hours > 24:
            status = "outdated"
            message = f"Gündem eski ({age_hours:.1f} saat önce)"
        elif age_hours > 6:
            status = "aging"
            message = f"Gündem yaşlanıyor ({age_hours:.1f} saat önce)"
        else:
            status = "fresh"
            message = f"Gündem güncel ({age_hours:.1f} saat önce)"
        
        # Dosya içeriğini kontrol et
        try:
            with open(newest_file, 'r', encoding='utf-8') as f:
                agenda_data = json.load(f)
            
            items_count = len(agenda_data.get('agenda_items', []))
            total_cost = agenda_data.get('total_cost', 0)
            
        except Exception as e:
            return {
                "status": "corrupt_file",
                "message": f"Gündem dosyası bozuk: {e}",
                "last_update": newest_time.isoformat(),
                "files_count": len(agenda_files)
            }
        
        return {
            "status": status,
            "message": message,
            "last_update": newest_time.isoformat(),
            "age_hours": round(age_hours, 1),
            "items_count": items_count,
            "total_cost": total_cost,
            "files_count": len(agenda_files),
            "filename": newest_file.name
        }
        
    except Exception as e:
        logger.error(f"Agenda status error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.delete("/api/agenda/clean")
async def clean_old_agenda():
    """Eski gündem dosyalarını temizle"""
    try:
        agenda_dir = Path("agenda_cache")
        
        if not agenda_dir.exists():
            return {
                "success": True,
                "message": "Temizlenecek dosya yok",
                "deleted_count": 0
            }
        
        # 48 saatten eski dosyaları sil
        cutoff_time = datetime.now() - timedelta(hours=48)
        deleted_count = 0
        
        for file_path in agenda_dir.glob("agenda_data_*.json"):
            try:
                date_str = file_path.stem.split('_')[-2] + '_' + file_path.stem.split('_')[-1]
                file_time = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
                
                if file_time < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
            except:
                continue
        
        return {
            "success": True,
            "message": f"{deleted_count} eski dosya silindi",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Clean agenda error: {e}")
        return {
            "success": False,
            "message": str(e)
        }

















@app.get("/api/reels/mix")
async def get_mixed_reels(
    count: int = Query(15, ge=5, le=30),
    categories: str = Query("guncel,ekonomi,spor,teknoloji"),
    voice: str = Query("alloy")
):
    """Karışık kategorilerden reel akışı"""
    try:
        category_list = [cat.strip() for cat in categories.split(",")]
        count_per_category = max(1, count // len(category_list))
        
        all_reels = []
        
        for category in category_list:
            try:
                # Her kategoriden az sayıda al
                articles = news_service.get_latest_news(
                    count=count_per_category + 2,  # Filtre için fazla al
                    category=category,
                    enable_scraping=True
                )
                
                if articles:
                    # Uygun olanları filtrele
                    suitable = news_service.filter_articles(
                        articles,
                        min_chars=200,
                        max_chars=1500,
                        require_scraping=True
                    )
                    
                    # En iyilerini seç
                    selected = suitable[:count_per_category]
                    
                    for article in selected:
                        tts_response = tts_service.convert_article_to_speech(
                            article=article,
                            voice=voice
                        )
                        
                        if tts_response.success:
                            filename = Path(tts_response.audio_file_path).name
                            sentences = _split_into_sentences(article.get_content_for_tts())
                            subtitles = _generate_subtitle_timing(sentences)
                            
                            reel_item = {
                                "id": f"{category}_{article.rss_data.guid or len(all_reels)}",
                                "title": article.get_title(),
                                "content": article.get_content_for_tts(),
                                "category": category,
                                "images": article.get_all_image_urls()[:5],  # Max 5 resim
                                "main_image": article.get_main_image_url(),
                                "audio_url": f"/audio/{filename}",
                                "subtitles": subtitles,
                                "estimated_duration": len(sentences) * 2.5,
                                "tags": article.get_tags()[:3]  # Max 3 tag
                            }
                            
                            all_reels.append(reel_item)
                            
            except Exception as e:
                logger.warning(f"Category {category} failed: {e}")
                continue
        
        # Karıştır (kategoriler arası)
        import random
        random.shuffle(all_reels)
        
        return {
            "success": True,
            "total_reels": len(all_reels),
            "categories": category_list,
            "reels": all_reels[:count]
        }
        
    except Exception as e:
        logger.error(f"Mixed reels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reels/trending")
async def get_trending_reels(
    count: int = Query(10, ge=5, le=20),
    voice: str = Query("nova")  # Trending için farklı ses
):
    """Trend olan haberlerden reels"""
    try:
        # Birden fazla kategoriden en popüler haberleri al
        trending_categories = ["guncel", "ekonomi", "teknoloji", "spor"]
        all_articles = []
        
        for category in trending_categories:
            articles = news_service.get_latest_news(
                count=5,
                category=category,
                enable_scraping=True
            )
            all_articles.extend(articles)
        
        # En çok resimli ve uzun olanları seç (trending criteria)
        scored_articles = []
        for article in all_articles:
            score = 0
            score += len(article.get_all_image_urls()) * 10  # Resim sayısı
            score += len(article.get_tags()) * 5  # Tag sayısı
            score += min(article.get_character_count() / 50, 20)  # Karakter
            
            if article.scraped_data and article.scraped_data.author:
                score += 15  # Yazarlı haberler
            
            scored_articles.append((score, article))
        
        # Skora göre sırala
        scored_articles.sort(reverse=True, key=lambda x: x[0])
        top_articles = [article for _, article in scored_articles[:count]]
        
        trending_reels = []
        
        for article in top_articles:
            tts_response = tts_service.convert_article_to_speech(
                article=article,
                voice=voice
            )
            
            if tts_response.success:
                filename = Path(tts_response.audio_file_path).name
                sentences = _split_into_sentences(article.get_content_for_tts())
                subtitles = _generate_subtitle_timing(sentences)
                
                trending_reel = {
                    "id": f"trending_{len(trending_reels)}",
                    "title": article.get_title(),
                    "content": article.get_content_for_tts(),
                    "category": article.rss_data.category,
                    "images": article.get_all_image_urls(),
                    "main_image": article.get_main_image_url(),
                    "audio_url": f"/audio/{filename}",
                    "subtitles": subtitles,
                    "estimated_duration": len(sentences) * 3,
                    "tags": article.get_tags(),
                    "is_trending": True,
                    "trend_score": scored_articles[trending_reels.__len__()][0]
                }
                
                trending_reels.append(trending_reel)
        
        return {
            "success": True,
            "count": len(trending_reels),
            "reels": trending_reels
        }
        
    except Exception as e:
        logger.error(f"Trending reels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _split_into_sentences(text: str) -> List[str]:
    """Metni cümlelere böl"""
    import re
    
    # Türkçe cümle sonları
    sentences = re.split(r'[.!?]+', text)
    
    # Temizle ve filtrele
    clean_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Çok kısa cümleleri atla
            clean_sentences.append(sentence)
    
    return clean_sentences


def _generate_subtitle_timing(sentences: List[str]) -> List[Dict]:
    """Cümleler için tahmini timing oluştur"""
    subtitles = []
    current_time = 0
    
    for sentence in sentences:
        # Cümle uzunluğuna göre süre hesapla
        word_count = len(sentence.split())
        duration = max(2, word_count * 0.4)  # ~2.5 kelime/saniye
        
        subtitles.append({
            "start": round(current_time, 1),
            "end": round(current_time + duration, 1),
            "text": sentence.strip()
        })
        
        current_time += duration + 0.3  # Cümleler arası kısa duraklama
    
    return subtitles
async def batch_news_to_tts(
    category: str = Query("guncel"),
    count: int = Query(5, ge=1, le=20),
    voice: str = Query("alloy"),
    model: str = Query("tts-1")
):
    """Toplu haber-TTS dönüştürme"""
    try:
        # Haberleri al
        articles = news_service.get_latest_news(
            count=count,
            category=category,
            enable_scraping=True
        )
        
        if not articles:
            raise HTTPException(status_code=404, detail="Haber bulunamadı")
        
        # Filtreleme
        filtered_articles = news_service.filter_articles(
            articles, min_chars=200, max_chars=8000, require_scraping=True
        )
        
        if not filtered_articles:
            raise HTTPException(status_code=400, detail="Filtre sonrası haber kalmadı")
        
        # TTS dönüştürme
        results = []
        total_cost = 0
        
        for article in filtered_articles:
            response = tts_service.convert_article_to_speech(
                article=article,
                voice=voice,
                model=model
            )
            
            if response.success:
                filename = Path(response.audio_file_path).name
                results.append({
                    "title": article.get_title(),
                    "audio_url": f"/audio/{filename}",
                    "filename": filename,
                    "character_count": response.character_count,
                    "estimated_cost": response.estimated_cost,
                    "success": True
                })
                total_cost += response.estimated_cost
            else:
                results.append({
                    "title": article.get_title(),
                    "error": response.error_message,
                    "success": False
                })
        
        successful_count = sum(1 for r in results if r.get('success'))
        
        return {
            "success": True,
            "category": category,
            "total_articles": len(filtered_articles),
            "successful_conversions": successful_count,
            "failed_conversions": len(filtered_articles) - successful_count,
            "total_estimated_cost": total_cost,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_local_ip():
    """Local ağ IP adresini al"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def main():
    """API serverını başlat"""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("📰 AA NEWS TTS API")
    print("=" * 60)
    print(f"Local IP: {local_ip}")
    print(f"Port: {app_config.api_port}")
    print(f"Scraping: {'Enabled' if app_config.enable_scraping else 'Disabled'}")
    print()
    print("API Endpoints:")
    print(f"  Documentation: http://{local_ip}:{app_config.api_port}/docs")
    print(f"  Health Check:  http://{local_ip}:{app_config.api_port}/health")
    print(f"  Latest News:   http://{local_ip}:{app_config.api_port}/api/news/latest")
    print(f"  TTS Convert:   http://{local_ip}:{app_config.api_port}/api/tts/convert")
    print(f"  Audio Files:   http://{local_ip}:{app_config.api_port}/audio/")
    print()
    print("Mobile Test URL:")
    print(f"  http://{local_ip}:{app_config.api_port}/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=app_config.api_host,
        port=app_config.api_port,
        log_level="info",
        reload=app_config.api_debug
    )


if __name__ == "__main__":
    main()