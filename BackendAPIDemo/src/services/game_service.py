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
        # self.active_games[game_id] = session
        
        
        
        # 🆕 Oyunu otomatik başlat
        session.status = "active"  # waiting yerine
        session.started_at = datetime.now()

        # 8. Memory'e kaydet
        self.active_games[game_id] = session
        
        print(f"✅ Game created: {game_id} with {len(questions)} questions")
        print(f"🎮 Active games count: {len(self.active_games)}")
        
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
        # 🆕 Artık user_viewed_news_storage'ın yeni fonksiyonunu kullan
        return user_viewed_news_storage.get_user_emojis_for_reels(user_id, reel_ids)
    
    
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
            # 🔥 AI RESPONSE DETAYLI YAZDIRMA
            print("=" * 80)
            print("🤖 AI RESPONSE:")
            print("=" * 80)

            print(f"📄 Raw AI Output ({len(ai_output)} chars):")
            print(ai_output)
            print("=" * 80)

            # Parse AI response
            ai_output = json.loads(ai_output)

            # 🔥 PARSE EDİLMİŞ ÇIKTI
            print(f"✅ Parsed {len(ai_output.get('questions', []))} questions:")
            for i, q in enumerate(ai_output.get('questions', [])):
                print(f"\n📋 QUESTION {i}:")
                print(f"   Q: {q.get('question', 'N/A')[:80]}...")
                print(f"   ✓ Correct: {q.get('correct_option', 'N/A')[:50]}...")
                print(f"   ✗ Wrong: {q.get('wrong_option', 'N/A')[:50]}...")
                print(f"   💬 Response: {q.get('correct_response', 'N/A')}")
                if q.get('emoji_comment'):
                    print(f"   😊 Emoji: {q.get('emoji_comment')}")

            print("=" * 80)
            
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
        
        🆕 Emoji bazlı dinamik cevaplar içerir
        """
        
        news_list = []
        for i, reel in enumerate(reels):
            player_turn = 1 if i % 2 == 0 else 2
            p1_emoji = player1_emojis.get(reel.id)
            p2_emoji = player2_emojis.get(reel.id)
            
            # Soran kişinin emojisi
            asker_emoji = p1_emoji if player_turn == 1 else p2_emoji
            # Cevaplayan kişinin emojisi
            responder_emoji = p2_emoji if player_turn == 1 else p1_emoji
            
            news_list.append({
                "index": i,
                "title": reel.news_data.title,
                "summary": reel.news_data.summary[:300],
                "player_asking": player_turn,
                "asker_emoji": asker_emoji,
                "responder_emoji": responder_emoji  # 🔥 BU KULLANILACAK
            })
        
        prompt = f"""Sen bir haber quiz oyunu için SABİT FORMATTA cevaplar üreten bir asistansın.

        İKİ OYUNCU VAR:
        - Player 1 (Soru sıraları: 0, 2, 4, 6)
        - Player 2 (Soru sıraları: 1, 3, 5, 7)

        HABERLER ({len(reels)} adet):
        {json.dumps(news_list, ensure_ascii=False, indent=2)}

        GÖREV:
        Her haber için SABİT FORMATTA diyalog senaryosu oluştur.

        🔥 ÖNEMLİ KURALLAR:

        1. SORU FORMATI (DEĞİŞMEZ):
        "[Haber başlığı] haberini duydun mu?"

        2. CEVAP SEÇENEKLERİ:
        - DOĞRU seçenek: "Evet evet, [haberin gerçek bir detayı 40-60 kelime]"
        - YANLIŞ seçenek: "Hayır hayır, [mantıklı ama yanlış detay 40-60 kelime]"

        3. DOĞRU CEVAP MESAJI (SABİT):
        "Evet evet, doğru bildin!"

        4. YANLIŞ CEVAP MESAJI (DOĞRUYU SÖYLE):
        "Yok ya, yanlış hatırlıyorsun sanki. Doğrusu şöyleydi: [haberin gerçek özeti 30-50 kelime]"

        5. PAS GEÇ MESAJI:
        "Haber şöyleydi: [haberin özeti 30-50 kelime]"

        6. EMOJİ YORUMU (SADECE responder_emoji VARSA):
        - ❤️ → "Ben de çok beğenmiştim bu haberi!"
        - 😢 → "Gerçekten üzücüydü"
        - 👍 → "Aynen, çok iyi gelişme"
        - 😮 → "Ben de çok şaşırmıştım"
        - 😡 → "Gerçekten sinir bozucuydu"
        - 🔥 → "Çok heyecan vericiydi!"
        - Emoji yoksa: emoji_comment alanı null olmalı

        JSON formatında dön:
        {{
        "questions": [
            {{
            "question": "[Haber başlığı] haberini duydun mu?",
            "correct_option": "Evet evet, [gerçek detay]",
            "wrong_option": "Hayır hayır, [yanlış detay]",
            "correct_response": "Evet evet, doğru bildin!",
            "wrong_response": "Yok ya, yanlış hatırlıyorsun sanki. Doğrusu şöyleydi: [gerçek özet]",
            "pass_response": "Haber şöyleydi: [özet]",
            "emoji_comment": "Ben de çok beğenmiştim bu haberi!"
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
        is_correct: bool,
        is_pass: bool = False
    ) -> Dict:
        """
        Soruya cevap ver ve skoru güncelle
        
        Returns:
            Round sonucu
        """
        session = self.active_games.get(game_id)
        if not session:
            return {"success": False, "message": "Game not found"}
        
        # 🔥 Pas geçilmediyse skor güncelle
        if not is_pass and is_correct:
            if player_id == session.player1_id:
                session.player1_score += 20
            else:
                session.player2_score += 20
        
        # Round history'ye ekle
        session.round_history.append({
            "round": round_index,
            "player_id": player_id,
            "is_correct": is_correct,
            "is_pass": is_pass,
            "timestamp": datetime.now().isoformat()
        })
        
        # Round ilerlet
        session.current_round += 1
        
        # Oyun bitti mi?
        # Oyun bitti mi?
        if session.current_round >= session.total_rounds:
            session.status = "finished"
            session.finished_at = datetime.now()
            
            # ============ NODE ÖDÜLÜ HESAPLA (YENİ) ============
            print(f"🏁 [Game Finished] {game_id}")
            print(f"   Player1 ({session.player1_id[:8]}): {session.player1_score} points")
            print(f"   Player2 ({session.player2_id[:8]}): {session.player2_score} points")
            
            # Her oyuncu için node ödülü hesapla ve uygula
            self._apply_node_rewards(game_id, session)
            
            # Oyunu kaydet
            self._save_finished_game(session)
        
        # 🔥 FIX: current_score ekle!
        current_score = (session.player1_score if player_id == session.player1_id 
                        else session.player2_score)
        
        return {
            "success": True,
            "current_round": session.current_round,
            "total_rounds": session.total_rounds,
            "player1_score": session.player1_score,
            "player2_score": session.player2_score,
            "current_score": current_score,  # ✅ EKLENDI!
            "game_finished": session.status == "finished",
            "xp_earned": 20 if (not is_pass and is_correct) else 0
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



    def _calculate_node_reward(self, session: GameSession, player_id: str) -> int:
            """
            Oyuncu için node ödülünü hesapla
            
            Kurallar:
                4/4 doğru = +3 node
                3/4 doğru = +2 node
                2/4 doğru = 0 node
                0-1 doğru = -1 node
            """
            # Oyuncunun doğru cevap sayısını hesapla
            correct_count = 0
            
            for round_data in session.round_history:
                if round_data["player_id"] == player_id:
                    if round_data["is_correct"] and not round_data["is_pass"]:
                        correct_count += 1
            
            # Node ödülünü hesapla
            if correct_count == 4:
                reward = 3
            elif correct_count == 3:
                reward = 2
            elif correct_count == 2:
                reward = 0
            else:  # 0 veya 1
                reward = -1
            
            print(f"🎯 [Node Reward] Player {player_id[:8]}: {correct_count}/4 correct → {reward:+d} nodes")
            
            return reward
        
    def _apply_node_rewards(self, game_id: str, session: GameSession):
        """Her iki oyuncuya node ödülünü uygula"""
        from .gamification_service import gamification_service
        
        try:
            # Player 1
            player1_reward = self._calculate_node_reward(session, session.player1_id)
            if player1_reward > 0:
                gamification_service.add_nodes(
                    user_id=session.player1_id,
                    amount=player1_reward,
                    source="game_win"
                )
                print(f"   ✅ Player1 gained {player1_reward} nodes")
            elif player1_reward < 0:
                gamification_service.spend_nodes(
                    user_id=session.player1_id,
                    amount=abs(player1_reward),
                    reason="game_loss"
                )
                print(f"   ❌ Player1 lost {abs(player1_reward)} node(s)")
            else:
                print(f"   ➖ Player1 no node change")
            
            # Player 2
            player2_reward = self._calculate_node_reward(session, session.player2_id)
            if player2_reward > 0:
                gamification_service.add_nodes(
                    user_id=session.player2_id,
                    amount=player2_reward,
                    source="game_win"
                )
                print(f"   ✅ Player2 gained {player2_reward} nodes")
            elif player2_reward < 0:
                gamification_service.spend_nodes(
                    user_id=session.player2_id,
                    amount=abs(player2_reward),
                    reason="game_loss"
                )
                print(f"   ❌ Player2 lost {abs(player2_reward)} node(s)")
            else:
                print(f"   ➖ Player2 no node change")
                
        except Exception as e:
            print(f"⚠️ [Node Reward] Error applying rewards: {e}")



# ============ GAME HISTORY (YENİ BÖLÜM) ============

    def _save_finished_game(self, session: GameSession):
        """
        Bitmiş oyunu JSON dosyasına kaydet (oyun geçmişi için)
        """
        try:
            game_file = self.storage_dir / f"{session.game_id}.json"
            
            game_data = {
                "game_id": session.game_id,
                "player1_id": session.player1_id,
                "player2_id": session.player2_id,
                "player1_score": session.player1_score,
                "player2_score": session.player2_score,
                "winner_id": self._get_winner_id(session),
                "created_at": session.created_at.isoformat(),
                "finished_at": session.finished_at.isoformat() if session.finished_at else None,
                "total_rounds": session.total_rounds,
                "round_history": session.round_history,
                "news_discussed": [
                    {
                        "reel_id": q.reel_id,
                        "title": q.news_title,
                        "url": q.news_url
                    }
                    for q in session.questions
                ]
            }
            
            with open(game_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Game saved to history: {session.game_id}")
            
            # Memory'den sil (optional, oyun bittikten sonra)
            # del self.active_games[session.game_id]
            
        except Exception as e:
            print(f"❌ Error saving game to history: {e}")

    def _get_winner_id(self, session: GameSession) -> Optional[str]:
        """Kim kazandı?"""
        if session.player1_score > session.player2_score:
            return session.player1_id
        elif session.player2_score > session.player1_score:
            return session.player2_id
        return None  # Berabere

    def get_game_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Kullanıcının oyun geçmişini getir
        
        Args:
            user_id: Kullanıcı ID
            limit: Kaç oyun getir (default: 20)
        
        Returns:
            List[Dict] - Oyun geçmişi listesi
        """
        history = []
        
        try:
            # Tüm game dosyalarını tara
            for game_file in sorted(self.storage_dir.glob("game_*.json"), reverse=True):
                if len(history) >= limit:
                    break
                
                with open(game_file, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
                
                # Bu oyunda kullanıcı var mı?
                if user_id in [game_data.get("player1_id"), game_data.get("player2_id")]:
                    # Kullanıcı için sonuç hesapla
                    is_player1 = user_id == game_data.get("player1_id")
                    my_score = game_data.get("player1_score" if is_player1 else "player2_score", 0)
                    opponent_score = game_data.get("player2_score" if is_player1 else "player1_score", 0)
                    winner_id = game_data.get("winner_id")
                    
                    if winner_id == user_id:
                        result = "win"
                    elif winner_id is None:
                        result = "draw"
                    else:
                        result = "lose"
                    
                    history.append({
                        "game_id": game_data.get("game_id"),
                        "opponent_id": game_data.get("player2_id" if is_player1 else "player1_id"),
                        "result": result,
                        "my_score": my_score,
                        "opponent_score": opponent_score,
                        "played_at": game_data.get("finished_at", game_data.get("created_at")),
                        "news_count": len(game_data.get("news_discussed", []))
                    })
        
        except Exception as e:
            print(f"❌ Error loading game history: {e}")
        
        return history

    def get_game_detail(self, game_id: str) -> Optional[Dict]:
        """
        Belirli bir oyunun detayını getir (geçmişten)
        
        Returns:
            Game detail dict veya None
        """
        try:
            game_file = self.storage_dir / f"{game_id}.json"
            
            if not game_file.exists():
                return None
            
            with open(game_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            print(f"❌ Error loading game detail: {e}")
            return None



    def _calculate_node_reward(self, game_id: str, player_id: str) -> int:
            """
            Oyuncu için node ödülünü hesapla
            
            Args:
                game_id: Oyun ID
                player_id: Oyuncu ID
                
            Returns:
                Node ödülü (-1, 0, 2, 3)
                
            Kurallar:
                4/4 doğru = +3 node
                3/4 doğru = +2 node
                2/4 doğru = 0 node
                0-1 doğru = -1 node
            """
            session = self.active_games.get(game_id)
            if not session:
                return 0
            
            # Oyuncunun doğru cevap sayısını hesapla
            correct_count = 0
            
            for round_data in session.round_history:
                if round_data["player_id"] == player_id:
                    if round_data["is_correct"] and not round_data["is_pass"]:
                        correct_count += 1
            
            # Node ödülünü hesapla
            if correct_count == 4:
                reward = 3
            elif correct_count == 3:
                reward = 2
            elif correct_count == 2:
                reward = 0
            else:  # 0 veya 1
                reward = -1
            
            print(f"🎯 [Node Reward] Player {player_id[:8]}: {correct_count}/4 correct → {reward:+d} nodes")
            
            return reward



# Global instance
game_service = GameService()