# backend/src/api/endpoints/gamification.py

"""
Gamification API - XP, Level, Node, Streak, Achievements
Frontend'deki puan sisteminin backend karşılığı
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

from ..utils.auth_utils import get_current_user_id

router = APIRouter(prefix="/api/gamification", tags=["gamification"])

# ============ MODELS ============

class AddXPRequest(BaseModel):
    """XP ekleme request"""
    xp_amount: int = Field(..., gt=0, description="XP miktarı (pozitif)")
    source: str = Field(..., description="XP kaynağı (reel_watch, emoji_given, etc)")
    metadata: Optional[Dict] = Field(default=None, description="Ek bilgiler")

class XPResponse(BaseModel):
    """XP response"""
    success: bool
    message: str
    xp_gained: int
    total_xp: int
    current_level: int
    current_node: int
    level_up: bool
    timestamp: str

class LevelDataResponse(BaseModel):
    """Level bilgisi"""
    success: bool
    current_level: int
    current_node: int
    nodes_in_level: int
    current_xp: int
    xp_needed_for_next_node: int
    total_xp: int
    timestamp: str

class UserStatsResponse(BaseModel):
    """Kullanıcı istatistikleri"""
    success: bool
    total_xp: int
    current_level: int
    current_streak: int
    today_stats: Dict
    timestamp: str

# ============ XP & LEVEL ENDPOINTS ============

@router.post("/add-xp", response_model=XPResponse)
async def add_xp(
    request: AddXPRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    XP ekle ve level kontrolü yap
    
    Frontend her aktivitede buraya istek atar:
    - Reel izleme: 10 XP
    - Emoji verme: 5 XP (ilk)
    - Detay okuma: 15 XP
    - Share verme: 20 XP (ilk)
    """
    try:
        from ...services.gamification_service import gamification_service
        
        result = await gamification_service.add_xp(
            user_id=user_id,
            xp_amount=request.xp_amount,
            source=request.source,
            metadata=request.metadata
        )
        
        return XPResponse(
            success=True,
            message="XP added successfully",
            xp_gained=request.xp_amount,
            total_xp=result["total_xp"],
            current_level=result["current_level"],
            current_node=result["current_node"],
            level_up=result["level_up"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/level/{user_id}", response_model=LevelDataResponse)
async def get_current_level(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının mevcut level bilgilerini getir
    """
    try:
        from ...services.gamification_service import gamification_service
        
        level_data = await gamification_service.get_level_data(user_id)
        
        return LevelDataResponse(
            success=True,
            current_level=level_data["current_level"],
            current_node=level_data["current_node"],
            nodes_in_level=level_data["nodes_in_level"],
            current_xp=level_data["current_xp"],
            xp_needed_for_next_node=level_data["xp_needed_for_next_node"],
            total_xp=level_data["total_xp"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcı istatistiklerini getir
    """
    try:
        from ...services.gamification_service import gamification_service
        
        stats = await gamification_service.get_user_stats(user_id)
        
        return UserStatsResponse(
            success=True,
            total_xp=stats["total_xp"],
            current_level=stats["current_level"],
            current_streak=stats["current_streak"],
            today_stats=stats["today_stats"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-daily/{user_id}")
async def reset_daily_progress(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Günlük ilerlemeyi sıfırla (gece yarısı otomatik)
    """
    try:
        from ...services.gamification_service import gamification_service
        
        await gamification_service.reset_daily_progress(user_id)
        
        return {
            "success": True,
            "message": "Daily progress reset"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ LEADERBOARD ENDPOINTS ============

@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = "all_time",  # all_time, monthly, weekly
    limit: int = 100,
    user_id: str = Depends(get_current_user_id)
):
    """
    Liderlik tablosu
    """
    try:
        from ...services.gamification_service import gamification_service
        
        leaderboard = await gamification_service.get_leaderboard(
            timeframe=timeframe,
            limit=limit
        )
        
        return {
            "success": True,
            "leaderboard": leaderboard,
            "timeframe": timeframe
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rank/{user_id}")
async def get_user_rank(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının sıralamasını getir
    """
    try:
        from ...services.gamification_service import gamification_service
        
        rank_data = await gamification_service.get_user_rank(user_id)
        
        return {
            "success": True,
            "rank": rank_data["rank"],
            "total_users": rank_data["total_users"],
            "percentile": rank_data["percentile"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ NODE MANAGEMENT ============
    
@router.get("/check-node-eligibility/{user_id}")
async def check_node_eligibility(
    user_id: str,
    required_nodes: int = 1,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının yeterli node'u var mı kontrol et
    
    Query params:
        required_nodes: Gereken node sayısı (default: 1)
    """
    try:
        from ...services.gamification_service import gamification_service
        
        has_nodes = gamification_service.has_available_nodes(
            user_id=user_id,
            required_nodes=required_nodes
        )
        
        # Kullanıcı bilgilerini al
        level_data = await gamification_service.get_level_data(user_id)
        
        return {
            "success": True,
            "eligible": has_nodes,
            "current_nodes": level_data["current_node"],
            "required_nodes": required_nodes,
            "message": "Yeterli node var" if has_nodes else f"En az {required_nodes} node gerekli"
        }
        
    except Exception as e:
        print(f"❌ [Check Node Eligibility] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SpendNodesRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Harcanacak node sayısı")
    reason: str = Field(default="game_entry", description="Harcama nedeni")


@router.post("/spend-nodes")
async def spend_nodes(
    request: SpendNodesRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Node harca (oyuna giriş vs için)
    
    Body:
        amount: Harcanacak node sayısı
        reason: Harcama nedeni
    """
    try:
        from ...services.gamification_service import gamification_service
        
        print(f"🎮 [API] Spend nodes request: user={user_id[:8]}, amount={request.amount}, reason={request.reason}")
        
        success = gamification_service.spend_nodes(
            user_id=user_id,
            amount=request.amount,
            reason=request.reason
        )
        
        if not success:
            return {
                "success": False,
                "message": "Yetersiz node"
            }
        
        # Güncel bilgileri al
        level_data = await gamification_service.get_level_data(user_id)
        
        return {
            "success": True,
            "message": f"{request.amount} node harcandı",
            "nodes_spent": request.amount,
            "current_level": level_data["current_level"],
            "current_node": level_data["current_node"],
            "total_xp": level_data["total_xp"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ [Spend Nodes] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AddNodesRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Eklenecek node sayısı")
    source: str = Field(default="game_reward", description="Node kaynağı")


@router.post("/add-nodes")
async def add_nodes(
    request: AddNodesRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Node ekle (oyun ödülü vs)
    
    Body:
        amount: Eklenecek node sayısı
        source: Node kaynağı (game_reward, etc)
    """
    try:
        from ...services.gamification_service import gamification_service
        
        print(f"🎮 [API] Add nodes request: user={user_id[:8]}, amount={request.amount}, source={request.source}")
        
        result = gamification_service.add_nodes(
            user_id=user_id,
            amount=request.amount,
            source=request.source
        )
        
        return {
            "success": True,
            "message": f"{request.amount} node eklendi",
            "nodes_added": request.amount,
            "current_level": result["current_level"],
            "current_node": result["current_node"],
            "total_xp": result["total_xp"],
            "level_up": result["level_up"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ [Add Nodes] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))











# ============ ACHIEVEMENTS ============

@router.get("/achievements/{user_id}")
async def get_achievements(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının başarımları
    """
    try:
        from ...services.gamification_service import gamification_service
        
        achievements = await gamification_service.get_achievements(user_id)
        
        return {
            "success": True,
            "achievements": achievements["list"],
            "total_unlocked": achievements["total_unlocked"],
            "total_achievements": achievements["total_achievements"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unlock-achievement")
async def unlock_achievement(
    achievement_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Başarım unlock
    """
    try:
        from ...services.gamification_service import gamification_service
        
        result = await gamification_service.unlock_achievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        
        return {
            "success": True,
            "unlocked": result["unlocked"],
            "achievement": result["achievement"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ SYNC ============

@router.post("/sync")
async def sync_state(
    local_state: Dict,
    user_id: str = Depends(get_current_user_id)
):
    """
    Frontend state'ini backend ile senkronize et
    """
    try:
        from ...services.gamification_service import gamification_service
        
        synced_state = await gamification_service.sync_state(
            user_id=user_id,
            local_state=local_state
        )
        
        return {
            "success": True,
            "synced_state": synced_state,
            "conflicts": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ DAILY PROGRESS ============

@router.get("/daily-progress/{user_id}")
async def get_daily_progress(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Günlük ilerleme
    """
    try:
        from ...services.gamification_service import gamification_service
        
        progress = await gamification_service.get_daily_progress(user_id)
        
        return {
            "success": True,
            "xp_earned_today": progress["xp_earned_today"],
            "daily_goal": progress["daily_goal"],
            "progress_percentage": progress["progress_percentage"],
            "goal_completed": progress["goal_completed"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))