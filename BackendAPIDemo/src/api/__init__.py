# ================================
# src/api/__init__.py - API Setup
# ================================

"""
FastAPI router setup
Tüm API endpoint'leri buradan toplanır
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import time

from ..config import settings

def create_app() -> FastAPI:
    """FastAPI app oluştur"""
    
    app = FastAPI(
        title="AA Universal API",
        description="News, TTS ve daha fazlası için universal API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS - development için
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Production'da kısıtla
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files - audio dosyaları için
    audio_path = Path(settings.storage_base_path)
    audio_path.mkdir(exist_ok=True)
    app.mount("/audio", StaticFiles(directory=audio_path), name="audio")
    
    # Request logging middleware (basit)
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"🌐 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response
    
    # Global error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"❌ Global error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error": str(exc) if settings.debug else "Server error"
            }
        )
    
    # Health check
    @app.get("/")
    async def root():
        return {
            "success": True,
            "message": "AA Universal API",
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "news": "/api/news/",
                "tts": "/api/tts/",
                "audio": "/audio/"
            }
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "success": True,
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "news": True,
                "tts": True,
                "storage": True
            }
        }
    
    return app