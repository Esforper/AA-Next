# ================================
# src/services/rss_worker.py - Fixed RSS Worker Service
# ================================

"""
RSS Worker Service - Background RSS monitoring and automatic reel creation
Runs continuously, checks RSS feeds, and creates reels automatically

FIX: Now properly compares RSS articles with EXISTING REELS instead of RSS self-comparison
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
    
    # ============ MAIN WORKER METHODS ============
    
    async def _get_new_articles_for_category(self, category: str) -> List[Article]:
        """
        🔥 FIX: Kategori için yeni makaleleri al - EXISTING REELS ile karşılaştır
        """
        try:
            self.logger.info(f"📰 Fetching RSS articles for category: {category}")
            
            # 1. RSS'den haberleri al
            news_response = await content_service.get_latest_news(
                count=self.worker_settings["max_articles_per_run"] * 3,  # Extra for filtering
                category=category,
                enable_scraping=True
            )
            
            if not news_response.success:
                self.logger.error(f"Failed to fetch news for {category}: {news_response.message}")
                return []
            
            self.logger.info(f"📥 Got {len(news_response.articles)} RSS articles")
            
            # 2. 🔥 FIX: Mevcut reels'lerin URL'lerini al (reels_analytics'den)
            existing_urls = await self._get_existing_reel_urls()
            self.logger.info(f"📊 Found {len(existing_urls)} existing reel URLs")
            
            # 3. 🔥 FIX: RSS haberlerini mevcut reels ile karşılaştır
            new_articles = []
            for article in news_response.articles:
                if str(article.url) not in existing_urls:
                    new_articles.append(article)
                else:
                    self.logger.debug(f"⏭️  Skipping existing article: {article.title[:50]}...")
            
            self.logger.info(f"🆕 Found {len(new_articles)} NEW articles (not in existing reels)")
            
            # 4. Quality filter uygula
            quality_articles = [
                article for article in new_articles
                if self.is_quality_article(article)
            ]
            
            self.logger.info(f"✅ {len(quality_articles)} articles passed quality filter")
            
            # 5. Timestamp-based filtering (opsiyonel, secondary check)
            if self.worker_settings.get("use_timestamp_filter", True):
                last_check = self.last_check_times.get(category)
                if last_check:
                    timestamp_filtered = [
                        article for article in quality_articles
                        if article.published_at and article.published_at > last_check
                    ]
                    if len(timestamp_filtered) < len(quality_articles):
                        self.logger.info(f"⏰ Timestamp filter: {len(quality_articles)} → {len(timestamp_filtered)}")
                        quality_articles = timestamp_filtered
            
            # 6. Limit to max per run
            final_articles = quality_articles[:self.worker_settings["max_articles_per_run"]]
            
            if final_articles:
                self.logger.info(f"🎯 Final selection: {len(final_articles)} articles to process")
                for i, article in enumerate(final_articles, 1):
                    self.logger.info(f"   {i}. {article.title[:60]}...")
            else:
                self.logger.info("🚫 No new articles to process")
            
            return final_articles
            
        except Exception as e:
            self.logger.error(f"Error getting new articles for {category}: {e}")
            return []
    
    async def _get_existing_reel_urls(self) -> Set[str]:
        """
        🔥 FIX: Mevcut reels'lerin URL'lerini al
        Bu fonksiyon reels_analytics'e bağlanır
        """
        try:
            # Import here to avoid circular imports
            from ..services.reels_analytics import reels_analytics
            
            # Tüm published reels'i al
            existing_reels = await reels_analytics.get_all_published_reels()
            
            # URL'leri extract et
            existing_urls = {
                str(reel.news_data.url) for reel in existing_reels
                if reel.news_data and reel.news_data.url
            }
            
            self.logger.debug(f"📊 Existing reel URLs: {len(existing_urls)}")
            return existing_urls
            
        except Exception as e:
            self.logger.error(f"Error getting existing reel URLs: {e}")
            return set()
    
    # ============ WORKER ITERATION METHODS ============
    
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
                
                # Get new articles for this category (FIXED METHOD)
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
                    if hasattr(result.result, 'estimated_cost'):
                        total_cost += result.result.estimated_cost
                    
                    self.logger.info(f"✅ Reel created: {article.title[:40]}...")
                else:
                    self.logger.error(f"❌ Failed to create reel: {result.message}")
                
            except Exception as e:
                self.logger.error(f"Error processing article {article.title[:30]}: {e}")
                
        return processed, created, total_cost
    
    def _is_over_daily_cost_limit(self) -> bool:
        """Daily cost limit kontrolü"""
        daily_limit = self.worker_settings.get("cost_limit_daily", 5.0)
        
        # Today's cost (basit implementation)
        today = datetime.now().date()
        # Bu gerçek implementationda daily cost tracking olmalı
        # Şimdilik global cost'u kullan
        
        return self.state.total_cost > daily_limit
    
    # ============ QUALITY CONTROL METHODS (Unchanged) ============
    
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
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Quality check error: {e}")
            return True  # Default to accept
    
    def _is_quality_title(self, title: str) -> bool:
        """Title kalite kontrolü"""
        if not title or len(title.strip()) < 10:
            return False
        
        # Spam pattern kontrolü
        for pattern in self.spam_patterns:
            if re.search(pattern, title):
                return False
        
        return True
    
    def _is_quality_content(self, content: str) -> bool:
        """Content kalite kontrolü"""
        if not content or len(content.strip()) < 50:
            return False
        
        # Encoding issue kontrolü
        text = content.lower()
        encoding_issues = ['ğ�', 'Ä°', 'ÄŸ', 'Å�', 'â€™', '&amp;', '&lt;', '&gt;']
        
        for issue in encoding_issues:
            if issue in text:
                return True
        
        # HTML tag kontrolü (temizlenmemiş)
        if re.search(r'<[^>]+>', text):
            return True
        
        return False
    
    # ============ WORKER MANAGEMENT (Unchanged) ============
    
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
    
    def _calculate_smart_interval(self) -> int:
        """Smart interval calculation based on content frequency"""
        base_interval = self.worker_settings["interval_minutes"] * 60
        
        # If no new content found in recent runs, increase interval
        if self.state.consecutive_failures == 0 and hasattr(self, '_last_content_found'):
            if not self._last_content_found:
                return min(base_interval * 2, 3600)  # Max 1 hour
        
        return base_interval
    
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
    
    # ============ WORKER STATUS ============
    
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