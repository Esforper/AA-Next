# backend/src/services/gamification_service.py

"""
Gamification Service - XP, Level, Node, Streak Management
Frontend'deki puan sisteminin backend karşılığı
JSON file-based persistent storage
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict
import json

from ..config import settings


class GamificationData:
    """Kullanıcı gamification verisi"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # XP & Level
        self.total_xp: int = 0
        self.current_level: int = 1
        self.current_node: int = 0  # 0-based (0 = ilk node)
        self.current_xp: int = 0     # Mevcut node'daki XP (0-100)
        
        # Streak
        self.current_streak: int = 0
        self.last_activity_date: Optional[str] = None  # ISO format date
        
        # Daily Progress
        self.daily_xp_goal: int = 300
        self.xp_earned_today: int = 0
        self.reels_watched_today: int = 0
        self.emojis_given_today: int = 0
        self.details_read_today: int = 0
        self.shares_given_today: int = 0
        
        # History
        self.xp_history: List[Dict] = []  # XP kazanma geçmişi
        self.level_history: List[Dict] = []  # Level atlama geçmişi
        
        # Achievements
        self.unlocked_achievements: List[str] = []
        
        # Timestamps
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür (JSON için)"""
        return {
            'user_id': self.user_id,
            'total_xp': self.total_xp,
            'current_level': self.current_level,
            'current_node': self.current_node,
            'current_xp': self.current_xp,
            'current_streak': self.current_streak,
            'last_activity_date': self.last_activity_date,
            'daily_xp_goal': self.daily_xp_goal,
            'xp_earned_today': self.xp_earned_today,
            'reels_watched_today': self.reels_watched_today,
            'emojis_given_today': self.emojis_given_today,
            'details_read_today': self.details_read_today,
            'shares_given_today': self.shares_given_today,
            'xp_history': self.xp_history,
            'level_history': self.level_history,
            'unlocked_achievements': self.unlocked_achievements,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GamificationData':
        """Dict'ten oluştur"""
        obj = cls(data['user_id'])
        obj.total_xp = data.get('total_xp', 0)
        obj.current_level = data.get('current_level', 1)
        obj.current_node = data.get('current_node', 0)
        obj.current_xp = data.get('current_xp', 0)
        obj.current_streak = data.get('current_streak', 0)
        obj.last_activity_date = data.get('last_activity_date')
        obj.daily_xp_goal = data.get('daily_xp_goal', 300)
        obj.xp_earned_today = data.get('xp_earned_today', 0)
        obj.reels_watched_today = data.get('reels_watched_today', 0)
        obj.emojis_given_today = data.get('emojis_given_today', 0)
        obj.details_read_today = data.get('details_read_today', 0)
        obj.shares_given_today = data.get('shares_given_today', 0)
        obj.xp_history = data.get('xp_history', [])
        obj.level_history = data.get('level_history', [])
        obj.unlocked_achievements = data.get('unlocked_achievements', [])
        obj.created_at = data.get('created_at', datetime.now().isoformat())
        obj.updated_at = data.get('updated_at', datetime.now().isoformat())
        return obj


class GamificationService:
    """
    Gamification Service - Main Logic
    
    Level System:
    - Her level'de farklı sayıda node var
    - Level 1: 2 node
    - Level 2-9: 3 node
    - Level 10+: 4 node
    - Her node 100 XP
    
    XP Sources:
    - Reel izleme: 10 XP
    - Emoji verme (ilk): 5 XP
    - Detay okuma: 15 XP
    - Share verme (ilk): 20 XP
    """
    
    def __init__(self):
        self.storage_dir = Path(settings.storage_base_path) / "gamification"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.storage_dir / "user_gamification.json"
        
        # Memory cache
        self.user_data: Dict[str, GamificationData] = {}
        
        # Load from file
        self._load_from_file()
        
        print("✅ Gamification Service initialized")
        print(f"📁 Storage: {self.data_file}")
        print(f"👥 Loaded: {len(self.user_data)} users")
    
    # ============ PERSISTENCE ============
    
    def _load_from_file(self):
        """JSON'dan yükle"""
        if not self.data_file.exists():
            print("📁 No existing gamification data, starting fresh")
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for user_id, user_dict in data.items():
                self.user_data[user_id] = GamificationData.from_dict(user_dict)
            
            print(f"✅ Loaded gamification data for {len(self.user_data)} users")
            
        except Exception as e:
            print(f"❌ Error loading gamification data: {e}")
            self.user_data = {}
    
    def _save_to_file(self):
        """JSON'a kaydet"""
        try:
            data = {
                user_id: user_data.to_dict()
                for user_id, user_data in self.user_data.items()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved gamification data for {len(data)} users")
            
        except Exception as e:
            print(f"❌ Error saving gamification data: {e}")
    
    # ============ USER DATA ============
    
    def _get_or_create_user(self, user_id: str) -> GamificationData:
        """Kullanıcı verisini al veya oluştur"""
        if user_id not in self.user_data:
            self.user_data[user_id] = GamificationData(user_id)
            self._save_to_file()
        return self.user_data[user_id]
    
    # ============ LEVEL CALCULATIONS ============
    
    def _get_nodes_in_level(self, level: int) -> int:
        """Bu level'de kaç node var?"""
        if level == 1:
            return 2
        elif level < 10:
            return 3
        else:
            return 4
    
    def _calculate_level_and_node(self, total_xp: int) -> tuple[int, int, int]:
        """
        Total XP'den level, node, current_xp hesapla
        
        Returns:
            (level, node, current_xp)
        """
        remaining_xp = total_xp
        level = 1
        
        while True:
            nodes_in_level = self._get_nodes_in_level(level)
            xp_for_level = nodes_in_level * 100
            
            if remaining_xp < xp_for_level:
                # Bu level'deyiz
                node = remaining_xp // 100
                current_xp = remaining_xp % 100
                return (level, node, current_xp)
            
            # Sonraki level'e geç
            remaining_xp -= xp_for_level
            level += 1
            
            # Safety: Max level 100
            if level > 100:
                return (100, 0, 0)
# ============ NODE MANAGEMENT ============
    
    def has_available_nodes(self, user_id: str, required_nodes: int = 1) -> bool:
        """
        Kullanıcının yeterli node'u var mı kontrol et
        
        Args:
            user_id: Kullanıcı ID
            required_nodes: Gereken node sayısı
            
        Returns:
            True: Yeterli node var
            False: Yetersiz node
        """
        user = self._get_or_create_user(user_id)
        has_nodes = user.current_node >= required_nodes
        
        print(f"🎮 [Node Check] User {user_id[:8]}: has {user.current_node} nodes, needs {required_nodes} → {has_nodes}")
        
        return has_nodes
    
    def spend_nodes(self, user_id: str, amount: int, reason: str = "game_entry") -> bool:
        """
        Node harca (XP'den düşerek)
        
        Args:
            user_id: Kullanıcı ID
            amount: Harcanacak node sayısı
            reason: Harcama nedeni
            
        Returns:
            True: Başarılı
            False: Yetersiz node
        """
        user = self._get_or_create_user(user_id)
        
        # Yeterli node var mı?
        if user.current_node < amount:
            print(f"❌ [Spend Node] User {user_id[:8]}: Insufficient nodes ({user.current_node} < {amount})")
            return False
        
        # Node'ları XP'ye çevir: 1 node = 100 XP
        xp_to_remove = amount * 100
        
        # Total XP'den düş (minimum 0)
        new_total_xp = max(0, user.total_xp - xp_to_remove)
        
        print(f"💸 [Spend Node] User {user_id[:8]}: Spending {amount} nodes ({xp_to_remove} XP)")
        print(f"   Before: Level {user.current_level}, Node {user.current_node}, Total XP {user.total_xp}")
        
        # Yeni level/node hesapla
        new_level, new_node, new_current_xp = self._calculate_level_and_node(new_total_xp)
        
        user.total_xp = new_total_xp
        user.current_level = new_level
        user.current_node = new_node
        user.current_xp = new_current_xp
        user.updated_at = datetime.now().isoformat()
        
        # XP history'ye ekle (negatif)
        user.xp_history.append({
            'timestamp': datetime.now().isoformat(),
            'xp_amount': -xp_to_remove,
            'source': f'spend_node_{reason}',
            'metadata': {'nodes_spent': amount},
            'total_xp_after': user.total_xp
        })
        
        print(f"   After: Level {new_level}, Node {new_node}, Total XP {new_total_xp}")
        print(f"✅ [Spend Node] Success!")
        
        # Kaydet
        self._save_to_file()
        
        return True
    
    def add_nodes(self, user_id: str, amount: int, source: str = "game_reward") -> Dict:
        """
        Node ekle (XP ekleyerek)
        
        Args:
            user_id: Kullanıcı ID
            amount: Eklenecek node sayısı
            source: Node kaynağı
            
        Returns:
            {
                'success': bool,
                'nodes_added': int,
                'total_xp': int,
                'current_level': int,
                'current_node': int
            }
        """
        user = self._get_or_create_user(user_id)
        
        # Node'ları XP'ye çevir: 1 node = 100 XP
        xp_amount = amount * 100
        
        print(f"🎁 [Add Node] User {user_id[:8]}: Adding {amount} nodes ({xp_amount} XP)")
        print(f"   Before: Level {user.current_level}, Node {user.current_node}, Total XP {user.total_xp}")
        
        # Önceki level'i kaydet
        old_level = user.current_level
        
        # XP ekle
        user.total_xp += xp_amount
        
        # Yeni level/node hesapla
        new_level, new_node, new_current_xp = self._calculate_level_and_node(user.total_xp)
        
        user.current_level = new_level
        user.current_node = new_node
        user.current_xp = new_current_xp
        user.updated_at = datetime.now().isoformat()
        
        # Level atladı mı?
        level_up = new_level > old_level
        
        # XP history'ye ekle
        user.xp_history.append({
            'timestamp': datetime.now().isoformat(),
            'xp_amount': xp_amount,
            'source': source,
            'metadata': {'nodes_added': amount},
            'total_xp_after': user.total_xp
        })
        
        if level_up:
            user.level_history.append({
                'timestamp': datetime.now().isoformat(),
                'old_level': old_level,
                'new_level': new_level
            })
            print(f"   🎉 LEVEL UP! {old_level} → {new_level}")
        
        print(f"   After: Level {new_level}, Node {new_node}, Total XP {user.total_xp}")
        print(f"✅ [Add Node] Success!")
        
        # Kaydet
        self._save_to_file()
        
        return {
            'success': True,
            'nodes_added': amount,
            'total_xp': user.total_xp,
            'current_level': user.current_level,
            'current_node': user.current_node,
            'level_up': level_up
        }


    # ============ XP MANAGEMENT ============
    
    async def add_xp(
        self,
        user_id: str,
        xp_amount: int,
        source: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        XP ekle ve level kontrolü yap
        
        Args:
            user_id: Kullanıcı ID
            xp_amount: Eklenecek XP miktarı
            source: XP kaynağı (reel_watch, emoji_given, etc)
            metadata: Ek bilgiler
        
        Returns:
            {
                'total_xp': int,
                'current_level': int,
                'current_node': int,
                'level_up': bool
            }
        """
        user = self._get_or_create_user(user_id)
        
        # Önceki level'i kaydet
        old_level = user.current_level
        
        # XP ekle
        user.total_xp += xp_amount
        user.xp_earned_today += xp_amount
        
        # Yeni level/node hesapla
        new_level, new_node, new_current_xp = self._calculate_level_and_node(user.total_xp)
        
        user.current_level = new_level
        user.current_node = new_node
        user.current_xp = new_current_xp
        
        # Level atladı mı?
        level_up = new_level > old_level
        
        # XP geçmişine ekle
        user.xp_history.append({
            'timestamp': datetime.now().isoformat(),
            'xp_amount': xp_amount,
            'source': source,
            'metadata': metadata,
            'total_xp_after': user.total_xp
        })
        
        # Level atlama geçmişi
        if level_up:
            user.level_history.append({
                'timestamp': datetime.now().isoformat(),
                'old_level': old_level,
                'new_level': new_level
            })
        
        # Streak güncelle
        self._update_streak(user)
        
        # Daily activity'ye göre artır
        if source == 'reel_watch':
            user.reels_watched_today += 1
        elif source == 'emoji_given':
            user.emojis_given_today += 1
        elif source == 'detail_read':
            user.details_read_today += 1
        elif source == 'share_given':
            user.shares_given_today += 1
        
        # Timestamp güncelle
        user.updated_at = datetime.now().isoformat()
        
        # Kaydet
        self._save_to_file()
        
        return {
            'total_xp': user.total_xp,
            'current_level': user.current_level,
            'current_node': user.current_node,
            'current_xp': user.current_xp,
            'level_up': level_up
        }
    
    # ============ STREAK MANAGEMENT ============
    
    def _update_streak(self, user: GamificationData):
        """Streak güncelle"""
        today = date.today().isoformat()
        
        if user.last_activity_date is None:
            # İlk aktivite
            user.current_streak = 1
            user.last_activity_date = today
        elif user.last_activity_date == today:
            # Bugün zaten aktivite var
            pass
        else:
            # Son aktivite tarihi
            last_date = date.fromisoformat(user.last_activity_date)
            days_diff = (date.today() - last_date).days
            
            if days_diff == 1:
                # Dün aktivite vardı, streak devam
                user.current_streak += 1
                user.last_activity_date = today
            elif days_diff > 1:
                # Streak kırıldı
                user.current_streak = 1
                user.last_activity_date = today
    
    # ============ GET METHODS ============
    
    async def get_level_data(self, user_id: str) -> Dict:
        """Level bilgilerini getir"""
        user = self._get_or_create_user(user_id)
        
        nodes_in_level = self._get_nodes_in_level(user.current_level)
        xp_needed = 100 - user.current_xp
        
        return {
            'current_level': user.current_level,
            'current_node': user.current_node,
            'nodes_in_level': nodes_in_level,
            'current_xp': user.current_xp,
            'xp_needed_for_next_node': xp_needed,
            'total_xp': user.total_xp
        }
    
    async def get_user_stats(self, user_id: str) -> Dict:
        """Kullanıcı istatistiklerini getir"""
        user = self._get_or_create_user(user_id)
        
        return {
            'total_xp': user.total_xp,
            'current_level': user.current_level,
            'current_streak': user.current_streak,
            'today_stats': {
                'reels_watched': user.reels_watched_today,
                'emojis_given': user.emojis_given_today,
                'details_read': user.details_read_today,
                'shares_given': user.shares_given_today,
                'xp_earned': user.xp_earned_today
            }
        }
    
    async def get_daily_progress(self, user_id: str) -> Dict:
        """Günlük ilerleme"""
        user = self._get_or_create_user(user_id)
        
        progress_pct = (user.xp_earned_today / user.daily_xp_goal) * 100
        goal_completed = user.xp_earned_today >= user.daily_xp_goal
        
        return {
            'xp_earned_today': user.xp_earned_today,
            'daily_goal': user.daily_xp_goal,
            'progress_percentage': min(100, progress_pct),
            'goal_completed': goal_completed
        }
    
    # ============ DAILY RESET ============
    
    async def reset_daily_progress(self, user_id: str):
        """Günlük ilerlemeyi sıfırla (gece yarısı cronjob)"""
        user = self._get_or_create_user(user_id)
        
        user.xp_earned_today = 0
        user.reels_watched_today = 0
        user.emojis_given_today = 0
        user.details_read_today = 0
        user.shares_given_today = 0
        
        user.updated_at = datetime.now().isoformat()
        self._save_to_file()
    
    # ============ LEADERBOARD ============
    
    async def get_leaderboard(self, timeframe: str = "all_time", limit: int = 100) -> List[Dict]:
        """
        Leaderboard getir
        
        Args:
            timeframe: 'all_time', 'monthly', 'weekly'
            limit: Kaç kullanıcı döndürülecek
        """
        # Tüm kullanıcıları XP'ye göre sırala
        sorted_users = sorted(
            self.user_data.values(),
            key=lambda u: u.total_xp,
            reverse=True
        )[:limit]
        
        leaderboard = []
        for rank, user in enumerate(sorted_users, 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user.user_id,
                'total_xp': user.total_xp,
                'current_level': user.current_level,
                'current_streak': user.current_streak
            })
        
        return leaderboard
    
    async def get_user_rank(self, user_id: str) -> Dict:
        """Kullanıcının sıralamasını getir"""
        user = self._get_or_create_user(user_id)
        
        # Tüm kullanıcıları XP'ye göre sırala
        sorted_users = sorted(
            self.user_data.values(),
            key=lambda u: u.total_xp,
            reverse=True
        )
        
        # Kullanıcının sırasını bul
        rank = None
        for idx, u in enumerate(sorted_users, 1):
            if u.user_id == user_id:
                rank = idx
                break
        
        total_users = len(self.user_data)
        percentile = ((total_users - rank + 1) / total_users * 100) if rank else 0
        
        return {
            'rank': rank or total_users + 1,
            'total_users': total_users,
            'percentile': round(percentile, 1)
        }
    
    # ============ ACHIEVEMENTS ============
    
    async def get_achievements(self, user_id: str) -> Dict:
        """Kullanıcının başarımları"""
        user = self._get_or_create_user(user_id)
        
        # Basit achievement listesi
        all_achievements = [
            {'id': 'first_reel', 'name': 'İlk Adım', 'description': 'İlk haberi izle'},
            {'id': 'streak_7', 'name': '7 Günlük Seri', 'description': '7 gün üst üste giriş yap'},
            {'id': 'level_10', 'name': 'Deneyimli', 'description': 'Level 10\'a ulaş'},
            {'id': 'emoji_master', 'name': 'Emoji Ustası', 'description': '50 emoji ver'},
        ]
        
        # Unlock durumunu kontrol et
        for achievement in all_achievements:
            achievement['unlocked'] = achievement['id'] in user.unlocked_achievements
        
        return {
            'list': all_achievements,
            'total_unlocked': len(user.unlocked_achievements),
            'total_achievements': len(all_achievements)
        }
    
    async def unlock_achievement(self, user_id: str, achievement_id: str) -> Dict:
        """Başarım unlock"""
        user = self._get_or_create_user(user_id)
        
        if achievement_id not in user.unlocked_achievements:
            user.unlocked_achievements.append(achievement_id)
            user.updated_at = datetime.now().isoformat()
            self._save_to_file()
            
            return {
                'unlocked': True,
                'achievement': {'id': achievement_id}
            }
        
        return {
            'unlocked': False,
            'achievement': {'id': achievement_id}
        }
    
    # ============ SYNC ============
    
    async def sync_state(self, user_id: str, local_state: Dict) -> Dict:
        """
        Frontend state'ini backend ile senkronize et
        Conflict varsa backend öncelikli
        """
        user = self._get_or_create_user(user_id)
        
        # Backend state'i döndür (backend öncelikli)
        return user.to_dict()


# Global instance
gamification_service = GamificationService()