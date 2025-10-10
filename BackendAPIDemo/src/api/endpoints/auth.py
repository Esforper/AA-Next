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
from typing import Optional, List

from ...models.user import (
    User, UserCreate, UserLogin, UserUpdate, PasswordChange,
    UserResponse, LoginResponse, RegisterResponse, FriendInfo,
    user_to_response
)
from ...services.auth_service import auth_service, require_admin, get_user_statistics

# Router setup - PREFIX /api KALDIRILDI
router = APIRouter(
    prefix="/api",
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
        print(f"❌ REGISTER ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")
    
@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    try:
        user, token = await auth_service.login(login_data)
        return LoginResponse(user=user_to_response(user), token=token)
    except ValueError as e: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.get("/auth/check-email/{email}")
async def check_email(email: str):
    exists = await auth_service.check_email_exists(email)
    return {"exists": exists, "available": not exists}

@router.get("/auth/check-username/{username}")
async def check_username(username: str):
    exists = await auth_service.check_username_exists(username)
    return {"exists": exists, "available": not exists}

# ============ PROTECTED ENDPOINTS ============
@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return user_to_response(current_user)

@router.put("/auth/me", response_model=UserResponse)
async def update_profile(update_data: UserUpdate, current_user: User = Depends(get_current_active_user)):
    try:
        updated_user = await auth_service.update_user(current_user.id, update_data)
        return user_to_response(updated_user)
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")

@router.post("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_active_user)):
    try:
        success = await auth_service.change_password(current_user.id, password_data.old_password, password_data.new_password)
        if success: return {"success": True, "message": "Password changed successfully"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to change password")
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password change failed")

@router.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    🚪 Logout - Token'ı invalidate et
    """
    try:
        await auth_service.invalidate_token(current_user.id)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")

@router.get("/auth/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str):
    profile = await auth_service.get_user_profile(user_id)
    if not profile: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile

# ============ FRIEND SYSTEM ENDPOINTS ============
@router.post("/friends/request/{target_user_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def send_friend_request(target_user_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        success = await auth_service.send_friend_request(current_user.id, target_user_id)
        if success: return {"success": True, "message": "Friend request sent successfully"}
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e: raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not send friend request")

@router.post("/friends/accept/{requester_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def accept_friend_request(requester_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        success = await auth_service.accept_friend_request(current_user.id, requester_id)
        if success: return {"success": True, "message": "Friend request accepted"}
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/friends/reject/{requester_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def reject_friend_request(requester_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        success = await auth_service.reject_friend_request(current_user.id, requester_id)
        if success: return {"success": True, "message": "Friend request rejected"}
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/friends/remove/{friend_id}", status_code=status.HTTP_200_OK, tags=["Friends"])
async def remove_friend(friend_id: str, current_user: User = Depends(get_current_active_user)):
    try:
        success = await auth_service.remove_friend(current_user.id, friend_id)
        if success: return {"success": True, "message": "Friend removed successfully"}
    except ValueError as e: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/friends/me", response_model=List[FriendInfo], tags=["Friends"])
async def get_my_friends(current_user: User = Depends(get_current_active_user)):
    return await auth_service.list_friends(current_user.id)

@router.get("/friends/requests/pending", response_model=List[FriendInfo], tags=["Friends"])
async def get_pending_friend_requests(current_user: User = Depends(get_current_active_user)):
    return await auth_service.list_friend_requests(current_user.id)

@router.get("/users/{user_id}/friends", response_model=List[FriendInfo], tags=["Friends"])
async def get_user_friends(user_id: str):
    user = await auth_service.get_user_profile(user_id)
    if not user: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await auth_service.list_friends(user_id)

# ============ ADMIN ENDPOINTS ============
@router.get("/auth/admin/users", response_model=list[UserResponse], tags=["Admin"])
async def list_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin_user)):
    users = await auth_service.list_users(skip=skip, limit=limit)
    return [user_to_response(user) for user in users]

@router.get("/auth/admin/statistics", tags=["Admin"])
async def get_statistics(current_user: User = Depends(get_current_admin_user)):
    stats = await get_user_statistics()
    return {"success": True, "data": stats}

@router.delete("/auth/admin/users/{user_id}", tags=["Admin"])
async def delete_user(user_id: str, current_user: User = Depends(get_current_admin_user)):
    if user_id == current_user.id: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    success = await auth_service.delete_user(user_id)
    if success: return {"success": True, "message": "User deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.patch("/auth/admin/users/{user_id}/status", tags=["Admin"])
async def update_user_status(user_id: str, status_update: dict, current_user: User = Depends(get_current_admin_user)):
    from ...models.user import UserStatus
    new_status = UserStatus(status_update.get("status"))
    success = await auth_service.update_user_status(user_id, new_status)
    if success: return {"success": True, "message": "User status updated"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# ============ UTILITY ENDPOINTS ============
@router.get("/auth/endpoints", tags=["System"])
async def list_endpoints():
    return {
        "public": ["/auth/register", "/auth/login", "/auth/check-email/{email}", "/auth/check-username/{username}"],
        "protected": ["/auth/me", "/auth/logout", "/auth/change-password", "/auth/profile/{user_id}"],
        "friends": ["/friends/request/{target_user_id}", "/friends/accept/{requester_id}", "/friends/reject/{requester_id}", "/friends/remove/{friend_id}", "/friends/me", "/friends/requests/pending"],
        "admin": ["/auth/admin/users", "/auth/admin/statistics", "/auth/admin/users/{user_id}", "/auth/admin/users/{user_id}/status"]
    }
    
    
    
    