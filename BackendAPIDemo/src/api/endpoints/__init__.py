# backend/src/api/endpoints/__init__.py

"""
API endpoint router'larını toplar ve export eder
Yeni router eklemek için buraya import ekle
"""

# ============ CORE ROUTERS ============

# Auth router
try:
    from .auth import router as auth_router
    print("✅ Auth router imported")
except ImportError as e:
    print(f"⚠️ Auth router import failed: {e}")
    auth_router = None

# News router
try:
    from .news import router as news_router
    print("✅ News router imported")
except ImportError as e:
    print(f"⚠️ News router import failed: {e}")
    news_router = None

# TTS router
try:
    from .tts import router as tts_router
    print("✅ TTS router imported")
except ImportError as e:
    print(f"⚠️ TTS router import failed: {e}")
    tts_router = None

# System router
try:
    from .system import router as system_router
    print("✅ System router imported")
except ImportError as e:
    print(f"⚠️ System router import failed: {e}")
    system_router = None


# ============ REELS ROUTERS (MODÜLER) ============

# Reels Tracking (track-view, track-detail-view)
try:
    from .reels_tracking import router as reels_tracking_router
    print("✅ Reels Tracking router imported")
except ImportError as e:
    print(f"⚠️ Reels Tracking router import failed: {e}")
    reels_tracking_router = None

# Reels Feed (feed, trending, latest)
try:
    from .reels_feed import router as reels_feed_router
    print("✅ Reels Feed router imported")
except ImportError as e:
    print(f"⚠️ Reels Feed router import failed: {e}")
    reels_feed_router = None

# Reels User (stats, progress, watched, session)
try:
    from .reels_user import router as reels_user_router
    print("✅ Reels User router imported")
except ImportError as e:
    print(f"⚠️ Reels User router import failed: {e}")
    reels_user_router = None

# Reels Analytics (analytics, overview, system/status)
try:
    from .reels_analytics import router as reels_analytics_router
    print("✅ Reels Analytics router imported")
except ImportError as e:
    print(f"⚠️ Reels Analytics router import failed: {e}")
    reels_analytics_router = None

# Reels Management (bulk-create, mark-seen, get-by-id)
try:
    from .reels_management import router as reels_management_router
    print("✅ Reels Management router imported")
except ImportError as e:
    print(f"⚠️ Reels Management router import failed: {e}")
    reels_management_router = None


# ============ OPTIONAL ROUTERS ============

# Game router
try:
    from .game import router as game_router
    print("✅ Game router imported")
except ImportError as e:
    print(f"⚠️ Game router import failed: {e}")
    game_router = None

# WebSocket router
try:
    from .websocket import router as websocket_router
    print("✅ WebSocket router imported")
except ImportError as e:
    print(f"⚠️ WebSocket router import failed: {e}")
    websocket_router = None

# Chat router
try:
    from .chat import router as chat_router
    print("✅ Chat router imported")
except ImportError as e:
    print(f"⚠️ Chat router import failed: {e}")
    chat_router = None


# ============ ROUTER REGISTRY ============

AVAILABLE_ROUTERS = {
    "auth": auth_router,
    "news": news_router,
    "tts": tts_router,
    "system": system_router,
    
    # Reels modüler router'ları
    "reels_tracking": reels_tracking_router,
    "reels_feed": reels_feed_router,
    "reels_user": reels_user_router,
    "reels_analytics": reels_analytics_router,
    "reels_management": reels_management_router,
    
    # Optional
    "game": game_router,
    "websocket": websocket_router,
    "chat": chat_router,
}

# Sadece mevcut olan router'ları export et
ACTIVE_ROUTERS = {
    name: router for name, router in AVAILABLE_ROUTERS.items() 
    if router is not None
}


# ============ UTILITY FUNCTIONS ============

def get_router(name: str):
    """Belirli bir router'ı al"""
    return AVAILABLE_ROUTERS.get(name)


def get_active_routers():
    """Aktif router'ların listesini al"""
    return ACTIVE_ROUTERS


def list_available_routers():
    """Mevcut router'ları listele"""
    return list(ACTIVE_ROUTERS.keys())


# ============ EXPORTS ============

__all__ = [
    # Core routers
    "auth_router",
    "news_router",
    "tts_router",
    "system_router",
    
    # Reels modüler routers
    "reels_tracking_router",
    "reels_feed_router",
    "reels_user_router",
    "reels_analytics_router",
    "reels_management_router",
    
    # Optional routers
    "game_router",
    "websocket_router",
    "chat_router",
    
    # Utility functions
    "get_router",
    "get_active_routers",
    "list_available_routers",
    
    # Registry
    "AVAILABLE_ROUTERS",
    "ACTIVE_ROUTERS"
]