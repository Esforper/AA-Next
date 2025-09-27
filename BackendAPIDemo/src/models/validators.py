# ================================
# src/models/validators.py
# ================================

from typing import Dict, Any, List

def validate_provider_config(provider_type: str, config: Dict[str, Any]) -> bool:
    """Provider config validation"""
    
    # Required fields for each provider type
    required_fields = {
        "news": ["source_url"],
        "tts": ["api_key"],
        "game": ["max_players"],
        "ai_chat": ["model", "api_key"],
        "storage": ["base_path"],
        "crypto": ["api_key", "api_secret"],
        "video": ["max_size_mb"],
        
        # Yeni sistem eklerken buraya ekle:
        # "ecommerce": ["payment_api_key", "currency"],
        # "iot": ["device_registry_url"],
    }
    
    if provider_type in required_fields:
        for field in required_fields[provider_type]:
            if field not in config:
                return False
    
    return True

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """File type validation"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [t.lower() for t in allowed_types]

def validate_text_length(text: str, min_length: int = 1, max_length: int = 50000) -> bool:
    """Text length validation"""
    return min_length <= len(text) <= max_length

# YENİ SİSTEM EKLEME REHBERİ:
# 1. src/models/ altında yeni dosya oluştur (örn: ecommerce.py)
# 2. Yeni modelleri tanımla
# 3. __init__.py dosyasına import ekle
# 4. validators.py'a gerekli validation'ları ekle
# 5. Enum'lara yeni değerler ekle