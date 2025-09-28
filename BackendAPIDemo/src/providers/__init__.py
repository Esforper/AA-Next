# ================================
# src/providers/__init__.py - Auto-loading Provider System
# ================================

"""
Provider sistemi - Otomatik provider yükleme
Provider dosyaları otomatik olarak import edilir ve register olur
"""

# Provider registry - otomatik keşif için
PROVIDERS = {}

def register_provider(name: str, provider_func):
    """Provider kaydet"""
    PROVIDERS[name] = provider_func
    print(f"✅ Provider registered: {name}")

def get_provider(name: str):
    """Provider al"""
    return PROVIDERS.get(name)

# ============ AUTO-LOADING PROVIDERS ============

def _load_providers():
    """Mevcut provider'ları otomatik yükle"""
    
    # News providers
    try:
        from . import news_aa
        print("✅ News AA provider loaded")
    except ImportError as e:
        print(f"⚠️  News AA provider failed: {e}")
    
    # TTS providers
    try:
        from . import tts_openai
        print("✅ TTS OpenAI provider loaded")
    except ImportError as e:
        print(f"⚠️  TTS OpenAI provider failed: {e}")
    
    # Game providers (optional)
    try:
        from . import game_engine
        print("✅ Game Engine provider loaded")
    except ImportError:
        pass  # Optional provider
    
    # Video providers (optional)
    try:
        from . import video_processor
        print("✅ Video Processor provider loaded")
    except ImportError:
        pass  # Optional provider
    
    # Yeni provider eklemek için buraya ekle:
    # try:
    #     from . import yeni_provider
    #     print("✅ Yeni Provider loaded")
    # except ImportError as e:
    #     print(f"⚠️  Yeni Provider failed: {e}")

# Provider'ları hemen yükle
_load_providers()

# Export functions
__all__ = [
    "PROVIDERS",
    "register_provider", 
    "get_provider"
]

# Debug: Provider sayısını göster
if PROVIDERS:
    print(f"🎯 Total providers loaded: {len(PROVIDERS)}")
    for provider_name in PROVIDERS.keys():
        print(f"   - {provider_name}")
else:
    print("⚠️  No providers loaded!")
    
# Provider status kontrolü
def get_provider_status():
    """Provider durumlarını kontrol et"""
    status = {
        "total_providers": len(PROVIDERS),
        "providers": list(PROVIDERS.keys()),
        "news_available": any("news_" in p for p in PROVIDERS.keys()),
        "tts_available": any("tts_" in p for p in PROVIDERS.keys()),
        "game_available": any("game_" in p for p in PROVIDERS.keys()),
        "video_available": any("video_" in p for p in PROVIDERS.keys())
    }
    return status