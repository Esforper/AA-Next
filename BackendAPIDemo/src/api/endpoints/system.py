# ================================
# src/api/endpoints/system.py - System API Endpoints
# ================================

"""
System management, health check, monitoring endpoints
Provider status, statistics ve debug bilgileri
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
import os
import psutil
from datetime import datetime

from ...config import settings
from ...providers import PROVIDERS, get_provider
from ...services.processing import processing_service
from ...models.base import BaseResponse, SystemInfo, HealthStatus

# Router oluştur
router = APIRouter(prefix="/api/system", tags=["system"])

# ============ HEALTH CHECK ENDPOINTS ============

@router.get("/health")
async def health_check():
    """
    Sistem sağlık kontrolü
    Tüm core servislerin durumunu kontrol eder
    """
    try:
        health_checks = {}
        overall_status = "healthy"
        
        # News provider check
        try:
            news_provider = get_provider(f"news_{settings.news_provider}")
            health_checks["news_provider"] = {
                "status": "healthy" if news_provider else "unavailable",
                "provider": settings.news_provider,
                "available": news_provider is not None
            }
            if not news_provider:
                overall_status = "degraded"
        except Exception as e:
            health_checks["news_provider"] = {
                "status": "error",
                "error": str(e)
            }
            overall_status = "degraded"
        
        # TTS provider check
        try:
            tts_provider = get_provider(f"tts_{settings.tts_provider}")
            health_checks["tts_provider"] = {
                "status": "healthy" if tts_provider else "unavailable",
                "provider": settings.tts_provider,
                "available": tts_provider is not None
            }
            if not tts_provider:
                overall_status = "degraded"
        except Exception as e:
            health_checks["tts_provider"] = {
                "status": "error", 
                "error": str(e)
            }
            overall_status = "degraded"
        
        # Storage check
        try:
            storage_path = Path(settings.storage_base_path)
            storage_exists = storage_path.exists()
            storage_writable = os.access(storage_path, os.W_OK) if storage_exists else False
            
            health_checks["storage"] = {
                "status": "healthy" if (storage_exists and storage_writable) else "error",
                "path": str(storage_path),
                "exists": storage_exists,
                "writable": storage_writable
            }
            
            if not (storage_exists and storage_writable):
                overall_status = "unhealthy"
                
        except Exception as e:
            health_checks["storage"] = {
                "status": "error",
                "error": str(e)
            }
            overall_status = "unhealthy"
        
        # API Keys check (without exposing values)
        api_key_checks = {
            "openai": bool(settings.openai_api_key),
        }
        
        health_checks["api_keys"] = {
            "status": "healthy" if any(api_key_checks.values()) else "warning",
            "configured": api_key_checks
        }
        
        return {
            "success": True,
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time(),
            "checks": health_checks,
            "version": settings.version
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/status")
async def get_system_status():
    """
    Detaylı sistem durumu
    """
    try:
        # System info
        system_info = {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "debug_mode": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
        
        # Memory ve CPU (eğer psutil varsa)
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            system_info.update({
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent
            })
        except:
            system_info["performance"] = "metrics_unavailable"
        
        # Provider status
        provider_status = {}
        for provider_type, providers in PROVIDERS.items():
            provider_status[provider_type] = {
                "available": list(providers.keys()),
                "count": len(providers)
            }
        
        # Storage info
        storage_info = {}
        try:
            storage_path = Path(settings.storage_base_path)
            if storage_path.exists():
                files = list(storage_path.glob("*"))
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                storage_info = {
                    "path": str(storage_path),
                    "total_files": len([f for f in files if f.is_file()]),
                    "total_size_mb": round(total_size / (1024*1024), 2),
                    "audio_files": len(list(storage_path.glob("*.mp3")))
                }
        except Exception as e:
            storage_info = {"error": str(e)}
        
        return {
            "success": True,
            "system": system_info,
            "providers": provider_status,
            "storage": storage_info,
            "config": {
                "news_provider": settings.news_provider,
                "tts_provider": settings.tts_provider,
                "storage_provider": settings.storage_provider,
                "websocket_enabled": settings.websocket_enabled
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

# ============ PROVIDER MANAGEMENT ============

@router.get("/providers")
async def list_providers(
    provider_type: Optional[str] = Query(None, description="Filter by provider type")
):
    """
    Mevcut provider'ları listele
    """
    try:
        if provider_type:
            # Specific provider type
            if provider_type in PROVIDERS:
                providers = {provider_type: PROVIDERS[provider_type]}
            else:
                raise HTTPException(status_code=404, detail=f"Provider type '{provider_type}' not found")
        else:
            # All providers
            providers = PROVIDERS
        
        # Provider details
        provider_details = {}
        for ptype, provider_dict in providers.items():
            provider_details[ptype] = {
                "available": list(provider_dict.keys()),
                "count": len(provider_dict),
                "active": True if provider_dict else False
            }
        
        return {
            "success": True,
            "providers": provider_details,
            "total_types": len(provider_details),
            "filter_applied": provider_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider list error: {str(e)}")

@router.get("/providers/{provider_name}/test")
async def test_provider(provider_name: str):
    """
    Belirli bir provider'ı test et
    """
    try:
        provider = get_provider(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
        
        test_results = {
            "provider": provider_name,
            "available": True,
            "functions": list(provider.keys()),
            "test_time": datetime.now().isoformat()
        }
        
        # Provider type'a göre basit test
        if "news_" in provider_name:
            # News provider test
            try:
                # Basit test - 1 makale al
                articles = await provider["get_latest_news"](count=1, category="guncel")
                test_results["test_result"] = {
                    "status": "success",
                    "articles_fetched": len(articles),
                    "first_article_title": articles[0].title if articles else None
                }
            except Exception as e:
                test_results["test_result"] = {
                    "status": "error",
                    "error": str(e)
                }
                
        elif "tts_" in provider_name:
            # TTS provider test (sadece function check, actual conversion yapmıyoruz)
            test_results["test_result"] = {
                "status": "available",
                "note": "TTS provider available but not tested (would incur cost)"
            }
        
        return {
            "success": True,
            "test": test_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider test error: {str(e)}")

# ============ STATISTICS & MONITORING ============

@router.get("/stats")
async def get_system_statistics():
    """
    Sistem istatistikleri
    """
    try:
        stats = {}
        
        # TTS stats
        try:
            tts_stats = await processing_service.get_tts_stats()
            stats["tts"] = tts_stats
        except Exception as e:
            stats["tts"] = {"error": str(e)}
        
        # File stats
        try:
            audio_files = await processing_service.list_audio_files()
            stats["files"] = {
                "total_audio_files": len(audio_files),
                "total_size_mb": sum(f.get("size_mb", 0) for f in audio_files)
            }
        except Exception as e:
            stats["files"] = {"error": str(e)}
        
        # Provider stats
        stats["providers"] = {
            "total_types": len(PROVIDERS),
            "total_providers": sum(len(providers) for providers in PROVIDERS.values()),
            "by_type": {ptype: len(providers) for ptype, providers in PROVIDERS.items()}
        }
        
        return {
            "success": True,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

# ============ CONFIGURATION ============

@router.get("/config")
async def get_system_config():
    """
    Sistem konfigürasyonu (güvenli bilgiler)
    """
    try:
        # Güvenli config bilgileri (API key'ler vs dahil değil)
        safe_config = {
            "app": {
                "name": settings.app_name,
                "version": settings.version,
                "debug": settings.debug,
                "host": settings.host,
                "port": settings.port
            },
            "news": {
                "provider": settings.news_provider,
                "default_category": settings.news_default_category,
                "max_articles": settings.news_max_articles,
                "scraping_enabled": settings.news_scraping_enabled
            },
            "tts": {
                "provider": settings.tts_provider,
                "voice": settings.tts_voice,
                "model": settings.tts_model,
                "speed": settings.tts_speed
            },
            "storage": {
                "provider": settings.storage_provider,
                "base_path": settings.storage_base_path
            },
            "features": {
                "websocket_enabled": settings.websocket_enabled,
                "game_enabled": getattr(settings, 'game_enabled', False),
                "ai_chat_enabled": getattr(settings, 'ai_chat_enabled', False)
            }
        }
        
        return {
            "success": True,
            "config": safe_config,
            "note": "Sensitive information (API keys) not included"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config error: {str(e)}")

# ============ LOGS & DEBUG ============

@router.get("/logs")
async def get_recent_logs(
    lines: int = Query(50, ge=1, le=1000, description="Number of log lines"),
    level: Optional[str] = Query(None, description="Log level filter")
):
    """
    Son log kayıtları (eğer log file varsa)
    """
    try:
        if not settings.log_file:
            return {
                "success": False,
                "message": "Log file not configured",
                "logs": []
            }
        
        log_path = Path(settings.log_file)
        if not log_path.exists():
            return {
                "success": False,
                "message": "Log file not found",
                "logs": []
            }
        
        # Son N satırı oku
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Level filter (basit)
        if level:
            filtered_lines = [line for line in recent_lines if level.upper() in line]
            recent_lines = filtered_lines
        
        return {
            "success": True,
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(recent_lines),
            "log_file": str(log_path),
            "filter_applied": level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logs error: {str(e)}")

# ============ UTILITY ENDPOINTS ============

@router.post("/cleanup")
async def cleanup_system(
    cleanup_type: str = Query("temp", description="Cleanup type: temp, logs, audio")
):
    """
    Sistem temizliği
    """
    try:
        cleaned_items = []
        
        if cleanup_type == "temp" or cleanup_type == "all":
            # Geçici dosyaları temizle
            storage_path = Path(settings.storage_base_path)
            if storage_path.exists():
                temp_files = list(storage_path.glob("temp_*"))
                for temp_file in temp_files:
                    temp_file.unlink()
                    cleaned_items.append(f"temp file: {temp_file.name}")
        
        if cleanup_type == "audio" or cleanup_type == "all":
            # Eski audio dosyalarını temizle (1 hafta+)
            from datetime import timedelta
            storage_path = Path(settings.storage_base_path)
            if storage_path.exists():
                cutoff_time = time.time() - timedelta(days=7).total_seconds()
                for audio_file in storage_path.glob("*.mp3"):
                    if audio_file.stat().st_mtime < cutoff_time:
                        audio_file.unlink()
                        cleaned_items.append(f"old audio: {audio_file.name}")
        
        return {
            "success": True,
            "message": f"Cleanup completed: {cleanup_type}",
            "cleaned_items": cleaned_items,
            "total_cleaned": len(cleaned_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")

@router.get("/version")
async def get_version_info():
    """
    Versiyon bilgileri
    """
    return {
        "success": True,
        "version": settings.version,
        "app_name": settings.app_name,
        "api_version": "1.0.0",
        "build_time": datetime.now().isoformat(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
    }