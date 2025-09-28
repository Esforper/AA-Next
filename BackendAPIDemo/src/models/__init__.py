# Base models - her zaman gerekli
from .base import (
    BaseResponse,
    ErrorResponse,
    UniversalRequest,
    UniversalResponse
)

# News models - core sistem
from .news import (
    Article,
    ArticleStatus,
    NewsResponse
)

# TTS models - core sistem
from .tts import (
    TTSRequest,
    AudioResult
)

# Storage models - core sistem
from .storage import (
    StorageFile
)

# Realtime models - core sistem
from .realtime import (
    WebSocketMessage
)

# from .reels_tracking import (
#     ReelView, UserDailyStats, UserReelStats, ReelAnalytics,
#     DailyProgress, ReelFeedItem, TrendingReels, TrendPeriod,
#     TrackViewRequest, TrackViewResponse, ViewStatus
# )

try:
    from .reels_tracking import (
        ReelView, UserDailyStats, UserReelStats, ReelAnalytics,
        DailyProgress, ReelFeedItem, TrendingReels, TrendPeriod,
        TrackViewRequest, TrackViewResponse, ViewStatus
    )
except ImportError as e:
    print(f"⚠️ Reels tracking models import failed: {e}")

# Optional systems - sadece gerektiğinde import et
try:
    from .game import (
        Player,
        PlayerPosition,
        GameAction,
        GameState
    )
except ImportError:
    # Game sistemi henüz eklenmemiş
    pass

try:
    from .ai_chat import (
        ChatMessage
    )
except ImportError:
    # AI Chat sistemi henüz eklenmemiş
    pass

# Validators
from .validators import validate_provider_config

# Export all
__all__ = [
    # Base
    "BaseResponse",
    "ErrorResponse", 
    "UniversalRequest",
    "UniversalResponse",
    
    # News
    "Article",
    "ArticleStatus",
    "NewsResponse",
    
    # TTS
    "TTSRequest",
    "AudioResult",
    
    # Storage
    "StorageFile",
    
    # Realtime
    "WebSocketMessage",
    
    # Game (optional)
    "Player",
    "PlayerPosition", 
    "GameAction",
    "GameState",
    
    # AI Chat (optional)
    "ChatMessage",
    
    # Utils
    "validate_provider_config"
]
