# ================================
# src/models/base.py
# ================================

from pydantic import BaseModel, Field
from typing import Dict, Any, Union, Optional, List
from datetime import datetime
from enum import Enum

class BaseResponse(BaseModel):
    """Tüm API response'lar için base model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class SystemInfo(BaseModel):
    """System information model"""
    name: str
    version: str
    status: HealthStatus
    uptime_seconds: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

class UniversalRequest(BaseModel):
    """Generic request model for any system"""
    system: str  # news, tts, game, ai_chat vb
    action: str  # get, create, update, delete vb
    payload: Dict[str, Any]
    options: Dict[str, Any] = {}

class UniversalResponse(BaseResponse):
    """Generic response model"""
    system: str
    action: str
    data: Union[Dict[str, Any], List[Dict[str, Any]], None] = None