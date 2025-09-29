from pydantic_settings import BaseSettings
from typing import Dict, Any, List, Optional
from pathlib import Path

class Settings(BaseSettings):
    """
    Universal configuration system
    Yeni sistem eklerken buraya yeni ayarlar ekle
    """
    
    # ============ CORE SETTINGS ============
    debug: bool = False
    app_name: str = "AA News Universal API"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ============ NEWS SYSTEM ============
    # Yeni news provider eklemek için: news_provider = "yeni_provider_adi"
    news_provider: str = "aa"  # aa, reuters, bbc, twitter vb
    news_default_category: str = "guncel"
    news_max_articles: int = 50
    news_scraping_enabled: bool = True
    news_cache_ttl: int = 300  # seconds
    
    # ============ TTS SYSTEM ============
    # Yeni TTS provider eklemek için: tts_provider = "yeni_provider"
    tts_provider: str = "openai"  # openai, azure, elevenlabs vb
    tts_voice: str = "nova"  # Updated default
    tts_model: str = "gpt-4o-mini-tts"  # Updated default
    tts_speed: float = 1.1  # Optimized for news reels
    
    # OpenAI specific
    openai_api_key: str = ""
    openai_base_url: Optional[str] = None
    
    # ============ STORAGE SYSTEM ============
    # Yeni storage provider eklemek için: storage_provider = "yeni_storage"
    storage_provider: str = "local"  # local, s3, azure, gcp vb
    storage_base_path: str = "outputs"
    
    # S3 settings (isteğe bağlı)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # ============ RSS WORKER SYSTEM (NEW) ============
    # Background RSS monitoring and reel creation
    rss_worker_enabled: bool = True
    rss_worker_interval_minutes: int = 15  # Check RSS every 15 minutes
    rss_worker_max_articles_per_run: int = 10  # Max articles to process per run
    rss_worker_categories: List[str] = ["guncel"]  # Categories to monitor
    rss_worker_voice: str = "nova"  # Default voice for worker-generated reels
    rss_worker_model: str = "gpt-4o-mini-tts"  # Default TTS model
    rss_worker_min_chars: int = 100  # Minimum characters for TTS processing
    rss_worker_max_chars: int = 8000  # Maximum characters for TTS processing
    
    # Worker retry & error handling
    rss_worker_max_retries: int = 3  # Max retries for failed operations
    rss_worker_retry_delay_seconds: int = 60  # Delay between retries
    rss_worker_stop_on_consecutive_failures: int = 5  # Stop worker after N consecutive failures
    
    # Worker file management
    rss_worker_data_file: str = "outputs/worker_data/last_check.json"  # Track last check times
    rss_worker_log_file: str = "outputs/worker_data/worker.log"  # Worker-specific logs
    rss_worker_pid_file: str = "outputs/worker_data/worker.pid"  # Process ID file
    
    # Worker scheduling
    rss_worker_start_delay_seconds: int = 10  # Wait before first run
    rss_worker_graceful_shutdown_timeout: int = 15  # Max time to wait for graceful shutdown
    
    # ============ GAME SYSTEM ============
    # Oyun sistemi eklemek için bu bölümü kullan
    game_enabled: bool = False
    game_max_players: int = 100
    game_tick_rate: float = 0.1  # seconds
    game_world_size: int = 1000
    game_save_interval: int = 30  # seconds
    
    # ============ AI CHAT SYSTEM ============
    # AI chat sistemi eklemek için
    ai_chat_enabled: bool = False
    ai_chat_model: str = "gpt-4"
    ai_chat_max_history: int = 50
    ai_chat_temperature: float = 0.7
    
    # ============ CRYPTO TRADING SYSTEM ============
    # Crypto trading sistemi eklemek için
    crypto_enabled: bool = False
    crypto_exchange: str = "binance"  # binance, coinbase vb
    crypto_api_key: Optional[str] = None
    crypto_api_secret: Optional[str] = None
    crypto_sandbox: bool = True
    
    # ============ VIDEO PROCESSING SYSTEM ============
    # Video işleme sistemi eklemek için
    video_enabled: bool = False
    video_max_size_mb: int = 100
    video_output_quality: str = "720p"
    video_supported_formats: List[str] = ["mp4", "avi", "mov"]
    
    # ============ REALTIME/WEBSOCKET SETTINGS ============
    websocket_enabled: bool = True
    websocket_max_connections: int = 1000
    websocket_ping_interval: int = 15
    
    # ============ DATABASE SETTINGS (İleride eklenebilir) ============
    database_url: Optional[str] = None
    database_echo: bool = False
    
    # ============ CACHE SETTINGS ============
    cache_enabled: bool = True
    cache_type: str = "memory"  # memory, redis
    redis_url: Optional[str] = None
    
    # ============ MONITORING & LOGGING ============
    log_level: str = "INFO"
    log_file: Optional[str] = "app.log"
    enable_metrics: bool = True
    sentry_dsn: Optional[str] = None
    
    # ============ UNIVERSAL PROVIDER SETTINGS ============
    # Yeni provider'lar için genel ayarlar
    providers: Dict[str, Any] = {}
    features: Dict[str, bool] = {}
    
    # RSS Worker feature flags (for A/B testing or gradual rollout)
    rss_worker_smart_scheduling: bool = True  # Adjust interval based on content frequency
    rss_worker_duplicate_detection: bool = True  # Skip duplicate articles
    rss_worker_quality_filter: bool = False  # Filter low-quality articles
    rss_worker_cost_limit_daily: float = 5.0  # Daily TTS cost limit in USD
    
    # Performance tuning
    rss_worker_concurrent_processing: bool = False  # Process multiple articles concurrently
    rss_worker_batch_size: int = 5  # Number of articles to process in batch
    
    # ÖRNEK: Yeni bir sistem eklemek
    # ecommerce_enabled: bool = False
    # ecommerce_payment_provider: str = "stripe"
    # ecommerce_currency: str = "USD"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable prefix
        # Örnek: RSS_WORKER_ENABLED=false -> settings.rss_worker_enabled
        env_prefix = ""

    def get_worker_data_dir(self) -> Path:
        """Worker data directory'yi al ve oluştur"""
        data_dir = Path(self.storage_base_path) / "worker_data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_worker_settings(self) -> Dict[str, Any]:
        """Worker'a özel ayarları dict olarak döndür"""
        return {
            "enabled": self.rss_worker_enabled,
            "interval_minutes": self.rss_worker_interval_minutes,
            "max_articles_per_run": self.rss_worker_max_articles_per_run,
            "categories": self.rss_worker_categories,
            "voice": self.rss_worker_voice,
            "model": self.rss_worker_model,
            "min_chars": self.rss_worker_min_chars,
            "max_chars": self.rss_worker_max_chars,
            "max_retries": self.rss_worker_max_retries,
            "retry_delay": self.rss_worker_retry_delay_seconds,
            "data_file": self.rss_worker_data_file,
            "log_file": self.rss_worker_log_file,
            "pid_file": self.rss_worker_pid_file,
            "cost_limit_daily": self.rss_worker_cost_limit_daily,
            "smart_scheduling": self.rss_worker_smart_scheduling,
            "duplicate_detection": self.rss_worker_duplicate_detection,
            "quality_filter": self.rss_worker_quality_filter
        }

# Global settings instance
settings = Settings()