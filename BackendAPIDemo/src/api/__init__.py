# ================================
# src/api/__init__.py - API Setup
# ================================

"""
FastAPI app factory ve router management
Basit ve genişletilebilir yapı
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
        description="News, TTS ve daha fazlası için universal API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Middleware'leri ekle
    _setup_middleware(app)
    
    # Static file serving
    _setup_static_files(app)
    
    # Core endpoints (her zaman dahil)
    _register_core_routes(app)
    
    # Router'ları dahil et
    _register_routers(app)
    
    # Error handlers
    _setup_error_handlers(app)
    
    return app

def _setup_middleware(app: FastAPI):
    """Middleware'leri yapılandır"""
    
    # CORS - development için açık, production'da kısıtla
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
        
        # Sadece debug modunda log
        if settings.debug:
            print(f"🌐 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response

def _setup_static_files(app: FastAPI):
    """Static file serving setup"""
    
    # Audio dosyaları için static serving
    audio_path = Path(settings.storage_base_path)
    audio_path.mkdir(parents=True, exist_ok=True)
    
    app.mount("/audio", StaticFiles(directory=audio_path), name="audio")

def _register_core_routes(app: FastAPI):
    """Core system routes (health, info vb.)"""
    
    @app.get("/")
    async def root():
        """API ana bilgileri"""
        return {
            "success": True,
            "message": "AA Universal API",
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "news": "/api/news/",
                "tts": "/api/tts/",
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
                "news": True,
                "tts": True,
                "storage": True,
                "websocket": settings.websocket_enabled
            }
        }

def _register_routers(app: FastAPI):
    """
    Router'ları dahil et
    Yeni sistem eklemek için buraya yeni import ekle
    """
    # Diğer import'lardan sonra ekle:
    # Diğer router'lardan sonra ekle:
    try:
        from .endpoints.reels_mockup import router as reels_mockup_router
        app.include_router(reels_mockup_router)
        print("✅ Reels Mockup router registered")
    except ImportError as e:
        print(f"⚠️  Reels Mockup router import failed: {e}")
        
        
    try:
        from .endpoints.reels import router as reels_router
        app.include_router(reels_router)
        print("✅ Reels router registered")
    except ImportError as e:
        print(f"⚠️  Reels Mockup router import failed: {e}")
        
    # Core routers - her zaman dahil
    try:
        from .endpoints.news import router as news_router
        app.include_router(news_router)
        print("✅ News router registered")
    except ImportError as e:
        print(f"⚠️  News router import failed: {e}")
    
    try:
        from .endpoints.tts import router as tts_router
        app.include_router(tts_router)
        print("✅ TTS router registered")
    except ImportError as e:
        print(f"⚠️  TTS router import failed: {e}")
    
    try:
        from .endpoints.system import router as system_router
        app.include_router(system_router)
        print("✅ System router registered")
    except ImportError as e:
        print(f"⚠️  System router import failed: {e}")
    
    

    
    
    # Optional routers - config'e göre dahil et
    if settings.websocket_enabled:
        try:
            from .endpoints.websocket import router as websocket_router
            app.include_router(websocket_router)
            print("✅ WebSocket router registered")
        except ImportError:
            print("⚠️  WebSocket router not available")
    
    # Gelecekte eklenecek sistemler için:
    # if settings.game_enabled:
    #     try:
    #         from .endpoints.game import router as game_router
    #         app.include_router(game_router)
    #         print("✅ Game router registered")
    #     except ImportError:
    #         print("⚠️  Game router not available")
    #
    # if settings.ai_chat_enabled:
    #     try:
    #         from .endpoints.chat import router as chat_router
    #         app.include_router(chat_router)
    #         print("✅ Chat router registered")
    #     except ImportError:
    #         print("⚠️  Chat router not available")

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
                    "/docs", "/health", "/api/news/", "/api/tts/", "/api/system/"
                ]
            }
        )

# Convenience functions
def get_app() -> FastAPI:
    """App instance'ını al (testing için)"""
    return create_app()

# Export
__all__ = ["create_app", "get_app"]