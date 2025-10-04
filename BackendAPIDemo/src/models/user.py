# ================================
# src/models/user.py - User Models
# ================================

"""
User authentication ve management için basit modeller
Minimal ama güvenli yaklaşım
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# ============ ENUMS ============

class UserRole(str, Enum):
    """Kullanıcı rolleri - basit yapı"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserStatus(str, Enum):
    """Kullanıcı durumu"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING = "pending"

# ============ BASE USER MODEL ============

class User(BaseModel):
    """
    Ana User modeli - Database'de tutulan
    """
    id: str = Field(..., description="Unique user ID (UUID)")
    email: EmailStr = Field(..., description="User email (unique)")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    hashed_password: str = Field(..., description="Bcrypt hashed password")

    # Profile bilgileri
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")

    # System bilgileri
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Account status")
    is_verified: bool = Field(default=False, description="Email verified")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    last_login: Optional[datetime] = Field(None, description="Last login time")

    # User preferences (isteğe bağlı ekstralar)
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata")
    
    # ===== YENİ: Arkadaşlık Sistemi Alanları =====
    friends: List[str] = Field(default_factory=list, description="List of friend user IDs")
    friend_requests_sent: List[str] = Field(default_factory=list, description="List of sent friend request user IDs")
    friend_requests_received: List[str] = Field(default_factory=list, description="List of received friend request user IDs")
    # ============================================

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "status": "active",
                "friends": ["friend_user_id_1", "friend_user_id_2"]
            }
        }

# ============ REQUEST MODELS ============

class UserCreate(BaseModel):
    """
    Yeni kullanıcı oluşturma (Register)
    """
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Username sadece alphanumeric ve _ içermeli"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscore allowed)')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        """Basit password kontrolü"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePass123",
                "full_name": "New User"
            }
        }

class UserLogin(BaseModel):
    """
    Kullanıcı giriş (Login)
    """
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }

class UserUpdate(BaseModel):
    """
    Kullanıcı bilgilerini güncelleme
    Tüm alanlar optional (sadece değiştirmek istediklerini gönderirler)
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscore allowed)')
        return v.lower() if v else v

class PasswordChange(BaseModel):
    """
    Şifre değiştirme
    """
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @validator('new_password')
    def password_strength(cls, v):
        """Basit password kontrolü"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v

# ============ RESPONSE MODELS ============

class UserResponse(BaseModel):
    """
    API'den dönen User bilgisi (password hariç!)
    """
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "role": "user",
                "status": "active",
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

class UserPublicProfile(BaseModel):
    """
    Public profile (başka kullanıcılar görebilir)
    Email ve hassas bilgiler dahil değil
    """
    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime

# ===== YENİ: Arkadaşlık Sistemi Response Modelleri =====
class FriendInfo(BaseModel):
    """
    Arkadaş listelerinde gösterilecek temel kullanıcı bilgisi
    """
    id: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
# =======================================================

# ============ TOKEN MODELS ============

class Token(BaseModel):
    """
    JWT Token response
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }

class TokenData(BaseModel):
    """
    JWT token içeriği (decode edildiğinde)
    """
    user_id: str
    email: EmailStr
    role: UserRole
    exp: datetime  # Expiration time

# ============ AUTH RESPONSE MODELS ============

class LoginResponse(BaseModel):
    """
    Login başarılı response
    """
    success: bool = True
    message: str = "Login successful"
    token: Token
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "token": { "...": "..." },
                "user": { "...": "..." }
            }
        }

class RegisterResponse(BaseModel):
    """
    Register başarılı response
    """
    success: bool = True
    message: str = "Registration successful"
    user: UserResponse
    token: Optional[Token] = None  # Direkt login yapılırsa token da dönebilir
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Registration successful",
                "user": { "...": "..." }
            }
        }

# ============ HELPER FUNCTIONS ============

def user_to_response(user: User) -> UserResponse:
    """User modelini UserResponse'a çevir (hashed_password hariç)"""
    return UserResponse(**user.model_dump())

def user_to_public_profile(user: User) -> UserPublicProfile:
    """User modelini Public Profile'a çevir"""
    return UserPublicProfile(**user.model_dump())

# ===== YENİ: Arkadaş bilgisine çeviren helper =====
def user_to_friend_info(user: User) -> FriendInfo:
    """User modelini FriendInfo'ya çevir"""
    return FriendInfo(**user.model_dump())
# ==================================================