# ================================
# src/api/endpoints/__init__.py - Router Export Management
# ================================

"""
API endpoint router'larını toplar ve export eder
Yeni router eklemek için buraya import ekle
"""

# Core routers - her zaman mevcut olması gereken
try:
    from .news import router as news_router
except ImportError:
    print("⚠️  News router import failed")
    news_router = None

try:
    from .tts import router as tts_router
except ImportError:
    print("⚠️  TTS router import failed") 
    tts_router = None

try:
    from .system import router as system_router
except ImportError:
    print("⚠️  System router import failed")
    system_router = None

# Optional routers - config'e göre enable/disable edilebilir
try:
    from .websocket import router as websocket_router
except ImportError:
    websocket_router = None

# Gelecekte eklenecek optional sistemler
try:
    from .game import router as game_router
except ImportError:
    game_router = None

try:
    from .chat import router as chat_router
except ImportError:
    chat_router = None

try:
    from .crypto import router as crypto_router
except ImportError:
    crypto_router = None

try:
    from .video import router as video_router
except ImportError:
    video_router = None

# Router registry - dinamik erişim için
AVAILABLE_ROUTERS = {
    "news": news_router,
    "tts": tts_router,
    "system": system_router,
    "websocket": websocket_router,
    "game": game_router,
    "chat": chat_router,
    "crypto": crypto_router,
    "video": video_router,
}

# Sadece mevcut olan router'ları export et
ACTIVE_ROUTERS = {
    name: router for name, router in AVAILABLE_ROUTERS.items() 
    if router is not None
}

def get_router(name: str):
    """Belirli bir router'ı al"""
    return AVAILABLE_ROUTERS.get(name)

def get_active_routers():
    """Aktif router'ların listesini al"""
    return ACTIVE_ROUTERS

def list_available_routers():
    """Mevcut router'ları listele"""
    return list(ACTIVE_ROUTERS.keys())

# Direct exports (backward compatibility için)
__all__ = [
    # Router instances
    "news_router",
    "tts_router", 
    "system_router",
    "websocket_router",
    "game_router",
    "chat_router",
    "crypto_router",
    "video_router",
    
    # Utility functions
    "get_router",
    "get_active_routers", 
    "list_available_routers",
    
    # Registry
    "AVAILABLE_ROUTERS",
    "ACTIVE_ROUTERS"
]

# Yeni router eklemek için:
# 1. Yukarıya import ekle:
#    try:
#        from .yeni_sistem import router as yeni_sistem_router
#    except ImportError:
#        yeni_sistem_router = None
#
# 2. AVAILABLE_ROUTERS'a ekle:
#    "yeni_sistem": yeni_sistem_router,
#
# 3. __all__'a ekle:
#    "yeni_sistem_router",