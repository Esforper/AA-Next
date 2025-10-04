# ================================
# src/services/reels_analytics.py - Enhanced with Worker Helper Methods
# ================================

"""
Reels Analytics Service - Tracking, Statistics ve Feed Management
File-based persistence ile güncellenmiş (in-memory + JSON backup)

ADDED: Worker helper methods for RSS comparison and duplicate detection
"""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import hashlib
import uuid
import json
from pathlib import Path

from ..models.reels_tracking import (
    ReelView, UserReelStats, UserDailyStats, DailyProgress,
    ReelAnalytics, ReelFeedItem, TrendingReels, TrendPeriod,
    TrackViewRequest, TrackViewResponse, ViewStatus, ReelStatus,
    NewsData, FeedResponse, FeedPagination, FeedMetadata
)
from ..models.news import Article
from ..config import settings

class ReelsAnalyticsService:
    """Reels analytics ve tracking servisi - persistent storage ile"""
    
    def __init__(self):
        # Storage paths
        self.storage_dir = Path(settings.storage_base_path) / "reels_data"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.reels_file = self.storage_dir / "reels.json"
        self.analytics_file = self.storage_dir / "analytics.json"
        self.views_file = self.storage_dir / "views.json"
        self.stats_file = self.storage_dir / "user_stats.json"
        
        # In-memory storage (with file backup)
        self.view_storage: Dict[str, List[ReelView]] = defaultdict(list)
        self.user_stats: Dict[str, UserReelStats] = {}
        self.daily_progress: Dict[str, Dict[str, DailyProgress]] = defaultdict(dict)
        self.reel_analytics: Dict[str, ReelAnalytics] = {}
        self.reel_storage: Dict[str, ReelFeedItem] = {}
        
        # Cache for performance
        self._trending_cache: Optional[TrendingReels] = None
        self._cache_expiry: Optional[datetime] = None
        self._url_cache: Optional[Set[str]] = None  # NEW: URL cache for worker
        self._url_cache_expiry: Optional[datetime] = None  # NEW: URL cache expiry
        
        # Load existing data
        self._load_persistent_data()
        
        print("✅ Reels Analytics Service initialized (persistent storage)")
        print(f"📁 Storage: {self.storage_dir}")
        print(f"🎬 Loaded reels: {len(self.reel_storage)}")
    
    # ============ PERSISTENCE METHODS ============
    
    def _load_persistent_data(self):
        """Persistent data'yı dosyalardan yükle"""
        try:
            # Load reels
            if self.reels_file.exists():
                with open(self.reels_file, 'r', encoding='utf-8') as f:
                    reels_data = json.load(f)
                
                # Convert back to ReelFeedItem objects
                for reel_id, reel_dict in reels_data.items():
                    try:
                        # Convert datetime strings back to datetime objects
                        if 'published_at' in reel_dict:
                            reel_dict['published_at'] = datetime.fromisoformat(reel_dict['published_at'])
                        if 'created_at' in reel_dict:
                            reel_dict['created_at'] = datetime.fromisoformat(reel_dict['created_at'])
                        
                        # Create ReelFeedItem from dict
                        reel = ReelFeedItem(**reel_dict)
                        self.reel_storage[reel_id] = reel
                        
                    except Exception as e:
                        print(f"⚠️ Could not load reel {reel_id}: {e}")
            
            # Load analytics (simplified)
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    analytics_data = json.load(f)
                    # Convert to ReelAnalytics objects if needed
                    # Simplified for now
            
            print(f"📂 Loaded {len(self.reel_storage)} reels from persistent storage")
            
        except Exception as e:
            print(f"⚠️ Error loading persistent data: {e}")
    
    def _save_persistent_data(self):
        """Persistent data'yı dosyalara kaydet"""
        try:
            # Save reels
            reels_data = {}
            for reel_id, reel in self.reel_storage.items():
                try:
                    # Convert ReelFeedItem to dict for JSON serialization
                    reel_dict = reel.model_dump()
                    # Convert datetime objects to strings
                    if 'published_at' in reel_dict and reel_dict['published_at']:
                        reel_dict['published_at'] = reel_dict['published_at'].isoformat() if isinstance(reel_dict['published_at'], datetime) else reel_dict['published_at']
                    if 'created_at' in reel_dict and reel_dict['created_at']:
                        reel_dict['created_at'] = reel_dict['created_at'].isoformat() if isinstance(reel_dict['created_at'], datetime) else reel_dict['created_at']
                    
                    reels_data[reel_id] = reel_dict
                except Exception as e:
                    print(f"⚠️ Could not serialize reel {reel_id}: {e}")
            
            with open(self.reels_file, 'w', encoding='utf-8') as f:
                json.dump(reels_data, f, indent=2, default=str, ensure_ascii=False)
            
            # Save analytics
            analytics_data = {}
            for reel_id, analytics in self.reel_analytics.items():
                try:
                    analytics_dict = analytics.model_dump() if hasattr(analytics, 'model_dump') else {}
                    analytics_data[reel_id] = analytics_dict
                except Exception as e:
                    print(f"⚠️ Could not serialize analytics {reel_id}: {e}")
            
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.reel_storage)} reels and {len(self.reel_analytics)} analytics")
            
        except Exception as e:
            print(f"❌ Error saving persistent data: {e}")
    
    # ============ WORKER HELPER METHODS (NEW) ============
    
    async def get_existing_article_urls(self) -> Set[str]:
        """
        🔥 NEW: Worker için - Mevcut reels'lerin article URL'lerini al
        Cache'li version for performance
        """
        try:
            # Check cache first
            if (self._url_cache is not None and 
                self._url_cache_expiry and 
                datetime.now() < self._url_cache_expiry):
                return self._url_cache
            
            # Get all published reels
            published_reels = await self.get_all_published_reels()
            
            # Extract URLs
            existing_urls = set()
            for reel in published_reels:
                if reel.news_data and reel.news_data.url:
                    existing_urls.add(str(reel.news_data.url))
            
            # Update cache (expires in 5 minutes)
            self._url_cache = existing_urls
            self._url_cache_expiry = datetime.now() + timedelta(minutes=5)
            
            return existing_urls
            
        except Exception as e:
            print(f"❌ Error getting existing article URLs: {e}")
            return set()
    
    async def get_articles_since_date(self, since_date: datetime) -> List[ReelFeedItem]:
        """
        🔥 NEW: Worker için - Belirli tarihten sonra oluşturulan reels
        """
        try:
            published_reels = await self.get_all_published_reels()
            
            recent_reels = [
                reel for reel in published_reels
                if reel.published_at and reel.published_at > since_date
            ]
            
            # Sort by publish date
            recent_reels.sort(key=lambda r: r.published_at, reverse=True)
            
            return recent_reels
            
        except Exception as e:
            print(f"❌ Error getting articles since date: {e}")
            return []
    
    async def get_reels_by_category(self, category: str) -> List[ReelFeedItem]:
        """
        🔥 NEW: Worker için - Kategoriye göre reels
        """
        try:
            published_reels = await self.get_all_published_reels()
            
            category_reels = [
                reel for reel in published_reels
                if reel.news_data and reel.news_data.category == category
            ]
            
            return category_reels
            
        except Exception as e:
            print(f"❌ Error getting reels by category: {e}")
            return []
    
    async def is_article_already_processed(self, article_url: str) -> bool:
        """
        🔥 NEW: Worker için - Article'ın daha önce işlenip işlenmediğini kontrol et
        """
        try:
            existing_urls = await self.get_existing_article_urls()
            return str(article_url) in existing_urls
            
        except Exception as e:
            print(f"❌ Error checking if article processed: {e}")
            return False
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        🔥 NEW: Worker için - İşleme istatistikleri
        """
        try:
            published_reels = await self.get_all_published_reels()
            
            # Basic stats
            total_reels = len(published_reels)
            
            # Category breakdown
            categories = {}
            for reel in published_reels:
                if reel.news_data and reel.news_data.category:
                    cat = reel.news_data.category
                    categories[cat] = categories.get(cat, 0) + 1
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_reels = [
                reel for reel in published_reels
                if reel.published_at and reel.published_at > yesterday
            ]
            
            # Total duration
            total_duration = sum(reel.duration_seconds for reel in published_reels)
            avg_duration = total_duration / max(total_reels, 1)
            
            # Estimated costs
            total_cost = sum(
                getattr(reel, 'estimated_cost', 0.0) for reel in published_reels
            )
            
            return {
                "total_reels": total_reels,
                "categories": categories,
                "recent_reels_24h": len(recent_reels),
                "total_duration_seconds": total_duration,
                "total_duration_minutes": round(total_duration / 60, 1),
                "average_duration_seconds": round(avg_duration, 1),
                "estimated_total_cost": round(total_cost, 6),
                "average_cost_per_reel": round(total_cost / max(total_reels, 1), 6),
                "storage_location": str(self.storage_dir),
                "cache_status": {
                    "url_cache_size": len(self._url_cache) if self._url_cache else 0,
                    "url_cache_expires": self._url_cache_expiry.isoformat() if self._url_cache_expiry else None
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting processing stats: {e}")
            return {}
    
    def invalidate_url_cache(self):
        """
        🔥 NEW: Worker için - URL cache'ini temizle
        Yeni reel eklenince cache'i güncelle
        """
        self._url_cache = None
        self._url_cache_expiry = None
    
    # ============ REEL MANAGEMENT METHODS (Enhanced with cache invalidation) ============
    
    async def create_reel_from_article(self, article: Article, audio_url: str, 
                                     duration_seconds: int, file_size_mb: float,
                                     voice_used: str = "alloy", estimated_cost: float = 0.0) -> ReelFeedItem:
        """
        Article'dan ReelFeedItem oluştur ve persist et
        ENHANCED: Cache invalidation added
        """
        try:
            # Unique reel ID oluştur
            reel_id = f"aa_{hashlib.md5(f'{article.url}{voice_used}'.encode()).hexdigest()[:12]}"
            
            # Article'dan NewsData oluştur
            news_data = NewsData(
                title=article.title,
                summary=article.summary or article.content[:200] + "...",
                full_content=article.content,
                url=article.url,
                category=article.category,
                author=article.author,
                location=article.location,
                published_date=article.published_at.isoformat() if article.published_at else datetime.now().isoformat(),
                scraped_date=datetime.now().isoformat(),
                main_image=article.main_image,
                images=article.images,
                tags=article.tags,
                keywords=article.tags,
                meta_description=article.summary,
                word_count=len(article.content.split()),
                character_count=len(article.content),
                estimated_reading_time=max(1, len(article.content.split()) // 200),
                source=article.source or "aa"
            )
            
            # TTS content oluştur
            tts_content = article.to_tts_content()
            
            # ReelFeedItem oluştur
            reel = ReelFeedItem(
                id=reel_id,
                news_data=news_data,
                tts_content=tts_content,
                voice_used=voice_used,
                model_used="tts-1",
                audio_url=audio_url,
                duration_seconds=duration_seconds,
                file_size_mb=file_size_mb,
                status=ReelStatus.PUBLISHED,
                published_at=article.published_at or datetime.now(),
                character_count=len(tts_content),
                estimated_cost=estimated_cost,
                processing_time_seconds=2.5,
                is_fresh=True,
                feed_reason="latest_news"
            )
            
            # Storage'a kaydet
            self.reel_storage[reel_id] = reel
            
            # Analytics kaydı oluştur
            await self._initialize_reel_analytics(reel_id, reel)
            
            # 🔥 NEW: Cache'leri invalidate et
            self.invalidate_url_cache()
            self._invalidate_trending_cache()
            
            # Persist to file
            self._save_persistent_data()
            
            print(f"✅ Reel created and saved: {reel_id} - {news_data.title[:50]}...")
            return reel
            
        except Exception as e:
            print(f"❌ Create reel error: {e}")
            raise
    
    async def get_reel_by_id(self, reel_id: str) -> Optional[ReelFeedItem]:
        """Reel ID'sine göre reel al"""
        return self.reel_storage.get(reel_id)
    
    async def get_all_published_reels(self) -> List[ReelFeedItem]:
        """Tüm yayınlanmış reels'i al"""
        published_reels = [
            reel for reel in self.reel_storage.values() 
            if reel.status == ReelStatus.PUBLISHED
        ]
        print(f"📊 Found {len(published_reels)} published reels")
        return published_reels
    
    async def update_reel_status(self, reel_id: str, status: ReelStatus) -> bool:
        """Reel durumunu güncelle"""
        if reel_id in self.reel_storage:
            self.reel_storage[reel_id].status = status
            
            # Cache invalidation if unpublishing
            if status != ReelStatus.PUBLISHED:
                self.invalidate_url_cache()
            
            self._save_persistent_data()
            return True
        return False
    
    # ============ CORE TRACKING METHODS ============
    
    async def track_reel_view(self, user_id: str, request: TrackViewRequest) -> TrackViewResponse:
        """
        Reel izleme kaydı oluştur ve tüm istatistikleri güncelle
        """
        try:
            # Reel'in var olup olmadığını kontrol et
            reel = await self.get_reel_by_id(request.reel_id)
            if not reel:
                return TrackViewResponse(
                    success=False,
                    message=f"Reel not found: {request.reel_id}"
                )
            
            # View kaydı oluştur
            view = ReelView(
                id=str(uuid.uuid4()),
                user_id=user_id,
                reel_id=request.reel_id,
                duration_ms=request.duration_ms,
                status=ViewStatus.COMPLETED if request.completed else ViewStatus.PARTIAL,
                category=request.category or reel.news_data.category,
                session_id=request.session_id
            )
            
            # Storage'a kaydet
            self.view_storage[user_id].append(view)
            
            # Response oluştur
            response = TrackViewResponse(
                success=True,
                message="View tracked successfully",
                view_id=view.id,
                meaningful_view=view.is_meaningful_view()
            )
            
            return response
            
        except Exception as e:
            return TrackViewResponse(
                success=False,
                message=f"Track view error: {str(e)}"
            )
    
    async def get_user_daily_progress(self, user_id: str, target_date: date = None) -> DailyProgress:
        """
        Kullanıcının günlük progress'ini al
        """
        if not target_date:
            target_date = date.today()
        
        date_str = target_date.isoformat()
        
        if user_id not in self.daily_progress:
            self.daily_progress[user_id] = {}
        
        if date_str not in self.daily_progress[user_id]:
            # Yeni progress oluştur
            total_published = await self._get_published_count_for_date(target_date)
            
            self.daily_progress[user_id][date_str] = DailyProgress(
                user_id=user_id,
                date=target_date,
                total_published_today=total_published
            )
        
        progress = self.daily_progress[user_id][date_str]
        
        # Progress'i yeniden hesapla
        progress.calculate_progress()
        
        return progress
    
    async def get_user_stats(self, user_id: str) -> UserReelStats:
        """
        Kullanıcının genel istatistiklerini al
        """
        if user_id not in self.user_stats:
            # Yeni kullanıcı için boş stats oluştur
            self.user_stats[user_id] = UserReelStats(user_id=user_id)
        
        return self.user_stats[user_id]
    
    # ============ FEED & TRENDING METHODS (Instagram-style) ============
    
    async def generate_user_feed(self, user_id: str, limit: int = 20, 
                                cursor: Optional[str] = None) -> FeedResponse:
        """
        Instagram-style kişiselleştirilmiş feed oluştur
        """
        try:
            # Algoritma ile reel listesi oluştur
            algorithm_reels = await self._generate_algorithmic_feed(user_id)
            
            print(f"🔄 Generated algorithmic feed: {len(algorithm_reels)} reels")
            
            # Cursor-based pagination
            start_index = 0
            if cursor:
                try:
                    start_index = next(
                        i for i, reel in enumerate(algorithm_reels) 
                        if reel.id == cursor
                    ) + 1
                except StopIteration:
                    start_index = 0
            
            # Sayfa verisini al
            page_reels = algorithm_reels[start_index:start_index + limit]
            
            # Kullanıcının izlediği reels'i işaretle
            watched_reel_ids = await self._get_user_watched_reel_ids(user_id)
            for reel in page_reels:
                reel.is_watched = reel.id in watched_reel_ids
            
            # Pagination bilgisi
            has_next = len(algorithm_reels) > start_index + limit
            next_cursor = page_reels[-1].id if page_reels and has_next else None
            
            pagination = FeedPagination(
                current_page=1,
                has_next=has_next,
                has_previous=start_index > 0,
                next_cursor=next_cursor,
                total_available=len(algorithm_reels)
            )
            
            # Feed metadata
            trending_count = sum(1 for reel in page_reels if reel.is_trending)
            fresh_count = sum(1 for reel in page_reels if reel.is_fresh)
            personalized_count = len(page_reels) - trending_count - fresh_count
            
            metadata = FeedMetadata(
                trending_count=trending_count,
                personalized_count=personalized_count,
                fresh_count=fresh_count,
                algorithm_version="v1.0"
            )
            
            return FeedResponse(
                success=True,
                reels=page_reels,
                pagination=pagination,
                feed_metadata=metadata
            )
            
        except Exception as e:
            print(f"❌ Generate feed error: {e}")
            return FeedResponse(
                success=False,
                reels=[],
                pagination=FeedPagination(),
                feed_metadata=FeedMetadata()
            )
    
    # ============ HELPER METHODS ============
    # src/services/reels_analytics.py içindeki _generate_algorithmic_feed metodunu GÜNCELLE:

    async def _generate_algorithmic_feed(
        self, 
        user_id: str,
        limit: int = 20
    ) -> List[ReelFeedItem]:
        """
        Personalized feed generation with preference engine
        """
        from .preference_engine import preference_engine
        
        # Tüm published reels
        all_reels = await self.get_all_published_reels()
        
        # Kullanıcının izlemediği reels
        watched_ids = await self._get_user_watched_reel_ids(user_id)
        unseen_reels = [r for r in all_reels if r.id not in watched_ids]
        
        # Son 3 günlük haberler (fresh content)
        three_days_ago = datetime.now() - timedelta(days=3)
        fresh_reels = [r for r in unseen_reels if r.published_at >= three_days_ago]
        
        # Preference engine ile skorla
        scored_reels = []
        for reel in fresh_reels:
            score = await preference_engine.predict_reel_score(user_id, reel)
            scored_reels.append((reel, score))
        
        # Sırala
        scored_reels.sort(key=lambda x: x[1], reverse=True)
        
        # %80 personalized + %20 exploration (random injection)
        personalized_count = int(limit * 0.8)
        exploration_count = limit - personalized_count
        
        # Top personalized
        top_personalized = [r for r, s in scored_reels[:personalized_count]]
        
        # Random exploration (düşük skorlulardan)
        low_score_reels = [r for r, s in scored_reels[personalized_count:]]
        import random
        exploration = random.sample(low_score_reels, min(exploration_count, len(low_score_reels)))
        
        # Karıştır
        final_feed = top_personalized + exploration
        random.shuffle(final_feed)
        
        return final_feed[:limit]
    
    async def _get_user_watched_reel_ids(self, user_id: str) -> Set[str]:
        """Kullanıcının izlediği reel ID'lerini al"""
        user_views = self.view_storage.get(user_id, [])
        return {view.reel_id for view in user_views if view.is_meaningful_view()}
    
    async def _get_published_count_for_date(self, target_date: date) -> int:
        """Belirli bir tarihte yayınlanan reel sayısı"""
        count = 0
        for reel in self.reel_storage.values():
            if (reel.status == ReelStatus.PUBLISHED and 
                reel.published_at.date() == target_date):
                count += 1
        return count
    
    async def _initialize_reel_analytics(self, reel_id: str, reel: ReelFeedItem = None):
        """Reel analytics'ini başlat"""
        if reel_id not in self.reel_analytics:
            # Reel bilgisini al
            if not reel:
                reel = await self.get_reel_by_id(reel_id)
            
            self.reel_analytics[reel_id] = ReelAnalytics(
                reel_id=reel_id,
                published_at=reel.published_at if reel else datetime.now(),
                category=reel.news_data.category if reel else None,
                tags=reel.news_data.tags if reel else []
            )
    
    def _invalidate_trending_cache(self):
        """Trending cache'i temizle"""
        self._trending_cache = None
        self._cache_expiry = None

# Global instance
reels_analytics = ReelsAnalyticsService()