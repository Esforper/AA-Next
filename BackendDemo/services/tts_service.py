"""
TTS Service
OpenAI Text-to-Speech API ile ses dönüştürme servisi
"""

import openai
import os
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import json

from models.news_models import TTSRequest, TTSResponse, CompleteNewsArticle
from utils.config import get_openai_config, get_app_config


class TTSService:
    """OpenAI TTS servisi"""
    
    def __init__(self):
        self.openai_config = get_openai_config()
        self.app_config = get_app_config()
        
        # OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_config.api_key)
        
        # Cost tracking
        self.cost_log_file = Path(self.app_config.logs_dir) / "tts_costs.json"
        self._init_cost_tracking()
        
        self.logger = logging.getLogger(__name__)
    
    def _init_cost_tracking(self):
        """Maliyet takip dosyasını başlat"""
        if not self.cost_log_file.exists():
            self._save_cost_log([])
    
    def _save_cost_log(self, entries: List[Dict]):
        """Maliyet kayıtlarını dosyaya yaz"""
        try:
            with open(self.cost_log_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Cost log yazma hatası: {e}")
    
    def _load_cost_log(self) -> List[Dict]:
        """Maliyet kayıtlarını dosyadan oku"""
        try:
            with open(self.cost_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _calculate_cost(self, char_count: int, model: str = None) -> float:
        """Maliyeti hesapla"""
        model = model or self.openai_config.model
        cost_per_1m = self.openai_config.pricing.get(model, 0.015)
        return (char_count / 1_000_000) * cost_per_1m
    
    def _log_usage(self, request: TTSRequest, response: TTSResponse) -> None:
        """Kullanımı kaydet"""
        try:
            entries = self._load_cost_log()
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'model': request.model,
                'voice': request.voice,
                'character_count': request.get_character_count(),
                'estimated_cost': response.estimated_cost,
                'file_path': response.audio_file_path,
                'file_size_bytes': response.file_size_bytes,
                'processing_time': response.processing_time_seconds,
                'success': response.success
            }
            
            entries.append(entry)
            self._save_cost_log(entries)
            
        except Exception as e:
            self.logger.error(f"Usage log hatası: {e}")
    
    def _generate_filename(self, text: str, voice: str, model: str) -> str:
        """Benzersiz dosya adı oluştur"""
        # Hash ile benzersiz ID
        content_hash = hashlib.md5(f"{text}{voice}{model}".encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Güvenli başlık (ilk 30 karakter)
        safe_title = "".join(c for c in text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        
        return f"tts_{timestamp}_{safe_title}_{content_hash}.{self.openai_config.response_format}"
    
    def _split_text(self, text: str, max_chars: int = 4000) -> List[str]:
        """Metni OpenAI limitine göre böl"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + ". " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= max_chars:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """Metni sese dönüştür"""
        start_time = time.time()
        
        try:
            # Metin uzunluğu kontrolü
            if len(request.text.strip()) < 10:
                return TTSResponse(
                    success=False,
                    error_message="Metin çok kısa (minimum 10 karakter)"
                )
            
            # Metni böl
            text_chunks = self._split_text(request.text)
            self.logger.info(f"Metin {len(text_chunks)} parçaya bölündü")
            
            # Dosya adı oluştur
            filename = self._generate_filename(request.text, request.voice, request.model)
            
            if len(text_chunks) == 1:
                # Tek dosya
                file_path = self._convert_single_chunk(request, text_chunks[0], filename)
                
                if file_path:
                    file_size = Path(file_path).stat().st_size
                    
                    response = TTSResponse(
                        success=True,
                        audio_file_path=file_path,
                        file_size_bytes=file_size,
                        character_count=request.get_character_count(),
                        estimated_cost=self._calculate_cost(request.get_character_count(), request.model),
                        processing_time_seconds=time.time() - start_time
                    )
                    
                    self._log_usage(request, response)
                    return response
                
            else:
                # Çoklu dosya
                file_paths = []
                total_size = 0
                
                base_name = filename.rsplit('.', 1)[0]
                extension = filename.rsplit('.', 1)[1]
                
                for i, chunk in enumerate(text_chunks):
                    chunk_filename = f"{base_name}_part{i+1:02d}.{extension}"
                    
                    chunk_request = TTSRequest(
                        text=chunk,
                        voice=request.voice,
                        model=request.model,
                        speed=request.speed,
                        response_format=request.response_format
                    )
                    
                    file_path = self._convert_single_chunk(chunk_request, chunk, chunk_filename)
                    
                    if file_path:
                        file_paths.append(file_path)
                        total_size += Path(file_path).stat().st_size
                    else:
                        # Başarısız chunk
                        return TTSResponse(
                            success=False,
                            error_message=f"Chunk {i+1} dönüştürülemedi"
                        )
                
                response = TTSResponse(
                    success=True,
                    audio_file_path=file_paths[0] if file_paths else None,  # İlk dosya
                    file_size_bytes=total_size,
                    character_count=request.get_character_count(),
                    estimated_cost=self._calculate_cost(request.get_character_count(), request.model),
                    processing_time_seconds=time.time() - start_time
                )
                
                self._log_usage(request, response)
                return response
        
        except Exception as e:
            self.logger.error(f"TTS dönüştürme hatası: {e}")
            return TTSResponse(
                success=False,
                error_message=str(e),
                processing_time_seconds=time.time() - start_time
            )
    
    def _convert_single_chunk(self, request: TTSRequest, text: str, filename: str) -> Optional[str]:
        """Tek chunk'ı dönüştür"""
        try:
            self.logger.debug(f"TTS API çağrısı: {len(text)} karakter")
            
            response = self.client.audio.speech.create(
                model=request.model,
                voice=request.voice,
                input=text,
                response_format=request.response_format,
                speed=request.speed
            )
            
            # Dosyayı kaydet
            file_path = Path(self.app_config.output_dir) / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Ses dosyası kaydedildi: {filename}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"API çağrısı hatası: {e}")
            return None
    
    def convert_article_to_speech(self, article: CompleteNewsArticle, 
                                 voice: str = None, 
                                 model: str = None) -> TTSResponse:
        """Haber makalesini sese dönüştür"""
        
        tts_text = article.get_content_for_tts()
        
        if not tts_text or len(tts_text.strip()) < 10:
            return TTSResponse(
                success=False,
                error_message="Makale metni yetersiz"
            )
        
        request = TTSRequest(
            text=tts_text,
            voice=voice or self.openai_config.voice,
            model=model or self.openai_config.model,
            speed=self.openai_config.speed,
            response_format=self.openai_config.response_format
        )
        
        return self.text_to_speech(request)
    
    def get_cost_statistics(self) -> Dict[str, Any]:
        """Maliyet istatistiklerini al"""
        entries = self._load_cost_log()
        
        if not entries:
            return {
                'total_requests': 0,
                'total_cost': 0.0,
                'total_characters': 0,
                'successful_requests': 0,
                'average_cost_per_request': 0.0,
                'most_used_voice': None,
                'most_used_model': None
            }
        
        successful_entries = [e for e in entries if e.get('success', False)]
        
        total_cost = sum(e.get('estimated_cost', 0) for e in successful_entries)
        total_chars = sum(e.get('character_count', 0) for e in successful_entries)
        
        # En çok kullanılan ses/model
        voices = [e.get('voice') for e in successful_entries]
        models = [e.get('model') for e in successful_entries]
        
        most_used_voice = max(set(voices), key=voices.count) if voices else None
        most_used_model = max(set(models), key=models.count) if models else None
        
        return {
            'total_requests': len(entries),
            'successful_requests': len(successful_entries),
            'total_cost': round(total_cost, 6),
            'total_characters': total_chars,
            'average_cost_per_request': round(total_cost / len(successful_entries), 6) if successful_entries else 0,
            'most_used_voice': most_used_voice,
            'most_used_model': most_used_model,
            'success_rate': f"{len(successful_entries)/len(entries)*100:.1f}%" if entries else "0%"
        }
    
    def list_audio_files(self) -> List[Dict[str, Any]]:
        """Oluşturulan ses dosyalarını listele"""
        audio_files = []
        output_dir = Path(self.app_config.output_dir)
        
        if not output_dir.exists():
            return []
        
        for file_path in output_dir.glob(f"*.{self.openai_config.response_format}"):
            stat = file_path.stat()
            
            audio_files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Tarihe göre sırala (en yeni önce)
        return sorted(audio_files, key=lambda x: x['created_at'], reverse=True)


# Test fonksiyonu
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        tts_service = TTSService()
        
        print("=== TTS SERVICE TEST ===")
        
        # Test metni
        test_text = "Merhaba! Bu bir test metnidir. OpenAI TTS API'sini test ediyoruz."
        
        # TTS request oluştur
        request = TTSRequest(
            text=test_text,
            voice="alloy",
            model="tts-1"
        )
        
        print(f"Test metni: {test_text}")
        print(f"Karakter sayısı: {request.get_character_count()}")
        print(f"Tahmini maliyet: ${request.estimate_cost():.6f}")
        
        # Onay iste
        confirm = input("\nSese dönüştürülsün mü? (e/h): ")
        
        if confirm.lower() == 'e':
            print("TTS dönüştürme başlatılıyor...")
            response = tts_service.text_to_speech(request)
            
            if response.success:
                print(f"Başarılı! Dosya: {response.audio_file_path}")
                print(f"Boyut: {response.file_size_bytes} bytes")
                print(f"Süre: {response.processing_time_seconds:.2f}s")
                print(f"Maliyet: ${response.estimated_cost:.6f}")
            else:
                print(f"Hata: {response.error_message}")
        
        # İstatistikler
        stats = tts_service.get_cost_statistics()
        print(f"\n=== İSTATİSTİKLER ===")
        print(f"Toplam istek: {stats['total_requests']}")
        print(f"Başarılı: {stats['successful_requests']}")
        print(f"Toplam maliyet: ${stats['total_cost']}")
        print(f"Başarı oranı: {stats['success_rate']}")
        
    except Exception as e:
        print(f"Test hatası: {e}")
        print("API key kontrolü yapın!")