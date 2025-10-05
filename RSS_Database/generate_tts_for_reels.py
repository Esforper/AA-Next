import json
import openai
import hashlib
from pathlib import Path
from datetime import datetime
import time
import os

from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv('../BackendAPIDemo/.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file!")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Audio output directory
AUDIO_DIR = Path("audio_output")
AUDIO_DIR.mkdir(exist_ok=True)

def generate_audio_filename(title: str, reel_id: str) -> str:
    """Ses dosyası adı oluştur"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title_short = "".join(c for c in title[:30] if c.isalnum() or c == ' ').replace(' ', '_')
    return f"tts_{timestamp}_{title_short}_{hash(reel_id) % 10000}.mp3"

def convert_to_speech(text: str, voice: str = "nova", model: str = "gpt-4o-mini-tts") -> dict:
    """
    BackendAPIDemo'daki TTS mantığını kullanarak metni sese çevir
    """
    try:
        # Dosya adı oluştur
        filename = generate_audio_filename(text[:50], str(hash(text)))
        file_path = AUDIO_DIR / filename
        
        print(f"  TTS çağrısı yapılıyor... ({len(text)} karakter)")
        
        # OpenAI TTS API çağrısı
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3",
            speed=1.0
        )
        
        # Dosyayı kaydet
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Dosya bilgileri
        file_size_bytes = file_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Süre tahmini (yaklaşık 150 kelime/dakika)
        word_count = len(text.split())
        duration_seconds = max(15, int(word_count / 2.5))  # ~150 wpm
        
        # Maliyet hesapla (gpt-4o-mini-tts için)
        char_count = len(text)
        # Input: $0.60 / 1M chars, Output: ~$0.015/minute
        input_cost = (char_count / 1_000_000) * 0.60
        output_cost = (duration_seconds / 60) * 0.015
        cost = input_cost + output_cost
        
        print(f"  ✓ Ses oluşturuldu: {filename} ({file_size_mb:.2f} MB)")
        
        return {
            'success': True,
            'filename': filename,
            'file_path': str(file_path),
            'audio_url': f"/audio/{filename}",
            'duration_seconds': duration_seconds,
            'file_size_mb': round(file_size_mb, 2),
            'character_count': char_count,
            'estimated_cost': round(cost, 6),
            'voice_used': voice,
            'model_used': model
        }
        
    except Exception as e:
        print(f"  ✗ TTS hatası: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def process_reels_for_tts(input_file: str, limit: int = 200, voice: str = "nova"):
    """
    Reels'leri TTS'e çevir
    """
    print("=" * 80)
    print("REELS TTS GENERATION")
    print("=" * 80)
    
    # JSON'u oku
    print(f"\n{input_file} dosyası okunuyor...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reels_data = json.load(f)
    
    total_reels = len(reels_data)
    print(f"Toplam reel: {total_reels}")
    
    # TTS'i olmayan reels'leri bul
    reels_without_tts = {
        reel_id: reel 
        for reel_id, reel in reels_data.items() 
        if reel.get('audio_url') is None
    }
    
    print(f"TTS'i olmayan reel: {len(reels_without_tts)}")
    print(f"İşlenecek reel sayısı: {min(limit, len(reels_without_tts))}")
    
    if len(reels_without_tts) == 0:
        print("\nTüm reels'lerin zaten TTS'i var!")
        return
    
    # İlk N tanesini seç
    reels_to_process = list(reels_without_tts.items())[:limit]
    
    print(f"\n{len(reels_to_process)} reel TTS'e çevriliyor...")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    total_cost = 0.0
    
    for i, (reel_id, reel) in enumerate(reels_to_process, 1):
        title = reel['news_data']['title'][:60]
        tts_content = reel.get('tts_content', '')
        
        print(f"\n[{i}/{len(reels_to_process)}] {title}...")
        
        if not tts_content:
            print("  ✗ TTS içeriği yok, atlanıyor")
            failed_count += 1
            continue
        
        # TTS oluştur
        result = convert_to_speech(tts_content, voice=voice, model="tts-1")
        
        if result['success']:
            # Reel'i güncelle
            reel['audio_url'] = result['audio_url']
            reel['duration_seconds'] = result['duration_seconds']
            reel['file_size_mb'] = result['file_size_mb']
            reel['voice_used'] = result['voice_used']
            reel['model_used'] = result['model_used']
            reel['estimated_cost'] = result['estimated_cost']
            reel['processing_time_seconds'] = 2.5  # Simulated
            reel['status'] = "published"
            
            success_count += 1
            total_cost += result['estimated_cost']
            
            print(f"  💰 Maliyet: ${result['estimated_cost']:.6f}")
        else:
            failed_count += 1
        
        # Rate limiting (OpenAI API limits için)
        time.sleep(0.5)
        
        # Her 20 reelde bir ara rapor
        if i % 20 == 0:
            print(f"\n--- İlerleme: {success_count} başarılı, {failed_count} başarısız ---")
            print(f"--- Toplam maliyet: ${total_cost:.4f} ---\n")
    
    print("\n" + "=" * 80)
    print("TTS İŞLEMİ TAMAMLANDI")
    print("=" * 80)
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {failed_count}")
    print(f"Toplam maliyet: ${total_cost:.4f}")
    
    # Güncellenmiş JSON'u kaydet
    output_file = input_file.replace('.json', '_with_tts.json')
    print(f"\nGüncellenmiş reels '{output_file}' dosyasına kaydediliyor...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reels_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Kaydedildi!")
    
    # İstatistikler
    print("\n" + "=" * 80)
    print("FINAL İSTATİSTİKLER")
    print("=" * 80)
    
    total_with_tts = sum(1 for reel in reels_data.values() if reel.get('audio_url'))
    total_without_tts = total_reels - total_with_tts
    
    print(f"Toplam reel: {total_reels}")
    print(f"TTS'li reel: {total_with_tts}")
    print(f"TTS'siz reel: {total_without_tts}")
    print(f"Bu çalıştırmada eklenen: {success_count}")
    
    print("\n" + "=" * 80)
    print("SONRAKİ ADIMLAR")
    print("=" * 80)
    print(f"1. Ses dosyaları: {AUDIO_DIR}")
    print(f"2. Güncellenmiş JSON: {output_file}")
    print(f"3. BackendAPIDemo'ya kopyala:")
    print(f"   cp {output_file} BackendAPIDemo/outputs/reels_data.json")
    print(f"   cp -r {AUDIO_DIR}/* BackendAPIDemo/outputs/audio/")

def main():
    import sys
    
    # Kullanım
    if len(sys.argv) < 2:
        print("Kullanım: python generate_tts_for_reels.py <input_file> [limit] [voice]")
        print("Örnek: python generate_tts_for_reels.py reels_data_ready_for_tts.json 200 nova")
        sys.exit(1)
    
    input_file = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    voice = sys.argv[3] if len(sys.argv) > 3 else "nova"
    
    # API key kontrolü
    if not OPENAI_API_KEY:
        print("HATA: OPENAI_API_KEY environment variable tanımlı değil!")
        print("Çalıştırmadan önce:")
        print("  export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    process_reels_for_tts(input_file, limit, voice)

if __name__ == "__main__":
    main()