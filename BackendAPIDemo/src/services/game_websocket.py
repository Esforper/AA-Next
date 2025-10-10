"""
Game WebSocket Manager - Gerçek Zamanlı Oyun İletişimi
Her oyun için ayrı "room" yönetimi
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import json
from datetime import datetime
import asyncio


class GameRoom:
    """Bir oyun odası - 2 oyuncu için"""
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.connections: Dict[str, WebSocket] = {}  # {user_id: websocket}
        self.player_ids: Set[str] = set()
        self.created_at = datetime.now()
    
    async def add_player(self, user_id: str, websocket: WebSocket):
        """Oyuncuyu odaya ekle"""
        self.connections[user_id] = websocket
        self.player_ids.add(user_id)
        print(f"✅ Player {user_id[:8]} joined room {self.game_id}")
        
        # Diğer oyuncuya haber ver
        await self.broadcast({
            "type": "player_joined",
            "player_id": user_id,
            "total_players": len(self.connections)
        }, exclude_user=user_id)
    
    async def remove_player(self, user_id: str):
        """Oyuncuyu odadan çıkar"""
        if user_id in self.connections:
            del self.connections[user_id]
            self.player_ids.discard(user_id)
            print(f"❌ Player {user_id[:8]} left room {self.game_id}")
            
            # Diğer oyuncuya haber ver
            await self.broadcast({
                "type": "player_left",
                "player_id": user_id,
                "total_players": len(self.connections)
            })
    
    async def send_to_player(self, user_id: str, message: dict):
        """Belirli bir oyuncuya mesaj gönder"""
        if user_id in self.connections:
            try:
                await self.connections[user_id].send_json({
                    **message,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"❌ Error sending to {user_id[:8]}: {e}")
    
    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """Tüm oyunculara mesaj gönder (opsiyonel exclude)"""
        for user_id, ws in list(self.connections.items()):
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await ws.send_json({
                    **message,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"❌ Error broadcasting to {user_id[:8]}: {e}")
    
    def is_full(self) -> bool:
        """Oda dolu mu? (2 oyuncu)"""
        return len(self.connections) >= 2
    
    def is_empty(self) -> bool:
        """Oda boş mu?"""
        return len(self.connections) == 0


class GameWebSocketManager:
    """
    Tüm oyun odalarını yönet
    
    Sorumluluklar:
    - Oyun odası oluşturma/silme
    - Oyuncuları odalara bağlama
    - Mesaj broadcast'i
    - Otomatik temizlik
    """
    
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}  # {game_id: GameRoom}
        print("✅ Game WebSocket Manager initialized")
    
    def get_or_create_room(self, game_id: str) -> GameRoom:
        """Oda yoksa oluştur, varsa getir"""
        if game_id not in self.rooms:
            self.rooms[game_id] = GameRoom(game_id)
            print(f"🏠 Created room for game {game_id}")
        
        return self.rooms[game_id]
    
    async def connect_player(self, game_id: str, user_id: str, websocket: WebSocket):
        """Oyuncuyu oyun odasına bağla"""
        await websocket.accept()
        
        room = self.get_or_create_room(game_id)
        await room.add_player(user_id, websocket)
        
        # Hoşgeldin mesajı
        await room.send_to_player(user_id, {
            "type": "connected",
            "game_id": game_id,
            "message": "WebSocket bağlantısı kuruldu"
        })
        
        return room
    
    async def disconnect_player(self, game_id: str, user_id: str):
        """Oyuncuyu oyun odasından çıkar"""
        if game_id in self.rooms:
            room = self.rooms[game_id]
            await room.remove_player(user_id)
            
            # Oda boşaldıysa sil
            if room.is_empty():
                del self.rooms[game_id]
                print(f"🗑️ Deleted empty room {game_id}")
    
    async def send_turn_update(self, game_id: str, data: dict):
        """Sıra değişimi mesajı gönder"""
        if game_id not in self.rooms:
            return
        
        room = self.rooms[game_id]
        await room.broadcast({
            "type": "turn_update",
            **data
        })
    
    async def send_answer_result(self, game_id: str, answering_player: str, data: dict):
        """Cevap sonucu mesajı gönder"""
        if game_id not in self.rooms:
            return
        
        room = self.rooms[game_id]
        
        # Cevap veren oyuncuya
        await room.send_to_player(answering_player, {
            "type": "answer_result",
            "for_me": True,
            **data
        })
        
        # Diğer oyuncuya (rakip cevap verdi)
        await room.broadcast({
            "type": "opponent_answered",
            "for_me": False,
            **data
        }, exclude_user=answering_player)
    
    async def send_new_question(self, game_id: str, data: dict):
        """Yeni soru mesajı gönder"""
        if game_id not in self.rooms:
            return
        
        room = self.rooms[game_id]
        await room.broadcast({
            "type": "new_question",
            **data
        })
    
    async def send_game_finished(self, game_id: str, data: dict):
        """Oyun bitti mesajı gönder"""
        if game_id not in self.rooms:
            return
        
        room = self.rooms[game_id]
        await room.broadcast({
            "type": "game_finished",
            **data
        })
    
    async def send_score_update(self, game_id: str, scores: dict):
        """Skor güncellemesi gönder"""
        if game_id not in self.rooms:
            return
        
        room = self.rooms[game_id]
        await room.broadcast({
            "type": "score_update",
            **scores
        })
    
    def get_room_status(self, game_id: str) -> Optional[dict]:
        """Oda durumunu getir"""
        if game_id not in self.rooms:
            return None
        
        room = self.rooms[game_id]
        return {
            "game_id": game_id,
            "connected_players": len(room.connections),
            "player_ids": list(room.player_ids),
            "is_full": room.is_full(),
            "created_at": room.created_at.isoformat()
        }
    
    async def cleanup_empty_rooms(self):
        """Boş odaları temizle (periyodik task)"""
        empty_rooms = [
            game_id for game_id, room in self.rooms.items()
            if room.is_empty()
        ]
        
        for game_id in empty_rooms:
            del self.rooms[game_id]
            print(f"🗑️ Cleaned up empty room {game_id}")


# Global instance
game_ws_manager = GameWebSocketManager()


# ============ PERIODIC CLEANUP TASK ============

async def cleanup_task():
    """Her 5 dakikada bir boş odaları temizle"""
    while True:
        await asyncio.sleep(300)  # 5 dakika
        await game_ws_manager.cleanup_empty_rooms()


# Uygulama başlangıcında bu task'ı başlatmak için:
# asyncio.create_task(cleanup_task())