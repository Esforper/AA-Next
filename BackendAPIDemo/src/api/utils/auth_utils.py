# backend/src/api/utils/auth_utils.py

"""
Authentication Utilities - Ortak Auth Helper'lar
Tekrar eden JWT token validation kodlarını tek noktada toplar
"""

from fastapi import Header, HTTPException
from typing import Optional

from ...services.auth_service import auth_service  # ✅ DÜZELTME


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    JWT token'dan user ID çıkar
    
    Tüm endpoint'lerde kullanılabilir ortak fonksiyon.
    Token yoksa veya geçersizse 401 döner.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(user_id: str = Depends(get_current_user_id)):
            ...
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Authentication required"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        # ✅ DÜZELTME: auth_service kullan
        user = await auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
        
        return user.id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


async def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    JWT token'dan user ID çıkar (opsiyonel)
    
    Token yoksa None döner, hata fırlatmaz.
    Hem authenticated hem guest kullanıcılar için endpoint'lerde kullanılır.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(user_id: Optional[str] = Depends(get_optional_user_id)):
            if user_id:
                # Authenticated user
            else:
                # Guest user
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    
    try:
        # ✅ DÜZELTME: auth_service kullan
        user = await auth_service.get_current_user(token)
        return user.id if user else None
    except:
        return None