# ================================
# src/services/feed_generator.py - Personalized Feed Generator
# ================================

"""
Feed Generator - Instagram-style Personalized Feed

3-tier approach:
- Cold start (0-10 interactions): Trending + Fresh
- Warm (10-50 interactions): Rule-based preference
- Hot (50+ interactions): NLP-powered personalization

Features:
- Adaptive algorithm based on user data
- Exploration/exploitation balance
- Diversity injection
- Real-time personalization
"""

from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import random

from ..models.reels_tracking import ReelFeedItem, FeedResponse, FeedPagination, FeedMetadata
from .reels_analytics import reels_analytics
from .incremental_nlp import incremental_nlp
from .user_preference import preference_engine


class FeedGenerator:
    """
    Personalized Feed Generator
    
    Main method: generate_feed(user_id, limit)
    
    Algorithm adapts based on user interaction count:
    - 0-10: Cold start (trending)
    - 10-50: Warm (rule-based)
    - 50+: Hot (NLP-powered)
    """
    
    def __init__(self):
        print("✅ Feed Generator initialized")
    
    async def generate_feed(
        self,
        user_id: str,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> FeedResponse:
        """
        Kullanıcıya özel feed oluştur
        
        Args:
            user_id: Kullanıcı ID
            limit: Kaç reel döndürsün
            cursor: Pagination cursor
        
        Returns:
            FeedResponse with reels + metadata
        """
        try:
            # Kullanıcı profilini al
            user_pref = preference_engine.get_or_create_preference(user_id)
            personalization_level = user_pref.get_personalization_level()
            
            print(f"📱 Generating feed for {user_id} (level: {personalization_level})")
            
            # Personalization seviyesine göre feed oluştur
            if personalization_level == "cold":
                reels = await self._cold_start_feed(user_id, limit)
                trending_count = int(limit * 0.7)
                fresh_count = int(limit * 0.3)
                personalized_count = 0
                exploration_count = 0
                
            elif personalization_level == "warm":
                reels = await self._warm_feed(user_id, limit)
                trending_count = 0
                fresh_count = 0
                personalized_count = int(limit * 0.8)
                exploration_count = int(limit * 0.2)
                
            else:  # hot
                reels = await self._hot_feed(user_id, limit)
                trending_count = 0
                fresh_count = 0
                personalized_count = int(limit * 0.85)
                exploration_count = int(limit * 0.15)
            
            # Pagination metadata
            pagination = FeedPagination(
                current_page=1,
                has_next=len(reels) >= limit,
                has_previous=False,
                next_cursor=reels[-1].id if len(reels) >= limit else None,
                total_available=await self._get_total_available(user_id)
            )
            
            # Feed metadata
            metadata = FeedMetadata(
                trending_count=trending_count,
                personalized_count=personalized_count,
                fresh_count=fresh_count,
                exploration_count=exploration_count,
                algorithm_version="v1.0",
                personalization_level=personalization_level
            )
            
            return FeedResponse(
                success=True,
                reels=reels[:limit],
                pagination=pagination,
                feed_metadata=metadata,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Feed generation error: {e}")
            # Fallback: latest reels
            fallback_reels = await self._get_latest_reels(limit)
            return FeedResponse(
                success=False,
                reels=fallback_reels,
                pagination=FeedPagination(),
                feed_metadata=FeedMetadata()
            )
    
    async def _cold_start_feed(self, user_id: str, limit: int) -> List[ReelFeedItem]:
        """
        Yeni kullanıcı feed (0-10 etkileşim)
        
        Strategy:
        - %70 Trending (herkes ne izliyor?)
        - %30 Fresh (son 3 saatteki haberler)
        
        Amaç: Kullanıcıyı sisteme alıştırmak, ilgi alanlarını keşfetmek
        """
        print("🆕 Cold start feed")
        
        # İzlenmemiş reels al
        unseen_reels = await self._get_unseen_reels(user_id)
        
        if not unseen_reels:
            return await self._get_latest_reels(limit)
        
        # Trending reels (engagement skoru yüksek)
        trending_count = int(limit * 0.7)
        trending = await self._get_trending_reels(unseen_reels, count=trending_count)
        
        # Fresh reels (son 3 saat)
        fresh_count = limit - len(trending)
        fresh = await self._get_fresh_reels(unseen_reels, hours=3, count=fresh_count)
        
        # Birleştir ve karıştır
        feed = trending + fresh
        random.shuffle(feed)
        
        # Metadata işaretle
        for reel in feed[:trending_count]:
            reel.is_trending = True
            reel.feed_reason = "trending"
        for reel in feed[trending_count:]:
            reel.is_fresh = True
            reel.feed_reason = "fresh"
        
        return feed[:limit]
    
    async def _warm_feed(self, user_id: str, limit: int) -> List[ReelFeedItem]:
        """
        Orta seviye feed (10-50 etkileşim)
        
        Strategy:
        - Rule-based preference scoring
        - Category + keyword matching
        - %80 personalized + %20 exploration
        
        Amaç: Tercihler netleşiyor, rule-based yeterli
        """
        print("🌡️ Warm feed (rule-based)")
        
        # İzlenmemiş reels
        unseen_reels = await self._get_unseen_reels(user_id, max_age_days=3)
        
        if not unseen_reels:
            return await self._cold_start_feed(user_id, limit)
        
        # Her reel için skor hesapla
        scored_reels = []
        for reel in unseen_reels:
            score = await preference_engine.predict_reel_score(user_id, reel)
            scored_reels.append((reel, score))
        
        # Sırala
        scored_reels.sort(key=lambda x: x[1], reverse=True)
        
        # %80 personalized (yüksek skorlular)
        personalized_count = int(limit * 0.8)
        personalized = [r for r, s in scored_reels[:personalized_count]]
        
        # %20 exploration (rastgele, düşük skorlular)
        exploration_count = limit - len(personalized)
        exploration_pool = [r for r, s in scored_reels[personalized_count:]]
        exploration = random.sample(
            exploration_pool, 
            min(exploration_count, len(exploration_pool))
        )
        
        # Birleştir
        feed = personalized + exploration
        random.shuffle(feed)
        
        # Metadata
        for i, reel in enumerate(feed):
            if i < personalized_count:
                reel.is_recommended = True
                reel.recommendation_reason = "preference_match"
            else:
                reel.feed_reason = "exploration"
        
        return feed[:limit]
    
    async def _hot_feed(self, user_id: str, limit: int) -> List[ReelFeedItem]:
        """
        Aktif kullanıcı feed (50+ etkileşim)
        
        Strategy:
        - NLP-powered semantic similarity
        - User vector vs reel vectors
        - %85 personalized + %15 exploration
        
        Amaç: Maksimum personalization, NLP kullan
        """
        print("🔥 Hot feed (NLP-powered)")
        
        # NLP fitted mi kontrol et
        if not incremental_nlp.is_fitted:
            print("⚠️ NLP not fitted, falling back to warm feed")
            return await self._warm_feed(user_id, limit)
        
        # Kullanıcının izlediği son 50 haberi al
        watch_history = await reels_analytics.get_user_watch_history(
            user_id, 
            limit=50,
            min_engagement=0.5  # Sadece beğendiklerini
        )
        
        if not watch_history:
            return await self._warm_feed(user_id, limit)
        
        # User profile vector oluştur (NLP)
        user_texts = [
            {
                "reel_id": view.reel_id,
                "text": f"{view.reel_title} {view.reel_summary}",
                "engagement": view.engagement_score
            }
            for view in watch_history
        ]
        
        user_vector = await incremental_nlp.build_user_profile(user_texts)
        
        if user_vector is None:
            return await self._warm_feed(user_id, limit)
        
        # İzlenmemiş aday reels
        unseen_reels = await self._get_unseen_reels(user_id, max_age_days=3)
        
        if not unseen_reels:
            return await self._cold_start_feed(user_id, limit)
        
        # NLP ile skorla
        candidate_texts = [
            {
                "reel_id": r.id,
                "text": f"{r.news_data.title} {r.news_data.summary}",
                "reel_obj": r
            }
            for r in unseen_reels
        ]
        
        # Cosine similarity ranking
        ranked_reels = await incremental_nlp.rank_reels(user_vector, candidate_texts)
        
        # %85 personalized (yüksek similarity)
        personalized_count = int(limit * 0.85)
        personalized = [r for r, score in ranked_reels[:personalized_count]]
        
        # %15 exploration
        exploration_count = limit - len(personalized)
        exploration_pool = [r for r, score in ranked_reels[personalized_count:]]
        exploration = random.sample(
            exploration_pool,
            min(exploration_count, len(exploration_pool))
        )
        
        # Birleştir ve hafif karıştır
        feed = personalized + exploration
        feed = self._smart_shuffle(feed, shuffle_ratio=0.3)
        
        # Metadata + recommendation score
        for i, reel in enumerate(feed):
            if i < personalized_count:
                reel.is_recommended = True
                # Similarity skorunu recommendation_score'a ata
                matching_score = next(
                    (score for r, score in ranked_reels if r.id == reel.id), 
                    0.5
                )
                reel.recommendation_score = matching_score
                reel.recommendation_reason = "nlp_similarity"
            else:
                reel.feed_reason = "exploration"
        
        return feed[:limit]
    
    async def _get_unseen_reels(
        self, 
        user_id: str, 
        max_age_days: int = 10 # Son 10 gün ÖNEMLİ: BURAYA GÖRE REELS AKIŞI AYARLANACAK
    ) -> List[ReelFeedItem]:
        """
        Kullanıcının izlemediği reels
        
        Args:
            user_id: Kullanıcı ID
            max_age_days: Maksimum yaş (gün)
        
        Returns:
            List of unseen reels
        """
        # Tüm published reels
        all_reels = await reels_analytics.get_all_published_reels()
        
        # İzlenen reel ID'leri
        watched_ids = await reels_analytics._get_user_watched_reel_ids(user_id)
        
        # Filtrele
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        unseen = [
            r for r in all_reels
            if r.id not in watched_ids and r.published_at >= cutoff_date
        ]
        
        return unseen
    
    async def _get_trending_reels(
        self, 
        reels: List[ReelFeedItem], 
        count: int
    ) -> List[ReelFeedItem]:
        """
        Trending reels al (engagement skoru yüksek)
        
        Args:
            reels: Aday reels
            count: Kaç tane
        
        Returns:
            Top trending reels
        """
        # Engagement skoruna göre sırala
        sorted_reels = sorted(
            reels,
            key=lambda r: r.trend_score if r.trend_score > 0 else r.total_views,
            reverse=True
        )
        
        return sorted_reels[:count]
    
    async def _get_fresh_reels(
        self,
        reels: List[ReelFeedItem],
        hours: int = 3,
        count: int = 10
    ) -> List[ReelFeedItem]:
        """
        Fresh reels al (son X saat)
        
        Args:
            reels: Aday reels
            hours: Son kaç saat
            count: Kaç tane
        
        Returns:
            Fresh reels
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        fresh = [
            r for r in reels
            if r.published_at >= cutoff_time
        ]
        
        # Yeniden eskiye sırala
        fresh.sort(key=lambda r: r.published_at, reverse=True)
        
        return fresh[:count]
    
    async def _get_latest_reels(self, limit: int) -> List[ReelFeedItem]:
        """
        Fallback: En yeni reels (tarihe göre)
        
        Args:
            limit: Kaç tane
        
        Returns:
            Latest reels
        """
        all_reels = await reels_analytics.get_all_published_reels()
        
        # Tarihe göre sırala
        sorted_reels = sorted(
            all_reels,
            key=lambda r: r.published_at,
            reverse=True
        )
        
        return sorted_reels[:limit]
    
    async def _get_total_available(self, user_id: str) -> int:
        """Toplam mevcut (izlenmemiş) reel sayısı"""
        unseen = await self._get_unseen_reels(user_id)
        return len(unseen)
    
    def _smart_shuffle(
        self, 
        items: List[ReelFeedItem], 
        shuffle_ratio: float = 0.3
    ) -> List[ReelFeedItem]:
        """
        Akıllı karıştırma (tamamen rastgele değil)
        
        İlk %70'i sıralı bırak, son %30'u karıştır
        Böylece en iyi öneriler üstte kalır ama monotonluk da olmaz
        
        Args:
            items: Reel listesi
            shuffle_ratio: Ne kadarını karıştırsın (0-1)
        
        Returns:
            Shuffled list
        """
        if not items:
            return items
        
        split_point = int(len(items) * (1 - shuffle_ratio))
        
        # İlk kısmı aynen bırak
        kept = items[:split_point]
        
        # Son kısmı karıştır
        shuffled = items[split_point:]
        random.shuffle(shuffled)
        
        return kept + shuffled


# Global instance
feed_generator = FeedGenerator()