# ================================
# src/services/processing.py - Updated Media Processing with Reel Integration
# ================================

"""
Processing Service - TTS, Image, Video işleme
Provider'ları kullanarak media processing
TTS işleminden sonra otomatik reel oluşturma entegrasyonu
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from ..models.tts import TTSRequest, TTSResponse, AudioResult, TTSVoice, TTSModel
from ..models.news import Article
from ..models.reels_tracking import ReelFeedItem
from ..providers import get_provider
from ..config import settings

class ProcessingService:
    """Media processing service with reel integration"""
    
    def __init__(self):
        self.tts_provider_name = f"tts_{settings.tts_provider}"
    
    # ============ CORE TTS METHODS ============
    
    async def text_to_speech(self, request: TTSRequest, create_reel: bool = False, 
                           article: Optional[Article] = None) -> TTSResponse:
        """
        Text'i sese çevir ve isteğe bağlı olarak reel oluştur
        
        Args:
            request: TTS request
            create_reel: TTS'den sonra reel oluşturulsun mu
            article: Reel oluşturmak için article verisi
        """
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
            
            # TTS başarılı ve reel oluşturma isteniyorsa
            if result.success and create_reel and article:
                try:
                    # Reels analytics service'i import et
                    from ..services.reels_analytics import reels_analytics
                    
                    # Reel oluştur
                    reel = await reels_analytics.create_reel_from_article(
                        article=article,
                        audio_url=result.file_url or "/audio/unknown.mp3",
                        duration_seconds=int(result.duration_seconds or 30),
                        file_size_mb=result.file_size_bytes / (1024*1024) if result.file_size_bytes else 1.0,
                        voice_used=request.voice,
                        estimated_cost=result.estimated_cost
                    )
                    
                    print(f"✅ Auto-created reel: {reel.id} from TTS")
                    
                except Exception as e:
                    print(f"⚠️ Reel creation failed after TTS: {e}")
                    # TTS başarılı olduğu için hatayı ignore et, sadece log
            
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
                               model: str = None,
                               create_reel: bool = True) -> TTSResponse:
        """
        Makaleyi sese çevir ve otomatik reel oluştur
        
        Args:
            article: Article objesi
            voice: TTS voice
            model: TTS model
            create_reel: Otomatik reel oluşturulsun mu (default: True)
        """
        try:
            # Article'dan TTS metni oluştur
            tts_text = article.to_tts_content()
            
            # TTS request oluştur
            request = TTSRequest(
                text=tts_text,
                voice=voice or settings.tts_voice,
                model=model or settings.tts_model
            )
            
            # TTS yap ve reel oluştur
            return await self.text_to_speech(
                request=request, 
                create_reel=create_reel, 
                article=article
            )
            
        except Exception as e:
            print(f"❌ Article TTS error: {e}")
            return TTSResponse(
                success=False,
                message=str(e),
                result=AudioResult(success=False, error_message=str(e))
            )
    
    # ============ RSS-SPECIFIC TTS METHODS ============
    
    async def rss_news_to_speech(self, 
                                article: Article,
                                voice: str = None,
                                model: str = None,
                                use_summary_only: bool = True) -> TTSResponse:
        """
        RSS'den gelen haber için özel TTS işlemi
        Sadece başlık + özet kullanır (reels için optimize)
        
        Args:
            article: RSS Article
            voice: TTS voice  
            model: TTS model
            use_summary_only: Sadece başlık+özet kullan (reels için ideal)
        """
        try:
            # RSS haberleri için optimize edilmiş metin
            if use_summary_only:
                # Sadece başlık + özet (reels için perfect)
                tts_text = f"{article.title}"
                if article.summary and len(article.summary.strip()) > 0:
                    tts_text += f". {article.summary}"
                else:
                    # Özet yoksa içerikten ilk 150 karakter al
                    content_preview = article.content[:150].strip()
                    if content_preview:
                        tts_text += f". {content_preview}..."
            else:
                # Full content (uzun video/podcast için)
                tts_text = article.to_tts_content()
            
            # TTS için ideal uzunluk kontrolü (15-45 saniye arası)
            if len(tts_text) < 30:
                # Çok kısa, biraz daha içerik ekle
                if article.content and len(article.content) > 100:
                    additional_content = article.content[:100].strip()
                    tts_text += f" {additional_content}..."
            
            # TTS request oluştur
            request = TTSRequest(
                text=tts_text,
                voice=voice or "nova",  # RSS için default voice 
                model=model or "gpt-4o-mini-tts",  # GPT-4O Mini TTS model
                speed=1.1  # RSS haberleri için biraz hızlı
            )
            
            print(f"🎙️ RSS TTS: {len(tts_text)} chars - {article.title[:50]}...")
            
            # TTS yap ve otomatik reel oluştur
            return await self.text_to_speech(
                request=request,
                create_reel=True,  # RSS haberlerinden her zaman reel oluştur
                article=article
            )
            
        except Exception as e:
            print(f"❌ RSS TTS error: {e}")
            return TTSResponse(
                success=False,
                message=f"RSS TTS failed: {str(e)}",
                result=AudioResult(success=False, error_message=str(e))
            )
    
    async def batch_rss_to_speech(self, 
                                 articles: List[Article],
                                 voice: str = None,
                                 model: str = None,
                                 max_concurrent: int = 3) -> List[TTSResponse]:
        """
        RSS makalelerini toplu sese çevir ve reel oluştur
        Özel olarak RSS haberleri için optimize edilmiş
        
        Args:
            articles: Article listesi
            voice: TTS voice
            model: TTS model  
            max_concurrent: Maksimum eş zamanlı işlem
        """
        results = []
        processed = 0
        successful = 0
        
        print(f"🔄 Starting batch RSS TTS: {len(articles)} articles")
        
        for i, article in enumerate(articles):
            try:
                print(f"🎵 [{i+1}/{len(articles)}] Processing: {article.title[:50]}...")
                
                # RSS optimized TTS
                result = await self.rss_news_to_speech(
                    article=article,
                    voice=voice,
                    model=model,
                    use_summary_only=True  # RSS için optimize
                )
                
                results.append(result)
                processed += 1
                
                if result.success:
                    successful += 1
                    duration = result.result.duration_seconds or 0
                    cost = result.result.estimated_cost or 0
                    print(f"   ✅ Success: {duration:.1f}s, ${cost:.4f}")
                else:
                    print(f"   ❌ Failed: {result.message}")
                
                # Rate limiting için kısa bekleme
                if i < len(articles) - 1:  # Son item değilse
                    import asyncio
                    await asyncio.sleep(0.5)  # 500ms delay
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results.append(TTSResponse(
                    success=False,
                    message=str(e),
                    result=AudioResult(success=False, error_message=str(e))
                ))
                processed += 1
        
        # Summary
        total_cost = sum(r.result.estimated_cost for r in results if r.success)
        success_rate = (successful / processed * 100) if processed > 0 else 0
        
        print(f"📊 Batch RSS TTS completed:")
        print(f"   ✅ Successful: {successful}/{processed} ({success_rate:.1f}%)")
        print(f"   💰 Total cost: ${total_cost:.4f}")
        print(f"   🎬 Reels created: {successful} (auto-generated)")
        
        return results
    
    # ============ ENHANCED BATCH OPERATIONS ============
    
    async def batch_articles_to_speech(self, 
                                      articles: List[Article],
                                      voice: str = None,
                                      model: str = None,
                                      create_reels: bool = True,
                                      rss_optimized: bool = True) -> List[TTSResponse]:
        """
        Gelişmiş toplu makale ses dönüştürme
        
        Args:
            articles: Article listesi
            voice: TTS voice
            model: TTS model
            create_reels: Otomatik reel oluştur
            rss_optimized: RSS için optimize et (başlık+özet)
        """
        
        if rss_optimized:
            # RSS için özel optimize edilmiş method kullan
            return await self.batch_rss_to_speech(articles, voice, model)
        else:
            # Eski full-content method
            return await self._legacy_batch_tts(articles, voice, model, create_reels)
    
    async def _legacy_batch_tts(self, articles: List[Article], voice: str, 
                               model: str, create_reels: bool) -> List[TTSResponse]:
        """Legacy batch TTS (full content için)"""
        results = []
        
        for i, article in enumerate(articles):
            print(f"🔄 Processing article {i+1}/{len(articles)}: {article.title[:50]}...")
            
            result = await self.article_to_speech(
                article=article, 
                voice=voice, 
                model=model,
                create_reel=create_reels
            )
            results.append(result)
            
            # Başarılı olanları logla
            if result.success:
                filename = Path(result.result.file_path).name if result.result.file_path else 'unknown'
                print(f"✅ TTS Success: {filename}")
            else:
                print(f"❌ TTS Failed: {result.message}")
        
        successful = sum(1 for r in results if r.success)
        print(f"📊 Legacy batch TTS completed: {successful}/{len(articles)} successful")
        
        return results
    
    # ============ RSS INTEGRATION UTILITIES ============
    
    async def create_reels_from_latest_news(self, 
                                          category: str = "guncel",
                                          count: int = 10,
                                          voice: str = None,
                                          min_chars: int = 50) -> Dict[str, Any]:
        """
        Son haberlerden otomatik reel oluştur
        RSS → TTS → Reel pipeline'ı
        
        Args:
            category: Haber kategorisi
            count: Kaç haber işlenecek
            voice: TTS voice
            min_chars: Minimum karakter sayısı
        """
        try:
            # Content service'i import et
            from ..services.content import content_service
            
            print(f"📰 Fetching latest news: {category}, count={count}")
            
            # RSS'den son haberleri al
            news_response = await content_service.get_latest_news(
                count=count * 2,  # Filtreleme için fazla al
                category=category,
                enable_scraping=True  # Detaylı içerik için
            )
            
            if not news_response.success:
                return {
                    "success": False,
                    "message": f"Failed to fetch news: {news_response.message}",
                    "reels_created": 0
                }
            
            # Filtreleme
            suitable_articles = []
            for article in news_response.articles:
                content_length = len(article.title + (article.summary or "") + article.content)
                if content_length >= min_chars:
                    suitable_articles.append(article)
                    if len(suitable_articles) >= count:
                        break
            
            if not suitable_articles:
                return {
                    "success": False,
                    "message": "No suitable articles found for TTS conversion",
                    "reels_created": 0
                }
            
            print(f"✅ Found {len(suitable_articles)} suitable articles")
            
            # Batch TTS + Reel creation
            tts_results = await self.batch_rss_to_speech(
                articles=suitable_articles,
                voice=voice or "nova",  # Default nova voice
                model="gpt-4o-mini-tts"  # GPT-4O Mini TTS model
            )
            
            # Summary
            successful_reels = sum(1 for result in tts_results if result.success)
            total_cost = sum(r.result.estimated_cost for r in tts_results if r.success)
            
            return {
                "success": True,
                "message": f"Created {successful_reels} reels from latest news",
                "reels_created": successful_reels,
                "total_articles_processed": len(suitable_articles),
                "success_rate": round((successful_reels / len(suitable_articles)) * 100, 1),
                "total_cost": round(total_cost, 6),
                "category": category,
                "voice_used": voice or TTSVoice.MINI_DEFAULT
            }
            
        except Exception as e:
            print(f"❌ Create reels from news error: {e}")
            return {
                "success": False,
                "message": str(e),
                "reels_created": 0
            }
    
    # ============ EXISTING METHODS (Updated) ============
    
    async def get_tts_stats(self) -> Dict:
        """TTS istatistikleri al"""
        try:
            provider = get_provider(self.tts_provider_name)
            if not provider or "get_cost_stats" not in provider:
                return {"error": "Stats not available"}
            
            base_stats = await provider["get_cost_stats"]()
            
            # Reel creation stats ekle
            try:
                from ..services.reels_analytics import reels_analytics
                all_reels = await reels_analytics.get_all_published_reels()
                
                base_stats.update({
                    "reels_created": len(all_reels),
                    "avg_cost_per_reel": round(base_stats.get("total_cost", 0) / len(all_reels), 6) if all_reels else 0,
                    "total_reel_duration": sum(reel.duration_seconds for reel in all_reels)
                })
            except Exception as e:
                print(f"⚠️ Could not get reel stats: {e}")
            
            return base_stats
            
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