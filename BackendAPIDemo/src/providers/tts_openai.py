# ================================
# src/providers/tts_openai.py - Süper Basit!
# ================================

"""
OpenAI TTS Provider - Basit ve Hızlı
"""

import openai
import hashlib
from pathlib import Path
from datetime import datetime
import json

from ..models.tts import TTSRequest, AudioResult
from ..config import settings
from . import register_provider

# OpenAI client
client = openai.OpenAI(api_key=settings.openai_api_key)

async def convert_to_speech(text: str, voice: str = "alloy", model: str = "tts-1", **kwargs) -> AudioResult:
    """
    Text'i sese çevir - Basit implementation
    """
    try:
        # Dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_short = "".join(c for c in text[:30] if c.isalnum() or c == ' ').replace(' ', '_')
        filename = f"tts_{timestamp}_{title_short}_{hash(text) % 10000}.mp3"
        
        # Output path
        output_dir = Path(settings.storage_base_path)
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / filename
        
        # OpenAI API çağrısı
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3",
            speed=kwargs.get('speed', 1.0)
        )
        
        # Dosyayı kaydet
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Maliyet hesapla
        char_count = len(text)
        cost = (char_count / 1_000_000) * 0.015  # $15 per 1M chars
        
        # Basit subtitle oluştur
        sentences = text.split('.')
        subtitles = []
        current_time = 0
        for sentence in sentences:
            if len(sentence.strip()) > 5:
                duration = max(2, len(sentence.split()) * 0.4)
                subtitles.append({
                    "start_time": current_time,
                    "end_time": current_time + duration,
                    "text": sentence.strip()
                })
                current_time += duration + 0.5
        
        # Cost tracking (basit)
        save_cost_log(char_count, cost, filename)
        
        result = AudioResult(
            success=True,
            file_path=str(file_path),
            file_url=f"/audio/{filename}",
            file_size_bytes=file_path.stat().st_size,
            character_count=char_count,
            estimated_cost=cost,
            subtitles=subtitles,
            provider="openai",
            model_used=model,
            voice_used=voice
        )
        
        print(f"✅ TTS: {filename} - {char_count} chars - ${cost:.4f}")
        return result
        
    except Exception as e:
        print(f"❌ TTS error: {e}")
        return AudioResult(
            success=False,
            error_message=str(e),
            character_count=len(text)
        )

def save_cost_log(char_count: int, cost: float, filename: str):
    """Basit cost tracking"""
    try:
        log_file = Path(settings.storage_base_path) / "tts_costs.json"
        
        # Mevcut log'u oku
        costs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                costs = json.load(f)
        
        # Yeni entry ekle
        costs.append({
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'character_count': char_count,
            'estimated_cost': cost
        })
        
        # Kaydet
        with open(log_file, 'w') as f:
            json.dump(costs, f, indent=2)
            
    except Exception as e:
        print(f"❌ Cost log error: {e}")

async def get_cost_stats() -> Dict:
    """Basit maliyet istatistikleri"""
    try:
        log_file = Path(settings.storage_base_path) / "tts_costs.json"
        if not log_file.exists():
            return {"total_cost": 0, "total_requests": 0}
        
        with open(log_file, 'r') as f:
            costs = json.load(f)
        
        total_cost = sum(c.get('estimated_cost', 0) for c in costs)
        total_chars = sum(c.get('character_count', 0) for c in costs)
        
        return {
            "total_requests": len(costs),
            "total_cost": round(total_cost, 6),
            "total_characters": total_chars,
            "average_cost": round(total_cost / len(costs), 6) if costs else 0
        }
        
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return {"error": str(e)}

# Provider'ı kaydet  
register_provider("tts_openai", {
    "convert_to_speech": convert_to_speech,
    "get_cost_stats": get_cost_stats
})