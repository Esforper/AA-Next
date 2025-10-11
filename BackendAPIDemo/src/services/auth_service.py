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
from datetime import datetime, timedelta, timezone
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
    Token, TokenData, FriendInfo,
    user_to_response, user_to_friend_info
)
from ..config import settings

# ============ PASSWORD HASHING ============
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool: return pwd_context.verify(plain_password, hashed_password)

# create_access_token fonksiyonunu güncelleyin:
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta  # ✅ Değişti
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)  # ✅ Değişti
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        if user_id is None or email is None: return None
        return TokenData(**payload)
    except JWTError:
        return None

# ============ USER STORAGE (JSON FILE) ============
class UserStorage:
    def __init__(self, storage_path: str = "storage/users/users.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists(): self._save_users([])
    
    def _load_users(self) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e: return []
    
    def _save_users(self, users: List[Dict[str, Any]]):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f: json.dump(users, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e: print(f"❌ Error saving users: {e}")

    def create_user(self, user: User) -> User:
        users = self._load_users()
        users.append(user.model_dump(mode='json'))
        self._save_users(users)
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        for user_dict in self._load_users():
            if user_dict.get('id') == user_id: return User(**user_dict)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        for user_dict in self._load_users():
            if user_dict.get('email') == email: return User(**user_dict)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        for user_dict in self._load_users():
            if user_dict.get('username') == username.lower(): return User(**user_dict)
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        users = self._load_users()
        for i, user_dict in enumerate(users):
            if user_dict.get('id') == user_id:
                user_dict.update(updates)
                user_dict['updated_at'] = datetime.now().isoformat()
                users[i] = user_dict
                self._save_users(users)
                return User(**user_dict)
        return None
    
    def delete_user(self, user_id: str) -> bool:
        users = self._load_users()
        filtered_users = [u for u in users if u.get('id') != user_id]
        if len(filtered_users) < len(users):
            self._save_users(filtered_users)
            return True
        return False
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = self._load_users()
        return [User(**u) for u in users[skip:skip + limit]]
    
    def count_users(self) -> int:
        return len(self._load_users())

user_storage = UserStorage()

# ============ AUTH SERVICE ============
class AuthService:
    def __init__(self, storage: UserStorage = user_storage):
        self.storage = storage
    
    # ... (Mevcut register, login, vb. fonksiyonlar burada kalacak)
    async def register(self, user_data: UserCreate) -> tuple[User, Token]:
        if self.storage.get_user_by_email(user_data.email): raise ValueError("Email already registered")
        if self.storage.get_user_by_username(user_data.username): raise ValueError("Username already taken")
        user = User(id=str(uuid.uuid4()), email=user_data.email, username=user_data.username.lower(), hashed_password=hash_password(user_data.password), full_name=user_data.full_name)
        created_user = self.storage.create_user(user)
        token = self._create_token_for_user(created_user)
        return created_user, token
    
    async def login(self, login_data: UserLogin) -> tuple[User, Token]:
        user = self.storage.get_user_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password): raise ValueError("Invalid email or password")
        if user.status == UserStatus.BANNED: raise ValueError("Account is banned")
        self.storage.update_user(user.id, {"last_login": datetime.now().isoformat()})
        return user, self._create_token_for_user(user)

    # get_current_user metodunu AuthService class'ı içinde güncelleyin:
    async def get_current_user(self, token: str) -> Optional[User]:
        token_data = decode_access_token(token)
        if not token_data or token_data.exp < datetime.now(timezone.utc):  # ✅ Değişti
            return None
        user = self.storage.get_user_by_id(token_data.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            return None
        return user

    async def update_profile(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data: return self.storage.get_user_by_id(user_id)
        if 'username' in update_data:
            existing = self.storage.get_user_by_username(update_data['username'])
            if existing and existing.id != user_id: raise ValueError("Username already taken")
        return self.storage.update_user(user_id, update_data)
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        user = self.storage.get_user_by_id(user_id)
        if not user or not verify_password(old_password, user.hashed_password): raise ValueError("Invalid current password")
        if verify_password(new_password, user.hashed_password): raise ValueError("New password cannot be same as old password")
        new_hashed = hash_password(new_password)
        return self.storage.update_user(user_id, {"hashed_password": new_hashed}) is not None

    async def get_user_profile(self, user_id: str) -> Optional[UserResponse]:
        user = self.storage.get_user_by_id(user_id)
        return user_to_response(user) if user else None
    
    def _create_token_for_user(self, user: User) -> Token:
        expires_delta = timedelta(hours=settings.jwt_expire_hours)
        token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data, expires_delta)
        return Token(access_token=access_token, expires_in=int(expires_delta.total_seconds()))

    # ===== YENİ: Arkadaşlık Servis Fonksiyonları =====
    async def send_friend_request(self, current_user_id: str, target_user_id: str) -> bool:
        if current_user_id == target_user_id: raise ValueError("Cannot send a friend request to yourself")
        
        sender = self.storage.get_user_by_id(current_user_id)
        receiver = self.storage.get_user_by_id(target_user_id)

        if not receiver: raise ValueError("Target user not found")
        if target_user_id in sender.friends: raise ValueError("You are already friends with this user")
        if target_user_id in sender.friend_requests_sent: raise ValueError("Friend request already sent")

        # İsteği gönderen ve alan kullanıcıların listelerini güncelle
        sender.friend_requests_sent.append(target_user_id)
        receiver.friend_requests_received.append(current_user_id)

        self.storage.update_user(sender.id, {"friend_requests_sent": sender.friend_requests_sent})
        self.storage.update_user(receiver.id, {"friend_requests_received": receiver.friend_requests_received})
        
        return True

    async def accept_friend_request(self, current_user_id: str, requester_id: str) -> bool:
        user = self.storage.get_user_by_id(current_user_id)
        requester = self.storage.get_user_by_id(requester_id)

        if not requester: raise ValueError("Requesting user not found")
        if requester_id not in user.friend_requests_received: raise ValueError("No friend request from this user")

        # İstek listelerinden ID'leri kaldır
        user.friend_requests_received.remove(requester_id)
        requester.friend_requests_sent.remove(current_user_id)
        
        # Arkadaş listelerine ekle
        user.friends.append(requester_id)
        requester.friends.append(current_user_id)
        
        self.storage.update_user(user.id, {
            "friend_requests_received": user.friend_requests_received,
            "friends": user.friends
        })
        self.storage.update_user(requester.id, {
            "friend_requests_sent": requester.friend_requests_sent,
            "friends": requester.friends
        })
        return True

    async def reject_friend_request(self, current_user_id: str, requester_id: str) -> bool:
        user = self.storage.get_user_by_id(current_user_id)
        requester = self.storage.get_user_by_id(requester_id)

        if not requester: raise ValueError("Requesting user not found")
        if requester_id not in user.friend_requests_received: raise ValueError("No friend request from this user")

        # İstek listelerinden ID'leri kaldır
        user.friend_requests_received.remove(requester_id)
        requester.friend_requests_sent.remove(current_user_id)

        self.storage.update_user(user.id, {"friend_requests_received": user.friend_requests_received})
        self.storage.update_user(requester.id, {"friend_requests_sent": requester.friend_requests_sent})
        return True

    async def remove_friend(self, current_user_id: str, friend_id: str) -> bool:
        user = self.storage.get_user_by_id(current_user_id)
        friend = self.storage.get_user_by_id(friend_id)

        if not friend: raise ValueError("Friend not found")
        if friend_id not in user.friends: raise ValueError("This user is not in your friends list")
        
        # Karşılıklı olarak arkadaş listelerinden çıkar
        user.friends.remove(friend_id)
        friend.friends.remove(current_user_id)
        
        self.storage.update_user(user.id, {"friends": user.friends})
        self.storage.update_user(friend.id, {"friends": friend.friends})
        return True
        
    async def list_friends(self, user_id: str) -> List[FriendInfo]:
        user = self.storage.get_user_by_id(user_id)
        if not user: return []
        
        friends_list = []
        for friend_id in user.friends:
            friend_user = self.storage.get_user_by_id(friend_id)
            if friend_user:
                friends_list.append(user_to_friend_info(friend_user))
        return friends_list

    async def list_friend_requests(self, user_id: str) -> List[FriendInfo]:
        user = self.storage.get_user_by_id(user_id)
        if not user: return []

        requests_list = []
        for requester_id in user.friend_requests_received:
            requester_user = self.storage.get_user_by_id(requester_id)
            if requester_user:
                requests_list.append(user_to_friend_info(requester_user))
        return requests_list
    # ==================================================

auth_service = AuthService()

# ============ HELPER FUNCTIONS ============
async def get_current_user_from_token(token: str) -> Optional[User]: return await auth_service.get_current_user(token)
async def require_admin(user: User) -> User:
    if user.role != UserRole.ADMIN: raise ValueError("Admin access required")
    return user

# ============ STATISTICS & ADMIN ============
async def get_user_statistics() -> Dict[str, Any]:
    # ... (Bu fonksiyon değişmedi)
    return {}