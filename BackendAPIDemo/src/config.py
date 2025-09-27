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
    tts_voice: str = "alloy"
    tts_model: str = "tts-1"
    tts_speed: float = 1.0
    
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
    websocket_ping_interval: int = 30
    
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
    
    # ÖRNEK: Yeni bir sistem eklemek
    # ecommerce_enabled: bool = False
    # ecommerce_payment_provider: str = "stripe"
    # ecommerce_currency: str = "USD"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable prefix
        # Örnek: NEWS_PROVIDER=reuters -> settings.news_provider
        env_prefix = ""

# Global settings instance
settings = Settings()