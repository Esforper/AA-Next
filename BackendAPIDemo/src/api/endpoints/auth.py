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
from typing import Optional, Annotated

from ...models.user import (
    User, UserCreate, UserLogin, UserUpdate, PasswordChange,
    UserResponse, LoginResponse, RegisterResponse,
    user_to_response
)
from ...services.auth_service import auth_service, require_admin, get_user_statistics

# Router setup
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# Security scheme
security = HTTPBearer()

# ============ DEPENDENCIES ============

async def get_token_from_header(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Authorization header'dan token'ı çıkar
    Format: "Bearer <token>"
    """
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    return authorization.replace("Bearer ", "")

async def get_current_user(
    token: Optional[str] = Depends(get_token_from_header)
) -> User:
    """
    Token'dan current user'ı al
    Protected endpoint'ler için dependency
    
    Raises:
        HTTPException(401) - Token geçersiz veya yok
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Active user kontrolü
    """
    from ...models.user import UserStatus
    
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Admin user kontrolü
    """
    try:
        return await require_admin(current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

# Optional auth - token varsa user döner, yoksa None
async def get_optional_user(
    token: Optional[str] = Depends(get_token_from_header)
) -> Optional[User]:
    """
    Optional authentication
    Token varsa user döner, yoksa None
    """
    if not token:
        return None
    
    return await auth_service.get_current_user(token)

# ============ PUBLIC ENDPOINTS ============

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    🆕 Yeni kullanıcı kaydı
    
    - Email ve username unique olmalı
    - Password en az 8 karakter, 1 harf, 1 rakam içermeli
    - Başarılı kayıt sonrası otomatik token oluşturulur
    """
    try:
        user, token = await auth_service.register(user_data)
        
        return RegisterResponse(
            success=True,
            message="Registration successful",
            user=user_to_response(user),
            token=token
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Register error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    """
    🔐 Kullanıcı girişi
    
    - Email ve password ile giriş
    - Başarılı girişte JWT token döner
    - Token 24 saat geçerli
    """
    try:
        user, token = await auth_service.login(login_data)
        
        return LoginResponse(
            success=True,
            message="Login successful",
            user=user_to_response(user),
            token=token
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/check-email/{email}")
async def check_email_availability(email: str):
    """
    📧 Email kullanılabilirlik kontrolü
    
    Register formunda kullanılabilir (real-time validation)
    """
    from ...services.auth_service import user_storage
    
    existing_user = user_storage.get_user_by_email(email)
    
    return {
        "success": True,
        "email": email,
        "available": existing_user is None,
        "message": "Email available" if existing_user is None else "Email already registered"
    }

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    👤 Username kullanılabilirlik kontrolü
    
    Register formunda kullanılabilir (real-time validation)
    """
    from ...services.auth_service import user_storage
    
    existing_user = user_storage.get_user_by_username(username)
    
    return {
        "success": True,
        "username": username,
        "available": existing_user is None,
        "message": "Username available" if existing_user is None else "Username already taken"
    }

# ============ PROTECTED ENDPOINTS ============

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    👤 Mevcut kullanıcı bilgileri
    
    Requires: Bearer token
    """
    return user_to_response(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    ✏️ Profil güncelleme
    
    Requires: Bearer token
    
    Güncellenebilir alanlar:
    - username
    - full_name
    - bio
    - avatar_url
    - preferences
    """
    try:
        updated_user = await auth_service.update_profile(current_user.id, updates)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_to_response(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Update profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    """
    🔑 Şifre değiştirme
    
    Requires: Bearer token
    
    - Eski şifre doğru olmalı
    - Yeni şifre eski şifreden farklı olmalı
    - Yeni şifre güvenlik kurallarına uymalı
    """
    try:
        success = await auth_service.change_password(
            current_user.id,
            password_data.old_password,
            password_data.new_password
        )
        
        if success:
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    🚪 Çıkış yapma
    
    Requires: Bearer token
    
    Not: JWT token stateless olduğu için token'ı blacklist'e eklemiyoruz.
    Frontend tarafında token'ı silmek yeterli.
    İleride Redis ile token blacklist eklenebilir.
    """
    return {
        "success": True,
        "message": "Logout successful",
        "note": "Please remove the token from your client"
    }

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    👤 Kullanıcı profili görüntüleme
    
    Optional auth: Token varsa daha detaylı bilgi döner
    """
    profile = await auth_service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile

# ============ ADMIN ENDPOINTS ============

@router.get("/admin/users")
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    📋 Tüm kullanıcıları listele
    
    Requires: Admin access
    """
    from ...services.auth_service import user_storage
    
    users = user_storage.list_users(skip=skip, limit=limit)
    total = user_storage.count_users()
    
    return {
        "success": True,
        "users": [user_to_response(u) for u in users],
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total
        }
    }

@router.get("/admin/statistics")
async def get_user_stats(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    📊 Kullanıcı istatistikleri
    
    Requires: Admin access
    """
    stats = await get_user_statistics()
    
    return {
        "success": True,
        "statistics": stats
    }

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🗑️ Kullanıcı silme
    
    Requires: Admin access
    
    ⚠️ Dikkat: Bu işlem geri alınamaz!
    """
    from ...services.auth_service import user_storage
    
    # Admin kendini silemez
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_storage.delete_user(user_id)
    
    if success:
        return {
            "success": True,
            "message": "User deleted successfully",
            "user_id": user_id
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.patch("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: str,  # active, inactive, banned
    admin_user: User = Depends(get_current_admin_user)
):
    """
    🔧 Kullanıcı durumunu güncelle
    
    Requires: Admin access
    
    Status options: active, inactive, banned
    """
    from ...services.auth_service import user_storage
    from ...models.user import UserStatus
    
    # Validate status
    try:
        new_status = UserStatus(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in UserStatus])}"
        )
    
    # Admin kendini ban edemez
    if user_id == admin_user.id and new_status == UserStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban your own account"
        )
    
    # Update
    updated_user = user_storage.update_user(user_id, {"status": new_status.value})
    
    if updated_user:
        return {
            "success": True,
            "message": f"User status updated to {new_status.value}",
            "user": user_to_response(updated_user)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# ============ UTILITY ENDPOINTS ============

@router.get("/endpoints")
async def list_auth_endpoints():
    """
    📚 Auth API endpoint'lerinin listesi
    """
    endpoints = {
        "public": [
            "POST /api/auth/register - Yeni kullanıcı kaydı",
            "POST /api/auth/login - Kullanıcı girişi",
            "GET /api/auth/check-email/{email} - Email kontrolü",
            "GET /api/auth/check-username/{username} - Username kontrolü"
        ],
        "protected": [
            "GET /api/auth/me - Mevcut kullanıcı bilgileri",
            "PUT /api/auth/me - Profil güncelleme",
            "POST /api/auth/change-password - Şifre değiştirme",
            "POST /api/auth/logout - Çıkış yapma",
            "GET /api/auth/profile/{user_id} - Kullanıcı profili"
        ],
        "admin": [
            "GET /api/auth/admin/users - Tüm kullanıcıları listele",
            "GET /api/auth/admin/statistics - Kullanıcı istatistikleri",
            "DELETE /api/auth/admin/users/{user_id} - Kullanıcı sil",
            "PATCH /api/auth/admin/users/{user_id}/status - Kullanıcı durumu güncelle"
        ]
    }
    
    return {
        "success": True,
        "endpoints": endpoints,
        "authentication": {
            "type": "Bearer Token (JWT)",
            "header": "Authorization: Bearer <token>",
            "token_lifetime": "24 hours"
        }
    }