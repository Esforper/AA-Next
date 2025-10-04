# ================================
# src/services/user_preference.py - User Preference Engine
# ================================

"""
User Preference Engine - Rule-based + NLP Hybrid

Kullanıcı tercihlerini yönetir:
- Kategori skorları (ekonomi: 0.85, spor: 0.3)
- Keyword skorları (dolar: 0.9, faiz: 0.88)
- Exponential moving average (son etkileşimler daha önemli)
- NLP vectorization desteği

Features:
- Lightweight (no heavy ML)
- Real-time updates
- Persistent storage
- Cold start handling
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import json
import math

from ..models.reels_tracking import ReelView, ReelFeedItem
from ..config import settings


class UserPreference:
    """
    Tek bir kullanıcının tercihleri
    
    Stores:
    - Category scores (ekonomi: 0.85)
    - Keyword scores (dolar: 0.9)
    - Total interactions
    - Last updated timestamp
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Kategori skorları (exponential moving average)
        self.category_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # Keyword skorları
        self.keyword_scores: Dict[str, float] = defaultdict(lambda: 0.3)
        
        # Yazar skorları (optional)
        self.author_scores: Dict[str, float] = defaultdict(lambda: 0.3)
        
        # Metadata
        self.total_interactions = 0
        self.last_updated = datetime.now()
        self.created_at = datetime.now()
    
    def update_category_score(self, category: str, weight: float):
        """
        Kategori skorunu güncelle (Exponential Moving Average)
        
        Args:
            category: Kategori adı
            weight: Engagement weight (0-1 arası)
        
        Formula: new_score = alpha * weight + (1-alpha) * old_score
        Alpha: Yeni verinin ağırlığı (0.3 = %30 yeni, %70 eski)
        """
        current = self.category_scores[category]
        
        # Exponential moving average
        alpha = 0.3  # Son etkileşim %30 ağırlık
        self.category_scores[category] = alpha * weight + (1 - alpha) * current
        
        self.total_interactions += 1
        self.last_updated = datetime.now()
    
    def update_keyword_score(self, keyword: str, weight: float):
        """
        Keyword skorunu güncelle
        
        Args:
            keyword: Anahtar kelime
            weight: Engagement weight
        """
        current = self.keyword_scores[keyword]
        alpha = 0.3
        self.keyword_scores[keyword] = alpha * weight + (1 - alpha) * current
    
    def update_author_score(self, author: str, weight: float):
        """
        Yazar skorunu güncelle
        
        Args:
            author: Yazar adı
            weight: Engagement weight
        """
        if not author:
            return
        
        current = self.author_scores[author]
        alpha = 0.25  # Yazar biraz daha yavaş öğrenilsin
        self.author_scores[author] = alpha * weight + (1 - alpha) * current
    
    def get_category_score(self, category: str) -> float:
        """Kategori skorunu al (0-1 arası)"""
        return self.category_scores.get(category, 0.5)
    
    def get_keyword_score(self, keyword: str) -> float:
        """Keyword skorunu al (0-1 arası)"""
        return self.keyword_scores.get(keyword, 0.3)
    
    def get_author_score(self, author: Optional[str]) -> float:
        """Yazar skorunu al (0-1 arası)"""
        if not author:
            return 0.3
        return self.author_scores.get(author, 0.3)
    
    def has_enough_data(self) -> bool:
        """Yeterli veri var mı personalization için"""
        return self.total_interactions >= 5
    
    def get_personalization_level(self) -> str:
        """
        Kullanıcının personalization seviyesi
        
        Returns:
            "cold": 0-10 etkileşim
            "warm": 10-50 etkileşim
            "hot": 50+ etkileşim
        """
        if self.total_interactions < 10:
            return "cold"
        elif self.total_interactions < 50:
            return "warm"
        else:
            return "hot"
    
    def to_dict(self) -> Dict:
        """Dict'e çevir (storage için)"""
        return {
            "user_id": self.user_id,
            "category_scores": dict(self.category_scores),
            "keyword_scores": dict(self.keyword_scores),
            "author_scores": dict(self.author_scores),
            "total_interactions": self.total_interactions,
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreference':
        """Dict'ten oluştur (load için)"""
        pref = cls(data["user_id"])
        pref.category_scores = defaultdict(lambda: 0.5, data.get("category_scores", {}))
        pref.keyword_scores = defaultdict(lambda: 0.3, data.get("keyword_scores", {}))
        pref.author_scores = defaultdict(lambda: 0.3, data.get("author_scores", {}))
        pref.total_interactions = data.get("total_interactions", 0)
        pref.last_updated = datetime.fromisoformat(data["last_updated"])
        pref.created_at = datetime.fromisoformat(data.get("created_at", data["last_updated"]))
        return pref


class UserPreferenceEngine:
    """
    User Preference Engine - Tüm kullanıcıların tercihlerini yönetir
    
    Usage:
    1. Her view sonrası update: update_from_view()
    2. Feed generation'da scoring: predict_reel_score()
    3. Detail view'da boost: boost_from_detail_view()
    """
    
    def __init__(self):
        # In-memory cache
        self.user_preferences: Dict[str, UserPreference] = {}
        
        # Storage
        self.storage_dir = Path(settings.storage_base_path) / "user_profiles"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ User Preference Engine initialized")
        print(f"   Storage: {self.storage_dir}")
    
    def get_or_create_preference(self, user_id: str) -> UserPreference:
        """
        Kullanıcı preference'ını al veya oluştur
        
        Args:
            user_id: Kullanıcı ID
        
        Returns:
            UserPreference instance
        """
        # Cache'de var mı?
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # Disk'ten yükle
        user_file = self.storage_dir / f"{user_id}.json"
        if user_file.exists():
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                pref = UserPreference.from_dict(data)
                self.user_preferences[user_id] = pref
                return pref
            except Exception as e:
                print(f"❌ Load preference error for {user_id}: {e}")
        
        # Yeni oluştur
        pref = UserPreference(user_id)
        self.user_preferences[user_id] = pref
        return pref
    
    async def update_from_view(
        self, 
        user_id: str, 
        reel: ReelFeedItem,
        view: ReelView
    ):
        """
        View event'ten preference güncelle
        
        Args:
            user_id: Kullanıcı ID
            reel: İzlenen reel
            view: View event
        
        Engagement skoruna göre kategori/keyword skorlarını günceller
        """
        pref = self.get_or_create_preference(user_id)
        
        # Engagement score hesapla (0-1 normalleştirilmiş)
        engagement = view.get_preference_weight()
        
        # Kategori skoru güncelle
        pref.update_category_score(reel.news_data.category, engagement)
        
        # Keyword skorları güncelle
        keywords = reel.news_data.keywords or self._extract_keywords(reel.news_data.title)
        for keyword in keywords[:10]:  # En fazla 10 keyword
            pref.update_keyword_score(keyword.lower(), engagement)
        
        # Yazar skorunu güncelle (varsa)
        if reel.news_data.author:
            pref.update_author_score(reel.news_data.author, engagement)
        
        # Persist to disk (async olarak)
        await self._save_preference(pref)
    
    async def boost_from_detail_view(
        self,
        user_id: str,
        reel: ReelFeedItem,
        engagement_score: float
    ):
        """
        Detay okuma sonrası EKSTRA boost
        
        Detay okuma çok güçlü bir sinyal!
        Normal engagement'tan %30-50 daha fazla ağırlık ver
        
        Args:
            user_id: Kullanıcı ID
            reel: İzlenen reel
            engagement_score: Detail engagement skoru (0-1)
        """
        pref = self.get_or_create_preference(user_id)
        
        # Kategori'ye EKSTRA boost (1.5x)
        boosted_engagement = min(engagement_score * 1.5, 1.0)
        pref.update_category_score(reel.news_data.category, boosted_engagement)
        
        # Keywords'e EKSTRA boost (1.3x)
        keywords = reel.news_data.keywords or self._extract_keywords(reel.news_data.title)
        for keyword in keywords[:10]:
            pref.update_keyword_score(keyword.lower(), engagement_score * 1.3)
        
        # Yazar tercihini kaydet (varsa)
        if reel.news_data.author:
            pref.update_author_score(reel.news_data.author, engagement_score)
        
        # Save
        await self._save_preference(pref)
    
    async def predict_reel_score(
        self,
        user_id: str,
        reel: ReelFeedItem
    ) -> float:
        """
        Bir reel'in kullanıcıya uygunluk skoru (0-1)
        
        Args:
            user_id: Kullanıcı ID
            reel: Aday reel
        
        Returns:
            Relevance score (0-1)
        
        Scoring breakdown:
        - Category match: 40%
        - Keyword match: 35%
        - Author preference: 15%
        - Recency bonus: 10%
        """
        pref = self.get_or_create_preference(user_id)
        
        # Cold start: yeterli veri yok
        if not pref.has_enough_data():
            return 0.5  # Nötr skor
        
        score = 0.0
        
        # 1. Kategori match (40%)
        category_score = pref.get_category_score(reel.news_data.category)
        score += category_score * 0.4
        
        # 2. Keyword match (35%)
        keywords = reel.news_data.keywords or self._extract_keywords(reel.news_data.title)
        if keywords:
            keyword_scores = [pref.get_keyword_score(kw.lower()) for kw in keywords[:10]]
            keyword_score = max(keyword_scores)  # En yüksek keyword skoru
        else:
            keyword_score = 0.3  # Default
        score += keyword_score * 0.35
        
        # 3. Yazar tercih (15%)
        author_score = pref.get_author_score(reel.news_data.author)
        score += author_score * 0.15
        
        # 4. Recency bonus (10%)
        recency_score = self._calculate_recency_score(reel)
        score += recency_score * 0.1
        
        return min(score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Basit keyword extraction (fallback)
        
        NLP engine varsa onu kullan, yoksa bu basit versiyonu
        """
        # Türkçe stop words
        stop_words = {
            've', 'bir', 'bu', 'ile', 'için', 'da', 'de', 'mi', 'mı',
            'mu', 'mü', 'olan', 'olarak', 'ise', 'şu', 'o', 'gibi',
            'daha', 'çok', 'her', 'en', 'ne', 'ki', 'var', 'yok'
        }
        
        # Basit split ve filter
        words = text.lower().split()
        keywords = [
            w for w in words 
            if w not in stop_words and len(w) > 3
        ]
        
        return keywords[:10]
    
    def _calculate_recency_score(self, reel: ReelFeedItem) -> float:
        """
        Yenilik bonusu (son haberler daha önemli)
        
        Returns:
            0.0 - 1.0 arası skor
        """
        age_hours = (datetime.now() - reel.published_at).total_seconds() / 3600
        
        if age_hours < 3:
            return 1.0  # Son 3 saat
        elif age_hours < 24:
            return 0.7  # Son 24 saat
        elif age_hours < 72:
            return 0.4  # Son 3 gün
        else:
            return 0.2  # Eski haber
    
    async def _save_preference(self, pref: UserPreference):
        """Preference'ı disk'e kaydet"""
        try:
            user_file = self.storage_dir / f"{pref.user_id}.json"
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(pref.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Save preference error for {pref.user_id}: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Kullanıcı istatistikleri"""
        pref = self.get_or_create_preference(user_id)
        
        # Top categories
        top_categories = sorted(
            pref.category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Top keywords
        top_keywords = sorted(
            pref.keyword_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            "user_id": user_id,
            "personalization_level": pref.get_personalization_level(),
            "total_interactions": pref.total_interactions,
            "top_categories": [{"name": k, "score": round(v, 3)} for k, v in top_categories],
            "top_keywords": [{"keyword": k, "score": round(v, 3)} for k, v in top_keywords],
            "last_updated": pref.last_updated.isoformat(),
            "created_at": pref.created_at.isoformat()
        }


# Global instance
preference_engine = UserPreferenceEngine()