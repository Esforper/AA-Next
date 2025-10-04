# src/services/preference_engine.py - YENİ DOSYA

"""
Kullanıcı tercih motoru - TF-IDF + Rule-based
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math

from ..models.reels_tracking import ReelView, ReelFeedItem
from ..models.news import Article


class UserPreferenceEngine:
    """
    Kullanıcı tercihlerini yöneten motor
    
    Kullanım:
    - Her view/detail view sonrası update
    - Feed generation'da scoring
    """
    
    def __init__(self):
        # In-memory cache
        self.user_preferences: Dict[str, UserPreference] = {}
    
    def get_or_create_preference(self, user_id: str) -> 'UserPreference':
        """Kullanıcı preference'ını al veya oluştur"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreference(user_id)
        return self.user_preferences[user_id]
    
    async def update_from_view(
        self, 
        user_id: str, 
        reel: ReelFeedItem,
        view: ReelView
    ):
        """View event'ten preference güncelle"""
        pref = self.get_or_create_preference(user_id)
        
        # Engagement score hesapla
        engagement = view.get_total_engagement_score()
        
        # Kategori skoru güncelle
        pref.update_category_score(reel.news_data.category, engagement)
        
        # Keyword skorları güncelle
        keywords = reel.news_data.tags or self._extract_keywords(reel.news_data.title)
        for keyword in keywords:
            pref.update_keyword_score(keyword, engagement)
    
    async def boost_from_detail_view(
        self,
        user_id: str,
        reel: ReelFeedItem,
        engagement_score: float
    ):
        """Detay okuma sonrası ekstra boost"""
        pref = self.get_or_create_preference(user_id)
        
        # Kategori'ye EKSTRA boost (çünkü detail view çok güçlü sinyal!)
        pref.update_category_score(reel.news_data.category, engagement_score * 1.5)
        
        # Keywords'e EKSTRA boost
        keywords = reel.news_data.tags or self._extract_keywords(reel.news_data.title)
        for keyword in keywords:
            pref.update_keyword_score(keyword, engagement_score * 1.3)
        
        # Yazar tercihini kaydet (eğer varsa)
        if reel.news_data.author:
            pref.update_author_score(reel.news_data.author, engagement_score)
    
    async def predict_reel_score(
        self,
        user_id: str,
        reel: ReelFeedItem
    ) -> float:
        """Bir reel'in kullanıcıya uygunluk skoru (0-1)"""
        pref = self.get_or_create_preference(user_id)
        
        if not pref.has_enough_data():
            # Yeni kullanıcı, cold start
            return 0.5  # Nötr skor
        
        score = 0.0
        
        # 1. Kategori match (40%)
        category_score = pref.get_category_score(reel.news_data.category)
        score += category_score * 0.4
        
        # 2. Keyword match (35%)
        keywords = reel.news_data.tags or self._extract_keywords(reel.news_data.title)
        keyword_scores = [pref.get_keyword_score(kw) for kw in keywords]
        keyword_score = max(keyword_scores) if keyword_scores else 0.3
        score += keyword_score * 0.35
        
        # 3. Yazar tercih (15%)
        author_score = pref.get_author_score(reel.news_data.author) if reel.news_data.author else 0.3
        score += author_score * 0.15
        
        # 4. Recency bonus (10%)
        recency_score = self._calculate_recency_score(reel)
        score += recency_score * 0.1
        
        return min(score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Basit keyword extraction (ileride NLP ile upgrade)"""
        # Türkçe stop words
        stop_words = {'bir', 've', 'ile', 'için', 'bu', 'da', 'de', 'mi', 'mı'}
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:10]  # En fazla 10 keyword
    
    def _calculate_recency_score(self, reel: ReelFeedItem) -> float:
        """Yenilik bonusu"""
        age_hours = (datetime.now() - reel.published_at).total_seconds() / 3600
        
        if age_hours < 3:
            return 1.0
        elif age_hours < 24:
            return 0.7
        elif age_hours < 72:
            return 0.4
        else:
            return 0.2


class UserPreference:
    """Tek bir kullanıcının tercihleri"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Kategori skorları (exponential moving average)
        self.category_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # Keyword skorları
        self.keyword_scores: Dict[str, float] = defaultdict(lambda: 0.3)
        
        # Yazar skorları
        self.author_scores: Dict[str, float] = defaultdict(lambda: 0.3)
        
        # Metadata
        self.total_interactions = 0
        self.last_updated = datetime.now()
    
    def update_category_score(self, category: str, weight: float):
        """Kategori skorunu güncelle (EMA)"""
        current = self.category_scores[category]
        
        # Exponential moving average (son interactionlar daha önemli)
        alpha = 0.3  # Yeni veri ağırlığı
        self.category_scores[category] = alpha * weight + (1 - alpha) * current
        
        self.total_interactions += 1
        self.last_updated = datetime.now()
    
    def update_keyword_score(self, keyword: str, weight: float):
        """Keyword skorunu güncelle"""
        current = self.keyword_scores[keyword]
        alpha = 0.3
        self.keyword_scores[keyword] = alpha * weight + (1 - alpha) * current
    
    def update_author_score(self, author: str, weight: float):
        """Yazar skorunu güncelle"""
        current = self.author_scores[author]
        alpha = 0.25  # Yazar biraz daha yavaş öğrenilsin
        self.author_scores[author] = alpha * weight + (1 - alpha) * current
    
    def get_category_score(self, category: str) -> float:
        """Kategori skorunu al"""
        return self.category_scores.get(category, 0.5)
    
    def get_keyword_score(self, keyword: str) -> float:
        """Keyword skorunu al"""
        return self.keyword_scores.get(keyword, 0.3)
    
    def get_author_score(self, author: Optional[str]) -> float:
        """Yazar skorunu al"""
        if not author:
            return 0.3
        return self.author_scores.get(author, 0.3)
    
    def has_enough_data(self) -> bool:
        """Yeterli veri var mı personalization için"""
        return self.total_interactions >= 5


# Global instance
preference_engine = UserPreferenceEngine()