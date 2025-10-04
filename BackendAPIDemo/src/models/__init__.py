# ================================
# src/models/__init__.py - Updated Model Exports
# ================================

"""
Model exports - Yeni ReelFeedItem, NewsData ve diğer güncellenmiş modellerle
Tüm modellerin merkezi export noktası
"""

# Base models - her zaman gerekli
from .base import (
    BaseResponse,
    ErrorResponse,
    UniversalRequest,
    UniversalResponse,
    SystemInfo,
    HealthStatus
)

# News models - core sistem
from .news import (
    Article,
    ArticleStatus,
    NewsCategory,
    NewsResponse,
    NewsFilter
)

# TTS models - core sistem
from .tts import (
    TTSRequest,
    TTSResponse,
    AudioResult,
    TTSVoice,
    TTSModel,
    SubtitleSegment
)

# Storage models - core sistem
from .storage import (
    StorageFile,
    StorageProvider,
    FileType
)

# Realtime models - core sistem
from .realtime import (
    WebSocketMessage,
    ConnectionInfo,
    MessageType
)

from .user import (
    User, UserCreate, UserLogin, UserUpdate,
    UserResponse, UserPublicProfile,
    Token, TokenData,
    LoginResponse, RegisterResponse,
    UserRole, UserStatus
)


# Reels Tracking models - Updated with new models
try:
    from .reels_tracking import (
        # Core tracking
        ReelView,
        UserDailyStats,
        UserReelStats,
        ReelAnalytics,
        DailyProgress,
        
        # News data (yeni)
        NewsData,
        DetailViewEvent,
        
        # Feed models (güncellenmiş)
        ReelFeedItem,
        TrendingReels,
        
        # Response models (yeni)
        FeedResponse,
        FeedPagination,
        FeedMetadata,
        
        # Request/Response
        TrackViewRequest,
        TrackViewResponse,
        TrackDetailViewRequest,
        
        # Enums (güncellenmiş)
        ViewStatus,
        TrendPeriod,
        ReelStatus,  # Yeni enum
        EmojiType,
        
        # Utility
        TimeRange,
        StatsFilter
    )
    
    # Reels models successfully imported flag
    REELS_MODELS_AVAILABLE = True
    print("✅ Reels tracking models imported successfully")
    
except ImportError as e:
    print(f"⚠️ Reels tracking models import failed: {e}")
    
    # Fallback dummy models to prevent import errors
    class ReelView: pass
    class UserDailyStats: pass
    class UserReelStats: pass
    class ReelAnalytics: pass
    class DailyProgress: pass
    class NewsData: pass
    class ReelFeedItem: pass
    class TrendingReels: pass
    class FeedResponse: pass
    class FeedPagination: pass
    class FeedMetadata: pass
    class TrackViewRequest: pass
    class TrackViewResponse: pass
    class ViewStatus: pass
    class TrendPeriod: pass
    class ReelStatus: pass
    class TimeRange: pass
    class StatsFilter: pass
    
    REELS_MODELS_AVAILABLE = False

# Optional systems - sadece gerektiğinde import et
try:
    from .game import (
        Player,
        PlayerPosition,
        GameAction,
        GameState
    )
    GAME_MODELS_AVAILABLE = True
    print("✅ Game models imported")
except ImportError:
    # Game sistemi henüz eklenmemiş
    class Player: pass
    class PlayerPosition: pass
    class GameAction: pass
    class GameState: pass
    GAME_MODELS_AVAILABLE = False

try:
    from .ai_chat import (
        ChatMessage,
        ChatSession,
        ChatResponse
    )
    AI_CHAT_MODELS_AVAILABLE = True
    print("✅ AI Chat models imported")
except ImportError:
    # AI Chat sistemi henüz eklenmemiş
    class ChatMessage: pass
    class ChatSession: pass
    class ChatResponse: pass
    AI_CHAT_MODELS_AVAILABLE = False

# Validators
from .validators import (
    validate_provider_config,
    validate_file_type,
    validate_text_length
)

# ============ EXPORT ALL ============

__all__ = [
    # Base models
    "BaseResponse",
    "ErrorResponse", 
    "UniversalRequest",
    "UniversalResponse",
    "SystemInfo",
    "HealthStatus",
    
    # News models
    "Article",
    "ArticleStatus",
    "NewsCategory",
    "NewsResponse",
    "NewsFilter",
    
    # TTS models
    "TTSRequest",
    "TTSResponse",
    "AudioResult",
    "TTSVoice",
    "TTSModel",
    "SubtitleSegment",
    
    # Storage models
    "StorageFile",
    "StorageProvider",
    "FileType",
    
    # Realtime models
    "WebSocketMessage",
    "ConnectionInfo",
    "MessageType",
    
    # Reels models (Updated)
    "ReelView",
    "UserDailyStats",
    "UserReelStats", 
    "ReelAnalytics",
    "DailyProgress",
    "NewsData",               # Yeni
    "DetailViewEvent",
    "ReelFeedItem",           # Güncellenmiş
    "TrendingReels",
    "FeedResponse",           # Yeni
    "FeedPagination",         # Yeni
    "FeedMetadata",           # Yeni
    "TrackViewRequest",
    "TrackViewResponse",
     "TrackDetailViewRequest", # <-- YENİ EKLENDİ
    "ViewStatus",
    "TrendPeriod",
    "ReelStatus",             # Yeni
    "EmojiType",
    "TimeRange",
    "StatsFilter",
    
    # Game models (optional)
    "Player",
    "PlayerPosition", 
    "GameAction",
    "GameState",
    
    # AI Chat models (optional)
    "ChatMessage",
    "ChatSession",
    "ChatResponse",
    
    # Validators
    "validate_provider_config",
    "validate_file_type",
    "validate_text_length"
]

# ============ MODEL AVAILABILITY FLAGS ============

MODEL_AVAILABILITY = {
    "reels": REELS_MODELS_AVAILABLE,
    "game": GAME_MODELS_AVAILABLE, 
    "ai_chat": AI_CHAT_MODELS_AVAILABLE
}

def get_available_models():
    """Mevcut model gruplarını döndür"""
    return {
        system: available 
        for system, available in MODEL_AVAILABILITY.items() 
        if available
    }

def check_model_availability(model_name: str) -> bool:
    """Belirli bir modelin mevcut olup olmadığını kontrol et"""
    # Core models (her zaman mevcut)
    core_models = [
        "BaseResponse", "Article", "TTSRequest", "StorageFile", "WebSocketMessage"
    ]
    
    if model_name in core_models:
        return True
    
    # Reels models
    reels_models = [
        "ReelView", "ReelFeedItem", "FeedResponse", "NewsData", "ReelStatus"
    ]
    
    if model_name in reels_models:
        return REELS_MODELS_AVAILABLE
    
    # Game models
    game_models = ["Player", "GameAction", "GameState"]
    if model_name in game_models:
        return GAME_MODELS_AVAILABLE
    
    # AI Chat models
    chat_models = ["ChatMessage", "ChatSession"]
    if model_name in chat_models:
        return AI_CHAT_MODELS_AVAILABLE
    
    return False

# ============ UTILITY FUNCTIONS ============

def list_all_models():
    """Tüm mevcut modelleri listele"""
    available_models = []
    
    for model_name in __all__:
        if check_model_availability(model_name):
            available_models.append(model_name)
    
    return {
        "total_models": len(__all__),
        "available_models": len(available_models),
        "models": available_models,
        "system_availability": MODEL_AVAILABILITY
    }

def get_model_info():
    """Model sistemi hakkında bilgi al"""
    return {
        "total_exported": len(__all__),
        "reels_system": "✅ Available" if REELS_MODELS_AVAILABLE else "❌ Not Available",
        "game_system": "✅ Available" if GAME_MODELS_AVAILABLE else "❌ Not Available", 
        "ai_chat_system": "✅ Available" if AI_CHAT_MODELS_AVAILABLE else "❌ Not Available",
        "core_models": [
            "BaseResponse", "Article", "TTSRequest", "StorageFile", "WebSocketMessage"
        ],
        "new_models": [
            "NewsData", "FeedResponse", "FeedPagination", "FeedMetadata", "ReelStatus"
        ] if REELS_MODELS_AVAILABLE else []
    }

# Debug output
if __name__ == "__main__":
    print("\n🎯 Model System Status:")
    print("=" * 50)
    
    info = get_model_info()
    print(f"📊 Total exported models: {info['total_exported']}")
    print(f"🎬 Reels system: {info['reels_system']}")
    print(f"🎮 Game system: {info['game_system']}")
    print(f"🤖 AI Chat system: {info['ai_chat_system']}")
    
    if info['new_models']:
        print(f"\n🆕 New models available:")
        for model in info['new_models']:
            print(f"   - {model}")
    
    print(f"\n✅ Core models: {', '.join(info['core_models'])}")

# ============ YENİ SİSTEM EKLEME REHBERİ ============

"""
Yeni bir sistem eklemek için:

1. src/models/ altında yeni dosya oluştur (örn: ecommerce.py)
2. Yeni modelleri tanımla
3. Bu dosyaya import ve export ekle:
   
   try:
       from .ecommerce import (
           Product,
           Order,
           PaymentMethod
       )
       ECOMMERCE_MODELS_AVAILABLE = True
   except ImportError:
       class Product: pass
       class Order: pass 
       class PaymentMethod: pass
       ECOMMERCE_MODELS_AVAILABLE = False

4. __all__ listesine ekle:
   "Product", "Order", "PaymentMethod"

5. MODEL_AVAILABILITY dict'ine ekle:
   "ecommerce": ECOMMERCE_MODELS_AVAILABLE

6. check_model_availability fonksiyonuna ekle:
   ecommerce_models = ["Product", "Order", "PaymentMethod"]
   if model_name in ecommerce_models:
       return ECOMMERCE_MODELS_AVAILABLE

Bu şekilde yeni sistem modelleri otomatik olarak import edilir ve 
import hatası durumunda fallback sınıflar kullanılır.
"""