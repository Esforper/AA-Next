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
    NewsData, FeedResponse, FeedPagination, FeedMetadata, DetailViewEvent,
    TrackDetailViewRequest, EmojiType
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
        """
        Persistent data'yı dosyalardan yükle
        
        🆕 Hata durumunda logla ama exception fırlatma
        """
        try:
            # Load reels
            if self.reels_file.exists():
                with open(self.reels_file, 'r', encoding='utf-8') as f:
                    reels_data = json.load(f)
                
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
            
            print(f"📂 Loaded {len(self.reel_storage)} reels from persistent storage")
            
        except Exception as e:
            # 🆕 Hata durumunda logla ama devam et
            print(f"⚠️ Error loading persistent data: {e}")
            # Boş storage ile devam et
    
    def _save_persistent_data(self):
        """
        Persistent data'yı dosyalara kaydet
        
        🆕 Hata durumunda logla ama exception fırlatma
        """
        try:
            # Save reels
            reels_data = {}
            for reel_id, reel in self.reel_storage.items():
                try:
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
                json.dump(reels_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(reels_data)} reels to persistent storage")
            
        except Exception as e:
            # 🆕 Hata durumunda logla ama devam et
            print(f"⚠️ Error saving persistent data: {e}")
            # Exception fırlatma, sistem çalışmaya devam etsin
    
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
    
    async def create_reel_from_article(
        self,
        article: Article,
        audio_url: str,
        duration_seconds: int,
        file_size_mb: float,
        voice_used: str = "alloy",
        estimated_cost: float = 0.0
    ) -> ReelFeedItem:
        """
        ✅ UPDATED: Article'dan ReelFeedItem oluştur
        """
        try:
            reel_id = f"reel_{hashlib.md5(str(article.url).encode()).hexdigest()[:12]}"
            
            # ✅ UPDATED: NewsData oluştur - full_content List[str] olarak
            news_data = NewsData(
                title=article.title,
                summary=article.summary or "",
                full_content=article.content_paragraphs,  # ✅ List[str] property kullan
                url=str(article.url),
                category=article.category,
                author=article.author,
                location=article.location,
                published_date=article.published_at.isoformat() if article.published_at else datetime.now().isoformat(),
                main_image=article.main_image,
                images=article.images,
                videos=article.videos,
                tags=article.tags,
                keywords=article.keywords,  # ✅ Yeni field
                word_count=len(article.content_text.split()),  # ✅ content_text kullan
                character_count=len(article.content_text),  # ✅ content_text kullan
                estimated_reading_time=max(1, len(article.content_text.split()) // 200),
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
            
            # Cache'leri invalidate et
            self.invalidate_url_cache()
            self._invalidate_trending_cache()
            
            # Persist to file
            self._save_persistent_data()
            
            print(f"✅ Reel created: {reel_id} - {news_data.title[:50]}...")
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
        Reel izleme kaydı oluştur (UPDATED: emoji + detail support)
        """
        try:
            reel = await self.get_reel_by_id(request.reel_id)
            if not reel:
                return TrackViewResponse(
                    success=False,
                    message=f"Reel not found: {request.reel_id}"
                )
            
            # View kaydı oluştur (UPDATED)
            view = ReelView(
                id=str(uuid.uuid4()),
                user_id=user_id,
                reel_id=request.reel_id,
                duration_ms=request.duration_ms,
                status=ViewStatus.COMPLETED if request.completed else ViewStatus.PARTIAL,
                category=request.category or reel.news_data.category,
                session_id=request.session_id,
                
                # 🆕 NEW: Emoji reaction
                emoji_reaction=request.emoji_reaction,
                emoji_timestamp=datetime.now() if request.emoji_reaction else None,
                
                # 🆕 NEW: Extra signals
                paused_count=request.paused_count or 0,
                replayed=request.replayed or False,
                shared=request.shared or False,
                saved=request.saved or False
            )
            
            # Storage'a kaydet
            self.view_storage[user_id].append(view)
            
            # 🆕 Reel analytics güncelle (emoji count)
            if request.reel_id in self.reel_analytics:
                analytics = self.reel_analytics[request.reel_id]
                
                # Total views
                analytics.total_views += 1
                
                # Emoji tracking
                if request.emoji_reaction:
                    analytics.total_emoji_reactions += 1
                    emoji_str = request.emoji_reaction.value
                    if emoji_str not in analytics.emoji_breakdown:
                        analytics.emoji_breakdown[emoji_str] = 0
                    analytics.emoji_breakdown[emoji_str] += 1
                    
                    # Emoji rate
                    analytics.emoji_rate = analytics.total_emoji_reactions / analytics.total_views
            
            # Response
            response = TrackViewResponse(
                success=True,
                message="View tracked successfully",
                view_id=view.id,
                meaningful_view=view.is_meaningful_view()
            )
            
            # Persist
            self._save_persistent_data()
            
            return response
            
        except Exception as e:
            return TrackViewResponse(
                success=False,
                message=f"Track view error: {str(e)}"
            )
    
    async def get_user_daily_progress(self, user_id: str, target_date: date = None) -> DailyProgress:
        """
        Kullanıcının günlük progress'ini al
        
        🆕 Yeni kullanıcı için otomatik olarak boş progress oluşturur
        """
        try:
            if not target_date:
                target_date = date.today()
            
            date_str = target_date.isoformat()
            
            if user_id not in self.daily_progress:
                self.daily_progress[user_id] = {}
            
            if date_str not in self.daily_progress[user_id]:
                # 🆕 Yeni progress oluştur
                print(f"📅 Creating new progress for user {user_id} on {date_str}")
                total_published = await self._get_published_count_for_date(target_date)
                
                self.daily_progress[user_id][date_str] = DailyProgress(
                    user_id=user_id,
                    date=target_date,
                    total_published_today=total_published
                )
                self._save_persistent_data()
            
            progress = self.daily_progress[user_id][date_str]
            
            # Progress'i yeniden hesapla
            progress.calculate_progress()
            
            return progress
            
        except Exception as e:
            # 🆕 Hata durumunda da boş progress döndür
            print(f"❌ Error getting daily progress for {user_id}: {e}")
            return DailyProgress(
                user_id=user_id,
                date=target_date or date.today(),
                total_published_today=0
            )
    
    async def get_user_stats(self, user_id: str) -> UserReelStats:
        """
        Kullanıcının genel istatistiklerini al
        
        🆕 Yeni kullanıcı için otomatik olarak boş stats oluşturur
        """
        try:
            if user_id not in self.user_stats:
                # 🆕 Yeni kullanıcı için boş stats oluştur
                print(f"📊 Creating new stats for user: {user_id}")
                self.user_stats[user_id] = UserReelStats(user_id=user_id)
                self._save_persistent_data()
            
            return self.user_stats[user_id]
            
        except Exception as e:
            # 🆕 Hata durumunda da boş stats döndür
            print(f"❌ Error getting user stats for {user_id}: {e}")
            return UserReelStats(user_id=user_id)
    
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
    
    
    
    async def get_user_watch_history(
        self,
        user_id: str,
        limit: int = 50,
        min_engagement: float = 0.0
    ) -> List[Dict]:
        """
        Kullanıcının izleme geçmişini al (NLP için)
        
        Args:
            user_id: Kullanıcı ID
            limit: Maksimum kayıt sayısı
            min_engagement: Minimum engagement skoru (0-1.5)
        
        Returns:
            List of watch history with reel info
            [{
                "reel_id": "...",
                "reel_title": "...",
                "reel_summary": "...",
                "category": "...",
                "engagement_score": 0.8,
                "watched_at": datetime,
                "completed": bool
            }, ...]
        """
        try:
            if user_id not in self.view_storage:
                return []
            
            # Kullanıcının tüm view'ları
            all_views = self.view_storage[user_id]
            
            # Filtrele: min_engagement'tan yüksek olanlar
            filtered_views = [
                v for v in all_views
                if v.get_engagement_score() >= min_engagement
            ]
            
            # Tarihe göre sırala (yeniden eskiye)
            filtered_views.sort(key=lambda v: v.viewed_at, reverse=True)
            
            # Limit uygula
            filtered_views = filtered_views[:limit]
            
            # Reel bilgilerini ekle
            history = []
            for view in filtered_views:
                reel = await self.get_reel_by_id(view.reel_id)
                if reel:
                    history.append({
                        "reel_id": view.reel_id,
                        "reel_title": reel.news_data.title,
                        "reel_summary": reel.news_data.summary,
                        "category": reel.news_data.category,
                        "keywords": reel.news_data.keywords,
                        "engagement_score": view.get_engagement_score(),
                        "watched_at": view.viewed_at,
                        "completed": view.status == ViewStatus.COMPLETED,
                        "detail_viewed": view.detail_viewed
                    })
            
            return history
            
        except Exception as e:
            print(f"❌ Get watch history error: {e}")
            return []    
    
    
    async def track_detail_view(
        self,
        user_id: str,
        detail_event: DetailViewEvent
    ) -> Dict:
        """
        Detay okuma event'ini kaydet
        
        Args:
            user_id: Kullanıcı ID
            detail_event: DetailViewEvent instance
        
        Returns:
            Success dict
        """
        try:
            # Reel analytics'ini güncelle
            reel_id = detail_event.reel_id
            
            if reel_id in self.reel_analytics:
                analytics = self.reel_analytics[reel_id]
                
                # Detail view count artır
                analytics.detail_view_count += 1
                
                # Average detail duration güncelle
                if analytics.detail_view_count == 1:
                    analytics.avg_detail_duration_ms = detail_event.read_duration_ms
                else:
                    # Running average
                    total_duration = (analytics.avg_detail_duration_ms * 
                                    (analytics.detail_view_count - 1) + 
                                    detail_event.read_duration_ms)
                    analytics.avg_detail_duration_ms = total_duration / analytics.detail_view_count
                
                # Detail view rate hesapla
                if analytics.total_views > 0:
                    analytics.detail_view_rate = analytics.detail_view_count / analytics.total_views
            
            # User daily stats güncelle
            today = date.today()
            date_str = today.isoformat()
            
            if user_id not in self.daily_progress:
                self.daily_progress[user_id] = {}
            
            if date_str not in self.daily_progress[user_id]:
                await self.get_user_daily_progress(user_id, today)
            
            progress = self.daily_progress[user_id][date_str]
            
            # User daily stats'a ekle (eğer varsa)
            # UserDailyStats içinde detail_views field'i var
            # Bu kısmı implement etmek için UserDailyStats tracking'e entegre etmen gerekir
            
            # Persist
            self._save_persistent_data()
            
            return {
                "success": True,
                "detail_view_recorded": True,
                "meaningful_read": detail_event.is_meaningful_read()
            }
            
        except Exception as e:
            print(f"❌ Track detail view error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    
    
    
    
    
    
    
    
    
    
    
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
        """
        Belirli bir tarihte yayınlanan reel sayısı
        
        🆕 Hata durumunda 0 döndürür
        """
        try:
            count = 0
            for reel in self.reel_storage.values():
                if (reel.status == ReelStatus.PUBLISHED and 
                    reel.published_at.date() == target_date):
                    count += 1
            return count
            
        except Exception as e:
            print(f"❌ Error counting published reels for {target_date}: {e}")
            return 0
    
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


    async def get_user_watched_reels(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Kullanıcının izlediği reels listesi
        
        🆕 Yeni kullanıcı için boş liste döndürür
        """
        try:
            if user_id not in self.view_storage:
                print(f"📭 No views found for user: {user_id}")
                return []
            
            user_views = self.view_storage[user_id]
            
            # Anlamlı izlemeler (3+ saniye)
            meaningful_views = [
                view for view in user_views 
                if view.is_meaningful_view()
            ]
            
            # Tarihe göre sırala (en yeni önce)
            meaningful_views.sort(key=lambda v: v.viewed_at, reverse=True)
            
            # Limit uygula
            limited_views = meaningful_views[:limit]
            
            # Reel bilgileriyle birleştir
            result = []
            for view in limited_views:
                reel = await self.get_reel_by_id(view.reel_id)
                if reel:
                    result.append({
                        "reel_id": view.reel_id,
                        "title": reel.news_data.title,
                        "category": reel.news_data.category,
                        "viewed_at": view.viewed_at.isoformat(),
                        "duration_ms": view.duration_ms,
                        "completed": view.completed
                    })
            
            return result
            
        except Exception as e:
            # 🆕 Hata durumunda da boş liste döndür
            print(f"❌ Error getting watched reels for {user_id}: {e}")
            return []



    async def get_reel_by_id(self, reel_id: str) -> Optional[ReelFeedItem]:
        """
        Reel ID'sine göre reel bilgisi al
        
        🆕 Bulunamazsa None döndürür (exception fırlatmaz)
        """
        try:
            return self.reel_storage.get(reel_id)
            
        except Exception as e:
            print(f"❌ Error getting reel {reel_id}: {e}")
            return None

# Global instance
reels_analytics = ReelsAnalyticsService()