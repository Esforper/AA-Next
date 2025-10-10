"""
Game Service - Haber Kapışması Oyunu
AI ile senaryo üretimi, oyun state management, gerçek zamanlı oyun mantığı
OPTIMIZED: Hızlı AI çağrıları ve timeout önleme
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
        3. AI ile her haber için senaryo üret (PARALEL VE HIZLI!)
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
        
        # 5. AI ile tüm senaryoyu üret (HIZLI!)
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
    
    
    # ============ AI SCENARIO GENERATION (OPTIMIZED!) ============
    
    async def _generate_game_scenario(
        self,
        reels: List,
        player1_emojis: Dict[str, str],
        player2_emojis: Dict[str, str]
    ) -> List[GameQuestion]:
        """
        AI ile oyun senaryosu üret (tüm sorular)
        
        🚀 OPTIMIZATION:
        - Tek bir AI çağrısı ile TÜM soruları üret (paralel değil, batch!)
        - Timeout: 25 saniye (mobile'ın 30 saniye timeout'undan önce)
        - Hata durumunda fallback
        
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
            
            # TEK BİR PROMPT İLE TÜM SORULARI ÜRET!
            prompt = self._build_batch_ai_prompt(reels, player1_emojis, player2_emojis)
            
            print(f"🤖 Sending batch AI request for {len(reels)} questions...")
            
            # AI çağrısı (timeout: 25 saniye)
            response = await client.chat.completions.create(
                    model="gpt-4o-mini",  # Hızlı ve ucuz
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
                    temperature=0.7,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
            
            # Parse AI response
            ai_output = json.loads(response.choices[0].message.content)
            
            # AI'dan gelen soruları GameQuestion'a çevir
            questions = []
            ai_questions = ai_output.get("questions", [])
            
            for i, (reel, ai_q) in enumerate(zip(reels, ai_questions)):
                question = GameQuestion(
                    reel_id=reel.id,
                    news_title=reel.news_data.title,
                    news_url=reel.news_data.url,
                    question_text=ai_q.get("question", f"{reel.news_data.title[:50]}... biliyor muydun?"),
                    correct_option=ai_q.get("correct_option", "Evet biliyorum"),
                    wrong_option=ai_q.get("wrong_option", "Hayır duymadım"),
                    correct_response=ai_q.get("correct_response", "Evet evet!"),
                    wrong_response=ai_q.get("wrong_response", "Yanlış hatırlıyorsun sanki"),
                    pass_response=ai_q.get("pass_response", f"Haber: {reel.news_data.summary[:100]}..."),
                    emoji_responses=ai_q.get("emoji_responses", {})
                )
                questions.append(question)
            
            print(f"✅ AI scenario generated: {len(questions)} questions")
            return questions
            
        except asyncio.TimeoutError:
            print(f"⏱️ AI request timeout (25s exceeded), using fallback")
            return self._generate_fallback_scenario(reels, player1_emojis, player2_emojis)
            
        except Exception as e:
            print(f"❌ AI scenario generation failed: {e}")
            print("⚠️ Falling back to template-based scenario")
            return self._generate_fallback_scenario(reels, player1_emojis, player2_emojis)
    
    
    def _build_batch_ai_prompt(
        self,
        reels: List,
        player1_emojis: Dict[str, str],
        player2_emojis: Dict[str, str]
    ) -> str:
        """
        Tüm haberler için tek bir batch prompt oluştur
        
        Bu sayede tek bir AI çağrısı ile tüm soruları üretiyoruz!
        """
        
        news_list = []
        for i, reel in enumerate(reels):
            player_turn = 1 if i % 2 == 0 else 2
            p1_emoji = player1_emojis.get(reel.id)
            p2_emoji = player2_emojis.get(reel.id)
            
            news_list.append({
                "index": i,
                "title": reel.news_data.title,
                "summary": reel.news_data.summary[:200],
                "player_asking": player_turn,
                "asker_emoji": p1_emoji if player_turn == 1 else p2_emoji,
                "responder_emoji": p2_emoji if player_turn == 1 else p1_emoji
            })
        
        prompt = f"""
Bir haber quiz oyunu için {len(reels)} adet soru senaryosu oluştur.

HABERLER:
{json.dumps(news_list, ensure_ascii=False, indent=2)}

GÖREV:
Her haber için bir diyalog senaryosu üret. Player 1 ve Player 2 sırayla soru soruyor (0,2,4,6->P1, 1,3,5,7->P2).

Her soru için üret:
1. question: Soran kişinin sorusu (örn: "... biliyor muydun?")
2. correct_option: Doğru cevap seçeneği (habere uygun detay)
3. wrong_option: Yanlış cevap seçeneği (mantıklı ama yanlış detay)
4. correct_response: Doğru cevapta verilecek yanıt (örn: "Evet evet!")
5. wrong_response: Yanlış cevapta verilecek yanıt (örn: "Yok ya, öyle değildi")
6. pass_response: Pas geçilirse açıklama (haberin kısa özeti)
7. emoji_responses: Emoji'ye göre ekstra yorumlar (varsa)

ÖNEMLI:
- Samimi ve doğal Türkçe konuşma tarzı
- Kısa ve öz cevaplar (max 50-60 kelime)
- Emoji varsa yoruma dahil et
- Her haber için FARKLI sorular

JSON formatında dön:
{{
  "questions": [
    {{
      "question": "...",
      "correct_option": "...",
      "wrong_option": "...",
      "correct_response": "...",
      "wrong_response": "...",
      "pass_response": "...",
      "emoji_responses": {{"❤️": "...", "👍": "..."}}
    }},
    ...
  ]
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
        Hızlı ve güvenilir fallback
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
            # Başlık kısaltma
            short_title = reel.news_data.title[:60] + "..." if len(reel.news_data.title) > 60 else reel.news_data.title
            
            question = GameQuestion(
                reel_id=reel.id,
                news_title=reel.news_data.title,
                news_url=reel.news_data.url,
                question_text=random.choice(templates["question"]).format(title=short_title),
                correct_option=f"{reel.news_data.summary[:80]}..." if len(reel.news_data.summary) > 80 else reel.news_data.summary,
                wrong_option="Başka bir şey olmuştu sanki",
                correct_response=random.choice(templates["correct_response"]),
                wrong_response=random.choice(templates["wrong_response"]),
                pass_response=f"Haber şöyleydi: {reel.news_data.summary[:120]}...",
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
        
        return {
            "success": True,
            "current_round": session.current_round,
            "total_rounds": session.total_rounds,
            "player1_score": session.player1_score,
            "player2_score": session.player2_score,
            "game_finished": session.status == "finished"
        }
    
    
    def get_game_result(self, game_id: str, player_id: str) -> Dict:
        """Oyun sonucunu getir"""
        session = self.active_games.get(game_id)
        if not session:
            return {"success": False, "message": "Game not found"}
        
        if session.status != "finished":
            return {"success": False, "message": "Game not finished yet"}
        
        # Kim kazandı?
        if session.player1_score > session.player2_score:
            winner_id = session.player1_id
        elif session.player2_score > session.player1_score:
            winner_id = session.player2_id
        else:
            winner_id = None  # Berabere
        
        # Bu oyuncu için sonuç
        is_player1 = player_id == session.player1_id
        my_score = session.player1_score if is_player1 else session.player2_score
        opponent_score = session.player2_score if is_player1 else session.player1_score
        
        if winner_id == player_id:
            result = "win"
        elif winner_id is None:
            result = "draw"
        else:
            result = "lose"
        
        return {
            "success": True,
            "game_id": game_id,
            "winner_id": winner_id,
            "result": result,
            "my_score": my_score,
            "opponent_score": opponent_score,
            "total_xp_earned": my_score,
            "news_discussed": [
                {
                    "reel_id": q.reel_id,
                    "title": q.news_title,
                    "url": q.news_url
                }
                for q in session.questions
            ]
        }


# Global instance
game_service = GameService()