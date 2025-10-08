# ================================
# src/api/endpoints/auth.py - Authentication Endpoints
# ================================

"""
User authentication API endpoints
- Register, Login, Logout
- Profile management
- Password change
- Token validation
"""

from fastapi import APIRouter, HTTPException, Depends, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List # List import edildi

from ...models.user import (
    User, UserCreate, UserLogin, UserUpdate, PasswordChange,
    UserResponse, LoginResponse, RegisterResponse, FriendInfo, # FriendInfo import edildi
    user_to_response
)
from ...services.auth_service import auth_service, require_admin, get_user_statistics

# Router setup
router = APIRouter(
    prefix="/api", # Prefix /api olarak değiştirildi, endpoint'ler daha anlamlı olacak
    tags=["Authentication & Users"]
)

# Security scheme
security = HTTPBearer()

# ============ DEPENDENCIES ============
async def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "): return None
    return authorization.replace("Bearer ", "")

async def get_current_user(token: Optional[str] = Depends(get_token_from_header)) -> User:
    if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = await auth_service.get_current_user(token)
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    from ...models.user import UserStatus
    if current_user.status != UserStatus.ACTIVE: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    return current_user
# ... (Diğer dependency'ler aynı kalıyor)
async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    try: return await require_admin(current_user)
    except ValueError as e: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
async def get_optional_user(token: Optional[str] = Depends(get_token_from_header)) -> Optional[User]:
    if not token: return None
    return await auth_service.get_current_user(token)

# ============ PUBLIC AUTH ENDPOINTS ============
@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    try:
        user, token = await auth_service.register(user_data)
        return RegisterResponse(user=user_to_response(user), token=token)
    except ValueError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: 
        print(f"❌❌❌ REGISTER ERROR: {e}")  # ← Bu satırı ekle
        import traceback
        traceback.print_exc()  # ← Ve bunu
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")
    
    
@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    try:
        user, token = await auth_service.login(login_data)
        return LoginResponse(user=user_to_response(user), token=token)
    except ValueError as e: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

# ... (Mevcut check-email, check-username, me, update, change-password, logout, profile endpoint'leri aynı kalıyor)

# ============ PROTECTED ENDPOINTS ============
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return user_to_response(current_user)

# ... (Diğer /me, /change-password, /logout endpoint'leri)

@router.get("/users/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str):
    profile = await auth_service.get_user_profile(user_id)
    if not profile: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile

# ===== YENİ: Arkadaşlık API Endpoint'leri =====
@router.post("/friends/request/{target_user_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def send_friend_request(target_user_id: str, current_user: User = Depends(get_current_active_user)):
    """
    🤝 Bir kullanıcıya arkadaşlık isteği gönder
    
    Requires: Bearer token
    """
    try:
        success = await auth_service.send_friend_request(current_user.id, target_user_id)
        if success:
            return {"success": True, "message": "Friend request sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not send friend request")

@router.post("/friends/accept/{requester_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def accept_friend_request(requester_id: str, current_user: User = Depends(get_current_active_user)):
    """
    ✅ Gelen bir arkadaşlık isteğini kabul et
    
    Requires: Bearer token
    """
    try:
        success = await auth_service.accept_friend_request(current_user.id, requester_id)
        if success:
            return {"success": True, "message": "Friend request accepted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/friends/reject/{requester_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def reject_friend_request(requester_id: str, current_user: User = Depends(get_current_active_user)):
    """
    ❌ Gelen bir arkadaşlık isteğini reddet
    
    Requires: Bearer token
    """
    try:
        success = await auth_service.reject_friend_request(current_user.id, requester_id)
        if success:
            return {"success": True, "message": "Friend request rejected"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/friends/remove/{friend_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def remove_friend(friend_id: str, current_user: User = Depends(get_current_active_user)):
    """
    🗑️ Bir arkadaşı sil
    
    Requires: Bearer token
    """
    try:
        success = await auth_service.remove_friend(current_user.id, friend_id)
        if success:
            return {"success": True, "message": "Friend removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/friends/me", response_model=List[FriendInfo], tags=["Friends"])
async def get_my_friends(current_user: User = Depends(get_current_active_user)):
    """
    🧑‍🤝‍🧑 Mevcut kullanıcının arkadaşlarını listele
    
    Requires: Bearer token
    """
    return await auth_service.list_friends(current_user.id)

@router.get("/friends/requests/pending", response_model=List[FriendInfo], tags=["Friends"])
async def get_pending_friend_requests(current_user: User = Depends(get_current_active_user)):
    """
    📥 Gelen ve bekleyen arkadaşlık isteklerini listele
    
    Requires: Bearer token
    """
    return await auth_service.list_friend_requests(current_user.id)

@router.get("/users/{user_id}/friends", response_model=List[FriendInfo], tags=["Friends"])
async def get_user_friends(user_id: str):
    """
    👀 Başka bir kullanıcının arkadaşlarını listele (Public)
    """
    user = await auth_service.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await auth_service.list_friends(user_id)
# ============================================

# ... (Mevcut ADMIN ve UTILITY endpoint'leri aynı kalıyor)