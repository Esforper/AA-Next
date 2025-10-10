"""
Game Service - Haber Kapışması Oyunu
AI ile senaryo üretimi, oyun state management, gerçek zamanlı oyun mantığı
"""

import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import asyncio

from ..models.user_viewed_news import user_viewed_news_storage
from ..services.reels_analytics import reels_analytics
from ..config import settings


# ============ GAME STATE MODELS ============

class GameQuestion:
    """Bir haber için üretilen soru"""
    def __init__(
        self,
        reel_id: str,
        news_title: str,
        news_url: str,
        question_text: str,
        correct_option: str,
        wrong_option: str,
        correct_response: str,
        wrong_response: str,
        pass_response: str,
        emoji_responses: Dict[str, str] = None
    ):
        self.reel_id = reel_id
        self.news_title = news_title
        self.news_url = news_url
        self.question_text = question_text
        self.correct_option = correct_option
        self.wrong_option = wrong_option
        self.correct_response = correct_response
        self.wrong_response = wrong_response
        self.pass_response = pass_response
        self.emoji_responses = emoji_responses or {}


class GameSession:
    """Bir oyun oturumu"""
    def __init__(
        self,
        game_id: str,
        player1_id: str,
        player2_id: str,
        questions: List[GameQuestion]
    ):
        self.game_id = game_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.questions = questions
        
        # Skorlar
        self.player1_score = 0
        self.player2_score = 0
        
        # Oyun durumu
        self.current_round = 0
        self.total_rounds = len(questions)
        self.status = "waiting"  # waiting, active, finished
        
        # Zaman
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        
        # Oyun geçmişi
        self.round_history: List[Dict] = []


# ============ GAME SERVICE ============

class GameService:
    """
    Oyun servis katmanı
    
    Sorumluluklar:
    - Oyun oturumu oluşturma
    - AI ile senaryo üretimi
    - Oyun state management
    - XP hesaplama
    """
    
    def __init__(self):
        # Aktif oyunlar (memory'de)
        self.active_games: Dict[str, GameSession] = {}
        
        # Oyun geçmişi storage path
        self.storage_dir = Path(settings.storage_base_path) / "games"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Game Service initialized")
    
    
    # ============ GAME CREATION ============
    
    async def create_game_session(
        self,
        player1_id: str,
        player2_id: str,
        days: int = 6,
        question_count: int = 8
    ) -> GameSession:
        """
        Yeni oyun oturumu oluştur
        
        Steps:
        1. Ortak haberleri bul
        2. Rastgele 8 haber seç
        3. AI ile her haber için senaryo üret
        4. GameSession oluştur
        
        Args:
            player1_id: 1. oyuncu
            player2_id: 2. oyuncu
            days: Son kaç gün (default: 6)
            question_count: Kaç haber (default: 8)
        
        Returns:
            GameSession instance
        """
        print(f"🎮 Creating game: {player1_id} vs {player2_id}")
        
        # 1. Ortak haberleri bul
        common_reel_ids = user_viewed_news_storage.find_common_reels(
            user1_id=player1_id,
            user2_id=player2_id,
            days=days,
            min_count=question_count
        )
        
        if len(common_reel_ids) < question_count:
            raise ValueError(
                f"Not enough common reels. Found: {len(common_reel_ids)}, "
                f"Required: {question_count}"
            )
        
        # 2. Rastgele 8 haber seç
        selected_reel_ids = random.sample(common_reel_ids, question_count)
        
        # 3. Her haber için reel bilgilerini al
        selected_reels = []
        for reel_id in selected_reel_ids:
            reel = await reels_analytics.get_reel_by_id(reel_id)
            if reel:
                selected_reels.append(reel)
        
        if len(selected_reels) < question_count:
            raise ValueError("Some reels not found in database")
        
        # 4. Her oyuncu için emoji bilgilerini al
        player1_emojis = self._get_user_emojis_for_reels(
            player1_id, 
            selected_reel_ids
        )
        player2_emojis = self._get_user_emojis_for_reels(
            player2_id, 
            selected_reel_ids
        )
        
        # 5. AI ile tüm senaryoyu üret
        questions = await self._generate_game_scenario(
            selected_reels,
            player1_emojis,
            player2_emojis
        )
        
        # 6. Game ID oluştur
        game_id = f"game_{player1_id[:8]}_{player2_id[:8]}_{int(datetime.now().timestamp())}"
        
        # 7. GameSession oluştur
        session = GameSession(
            game_id=game_id,
            player1_id=player1_id,
            player2_id=player2_id,
            questions=questions
        )
        
        # 8. Memory'e kaydet
        self.active_games[game_id] = session
        
        print(f"✅ Game created: {game_id} with {len(questions)} questions")
        
        return session
    
    
    def _get_user_emojis_for_reels(
        self,
        user_id: str,
        reel_ids: List[str]
    ) -> Dict[str, str]:
        """
        Kullanıcının belirli reels'e verdiği emojileri getir
        
        Returns:
            {reel_id: emoji} dict
        """
        user_views = user_viewed_news_storage.get_user_views(user_id, days=30)
        
        emoji_map = {}
        for view in user_views:
            if view.reel_id in reel_ids and view.emoji_reaction:
                emoji_map[view.reel_id] = view.emoji_reaction
        
        return emoji_map
    
    
    # ============ AI SCENARIO GENERATION ============
    
    async def _generate_game_scenario(
        self,
        reels: List,
        player1_emojis: Dict[str, str],
        player2_emojis: Dict[str, str]
    ) -> List[GameQuestion]:
        """
        AI ile oyun senaryosu üret (tüm sorular)
        
        OpenAI kullanarak:
        - Her haber için bir soru
        - 2 seçenek (1 doğru, 1 yanlış)
        - Doğru/yanlış cevap mesajları
        - Emoji bazlı yorumlar
        - Pas geçme mesajları
        
        Args:
            reels: Seçilen haberler
            player1_emojis: 1. oyuncunun emojileri
            player2_emojis: 2. oyuncunun emojileri
        
        Returns:
            List[GameQuestion]
        """
        # OpenAI kullanmak için check
        if not hasattr(settings, 'openai_api_key') or not settings.openai_api_key:
            print("⚠️ OpenAI API key not found, using fallback scenario generator")
            return self._generate_fallback_scenario(reels, player1_emojis, player2_emojis)
        
        try:
            # OpenAI import (lazy)
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            # Her haber için prompt oluştur ve AI'dan senaryo al
            questions = []
            
            for i, reel in enumerate(reels):
                player_turn = 1 if i % 2 == 0 else 2  # Sırayla oyuncular sorar
                
                # Bu habere emoji var mı?
                p1_emoji = player1_emojis.get(reel.id)
                p2_emoji = player2_emojis.get(reel.id)
                
                # AI prompt
                prompt = self._build_ai_prompt(
                    reel=reel,
                    player_turn=player_turn,
                    asker_emoji=p1_emoji if player_turn == 1 else p2_emoji,
                    responder_emoji=p2_emoji if player_turn == 1 else p1_emoji
                )
                
                # AI çağrısı
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",  # Ucuz ve hızlı
                    messages=[
                        {
                            "role": "system",
                            "content": "Sen Türkçe haber quiz oyunu için doğal ve samimi diyaloglar üreten bir asistansın. Cevaplar konuşma tarzında, kısa ve doğal olmalı."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                # Parse AI response
                ai_output = json.loads(response.choices[0].message.content)
                
                # GameQuestion oluştur
                question = GameQuestion(
                    reel_id=reel.id,
                    news_title=reel.news_data.title,
                    news_url=reel.news_data.url,
                    question_text=ai_output.get("question", "Bu haberi duydun mu?"),
                    correct_option=ai_output.get("correct_option", "Evet biliyorum"),
                    wrong_option=ai_output.get("wrong_option", "Hayır duymadım"),
                    correct_response=ai_output.get("correct_response", "Evet evet!"),
                    wrong_response=ai_output.get("wrong_response", "Yanlış hatırlıyorsun sanki"),
                    pass_response=ai_output.get("pass_response", "Şöyle olmuştu aslında..."),
                    emoji_responses=ai_output.get("emoji_responses", {})
                )
                
                questions.append(question)
                
                # Rate limit için kısa bekleme
                await asyncio.sleep(0.3)
            
            print(f"✅ AI scenario generated: {len(questions)} questions")
            return questions
            
        except Exception as e:
            print(f"❌ AI scenario generation failed: {e}")
            print("⚠️ Falling back to template-based scenario")
            return self._generate_fallback_scenario(reels, player1_emojis, player2_emojis)
    
    
    def _build_ai_prompt(
        self,
        reel,
        player_turn: int,
        asker_emoji: Optional[str],
        responder_emoji: Optional[str]
    ) -> str:
        """AI için prompt oluştur"""
        
        news_title = reel.news_data.title
        news_summary = reel.news_data.summary
        
        prompt = f"""
Bir haber quiz oyunu için diyalog senaryosu oluştur.

HABER:
Başlık: {news_title}
Özet: {news_summary}

GÖREV:
Player {player_turn} bu haberi Player {3-player_turn}'e soruyor.

Üret:
1. question: Soran kişinin sorusu (örn: "... biliyor muydun?")
2. correct_option: Doğru cevap seçeneği (habere uygun detay)
3. wrong_option: Yanlış cevap seçeneği (mantıklı ama yanlış detay)
4. correct_response: Doğru cevapta verilecek yanıt (örn: "Evet evet duydum!")
5. wrong_response: Yanlış cevapta verilecek yanıt (örn: "Yok ya, böyle değildi")
6. pass_response: Pas geçilirse açıklama (haberin özeti)
7. emoji_responses: Emoji'ye göre ekstra yorumlar

{f"Soran kişinin emojisi: {asker_emoji}" if asker_emoji else ""}
{f"Cevaplayan kişinin emojisi: {responder_emoji}" if responder_emoji else ""}

ÖNEMLI:
- Samimi ve doğal konuşma tarzı
- Kısa ve öz cevaplar
- Emoji varsa yoruma dahil et (örn: "Baya sevmişsin bu haberi 😊")

JSON formatında dön:
{{
  "question": "...",
  "correct_option": "...",
  "wrong_option": "...",
  "correct_response": "...",
  "wrong_response": "...",
  "pass_response": "...",
  "emoji_responses": {{
    "❤️": "...",
    "👍": "..."
  }}
}}
"""
        return prompt
    
    
    def _generate_fallback_scenario(
        self,
        reels: List,
        player1_emojis: Dict[str, str],
        player2_emojis: Dict[str, str]
    ) -> List[GameQuestion]:
        """
        AI yoksa template-based senaryo üret
        """
        questions = []
        
        templates = {
            "question": [
                "{title} haberini duydun mu?",
                "Bu haberi gördün mü: {title}?",
                "{title} hakkında ne biliyorsun?",
            ],
            "correct_response": [
                "Evet evet, ben de gördüm!",
                "Aynen öyle!",
                "Doğru doğru!",
            ],
            "wrong_response": [
                "Yok ya, öyle değildi sanki",
                "Yanlış hatırlıyorsun galiba",
                "Böyle olmamıştı diye hatırlıyorum",
            ]
        }
        
        for i, reel in enumerate(reels):
            question = GameQuestion(
                reel_id=reel.id,
                news_title=reel.news_data.title,
                news_url=reel.news_data.url,
                question_text=random.choice(templates["question"]).format(
                    title=reel.news_data.title[:50]
                ),
                correct_option=f"{reel.news_data.summary[:80]}...",
                wrong_option="Başka bir şey olmuştu sanki",
                correct_response=random.choice(templates["correct_response"]),
                wrong_response=random.choice(templates["wrong_response"]),
                pass_response=f"Haber şöyleydi: {reel.news_data.summary[:100]}...",
                emoji_responses={}
            )
            questions.append(question)
        
        print(f"✅ Fallback scenario generated: {len(questions)} questions")
        return questions
    
    
    # ============ GAME STATE MANAGEMENT ============
    
    def get_game_session(self, game_id: str) -> Optional[GameSession]:
        """Oyun oturumunu getir"""
        return self.active_games.get(game_id)
    
    
    def start_game(self, game_id: str) -> bool:
        """Oyunu başlat"""
        session = self.active_games.get(game_id)
        if not session:
            return False
        
        session.status = "active"
        session.started_at = datetime.now()
        return True
    
    
    def answer_question(
        self,
        game_id: str,
        player_id: str,
        round_index: int,
        is_correct: bool
    ) -> Dict:
        """
        Soruya cevap ver ve skoru güncelle
        
        Returns:
            Round sonucu
        """
        session = self.active_games.get(game_id)
        if not session:
            return {"success": False, "message": "Game not found"}
        
        # Skor güncelle
        if is_correct:
            if player_id == session.player1_id:
                session.player1_score += 20  # 20 XP per correct
            else:
                session.player2_score += 20
        
        # Round history'ye ekle
        session.round_history.append({
            "round": round_index,
            "player_id": player_id,
            "is_correct": is_correct,
            "timestamp": datetime.now().isoformat()
        })
        
        # Round ilerlet
        session.current_round += 1
        
        # Oyun bitti mi?
        if session.current_round >= session.total_rounds:
            session.status = "finished"
            session.finished_at = datetime.now()
            self._save_game_to_history(session)
        
        return {
            "success": True,
            "is_correct": is_correct,
            "xp_earned": 20 if is_correct else 0,
            "current_score": (
                session.player1_score if player_id == session.player1_id 
                else session.player2_score
            )
        }
    
    
    def _save_game_to_history(self, session: GameSession):
        """Bitmiş oyunu geçmişe kaydet"""
        try:
            game_file = self.storage_dir / f"{session.game_id}.json"
            
            game_data = {
                "game_id": session.game_id,
                "player1_id": session.player1_id,
                "player2_id": session.player2_id,
                "player1_score": session.player1_score,
                "player2_score": session.player2_score,
                "total_rounds": session.total_rounds,
                "created_at": session.created_at.isoformat(),
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "finished_at": session.finished_at.isoformat() if session.finished_at else None,
                "news_discussed": [
                    {
                        "reel_id": q.reel_id,
                        "title": q.news_title,
                        "url": q.news_url
                    }
                    for q in session.questions
                ],
                "round_history": session.round_history
            }
            
            with open(game_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Game saved to history: {session.game_id}")
            
            # Memory'den sil
            if session.game_id in self.active_games:
                del self.active_games[session.game_id]
                
        except Exception as e:
            print(f"❌ Failed to save game history: {e}")


# ============ GLOBAL INSTANCE ============

game_service = GameService()