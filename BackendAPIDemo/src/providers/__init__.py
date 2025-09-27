# ================================
# src/providers/__init__.py - Süper Basit!
# ================================

"""
Basit provider sistemi
Yeni provider eklemek için sadece dosya oluştur + 2 function yaz
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