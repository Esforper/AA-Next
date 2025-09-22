"""
Configuration Management
Environment variables, API keys ve uygulama ayarları
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


@dataclass
class OpenAIConfig:
    """OpenAI API ayarları"""
    api_key: str
    model: str = "tts-1"
    voice: str = "alloy"
    speed: float = 1.0
    response_format: str = "mp3"
    
    # Pricing (USD per 1M characters)
    pricing: Dict[str, float] = None
    
    def __post_init__(self):
        if self.pricing is None:
            self.pricing = {
                "tts-1": 0.015,     # $15/1M chars
                "tts-1-hd": 0.030   # $30/1M chars
            }


@dataclass
class AppConfig:
    """Uygulama ayarları"""
    # Directories
    output_dir: str = "audio_outputs"
    logs_dir: str = "logs"
    cache_dir: str = "cache"
    
    # RSS settings
    default_category: str = "guncel"
    rss_timeout: int = 30
    rss_max_retries: int = 3
    
    # Scraping settings
    scraping_delay: float = 1.5
    scraping_timeout: int = 20
    scraping_max_workers: int = 3
    enable_scraping: bool = True
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    max_log_files: int = 10
    
    def __post_init__(self):
        # Dizinleri oluştur
        for directory in [self.output_dir, self.logs_dir, self.cache_dir]:
            Path(directory).mkdir(exist_ok=True)


class ConfigManager:
    """Konfigürasyon yöneticisi"""
    
    def __init__(self):
        self._openai_config = None
        self._app_config = None
    
    def get_openai_config(self) -> OpenAIConfig:
        """OpenAI konfigürasyonunu al"""
        if self._openai_config is None:
            self._openai_config = self._load_openai_config()
        return self._openai_config
    
    def get_app_config(self) -> AppConfig:
        """Uygulama konfigürasyonunu al"""
        if self._app_config is None:
            self._app_config = self._load_app_config()
        return self._app_config
    
    def _load_openai_config(self) -> OpenAIConfig:
        """OpenAI konfigürasyonunu yükle"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "OpenAI API key bulunamadı! "
                "OPENAI_API_KEY environment variable ayarlayın"
            )
        
        return OpenAIConfig(
            api_key=api_key,
            model=os.getenv('OPENAI_TTS_MODEL', 'tts-1'),
            voice=os.getenv('OPENAI_TTS_VOICE', 'alloy'),
            speed=float(os.getenv('OPENAI_TTS_SPEED', '1.0')),
            response_format=os.getenv('OPENAI_TTS_FORMAT', 'mp3')
        )
    
    def _load_app_config(self) -> AppConfig:
        """Uygulama konfigürasyonunu yükle"""
        return AppConfig(
            output_dir=os.getenv('OUTPUT_DIR', 'audio_outputs'),
            logs_dir=os.getenv('LOGS_DIR', 'logs'),
            cache_dir=os.getenv('CACHE_DIR', 'cache'),
            default_category=os.getenv('DEFAULT_CATEGORY', 'guncel'),
            rss_timeout=int(os.getenv('RSS_TIMEOUT', '30')),
            rss_max_retries=int(os.getenv('RSS_MAX_RETRIES', '3')),
            scraping_delay=float(os.getenv('SCRAPING_DELAY', '1.5')),
            scraping_timeout=int(os.getenv('SCRAPING_TIMEOUT', '20')),
            scraping_max_workers=int(os.getenv('SCRAPING_MAX_WORKERS', '3')),
            enable_scraping=os.getenv('ENABLE_SCRAPING', 'true').lower() == 'true',
            api_host=os.getenv('API_HOST', '0.0.0.0'),
            api_port=int(os.getenv('API_PORT', '8000')),
            api_debug=os.getenv('API_DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            max_log_files=int(os.getenv('MAX_LOG_FILES', '10'))
        )
    
    def create_sample_env(self) -> str:
        """Örnek .env dosyası oluştur"""
        env_content = """# OpenAI API Settings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
OPENAI_TTS_SPEED=1.0
OPENAI_TTS_FORMAT=mp3

# Application Settings
OUTPUT_DIR=audio_outputs
LOGS_DIR=logs
CACHE_DIR=cache

# RSS Settings
DEFAULT_CATEGORY=guncel
RSS_TIMEOUT=30
RSS_MAX_RETRIES=3

# Web Scraping Settings
SCRAPING_DELAY=1.5
SCRAPING_TIMEOUT=20
SCRAPING_MAX_WORKERS=3
ENABLE_SCRAPING=true

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Logging
LOG_LEVEL=INFO
MAX_LOG_FILES=10
"""
        
        env_file = ".env"
        if not os.path.exists(env_file):
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            return f"Örnek {env_file} dosyası oluşturuldu"
        else:
            return f"{env_file} dosyası zaten mevcut"
    
    def validate_config(self) -> Dict[str, bool]:
        """Konfigürasyon doğruluğunu kontrol et"""
        results = {}
        
        try:
            openai_config = self.get_openai_config()
            results['openai_api_key'] = bool(openai_config.api_key)
            results['openai_model'] = openai_config.model in openai_config.pricing
        except Exception as e:
            results['openai_config'] = False
            results['openai_error'] = str(e)
        
        try:
            app_config = self.get_app_config()
            results['directories'] = all([
                Path(app_config.output_dir).exists(),
                Path(app_config.logs_dir).exists(),
                Path(app_config.cache_dir).exists()
            ])
            results['api_port'] = 1000 <= app_config.api_port <= 65535
        except Exception as e:
            results['app_config'] = False
            results['app_error'] = str(e)
        
        return results


# Global config manager instance
config_manager = ConfigManager()

def get_openai_config() -> OpenAIConfig:
    """OpenAI konfigürasyonunu al (global function)"""
    return config_manager.get_openai_config()

def get_app_config() -> AppConfig:
    """App konfigürasyonunu al (global function)"""
    return config_manager.get_app_config()


# Test ve örnek kullanım
if __name__ == "__main__":
    print("=== CONFIGURATION TEST ===")
    
    # Örnek .env dosyası oluştur
    result = config_manager.create_sample_env()
    print(f"ENV file: {result}")
    
    # Konfigürasyon doğrulama
    validation = config_manager.validate_config()
    print(f"\nValidation results:")
    for key, value in validation.items():
        status = "✓" if value else "✗"
        print(f"  {key}: {status}")
    
    try:
        # OpenAI config
        openai_config = get_openai_config()
        print(f"\nOpenAI Config:")
        print(f"  Model: {openai_config.model}")
        print(f"  Voice: {openai_config.voice}")
        print(f"  API Key: {'***' + openai_config.api_key[-4:] if openai_config.api_key else 'Not set'}")
    except Exception as e:
        print(f"\nOpenAI Config Error: {e}")
    
    try:
        # App config
        app_config = get_app_config()
        print(f"\nApp Config:")
        print(f"  Default category: {app_config.default_category}")
        print(f"  Scraping enabled: {app_config.enable_scraping}")
        print(f"  API port: {app_config.api_port}")
        print(f"  Output dir: {app_config.output_dir}")
    except Exception as e:
        print(f"\nApp Config Error: {e}")