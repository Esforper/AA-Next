# ================================
# src/services/processing.py - Media Processing
# ================================

"""
Processing Service - TTS, Image, Video işleme
Provider'ları kullanarak media processing
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..models.tts import TTSRequest, TTSResponse, AudioResult
from ..models.news import Article
from ..providers import get_provider
from ..config import settings

class ProcessingService:
    """Media processing service"""
    
    def __init__(self):
        self.tts_provider_name = f"tts_{settings.tts_provider}"
    
    async def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """Text'i sese çevir"""
        try:
            # Provider'ı al
            provider = get_provider(self.tts_provider_name)
            if not provider:
                return TTSResponse(
                    success=False,
                    message=f"TTS provider '{self.tts_provider_name}' not found",
                    result=AudioResult(
                        success=False,
                        error_message="Provider not found"
                    )
                )
            
            # Business rules: text validation
            if len(request.text.strip()) < 10:
                return TTSResponse(
                    success=False,
                    message="Text too short (minimum 10 characters)",
                    result=AudioResult(
                        success=False,
                        error_message="Text too short"
                    )
                )
            
            if len(request.text) > 50000:
                return TTSResponse(
                    success=False,
                    message="Text too long (maximum 50000 characters)", 
                    result=AudioResult(
                        success=False,
                        error_message="Text too long"
                    )
                )
            
            # Provider'dan TTS yap
            result = await provider["convert_to_speech"](
                text=request.text,
                voice=request.voice,
                model=request.model,
                speed=request.speed
            )
            
            return TTSResponse(
                success=result.success,
                message="TTS conversion completed" if result.success else "TTS conversion failed",
                result=result
            )
            
        except Exception as e:
            print(f"❌ TTS service error: {e}")
            return TTSResponse(
                success=False,
                message=str(e),
                result=AudioResult(
                    success=False,
                    error_message=str(e)
                )
            )
    
    async def article_to_speech(self, 
                               article: Article, 
                               voice: str = None, 
                               model: str = None) -> TTSResponse:
        """Makaleyi sese çevir"""
        try:
            # Article'dan TTS metni oluştur
            tts_text = article.to_tts_content()
            
            # TTS request oluştur
            request = TTSRequest(
                text=tts_text,
                voice=voice or settings.tts_voice,
                model=model or settings.tts_model
            )
            
            return await self.text_to_speech(request)
            
        except Exception as e:
            print(f"❌ Article TTS error: {e}")
            return TTSResponse(
                success=False,
                message=str(e),
                result=AudioResult(success=False, error_message=str(e))
            )
    
    async def batch_articles_to_speech(self, 
                                      articles: List[Article],
                                      voice: str = None,
                                      model: str = None) -> List[TTSResponse]:
        """Toplu makale ses dönüştürme"""
        results = []
        
        for i, article in enumerate(articles):
            print(f"🔄 Processing article {i+1}/{len(articles)}: {article.title[:50]}...")
            
            result = await self.article_to_speech(article, voice, model)
            results.append(result)
            
            # Başarılı olanları logla
            if result.success:
                print(f"✅ TTS Success: {Path(result.result.file_path).name if result.result.file_path else 'unknown'}")
            else:
                print(f"❌ TTS Failed: {result.message}")
        
        successful = sum(1 for r in results if r.success)
        print(f"📊 Batch TTS completed: {successful}/{len(articles)} successful")
        
        return results
    
    async def get_tts_stats(self) -> Dict[str, Any]:
        """TTS istatistikleri al"""
        try:
            provider = get_provider(self.tts_provider_name)
            if not provider or "get_cost_stats" not in provider:
                return {"error": "Stats not available"}
            
            return await provider["get_cost_stats"]()
            
        except Exception as e:
            print(f"❌ TTS stats error: {e}")
            return {"error": str(e)}
    
    async def list_audio_files(self) -> List[Dict[str, Any]]:
        """Ses dosyalarını listele"""
        try:
            audio_dir = Path(settings.storage_base_path)
            if not audio_dir.exists():
                return []
            
            files = []
            for file_path in audio_dir.glob("*.mp3"):
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "download_url": f"/audio/{file_path.name}"
                })
            
            # Tarihe göre sırala (en yeni önce)
            files.sort(key=lambda x: x["created_at"], reverse=True)
            return files
            
        except Exception as e:
            print(f"❌ List audio files error: {e}")
            return []

# Global instance
processing_service = ProcessingService()