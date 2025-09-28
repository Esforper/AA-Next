# ================================
# src/services/rss_worker.py - Background RSS Worker Service
# ================================

"""
RSS Worker Service - Background RSS monitoring and automatic reel creation
Runs continuously, checks RSS feeds, and creates reels automatically
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import hashlib
import re

from ..config import settings
from ..models.news import Article
from ..services.content import content_service
from ..services.processing import processing_service

@dataclass
class WorkerState:
    """Worker durumu"""
    is_running: bool = False
    start_time: Optional[datetime] = None
    last_check_time: Optional[datetime] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    consecutive_failures: int = 0
    total_articles_processed: int = 0
    total_reels_created: int = 0
    total_cost: float = 0.0
    last_error: Optional[str] = None

class RSSWorkerService:
    """Background RSS Worker Service"""
    
    def __init__(self):
        self.state = WorkerState()
        self.worker_settings = settings.get_worker_settings()
        self.data_dir = settings.get_worker_data_dir()
        self.should_stop = False
        
        # File paths
        self.data_file = Path(self.worker_settings["data_file"])
        self.log_file = Path(self.worker_settings["log_file"])
        self.pid_file = Path(self.worker_settings["pid_file"])
        
        # Last check times per category
        self.last_check_times: Dict[str, datetime] = {}
        
        # Quality filter patterns
        self.spam_patterns = [
            r'^[A-Z\s!]+$',  # Sadece büyük harf
            r'(.)\1{4,}',    # Aynı karakter 5+ kez
            r'[^\w\s]{5,}',  # 5+ özel karakter peş peşe
        ]
        
        self.setup_logging()
        self.load_persistent_data()
        
        print("✅ RSS Worker Service initialized")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"⚙️  Settings: {self.worker_settings}")
    
    def setup_logging(self):
        """Worker'a özel logging setup"""
        self.logger = logging.getLogger('rss_worker')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        if not self.log_file.parent.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - RSS Worker - %(levelname)s - %(message)s'
        ))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '🤖 %(asctime)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def load_persistent_data(self):
        """Persistent worker data'yı yükle"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Last check times
                self.last_check_times = {
                    category: datetime.fromisoformat(timestamp)
                    for category, timestamp in data.get('last_check_times', {}).items()
                }
                
                # Worker state
                state_data = data.get('worker_state', {})
                self.state.total_runs = state_data.get('total_runs', 0)
                self.state.successful_runs = state_data.get('successful_runs', 0)
                self.state.failed_runs = state_data.get('failed_runs', 0)
                self.state.total_articles_processed = state_data.get('total_articles_processed', 0)
                self.state.total_reels_created = state_data.get('total_reels_created', 0)
                self.state.total_cost = state_data.get('total_cost', 0.0)
                
                self.logger.info(f"Loaded worker data: {len(self.last_check_times)} categories tracked")
                
        except Exception as e:
            self.logger.warning(f"Could not load worker data: {e}")
    
    def save_persistent_data(self):
        """Worker data'yı kaydet"""
        try:
            data = {
                'last_check_times': {
                    category: timestamp.isoformat()
                    for category, timestamp in self.last_check_times.items()
                },
                'worker_state': {
                    'total_runs': self.state.total_runs,
                    'successful_runs': self.state.successful_runs,
                    'failed_runs': self.state.failed_runs,
                    'total_articles_processed': self.state.total_articles_processed,
                    'total_reels_created': self.state.total_reels_created,
                    'total_cost': self.state.total_cost,
                    'last_save': datetime.now().isoformat()
                }
            }
            
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Could not save worker data: {e}")
    
    def write_pid_file(self):
        """Process ID'yi dosyaya yaz"""
        try:
            import os
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            self.logger.info(f"PID file written: {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Could not write PID file: {e}")
    
    def remove_pid_file(self):
        """PID dosyasını sil"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.info("PID file removed")
        except Exception as e:
            self.logger.error(f"Could not remove PID file: {e}")
    
    # ============ QUALITY FILTER METHODS ============
    
    def is_quality_article(self, article: Article) -> bool:
        """Article kalite kontrolü"""
        if not self.worker_settings["quality_filter"]:
            return True
        
        try:
            # 1. Minimum length check
            content_length = len(article.title) + len(article.content)
            if content_length < self.worker_settings["min_chars"]:
                return False
            
            # 2. Maximum length check  
            if content_length > self.worker_settings["max_chars"]:
                return False
            
            # 3. Title quality check
            if not self._is_quality_title(article.title):
                return False
            
            # 4. Content quality check
            if not self._is_quality_content(article.content):
                return False
            
            # 5. Encoding check
            if self._has_encoding_issues(article.title + article.content):
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Quality check error for article {article.url}: {e}")
            return False
    
    def _is_quality_title(self, title: str) -> bool:
        """Başlık kalite kontrolü"""
        if len(title) < 10:  # Çok kısa başlık
            return False
        
        if len(title) > 200:  # Çok uzun başlık
            return False
        
        # Spam pattern kontrolü
        for pattern in self.spam_patterns:
            if re.search(pattern, title):
                return False
        
        # Teknik mesaj kontrolü
        tech_keywords = [
            'site bakımda', 'sayfa güncellenecek', 'hata oluştu',
            'test mesajı', 'coming soon', 'under construction'
        ]
        
        title_lower = title.lower()
        for keyword in tech_keywords:
            if keyword in title_lower:
                return False
        
        return True
    
    def _is_quality_content(self, content: str) -> bool:
        """İçerik kalite kontrolü"""
        if len(content) < 50:  # Çok kısa içerik
            return False
        
        # Placeholder content kontrolü
        placeholder_phrases = [
            'detaylar takip ediliyor',
            'daha fazla bilgi için',
            'foto galeri',
            'video galeri',
            'haber devam ediyor'
        ]
        
        content_lower = content.lower()
        placeholder_count = sum(1 for phrase in placeholder_phrases if phrase in content_lower)
        
        # İçeriğin %50'si placeholder ise red
        if placeholder_count > len(placeholder_phrases) * 0.5:
            return False
        
        # Tekrar eden kelime kontrolü
        words = content.split()
        if len(words) > 10:
            word_count = {}
            for word in words:
                word_lower = word.lower()
                word_count[word_lower] = word_count.get(word_lower, 0) + 1
            
            # En sık kullanılan kelimenin oranı
            most_common_word_ratio = max(word_count.values()) / len(words)
            if most_common_word_ratio > 0.3:  # %30'dan fazla tekrar varsa
                return False
        
        return True
    
    def _has_encoding_issues(self, text: str) -> bool:
        """Encoding problemi kontrolü"""
        encoding_issues = ['�', '???', 'ÄŸ', 'Å�', 'â€™', '&amp;', '&lt;', '&gt;']
        
        for issue in encoding_issues:
            if issue in text:
                return True
        
        # HTML tag kontrolü (temizlenmemiş)
        if re.search(r'<[^>]+>', text):
            return True
        
        return False
    
    # ============ DUPLICATE DETECTION ============
    
    def is_duplicate_article(self, article: Article, recent_articles: List[Article]) -> bool:
        """Duplicate article kontrolü"""
        if not self.worker_settings["duplicate_detection"]:
            return False
        
        try:
            article_hash = self._get_article_hash(article)
            
            for recent_article in recent_articles:
                recent_hash = self._get_article_hash(recent_article)
                
                # Exact match
                if article_hash == recent_hash:
                    return True
                
                # Title similarity (>80% benzer)
                if self._calculate_similarity(article.title, recent_article.title) > 0.8:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Duplicate check error: {e}")
            return False
    
    def _get_article_hash(self, article: Article) -> str:
        """Article için unique hash oluştur"""
        content = f"{article.title}{article.url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Basit text similarity hesaplama"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    # ============ MAIN WORKER LOGIC ============
    
    async def start_worker(self):
        """Worker'ı başlat"""
        if self.state.is_running:
            self.logger.warning("Worker already running")
            return
        
        if not self.worker_settings["enabled"]:
            self.logger.warning("Worker disabled in settings")
            return
        
        self.logger.info("🚀 Starting RSS Worker...")
        
        # State güncelle
        self.state.is_running = True
        self.state.start_time = datetime.now()
        self.should_stop = False
        
        # PID file yaz
        self.write_pid_file()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Initial delay
            if self.worker_settings.get("start_delay_seconds", 0) > 0:
                self.logger.info(f"Initial delay: {self.worker_settings['start_delay_seconds']}s")
                await asyncio.sleep(self.worker_settings["start_delay_seconds"])
            
            # Main worker loop
            while not self.should_stop:
                try:
                    await self._worker_iteration()
                    self.state.consecutive_failures = 0  # Reset failure counter
                    
                except Exception as e:
                    self.state.failed_runs += 1
                    self.state.consecutive_failures += 1
                    self.state.last_error = str(e)
                    
                    self.logger.error(f"Worker iteration failed: {e}")
                    
                    # Stop worker after consecutive failures
                    if (self.state.consecutive_failures >= 
                        self.worker_settings.get("stop_on_consecutive_failures", 5)):
                        self.logger.error("Too many consecutive failures. Stopping worker.")
                        break
                
                # Wait for next iteration
                if not self.should_stop:
                    interval = self.worker_settings["interval_minutes"] * 60
                    
                    # Smart scheduling: adjust interval based on content frequency
                    if self.worker_settings.get("smart_scheduling", False):
                        interval = self._calculate_smart_interval()
                    
                    self.logger.info(f"Next check in {interval/60:.1f} minutes")
                    
                    # Sleep with interrupt check
                    for _ in range(int(interval)):
                        if self.should_stop:
                            break
                        await asyncio.sleep(1)
        
        except Exception as e:
            self.logger.error(f"Worker error: {e}")
        
        finally:
            self._cleanup()
    
    async def _worker_iteration(self):
        """Single worker iteration"""
        self.logger.info("🔄 Starting worker iteration")
        
        self.state.total_runs += 1
        self.state.last_check_time = datetime.now()
        
        # Daily cost check
        if self._is_over_daily_cost_limit():
            self.logger.warning("Daily cost limit reached. Skipping iteration.")
            return
        
        total_processed = 0
        total_created = 0
        iteration_cost = 0.0
        
        # Process each category
        for category in self.worker_settings["categories"]:
            try:
                self.logger.info(f"📰 Processing category: {category}")
                
                # Get new articles for this category
                new_articles = await self._get_new_articles_for_category(category)
                
                if not new_articles:
                    self.logger.info(f"No new articles in {category}")
                    continue
                
                self.logger.info(f"Found {len(new_articles)} new articles in {category}")
                
                # Process articles
                processed, created, cost = await self._process_articles(new_articles, category)
                
                total_processed += processed
                total_created += created
                iteration_cost += cost
                
                # Update last check time for this category
                self.last_check_times[category] = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error processing category {category}: {e}")
                continue
        
        # Update global stats
        self.state.total_articles_processed += total_processed
        self.state.total_reels_created += total_created
        self.state.total_cost += iteration_cost
        self.state.successful_runs += 1
        
        # Save persistent data
        self.save_persistent_data()
        
        self.logger.info(f"✅ Worker iteration completed: {total_processed} processed, {total_created} reels created, ${iteration_cost:.4f} cost")
    
    async def _get_new_articles_for_category(self, category: str) -> List[Article]:
        """Kategori için yeni makaleleri al"""
        try:
            # Get latest news
            news_response = await content_service.get_latest_news(
                count=self.worker_settings["max_articles_per_run"] * 2,  # Get extra for filtering
                category=category,
                enable_scraping=True
            )
            
            if not news_response.success:
                self.logger.error(f"Failed to fetch news for {category}: {news_response.message}")
                return []
            
            # Filter new articles (since last check)
            last_check = self.last_check_times.get(category)
            if last_check:
                new_articles = [
                    article for article in news_response.articles
                    if article.published_at and article.published_at > last_check
                ]
            else:
                # First run for this category
                new_articles = news_response.articles
            
            # Apply quality filter
            quality_articles = [
                article for article in new_articles
                if self.is_quality_article(article)
            ]
            
            # Apply duplicate detection
            if self.worker_settings["duplicate_detection"]:
                # Get recent articles for duplicate check (simplified)
                recent_articles = news_response.articles[:20]  # Last 20 for comparison
                
                unique_articles = []
                for article in quality_articles:
                    if not self.is_duplicate_article(article, recent_articles):
                        unique_articles.append(article)
                
                quality_articles = unique_articles
            
            # Limit to max per run
            return quality_articles[:self.worker_settings["max_articles_per_run"]]
            
        except Exception as e:
            self.logger.error(f"Error getting new articles for {category}: {e}")
            return []
    
    async def _process_articles(self, articles: List[Article], category: str) -> tuple[int, int, float]:
        """Articles'ı işle ve reel oluştur"""
        processed = 0
        created = 0
        total_cost = 0.0
        
        for article in articles:
            try:
                self.logger.info(f"🎵 Processing: {article.title[:50]}...")
                
                # Create reel using RSS-optimized TTS
                result = await processing_service.rss_news_to_speech(
                    article=article,
                    voice=self.worker_settings["voice"],
                    model=self.worker_settings["model"],
                    use_summary_only=True
                )
                
                processed += 1
                
                if result.success:
                    created += 1
                    total_cost += result.result.estimated_cost
                    self.logger.info(f"✅ Reel created: {result.result.file_url}")
                else:
                    self.logger.warning(f"❌ TTS failed: {result.message}")
                
                # Delay between articles to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error processing article {article.title}: {e}")
                continue
        
        return processed, created, total_cost
    
    def _is_over_daily_cost_limit(self) -> bool:
        """Günlük maliyet limiti kontrolü"""
        daily_limit = self.worker_settings.get("cost_limit_daily", 5.0)
        
        # Today's cost calculation (simplified)
        # In production, this should track daily costs properly
        return self.state.total_cost > daily_limit
    
    def _calculate_smart_interval(self) -> int:
        """Smart interval hesaplama"""
        base_interval = self.worker_settings["interval_minutes"] * 60
        
        # If many new articles in last run, check more frequently
        if self.state.total_articles_processed > 0:
            recent_activity = min(self.state.total_articles_processed / 10, 2.0)
            return max(base_interval // 2, int(base_interval / recent_activity))
        
        return base_interval
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.should_stop = True
    
    def _cleanup(self):
        """Worker cleanup"""
        self.logger.info("🛑 Stopping RSS Worker...")
        
        self.state.is_running = False
        self.save_persistent_data()
        self.remove_pid_file()
        
        self.logger.info("✅ RSS Worker stopped")
    
    # ============ WORKER MANAGEMENT ============
    
    def get_worker_status(self) -> Dict[str, Any]:
        """Worker durumu"""
        return {
            "is_running": self.state.is_running,
            "start_time": self.state.start_time.isoformat() if self.state.start_time else None,
            "last_check_time": self.state.last_check_time.isoformat() if self.state.last_check_time else None,
            "uptime_minutes": (datetime.now() - self.state.start_time).total_seconds() / 60 if self.state.start_time else 0,
            "total_runs": self.state.total_runs,
            "successful_runs": self.state.successful_runs,
            "failed_runs": self.state.failed_runs,
            "success_rate": (self.state.successful_runs / self.state.total_runs * 100) if self.state.total_runs > 0 else 0,
            "consecutive_failures": self.state.consecutive_failures,
            "total_articles_processed": self.state.total_articles_processed,
            "total_reels_created": self.state.total_reels_created,
            "total_cost": round(self.state.total_cost, 6),
            "last_error": self.state.last_error,
            "categories_tracked": list(self.last_check_times.keys()),
            "next_check_in_minutes": self.worker_settings["interval_minutes"] if self.state.is_running else None,
            "settings": self.worker_settings
        }
    
    async def stop_worker(self):
        """Worker'ı durdur"""
        if not self.state.is_running:
            self.logger.warning("Worker not running")
            return
        
        self.logger.info("Stopping worker...")
        self.should_stop = True
        
        # Wait for graceful shutdown
        timeout = self.worker_settings.get("graceful_shutdown_timeout", 30)
        for _ in range(timeout):
            if not self.state.is_running:
                break
            await asyncio.sleep(1)
        
        if self.state.is_running:
            self.logger.warning("Worker did not stop gracefully")

# Global instance
rss_worker = RSSWorkerService()