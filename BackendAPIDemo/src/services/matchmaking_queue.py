# BackendAPIDemo/src/services/matchmaking_queue.py
"""
Matchmaking Queue - Hafıza Tabanlı Basit Queue Sistemi
Az kod çok iş: Bekleyen oyuncuları yönet, eşleştir
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio


@dataclass
class QueueEntry:
    """Queue'da bekleyen oyuncu"""
    user_id: str
    days: int
    min_common_reels: int
    joined_at: datetime
    common_reels_count: int = 0  # Cache için


class MatchmakingQueue:
    """
    Basit hafıza tabanlı matchmaking queue
    Gerçek zamanlı eşleştirme için yeterli
    """
    
    def __init__(self):
        self.queue: Dict[str, QueueEntry] = {}  # user_id -> entry
        self.timeout_seconds = 60  # 60 saniye timeout
        print("✅ Matchmaking Queue initialized")
    
    
    def add_to_queue(
        self, 
        user_id: str, 
        days: int, 
        min_common_reels: int,
        common_reels_count: int = 0
    ) -> bool:
        """
        Kullanıcıyı queue'ya ekle
        Returns: True if added, False if already in queue
        """
        if user_id in self.queue:
            # Zaten queue'da
            return False
        
        self.queue[user_id] = QueueEntry(
            user_id=user_id,
            days=days,
            min_common_reels=min_common_reels,
            joined_at=datetime.now(),
            common_reels_count=common_reels_count
        )
        
        print(f"➕ Added to queue: {user_id} (Queue size: {len(self.queue)})")
        return True
    
    
    def remove_from_queue(self, user_id: str) -> bool:
        """
        Kullanıcıyı queue'dan çıkar
        Returns: True if removed, False if not in queue
        """
        if user_id in self.queue:
            del self.queue[user_id]
            print(f"➖ Removed from queue: {user_id} (Queue size: {len(self.queue)})")
            return True
        return False
    
    
    def find_match(self, user_id: str, matchable_users: List[str]) -> Optional[str]:
        """
        Queue'daki matchable kullanıcıları kontrol et
        
        Args:
            user_id: Eşleşme arayan kullanıcı
            matchable_users: Bu kullanıcı ile eşleşebilecek user_id listesi
        
        Returns:
            Eşleşen user_id veya None
        """
        # Queue'da olan matchable kullanıcıları bul
        for candidate_id in matchable_users:
            if candidate_id in self.queue and candidate_id != user_id:
                print(f"🎯 Match found: {user_id} <-> {candidate_id}")
                return candidate_id
        
        return None
    
    
    def get_queue_info(self, user_id: str) -> Optional[Dict]:
        """
        Kullanıcının queue bilgisini getir
        """
        entry = self.queue.get(user_id)
        if not entry:
            return None
        
        wait_time = (datetime.now() - entry.joined_at).seconds
        remaining_time = max(0, self.timeout_seconds - wait_time)
        
        return {
            "user_id": entry.user_id,
            "wait_time_seconds": wait_time,
            "remaining_time_seconds": remaining_time,
            "queue_position": list(self.queue.keys()).index(user_id) + 1,
            "queue_size": len(self.queue)
        }
    
    
    def cleanup_expired(self):
        """
        Timeout olan kullanıcıları temizle
        """
        now = datetime.now()
        expired = [
            user_id for user_id, entry in self.queue.items()
            if (now - entry.joined_at).seconds > self.timeout_seconds
        ]
        
        for user_id in expired:
            self.remove_from_queue(user_id)
            print(f"⏱️ Timeout: {user_id}")
        
        return len(expired)
    
    
    def get_queue_size(self) -> int:
        """Queue boyutunu döndür"""
        return len(self.queue)
    
    
    def is_in_queue(self, user_id: str) -> bool:
        """Kullanıcı queue'da mı?"""
        return user_id in self.queue


# Global singleton instance
matchmaking_queue = MatchmakingQueue()


# Background task: Her 10 saniyede expired temizle
async def cleanup_task():
    """Background task: Expired entries temizle"""
    while True:
        await asyncio.sleep(10)
        matchmaking_queue.cleanup_expired()