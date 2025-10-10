"""
Game API Endpoints - Haber Kapışması Oyunu (UPDATED)
GameService entegrasyonu ile gerçek oyun mantığı
"""

from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from ...models.user_viewed_news import user_viewed_news_storage
from ...services.reels_analytics import reels_analytics
from ...services.game_service import game_service
from ..utils.auth_utils import get_current_user_id
from ...services.matchmaking_queue import matchmaking_queue
router = APIRouter(prefix="/api/game", tags=["game"])


# ============ REQUEST/RESPONSE MODELS ============

class MatchmakingRequest(BaseModel):
    """Eşleşme talebi"""
    days: int = Field(default=6, ge=1, le=30, description="Son kaç gün")
    min_common_reels: int = Field(default=8, ge=4, le=20, description="Minimum ortak haber")


class MatchmakingResponse(BaseModel):
    """Eşleşme sonucu"""
    success: bool
    matched: bool = False
    opponent_id: Optional[str] = None
    game_id: Optional[str] = None
    common_reels_count: int = 0
    estimated_wait_time_seconds: Optional[int] = None
    message: str = ""


class GameCreatedResponse(BaseModel):
    """Oyun oluşturuldu response"""
    success: bool
    game_id: str
    player1_id: str
    player2_id: str
    total_questions: int
    status: str
    message: str = "Game created successfully"


class GameQuestionResponse(BaseModel):
    """Oyun sorusu response"""
    success: bool
    round_number: int
    total_rounds: int
    question_text: str
    options: List[str]  # [correct_option, wrong_option] karışık sırada
    correct_index: int  # Frontend'de saklanmayacak, sadece answer'da kullanılacak
    reel_id: str
    news_title: str
    asker_id: str  # Kim soruyor


class AnswerQuestionRequest(BaseModel):
    """Soruya cevap request"""
    selected_index: int = Field(..., ge=0, le=1, description="Seçilen şık (0 veya 1)")
    is_pass: bool = Field(default=False, description="Pas geçildi mi")


class AnswerQuestionResponse(BaseModel):
    """Soruya cevap response"""
    success: bool
    is_correct: bool
    xp_earned: int
    current_score: int
    response_message: str  # Doğru/yanlış/pas mesajı
    emoji_comment: Optional[str] = None
    news_url: str  # Habere link


class GameStatusResponse(BaseModel):
    """Oyun durumu"""
    success: bool
    game_id: str
    status: str  # "waiting", "active", "finished"
    player1_id: str
    player2_id: str
    player1_score: int
    player2_score: int
    current_round: int
    total_rounds: int
    created_at: str


class GameResultResponse(BaseModel):
    """Oyun sonucu"""
    success: bool
    game_id: str
    winner_id: Optional[str]
    result: str  # "win", "lose", "draw"
    my_score: int
    opponent_score: int
    total_xp_earned: int
    news_discussed: List[Dict]


# ============ MATCHMAKING ENDPOINTS ============

@router.post("/matchmaking/start", response_model=MatchmakingResponse)
async def start_matchmaking(
    request: MatchmakingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Eşleşme aramaya başla ve HEMEN oyun oluştur
    """
    try:
        # 1. Uygunluk kontrolü
        user_views = user_viewed_news_storage.get_user_views(
            user_id=user_id,
            days=request.days
        )
        
        if len(user_views) < request.min_common_reels:
            return MatchmakingResponse(
                success=False,
                matched=False,
                message=f"Son {request.days} günde en az {request.min_common_reels} haber izlemelisiniz. "
                        f"Şu an: {len(user_views)} haber."
            )
        
        # 2. Eşleşebilir kullanıcı ara
        matchable_users = user_viewed_news_storage.find_matchable_users(
            current_user_id=user_id,
            days=request.days,
            min_common_reels=request.min_common_reels
        )
        
        if not matchable_users:
            return MatchmakingResponse(
                success=True,
                matched=False,
                estimated_wait_time_seconds=60,
                message=f"Şu anda uygun rakip bulunamadı. Daha fazla haber izleyin!"
            )
        
        # 3. İlk uygun kullanıcıyı seç
        opponent_id = matchable_users[0]
        
        # 4. OYUN OLUŞTUR! (AI senaryo üretimi burada olacak)
        try:
            game_session = await game_service.create_game_session(
                player1_id=user_id,
                player2_id=opponent_id,
                days=request.days,
                question_count=8
            )
            
            print(f"🎮 Game created successfully: {game_session.game_id}")
            
            return MatchmakingResponse(
                success=True,
                matched=True,
                opponent_id=opponent_id,
                game_id=game_session.game_id,
                common_reels_count=len(game_session.questions),
                message="Rakip bulundu! Oyun oluşturuluyor..."
            )
            
        except Exception as e:
            print(f"❌ Game creation failed: {e}")
            return MatchmakingResponse(
                success=False,
                matched=False,
                message=f"Oyun oluşturulurken hata: {str(e)}"
            )
        
    except Exception as e:
        print(f"❌ Matchmaking error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Matchmaking failed: {str(e)}"
        )


# ============ GAME SESSION ENDPOINTS ============

@router.get("/session/{game_id}", response_model=GameStatusResponse)
async def get_game_status(
    game_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Oyun durumunu getir
    """
    try:
        session = game_service.get_game_session(game_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Kullanıcı bu oyunda mı kontrol et
        if user_id not in [session.player1_id, session.player2_id]:
            raise HTTPException(status_code=403, detail="Not your game")
        
        return GameStatusResponse(
            success=True,
            game_id=session.game_id,
            status=session.status,
            player1_id=session.player1_id,
            player2_id=session.player2_id,
            player1_score=session.player1_score,
            player2_score=session.player2_score,
            current_round=session.current_round,
            total_rounds=session.total_rounds,
            created_at=session.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{game_id}/start")
async def start_game_session(
    game_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Oyunu başlat (her iki oyuncu hazır olunca)
    """
    try:
        session = game_service.get_game_session(game_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Game not found")
        
        if user_id not in [session.player1_id, session.player2_id]:
            raise HTTPException(status_code=403, detail="Not your game")
        
        # Oyunu başlat
        success = game_service.start_game(game_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot start game")
        
        return {
            "success": True,
            "game_id": game_id,
            "message": "Game started!",
            "first_question_round": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{game_id}/question/{round_number}")
async def get_question(
    game_id: str,
    round_number: int,
    user_id: str = Depends(get_current_user_id)
):
    """
    Belirli bir round'un sorusunu getir
    """
    try:
        session = game_service.get_game_session(game_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Game not found")
        
        if user_id not in [session.player1_id, session.player2_id]:
            raise HTTPException(status_code=403, detail="Not your game")
        
        if round_number >= len(session.questions):
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = session.questions[round_number]
        
        # Seçenekleri karıştır (her seferinde aynı seed ile)
        import random
        random.seed(game_id + str(round_number))  # Deterministik karıştırma
        
        options = [question.correct_option, question.wrong_option]
        random.shuffle(options)
        
        correct_index = options.index(question.correct_option)
        
        # Kim soruyor? (0,2,4,6 -> player1, 1,3,5,7 -> player2)
        asker_id = session.player1_id if round_number % 2 == 0 else session.player2_id
        
        return {
            "success": True,
            "round_number": round_number,
            "total_rounds": session.total_rounds,
            "question_text": question.question_text,
            "options": options,
            "correct_index": correct_index,  # Frontend'de SAKLANMAMALI
            "reel_id": question.reel_id,
            "news_title": question.news_title,
            "asker_id": asker_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{game_id}/answer/{round_number}")
async def answer_question(
    game_id: str,
    round_number: int,
    request: AnswerQuestionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Soruya cevap ver
    """
    try:
        session = game_service.get_game_session(game_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Game not found")
        
        if user_id not in [session.player1_id, session.player2_id]:
            raise HTTPException(status_code=403, detail="Not your game")
        
        if round_number >= len(session.questions):
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = session.questions[round_number]
        
        # Seçenekleri aynı şekilde karıştır (deterministik)
        import random
        random.seed(game_id + str(round_number))
        
        options = [question.correct_option, question.wrong_option]
        random.shuffle(options)
        
        correct_index = options.index(question.correct_option)
        
        # Cevap doğru mu?
        is_correct = request.selected_index == correct_index if not request.is_pass else False
        
        # Skoru güncelle
        result = game_service.answer_question(
            game_id=game_id,
            player_id=user_id,
            round_index=round_number,
            is_correct=is_correct
        )
        
        # Response mesajı
        if request.is_pass:
            response_message = question.pass_response
        elif is_correct:
            response_message = question.correct_response
        else:
            response_message = question.wrong_response
        
        # Emoji yorumu var mı?
        # TODO: Kullanıcının bu habere verdiği emoji'yi al ve emoji_responses'tan mesaj döndür
        emoji_comment = None
        
        return {
            "success": True,
            "is_correct": is_correct,
            "xp_earned": result["xp_earned"],
            "current_score": result["current_score"],
            "response_message": response_message,
            "emoji_comment": emoji_comment,
            "news_url": question.news_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{game_id}/result")
async def get_game_result(
    game_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Oyun sonucunu getir
    """
    try:
        session = game_service.get_game_session(game_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Game not found")
        
        if user_id not in [session.player1_id, session.player2_id]:
            raise HTTPException(status_code=403, detail="Not your game")
        
        if session.status != "finished":
            raise HTTPException(status_code=400, detail="Game not finished yet")
        
        # Kim kazandı?
        my_score = session.player1_score if user_id == session.player1_id else session.player2_score
        opponent_score = session.player2_score if user_id == session.player1_id else session.player1_score
        
        if my_score > opponent_score:
            result = "win"
            winner_id = user_id
        elif my_score < opponent_score:
            result = "lose"
            winner_id = session.player2_id if user_id == session.player1_id else session.player1_id
        else:
            result = "draw"
            winner_id = None
        
        # Bahsedilen haberler
        news_discussed = [
            {
                "reel_id": q.reel_id,
                "title": q.news_title,
                "url": q.news_url
            }
            for q in session.questions
        ]
        
        return {
            "success": True,
            "game_id": game_id,
            "winner_id": winner_id,
            "result": result,
            "my_score": my_score,
            "opponent_score": opponent_score,
            "total_xp_earned": my_score,  # Tüm skorlar XP
            "news_discussed": news_discussed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ GAME INFO ENDPOINTS ============

@router.get("/check-eligibility")
async def check_game_eligibility(
    user_id: str = Depends(get_current_user_id),
    days: int = 6,
    min_reels: int = 8
):
    """
    Kullanıcının oyun oynayabilir mi kontrol et
    """
    try:
        user_views = user_viewed_news_storage.get_user_views(
            user_id=user_id,
            days=days
        )
        
        current_count = len(user_views)
        eligible = current_count >= min_reels
        needed = max(0, min_reels - current_count)
        
        return {
            "success": True,
            "eligible": eligible,
            "current_count": current_count,
            "required": min_reels,
            "needed": needed,
            "message": (
                "Oyun oynayabilirsiniz!" if eligible
                else f"Daha {needed} haber izlemelisiniz."
            )
        }
        
    except Exception as e:
        print(f"❌ Check eligibility error: {e}")
        return {
            "success": False,
            "eligible": False,
            "message": f"Error: {str(e)}"
        }


# ============ DEBUG ENDPOINTS ============

@router.get("/debug/active-games")
async def debug_active_games():
    """Debug: Aktif oyunları göster"""
    try:
        games = []
        for game_id, session in game_service.active_games.items():
            games.append({
                "game_id": game_id,
                "status": session.status,
                "player1": session.player1_id,
                "player2": session.player2_id,
                "scores": f"{session.player1_score} - {session.player2_score}",
                "round": f"{session.current_round}/{session.total_rounds}"
            })
        
        return {
            "success": True,
            "active_games_count": len(games),
            "games": games
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        
        
# ============ YENİ ENDPOINT: QUEUE'YA KATIL ============
@router.post("/matchmaking/join", response_model=MatchmakingResponse)
async def join_matchmaking_queue(
    request: MatchmakingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Matchmaking queue'ya katıl ve BEKLE
    Eşleşme varsa hemen döner, yoksa queue'ya ekler
    """
    try:
        # 1. Uygunluk kontrolü
        user_views = user_viewed_news_storage.get_user_views(
            user_id=user_id,
            days=request.days
        )
        
        if len(user_views) < request.min_common_reels:
            return MatchmakingResponse(
                success=False,
                matched=False,
                message=f"Son {request.days} günde en az {request.min_common_reels} haber izlemelisiniz."
            )
        
        # 2. Matchable kullanıcıları bul
        matchable_users = user_viewed_news_storage.find_matchable_users(
            current_user_id=user_id,
            days=request.days,
            min_common_reels=request.min_common_reels
        )
        
        # 3. Queue'da bekleyen var mı kontrol et
        opponent_id = matchmaking_queue.find_match(user_id, matchable_users)
        
        if opponent_id:
            # ✅ Eşleşme bulundu! Oyun oluştur
            matchmaking_queue.remove_from_queue(opponent_id)
            
            game_session = await game_service.create_game_session(
                player1_id=user_id,
                player2_id=opponent_id,
                days=request.days,
                question_count=8
            )
            
            return MatchmakingResponse(
                success=True,
                matched=True,
                opponent_id=opponent_id,
                game_id=game_session.game_id,
                common_reels_count=len(game_session.questions),
                message="Rakip bulundu!"
            )
        
        else:
            # ❌ Eşleşme yok, queue'ya ekle
            added = matchmaking_queue.add_to_queue(
                user_id=user_id,
                days=request.days,
                min_common_reels=request.min_common_reels,
                common_reels_count=len(user_views)
            )
            
            return MatchmakingResponse(
                success=True,
                matched=False,
                estimated_wait_time_seconds=60,
                message="Rakip aranıyor..." if added else "Zaten aramada"
            )
        
    except Exception as e:
        print(f"❌ Matchmaking join error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ YENİ ENDPOINT: QUEUE DURUMU ============
@router.get("/matchmaking/status")
async def get_matchmaking_status(
    user_id: str = Depends(get_current_user_id)
):
    """
    Kullanıcının queue durumunu kontrol et
    Mobile polling için kullanılır
    """
    try:
        queue_info = matchmaking_queue.get_queue_info(user_id)
        
        if not queue_info:
            return {
                "success": True,
                "in_queue": False,
                "message": "Queue'da değilsiniz"
            }
        
        # Queue'dayken matchable kontrol et
        user_views = user_viewed_news_storage.get_user_views(
            user_id=user_id,
            days=6
        )
        
        matchable_users = user_viewed_news_storage.find_matchable_users(
            current_user_id=user_id,
            days=6,
            min_common_reels=8
        )
        
        # Eşleşme var mı?
        opponent_id = matchmaking_queue.find_match(user_id, matchable_users)
        
        if opponent_id:
            # Eşleşme bulundu! Oyun oluştur
            matchmaking_queue.remove_from_queue(user_id)
            matchmaking_queue.remove_from_queue(opponent_id)
            
            game_session = await game_service.create_game_session(
                player1_id=user_id,
                player2_id=opponent_id,
                days=6,
                question_count=8
            )
            
            return {
                "success": True,
                "matched": True,
                "game_id": game_session.game_id,
                "opponent_id": opponent_id,
                "message": "Rakip bulundu!"
            }
        
        return {
            "success": True,
            "in_queue": True,
            "matched": False,
            **queue_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ YENİ ENDPOINT: QUEUE'DAN ÇIKIŞ ============
@router.post("/matchmaking/cancel")
async def cancel_matchmaking(
    user_id: str = Depends(get_current_user_id)
):
    """
    Matchmaking'i iptal et, queue'dan çık
    """
    try:
        removed = matchmaking_queue.remove_from_queue(user_id)
        
        return {
            "success": True,
            "removed": removed,
            "message": "İptal edildi" if removed else "Zaten queue'da değildiniz"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))