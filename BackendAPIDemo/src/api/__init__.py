# backend/src/api/__init__.py

"""
FastAPI app factory ve router management
Modüler ve genişletilebilir yapı
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import time

from ..config import settings


def create_app() -> FastAPI:
    """
    FastAPI app oluştur ve yapılandır
    Tüm router'ları otomatik olarak dahil et
    """
    
    app = FastAPI(
        title="AA Universal API",
        description="News, TTS, Reels ve daha fazlası için universal API",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Middleware'leri ekle
    _setup_middleware(app)
    
    # Static file serving
    _setup_static_files(app)
    
    # Core endpoints
    _register_core_routes(app)
    
    # Router'ları dahil et
    _register_routers(app)
    
    # Error handlers
    _setup_error_handlers(app)
    
    return app


def _setup_middleware(app: FastAPI):
    """Middleware'leri yapılandır"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        if settings.debug:
            print(f"🌐 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response


def _setup_static_files(app: FastAPI):
    """Static file serving setup"""
    
    # Audio dosyaları için path
    audio_path = Path(settings.storage_base_path) / "reels_data" / "audio"
    audio_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Audio files serving from: {audio_path.absolute()}")
    
    # Static mount
    try:
        app.mount("/audio", StaticFiles(directory=str(audio_path)), name="audio")
        print("✅ Audio static files mounted successfully!")
    except Exception as e:
        print(f"❌ Failed to mount audio files: {e}")


def _register_core_routes(app: FastAPI):
    """Core system routes"""
    
    @app.get("/")
    async def root():
        """API ana bilgileri"""
        return {
            "success": True,
            "message": "AA Universal API v2.0",
            "version": "2.0.0",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "auth": "/api/auth/",
                "news": "/api/news/",
                "tts": "/api/tts/",
                "reels": "/api/reels/",
                "audio": "/audio/",
                "system": "/api/system/"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "success": True,
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "auth": True,
                "news": True,
                "tts": True,
                "reels": True,
                "storage": True
            }
        }


def _register_routers(app: FastAPI):
    """
    Router'ları dahil et
    Modüler reels yapısı ile
    """
    
    # Auth router
    try:
        from .endpoints.auth import router as auth_router
        app.include_router(auth_router)
        print("✅ Auth router registered")
    except ImportError as e:
        print(f"⚠️ Auth router import failed: {e}")
    
    # News router
    try:
        from .endpoints.news import router as news_router
        app.include_router(news_router)
        print("✅ News router registered")
    except ImportError as e:
        print(f"⚠️ News router import failed: {e}")
    
    # TTS router
    try:
        from .endpoints.tts import router as tts_router
        app.include_router(tts_router)
        print("✅ TTS router registered")
    except ImportError as e:
        print(f"⚠️ TTS router import failed: {e}")
    
    # System router
    try:
        from .endpoints.system import router as system_router
        app.include_router(system_router)
        print("✅ System router registered")
    except ImportError as e:
        print(f"⚠️ System router import failed: {e}")
    
    # ============ REELS MODÜLER ROUTERS ============
    
    # Reels Tracking
    try:
        from .endpoints.reels_tracking import router as reels_tracking_router
        app.include_router(reels_tracking_router)
        print("✅ Reels Tracking router registered")
    except ImportError as e:
        print(f"⚠️ Reels Tracking router import failed: {e}")
    
    # Reels Feed
    try:
        from .endpoints.reels_feed import router as reels_feed_router
        app.include_router(reels_feed_router)
        print("✅ Reels Feed router registered")
    except ImportError as e:
        print(f"⚠️ Reels Feed router import failed: {e}")
    
    # Reels User
    try:
        from .endpoints.reels_user import router as reels_user_router
        app.include_router(reels_user_router)
        print("✅ Reels User router registered")
    except ImportError as e:
        print(f"⚠️ Reels User router import failed: {e}")
    
    # Reels Analytics
    try:
        from .endpoints.reels_analytics import router as reels_analytics_router
        app.include_router(reels_analytics_router)
        print("✅ Reels Analytics router registered")
    except ImportError as e:
        print(f"⚠️ Reels Analytics router import failed: {e}")
    
    # Reels Management
    try:
        from .endpoints.reels_management import router as reels_management_router
        app.include_router(reels_management_router)
        print("✅ Reels Management router registered")
    except ImportError as e:
        print(f"⚠️ Reels Management router import failed: {e}")
    
    # ============ OPTIONAL ROUTERS ============
    
    # Game router
    try:
        from .endpoints.game import router as game_router
        app.include_router(game_router)
        print("✅ Game router registered")
    except ImportError as e:
        print(f"⚠️ Game router import failed: {e}")


def _setup_error_handlers(app: FastAPI):
    """Global error handler'ları setup et"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        
        error_msg = str(exc) if settings.debug else "Internal server error"
        
        print(f"❌ Global error on {request.url.path}: {exc}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error": error_msg,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """404 handler"""
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Endpoint not found",
                "path": str(request.url.path),
                "available_endpoints": [
                    "/docs", "/health", "/api/auth/", "/api/news/", 
                    "/api/tts/", "/api/reels/", "/api/system/"
                ]
            }
        )


# Convenience functions
def get_app() -> FastAPI:
    """App instance'ını al (testing için)"""
    return create_app()


# Export
__all__ = ["create_app", "get_app"]