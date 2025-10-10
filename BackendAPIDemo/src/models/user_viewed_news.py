"""
User Viewed News - Persistent Storage
Kullanıcıların izlediği haberleri JSON dosyada saklar
Oyun eşleştirmesi için son 6 günlük ortak haberleri bulur
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from pathlib import Path
import json
from collections import defaultdict
from pydantic import BaseModel, Field

# ============ MODELS ============

class UserViewedNews(BaseModel):
    """Kullanıcının izlediği tek bir haber kaydı"""
    user_id: str
    reel_id: str
    news_title: str
    news_url: str
    category: str
    keywords: List[str] = []
    viewed_at: datetime
    duration_ms: int
    completed: bool
    emoji_reaction: Optional[str] = None
    engagement_score: float = 0.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserViewStats(BaseModel):
    """Kullanıcının genel izlenme istatistikleri"""
    user_id: str
    total_views: int = 0
    completed_views: int = 0
    total_duration_ms: int = 0
    favorite_categories: Dict[str, int] = {}
    last_viewed_at: Optional[datetime] = None
    recent_keywords: List[str] = []


# ============ STORAGE SERVICE ============

class UserViewedNewsStorage:
    """
    Kullanıcıların izlediği haberleri persistent olarak saklar
    Oyun eşleştirmesi için ortak haber bulma fonksiyonları
    """
    
    def __init__(self, storage_path: str = "data/user_viewed_news.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Memory cache
        self.user_views: Dict[str, List[UserViewedNews]] = defaultdict(list)
        self.user_stats: Dict[str, UserViewStats] = {}
        
        # Load from file
        self._load_from_file()
    
    def _load_from_file(self):
        """JSON dosyadan yükle"""
        if not self.storage_path.exists():
            print("📁 No existing user_viewed_news.json, creating new")
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse user views
            for user_id, views_data in data.get('views', {}).items():
                self.user_views[user_id] = [
                    UserViewedNews(**view) for view in views_data
                ]
            
            # Parse user stats
            for user_id, stats_data in data.get('stats', {}).items():
                stats_data['last_viewed_at'] = datetime.fromisoformat(stats_data['last_viewed_at']) if stats_data.get('last_viewed_at') else None
                self.user_stats[user_id] = UserViewStats(**stats_data)
            
            print(f"✅ Loaded {len(self.user_views)} users' view history")
            
        except Exception as e:
            print(f"❌ Error loading user_viewed_news.json: {e}")
            self.user_views = defaultdict(list)
            self.user_stats = {}
    
    def _save_to_file(self):
        """JSON dosyaya kaydet"""
        try:
            data = {
                'views': {
                    user_id: [view.dict() for view in views]
                    for user_id, views in self.user_views.items()
                },
                'stats': {
                    user_id: stats.dict()
                    for user_id, stats in self.user_stats.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 Saved user_viewed_news.json ({len(self.user_views)} users)")
            
        except Exception as e:
            print(f"❌ Error saving user_viewed_news.json: {e}")
    
    # ============ CORE METHODS ============
    
    def add_view(
        self,
        user_id: str,
        reel_id: str,
        news_title: str,
        news_url: str,
        category: str,
        keywords: List[str],
        duration_ms: int,
        completed: bool,
        emoji_reaction: Optional[str] = None,
        engagement_score: float = 0.0
    ) -> UserViewedNews:
        """Yeni izlenme kaydı ekle"""
        
        view = UserViewedNews(
            user_id=user_id,
            reel_id=reel_id,
            news_title=news_title,
            news_url=news_url,
            category=category,
            keywords=keywords,
            viewed_at=datetime.now(),
            duration_ms=duration_ms,
            completed=completed,
            emoji_reaction=emoji_reaction,
            engagement_score=engagement_score
        )
        
        # Memory'e ekle
        self.user_views[user_id].append(view)
        
        # Stats güncelle
        self._update_user_stats(user_id, view)
        
        # Dosyaya kaydet
        self._save_to_file()
        
        return view
    
    def _update_user_stats(self, user_id: str, view: UserViewedNews):
        """Kullanıcı istatistiklerini güncelle"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserViewStats(user_id=user_id)
        
        stats = self.user_stats[user_id]
        stats.total_views += 1
        if view.completed:
            stats.completed_views += 1
        stats.total_duration_ms += view.duration_ms
        stats.last_viewed_at = view.viewed_at
        
        # Kategori sayacı
        if view.category not in stats.favorite_categories:
            stats.favorite_categories[view.category] = 0
        stats.favorite_categories[view.category] += 1
        
        # Son keywords (max 50)
        stats.recent_keywords.extend(view.keywords)
        stats.recent_keywords = stats.recent_keywords[-50:]
    
    # ============ QUERY METHODS ============
    
    def get_user_views(
        self,
        user_id: str,
        days: int = 6,
        min_engagement: float = 0.0
    ) -> List[UserViewedNews]:
        """
        Kullanıcının son N gündeki izlemelerini getir
        
        Args:
            user_id: Kullanıcı ID
            days: Kaç gün geriye git (default: 6)
            min_engagement: Minimum engagement score (0.0 - 1.0)
        """
        if user_id not in self.user_views:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_views = [
            view for view in self.user_views[user_id]
            if view.viewed_at >= cutoff_date
            and view.engagement_score >= min_engagement
        ]
        
        # En yeniden eskiye sırala
        filtered_views.sort(key=lambda v: v.viewed_at, reverse=True)
        
        return filtered_views
    
    def get_user_viewed_reel_ids(
        self,
        user_id: str,
        days: int = 6
    ) -> Set[str]:
        """Kullanıcının son N günde izlediği reel ID'leri (set)"""
        views = self.get_user_views(user_id, days=days)
        return {view.reel_id for view in views}
    
    def find_common_reels(
        self,
        user1_id: str,
        user2_id: str,
        days: int = 6,
        min_count: int = 8
    ) -> List[str]:
        """
        İki kullanıcının son N günde ortak izlediği reel ID'leri bul
        
        Args:
            user1_id: 1. kullanıcı
            user2_id: 2. kullanıcı
            days: Kaç gün geriye git
            min_count: Minimum ortak reel sayısı
        
        Returns:
            Ortak reel ID listesi (en az min_count tane varsa)
        """
        user1_reels = self.get_user_viewed_reel_ids(user1_id, days=days)
        user2_reels = self.get_user_viewed_reel_ids(user2_id, days=days)
        
        common_reels = user1_reels & user2_reels  # Set intersection
        
        if len(common_reels) >= min_count:
            return list(common_reels)
        else:
            return []
    
    def find_matchable_users(
        self,
        current_user_id: str,
        days: int = 6,
        min_common_reels: int = 8
    ) -> List[str]:
        """
        Mevcut kullanıcı ile eşleşebilecek (yeterli ortak haberi olan) kullanıcıları bul
        
        Args:
            current_user_id: Şu anki kullanıcı
            days: Son kaç gün
            min_common_reels: Minimum ortak reel sayısı
        
        Returns:
            Eşleşebilir kullanıcı ID listesi
        """
        matchable_users = []
        
        current_user_reels = self.get_user_viewed_reel_ids(current_user_id, days=days)
        
        # Tüm kullanıcıları tara
        for user_id in self.user_views.keys():
            if user_id == current_user_id:
                continue
            
            # Ortak reel sayısını kontrol et
            common_reels = self.find_common_reels(
                current_user_id,
                user_id,
                days=days,
                min_count=min_common_reels
            )
            
            if len(common_reels) >= min_common_reels:
                matchable_users.append(user_id)
        
        return matchable_users
    
    def get_user_stats_summary(self, user_id: str) -> Optional[UserViewStats]:
        """Kullanıcı istatistiklerini getir"""
        return self.user_stats.get(user_id)
    
    def cleanup_old_views(self, days: int = 30):
        """30+ gün önceki izlenmeleri temizle (performans için)"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for user_id in list(self.user_views.keys()):
            self.user_views[user_id] = [
                view for view in self.user_views[user_id]
                if view.viewed_at >= cutoff_date
            ]
            
            # Eğer hiç view kalmadıysa user'ı da sil
            if not self.user_views[user_id]:
                del self.user_views[user_id]
                if user_id in self.user_stats:
                    del self.user_stats[user_id]
        
        self._save_to_file()
        print(f"🧹 Cleaned up views older than {days} days")


# ============ GLOBAL INSTANCE ============

user_viewed_news_storage = UserViewedNewsStorage()