"""
Gelişmiş TTS Dönüştürücü - Seçilmiş AA Haberleri için
OpenAI TTS API kullanarak ses dosyaları oluşturur
"""

import json
import openai
import hashlib
from pathlib import Path
from datetime import datetime
import time
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

class EnhancedTTSGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """TTS Generator başlat"""
        # .env dosyasından API key yükle
        env_paths = [
            '.env',
            '../.env',
            '../BackendAPIDemo/.env',
            'BackendAPIDemo/.env'
        ]
        
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                break
        
        # API key ayarla
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY bulunamadı! .env dosyası veya parameter olarak sağlayın.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Audio output directory
        self.audio_dir = Path("audio_output")
        self.audio_dir.mkdir(exist_ok=True)
        
        # TTS ayarları
        self.default_voice = "nova"  # nova, alloy, echo, fable, onyx, shimmer
        self.default_model = "tts-1"  # tts-1 veya tts-1-hd
        self.default_speed = 1.0
        
        # İstatistikler
        self.stats = {
            'total_processed': 0,
            'success': 0,
            'failed': 0,
            'total_cost': 0.0,
            'total_duration': 0,
            'total_characters': 0
        }
    
    def generate_audio_filename(self, title: str, guid: str) -> str:
        """Ses dosyası adı oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Başlıktan güvenli dosya adı oluştur
        title_safe = "".join(c for c in title[:30] if c.isalnum() or c == ' ').replace(' ', '_')
        # GUID'den kısa hash
        guid_hash = hashlib.md5(str(guid).encode()).hexdigest()[:8]
        return f"tts_{timestamp}_{title_safe}_{guid_hash}.mp3"
    
    def prepare_tts_content(self, news_item: Dict) -> str:
            """Haber verisinden TTS içeriği hazırla (Öncelik: summary)."""
            scraped = news_item.get('scraped_content', {})
            
            # Öncelik 1: 'summary' alanını al
            # 'description' alanını da bir yedek olarak kullanabiliriz
            summary = scraped.get('summary') or news_item.get('description')
            
            # summary varsa ve boş değilse, sadece summary'yi döndür
            if summary and summary.strip():
                return summary.strip()
            
            # Öncelik 2: 'summary' yoksa 'title' alanına geri dön
            title = news_item.get('title')
            if title and title.strip():
                return title.strip()
                
            # Hiçbir şey bulunamazsa boş string döndür
            return ""
    
    def calculate_cost(self, char_count: int, model: str = "tts-1") -> float:
        """TTS maliyetini hesapla"""
        # OpenAI TTS pricing (2024)
        # tts-1: $0.015 per 1K characters
        # tts-1-hd: $0.030 per 1K characters
        
        if model == "tts-1-hd":
            rate = 0.030
        else:
            rate = 0.015
        
        return (char_count / 1000) * rate
    
    def estimate_duration(self, text: str) -> int:
        """Metin uzunluğundan tahmini ses süresi hesapla"""
        # Ortalama konuşma hızı: 150 kelime/dakika
        word_count = len(text.split())
        minutes = word_count / 150
        seconds = int(minutes * 60)
        # Minimum 10 saniye
        return max(10, seconds)
    
    async def convert_single_to_speech(self, 
                                      text: str, 
                                      filename: str,
                                      voice: Optional[str] = None,
                                      model: Optional[str] = None,
                                      speed: Optional[float] = None) -> Dict:
        """Tek bir metni sese çevir"""
        try:
            voice = voice or self.default_voice
            model = model or self.default_model
            speed = speed or self.default_speed
            
            file_path = self.audio_dir / filename
            
            print(f"  🎙️ TTS işlemi: {len(text)} karakter, {voice} ses, {model} model")
            
            # OpenAI TTS API çağrısı
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="mp3",
                speed=speed
            )
            
            # Dosyayı kaydet
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Dosya bilgileri
            file_size_bytes = file_path.stat().st_size
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Metrikler
            duration_seconds = self.estimate_duration(text)
            cost = self.calculate_cost(len(text), model)
            
            print(f"  ✓ Ses oluşturuldu: {filename} ({file_size_mb:.2f} MB, {duration_seconds}s)")
            
            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'audio_url': f"/audio/{filename}",
                'duration_seconds': duration_seconds,
                'file_size_mb': round(file_size_mb, 2),
                'character_count': len(text),
                'word_count': len(text.split()),
                'estimated_cost': round(cost, 6),
                'voice_used': voice,
                'model_used': model,
                'speed_used': speed,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ❌ TTS hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    def convert_to_speech_sync(self, 
                               text: str, 
                               filename: str,
                               voice: Optional[str] = None,
                               model: Optional[str] = None,
                               speed: Optional[float] = None) -> Dict:
        """Senkron TTS dönüşümü (async olmayan versiyon)"""
        try:
            voice = voice or self.default_voice
            model = model or self.default_model
            speed = speed or self.default_speed
            
            file_path = self.audio_dir / filename
            
            # OpenAI TTS API çağrısı
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="mp3",
                speed=speed
            )
            
            # Dosyayı kaydet
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Dosya bilgileri
            file_size_bytes = file_path.stat().st_size
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Metrikler
            duration_seconds = self.estimate_duration(text)
            cost = self.calculate_cost(len(text), model)
            
            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'audio_url': f"/audio/{filename}",
                'duration_seconds': duration_seconds,
                'file_size_mb': round(file_size_mb, 2),
                'character_count': len(text),
                'word_count': len(text.split()),
                'estimated_cost': round(cost, 6),
                'voice_used': voice,
                'model_used': model,
                'speed_used': speed,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    def load_existing_audio_records(self, audio_record_file: str = "audio_records.json") -> Dict:
        """Daha önce oluşturulmuş ses kayıtlarını yükle"""
        if os.path.exists(audio_record_file):
            with open(audio_record_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_audio_record(self, guid: str, audio_info: Dict, audio_record_file: str = "audio_records.json"):
        """Ses kaydını kaydet"""
        records = self.load_existing_audio_records(audio_record_file)
        records[guid] = audio_info
        with open(audio_record_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def process_news_collection(self, 
                               input_file: str,
                               output_file: Optional[str] = None,
                               limit: Optional[int] = None,
                               voice: Optional[str] = None,
                               model: Optional[str] = None,
                               categories: Optional[List[str]] = None) -> Dict:
        """Haber koleksiyonunu TTS'e çevir"""
        
        print("=" * 60)
        print("GELİŞMİŞ TTS DÖNÜŞTÜRME")
        print("=" * 60)
        
        # Mevcut ses kayıtlarını yükle
        existing_audio = self.load_existing_audio_records()
        print(f"✓ {len(existing_audio)} mevcut ses kaydı bulundu")
        
        # JSON yükle
        print(f"\n📂 {input_file} yükleniyor...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Haberleri al (farklı formatları destekle)
        if 'all_unique_news' in data:
            all_news = list(data['all_unique_news'].values())
        elif 'selected_news_by_category' in data:
            all_news = []
            for news_list in data['selected_news_by_category'].values():
                all_news.extend(news_list)
        elif isinstance(data, dict):
            all_news = list(data.values())
        elif isinstance(data, list):
            all_news = data
        else:
            raise ValueError("Desteklenmeyen JSON formatı!")
        
        print(f"✓ {len(all_news)} haber bulundu")
        
        # Kategori filtresi
        if categories:
            filtered = []
            for news in all_news:
                news_cat = news.get('category') or news.get('scraped_content', {}).get('category')
                if news_cat in categories:
                    filtered.append(news)
            all_news = filtered
            print(f"✓ Kategori filtresi sonrası: {len(all_news)} haber")
        
        # Limit uygula
        if limit:
            all_news = all_news[:limit]
            print(f"✓ Limit uygulandı: {len(all_news)} haber işlenecek")
        
        # İşleme başla
        print(f"\n🎙️ TTS dönüşümü başlıyor...")
        print(f"Ses: {voice or self.default_voice}, Model: {model or self.default_model}")
        print("=" * 60)
        
        processed_news = []
        
        for i, news in enumerate(all_news, 1):
            # İlerleme
            if i % 10 == 0:
                print(f"\n--- İlerleme: {i}/{len(all_news)} ---")
                print(f"--- Maliyet: ${self.stats['total_cost']:.4f} ---\n")
            
            # Başlık
            title = news.get('title', 'Başlıksız')[:60]
            guid = news.get('guid', str(i))
            
            print(f"\n[{i}/{len(all_news)}] {title}...")
            
            # Duplicate kontrolü
            if guid in existing_audio:
                print(f"  ⊘ Ses kaydı zaten mevcut: {existing_audio[guid]['filename']}")
                # Mevcut kaydı kullan
                news['tts_info'] = existing_audio[guid]
                news['has_audio'] = True
                processed_news.append(news)
                continue
            
            # TTS içeriği hazırla
            tts_content = self.prepare_tts_content(news)
            
            if not tts_content:
                print("  ⊘ TTS içeriği boş, atlanıyor")
                self.stats['failed'] += 1
                continue
            
            # Dosya adı oluştur
            filename = self.generate_audio_filename(title, guid)
            
            # TTS dönüşümü
            result = self.convert_to_speech_sync(
                text=tts_content,
                filename=filename,
                voice=voice,
                model=model
            )
            
            if result['success']:
                # Habere TTS bilgilerini ekle
                news['tts_info'] = result
                news['has_audio'] = True
                
                # İstatistikleri güncelle
                self.stats['success'] += 1
                self.stats['total_cost'] += result['estimated_cost']
                self.stats['total_duration'] += result['duration_seconds']
                self.stats['total_characters'] += result['character_count']
                
                # Audio kaydını sakla (duplicate kontrolü için)
                self.save_audio_record(guid, result)
                
                print(f"  💰 Maliyet: ${result['estimated_cost']:.6f}")
            else:
                self.stats['failed'] += 1
                news['tts_error'] = result.get('error')
                print(f"  ❌ Hata: {result.get('error')}")
            
            processed_news.append(news)
            
            # Rate limiting
            time.sleep(0.5)
        
        self.stats['total_processed'] = len(all_news)
        
        # Sonuçları kaydet
        if not output_file:
            base_name = Path(input_file).stem
            output_file = f"{base_name}_with_tts.json"
        
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'input_file': input_file,
                'tts_stats': self.stats,
                'voice_used': voice or self.default_voice,
                'model_used': model or self.default_model
            },
            'news_with_audio': processed_news
        }
        
        print(f"\n💾 Sonuçlar {output_file} dosyasına kaydediliyor...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Final rapor
        self.print_final_report()
        
        return self.stats
    
    def print_final_report(self):
        """Final istatistik raporu"""
        print("\n" + "=" * 60)
        print("TTS DÖNÜŞÜM RAPORU")
        print("=" * 60)
        print(f"Toplam işlenen    : {self.stats['total_processed']}")
        print(f"Başarılı          : {self.stats['success']}")
        print(f"Başarısız         : {self.stats['failed']}")
        print(f"Toplam maliyet    : ${self.stats['total_cost']:.4f}")
        print(f"Toplam süre       : {self.stats['total_duration']:,} saniye")
        print(f"Toplam karakter   : {self.stats['total_characters']:,}")
        
        if self.stats['success'] > 0:
            avg_cost = self.stats['total_cost'] / self.stats['success']
            avg_duration = self.stats['total_duration'] / self.stats['success']
            avg_chars = self.stats['total_characters'] / self.stats['success']
            
            print("\nOrtalamalar:")
            print(f"Haber başına maliyet : ${avg_cost:.6f}")
            print(f"Ortalama süre        : {avg_duration:.1f} saniye")
            print(f"Ortalama karakter    : {avg_chars:.0f}")
        
        print("\nSes dosyaları: ./audio_output/")
        print("=" * 60)


def main():
    """CLI kullanımı için main fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Haber TTS Dönüştürücü')
    parser.add_argument('input_file', help='Girdi JSON dosyası')
    parser.add_argument('--output', '-o', help='Çıktı JSON dosyası')
    parser.add_argument('--limit', '-l', type=int, help='İşlenecek haber sayısı limiti')
    parser.add_argument('--voice', '-v', default='nova', 
                       choices=['alloy', 'echo', 'fable', 'nova', 'onyx', 'shimmer'],
                       help='TTS ses seçimi')
    parser.add_argument('--model', '-m', default='tts-1',
                       choices=['tts-1', 'tts-1-hd'],
                       help='TTS model seçimi')
    parser.add_argument('--categories', '-c', nargs='+',
                       help='Sadece belirli kategorileri işle')
    parser.add_argument('--api-key', help='OpenAI API anahtarı')
    
    args = parser.parse_args()
    
    # TTS Generator başlat
    try:
        generator = EnhancedTTSGenerator(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Hata: {e}")
        print("\nAPI key sağlama yöntemleri:")
        print("1. .env dosyasında: OPENAI_API_KEY=sk-...")
        print("2. Komut satırında: --api-key sk-...")
        print("3. Environment variable: export OPENAI_API_KEY=sk-...")
        return 1
    
    # İşlemi başlat
    stats = generator.process_news_collection(
        input_file=args.input_file,
        output_file=args.output,
        limit=args.limit,
        voice=args.voice,
        model=args.model,
        categories=args.categories
    )
    
    return 0 if stats['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())