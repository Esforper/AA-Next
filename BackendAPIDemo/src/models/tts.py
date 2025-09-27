# ================================
# src/models/tts.py
# ================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseResponse

class TTSVoice(str, Enum):
    # OpenAI voices
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"
    
    # Yeni provider voice'ları buraya ekle
    # AZURE_JENNY = "azure_jenny"
    # ELEVENLABS_RACHEL = "elevenlabs_rachel"

class TTSModel(str, Enum):
    # OpenAI models
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    
    # Yeni provider modelleri buraya ekle

class TTSRequest(BaseModel):
    """TTS conversion request"""
    text: str = Field(..., min_length=1, max_length=50000)
    voice: str = TTSVoice.ALLOY
    model: str = TTSModel.TTS_1
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    output_format: str = "mp3"
    
    # Advanced options
    pitch: Optional[float] = None  # Provider-specific
    volume: Optional[float] = None  # Provider-specific
    
    # Additional options (provider-specific)
    options: Dict[str, Any] = {}

class SubtitleSegment(BaseModel):
    """Subtitle segment with timing"""
    start_time: float  # seconds
    end_time: float    # seconds
    text: str
    confidence: Optional[float] = None

class AudioResult(BaseModel):
    """TTS conversion result"""
    success: bool
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    
    # Cost tracking
    character_count: int = 0
    estimated_cost: float = 0.0
    processing_time_seconds: Optional[float] = None
    
    # Error info
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Subtitles/timestamps
    subtitles: List[SubtitleSegment] = []
    
    # Provider info
    provider: Optional[str] = None
    model_used: Optional[str] = None
    voice_used: Optional[str] = None

class TTSResponse(BaseResponse):
    """TTS API response"""
    result: AudioResult