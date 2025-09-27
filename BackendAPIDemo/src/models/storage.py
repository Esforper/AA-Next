# ================================
# src/models/storage.py
# ================================

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StorageProvider(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCP = "gcp"
    # Yeni storage provider ekle

class FileType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image" 
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"

class StorageFile(BaseModel):
    """File storage model"""
    file_id: str
    original_name: str
    stored_path: str
    file_size: int
    mime_type: str
    file_type: FileType
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.now)
    accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Access control
    public: bool = False
    owner_id: Optional[str] = None
    permissions: List[str] = []
    
    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Storage info
    provider: Optional[str] = None
    bucket: Optional[str] = None
    region: Optional[str] = None