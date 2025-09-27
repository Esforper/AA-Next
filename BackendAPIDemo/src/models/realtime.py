# ================================
# src/models/realtime.py
# ================================

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    # News events
    NEWS_UPDATE = "news_update"
    ARTICLE_PUBLISHED = "article_published"
    
    # TTS events  
    TTS_STARTED = "tts_started"
    TTS_COMPLETED = "tts_completed"
    TTS_FAILED = "tts_failed"
    
    # Game events (optional)
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_STATE_UPDATE = "game_state_update"
    
    # Chat events (optional)
    CHAT_MESSAGE = "chat_message"
    USER_TYPING = "user_typing"
    
    # System events
    SYSTEM_NOTIFICATION = "system_notification"
    CONNECTION_STATUS = "connection_status"
    
    # Yeni event tipi eklemek için buraya ekle

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Optional fields
    sender_id: Optional[str] = None
    room_id: Optional[str] = None
    broadcast: bool = False
    
    # Message metadata
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
class ConnectionInfo(BaseModel):
    """WebSocket connection info"""
    connection_id: str
    user_id: Optional[str] = None
    room_ids: List[str] = []
    connected_at: datetime = Field(default_factory=datetime.now)
    last_ping: Optional[datetime] = None
    
    # Connection metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = {}
