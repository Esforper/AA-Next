# ================================
# src/services/auth_service.py - Authentication Service
# ================================

"""
Minimal ama güvenli authentication servisi
- Password hashing (bcrypt)
- JWT token management
- User storage (JSON file)
- Register/Login logic
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..models.user import (
    User, UserCreate, UserLogin, UserUpdate,
    UserResponse, UserRole, UserStatus,
    Token, TokenData,
    user_to_response
)
from ..config import settings

# ============ PASSWORD HASHING ============

# Bcrypt context - password hashing için
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Şifreyi hash'le"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrula"""
    return pwd_context.verify(plain_password, hashed_password)

# ============ JWT TOKEN MANAGEMENT ============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token oluştur
    """
    to_encode = data.copy()
    
    # Expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)
    
    to_encode.update({"exp": expire})
    
    # JWT encode
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """
    JWT token'ı decode et ve validate et
    """
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp: float = payload.get("exp")
        
        if user_id is None or email is None:
            return None
        
        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role),
            exp=datetime.fromtimestamp(exp)
        )
        
    except JWTError:
        return None

# ============ USER STORAGE (JSON FILE) ============

class UserStorage:
    """
    Basit JSON file storage
    Production'da SQLite veya PostgreSQL kullanılabilir
    """
    
    def __init__(self, storage_path: str = "storage/users/users.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Eğer dosya yoksa boş liste oluştur
        if not self.storage_path.exists():
            self._save_users([])
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Tüm kullanıcıları yükle"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading users: {e}")
            return []
    
    def _save_users(self, users: List[Dict[str, Any]]):
        """Kullanıcıları kaydet"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving users: {e}")
    
    def create_user(self, user: User) -> User:
        """Yeni kullanıcı oluştur"""
        users = self._load_users()
        
        # User'ı dict'e çevir
        user_dict = user.model_dump(mode='json')
        users.append(user_dict)
        
        self._save_users(users)
        print(f"✅ User created: {user.email}")
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID ile kullanıcı bul"""
        users = self._load_users()
        
        for user_dict in users:
            if user_dict.get('id') == user_id:
                return User(**user_dict)
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Email ile kullanıcı bul"""
        users = self._load_users()
        
        for user_dict in users:
            if user_dict.get('email') == email:
                return User(**user_dict)
        
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Username ile kullanıcı bul"""
        users = self._load_users()
        
        for user_dict in users:
            if user_dict.get('username') == username.lower():
                return User(**user_dict)
        
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Kullanıcı bilgilerini güncelle"""
        users = self._load_users()
        
        for i, user_dict in enumerate(users):
            if user_dict.get('id') == user_id:
                # Update fields
                user_dict.update(updates)
                user_dict['updated_at'] = datetime.now().isoformat()
                
                users[i] = user_dict
                self._save_users(users)
                
                print(f"✅ User updated: {user_id}")
                return User(**user_dict)
        
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcı sil"""
        users = self._load_users()
        
        filtered_users = [u for u in users if u.get('id') != user_id]
        
        if len(filtered_users) < len(users):
            self._save_users(filtered_users)
            print(f"✅ User deleted: {user_id}")
            return True
        
        return False
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Kullanıcı listesi (pagination)"""
        users = self._load_users()
        
        # Pagination
        paginated = users[skip:skip + limit]
        
        return [User(**user_dict) for user_dict in paginated]
    
    def count_users(self) -> int:
        """Toplam kullanıcı sayısı"""
        users = self._load_users()
        return len(users)

# Global storage instance
user_storage = UserStorage()

# ============ AUTH SERVICE ============

class AuthService:
    """
    Authentication servisi
    Register, Login, Token validation
    """
    
    def __init__(self, storage: UserStorage = user_storage):
        self.storage = storage
    
    async def register(self, user_data: UserCreate) -> tuple[User, Token]:
        """
        Yeni kullanıcı kaydı
        
        Returns:
            (User, Token) - Oluşturulan user ve JWT token
        
        Raises:
            ValueError - Email veya username zaten kullanımda
        """
        
        # Email kontrolü
        existing_user = self.storage.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Username kontrolü
        existing_user = self.storage.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already taken")
        
        # User oluştur
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username.lower(),
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_verified=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            preferences={},
            metadata={}
        )
        
        # Kaydet
        created_user = self.storage.create_user(user)
        
        # Token oluştur
        token = self._create_token_for_user(created_user)
        
        print(f"✅ Registration successful: {created_user.email}")
        
        return created_user, token
    
    async def login(self, login_data: UserLogin) -> tuple[User, Token]:
        """
        Kullanıcı girişi
        
        Returns:
            (User, Token) - User ve JWT token
        
        Raises:
            ValueError - Email veya şifre hatalı
        """
        
        # Email ile user bul
        user = self.storage.get_user_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Şifre kontrolü
        if not verify_password(login_data.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Banned kontrol
        if user.status == UserStatus.BANNED:
            raise ValueError("Account is banned")
        
        # Last login güncelle
        self.storage.update_user(user.id, {
            "last_login": datetime.now().isoformat()
        })
        
        # Token oluştur
        token = self._create_token_for_user(user)
        
        print(f"✅ Login successful: {user.email}")
        
        return user, token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Token'dan current user'ı al
        
        Args:
            token: JWT access token
        
        Returns:
            User veya None
        """
        
        # Token decode
        token_data = decode_access_token(token)
        if not token_data:
            return None
        
        # Token expire kontrol
        if token_data.exp < datetime.utcnow():
            return None
        
        # User'ı getir
        user = self.storage.get_user_by_id(token_data.user_id)
        if not user:
            return None
        
        # Status kontrol
        if user.status != UserStatus.ACTIVE:
            return None
        
        return user
    
    async def update_profile(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        """
        Kullanıcı profilini güncelle
        """
        
        # Sadece None olmayan alanları al
        update_data = updates.model_dump(exclude_unset=True)
        
        if not update_data:
            # Hiçbir şey güncellenmemiş
            return self.storage.get_user_by_id(user_id)
        
        # Username değiştiriliyorsa unique kontrolü
        if 'username' in update_data:
            existing = self.storage.get_user_by_username(update_data['username'])
            if existing and existing.id != user_id:
                raise ValueError("Username already taken")
        
        # Güncelle
        updated_user = self.storage.update_user(user_id, update_data)
        
        if updated_user:
            print(f"✅ Profile updated: {user_id}")
        
        return updated_user
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Kullanıcı şifresini değiştir
        """
        
        # User'ı getir
        user = self.storage.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Eski şifre kontrolü
        if not verify_password(old_password, user.hashed_password):
            raise ValueError("Invalid current password")
        
        # Yeni şifre aynı olamaz
        if verify_password(new_password, user.hashed_password):
            raise ValueError("New password cannot be same as old password")
        
        # Şifreyi güncelle
        new_hashed = hash_password(new_password)
        updated = self.storage.update_user(user_id, {
            "hashed_password": new_hashed
        })
        
        if updated:
            print(f"✅ Password changed: {user_id}")
            return True
        
        return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserResponse]:
        """
        Kullanıcı profilini getir (response formatında)
        """
        user = self.storage.get_user_by_id(user_id)
        if not user:
            return None
        
        return user_to_response(user)
    
    def _create_token_for_user(self, user: User) -> Token:
        """
        User için JWT token oluştur
        """
        
        # Token data
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        }
        
        # Expiration
        expires_delta = timedelta(hours=settings.jwt_expire_hours)
        
        # Token oluştur
        access_token = create_access_token(token_data, expires_delta)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds())
        )

# Global service instance
auth_service = AuthService()

# ============ HELPER FUNCTIONS ============

async def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Helper function - Token'dan user al
    FastAPI dependency olarak kullanılabilir
    """
    return await auth_service.get_current_user(token)

async def require_admin(user: User) -> User:
    """
    Admin kontrolü
    
    Raises:
        ValueError - User admin değilse
    """
    if user.role != UserRole.ADMIN:
        raise ValueError("Admin access required")
    return user

# ============ STATISTICS & ADMIN ============

async def get_user_statistics() -> Dict[str, Any]:
    """
    Kullanıcı istatistikleri (admin için)
    """
    
    users = user_storage.list_users(limit=10000)
    
    # Status counts
    status_counts = {}
    for status in UserStatus:
        status_counts[status.value] = sum(1 for u in users if u.status == status)
    
    # Role counts
    role_counts = {}
    for role in UserRole:
        role_counts[role.value] = sum(1 for u in users if u.role == role)
    
    # Recent registrations (son 7 gün)  
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_count = sum(1 for u in users if u.created_at > seven_days_ago)
    
    return {
        "total_users": len(users),
        "by_status": status_counts,
        "by_role": role_counts,
        "recent_registrations": recent_count,
        "verified_users": sum(1 for u in users if u.is_verified)
    }