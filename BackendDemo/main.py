"""
AA News TTS CLI Interface
Command line interface for the news-to-speech system
"""

import argparse
import logging
import sys
from pathlib import Path
import json
from datetime import datetime
import time

from utils.config import config_manager, get_app_config
from services.news_service import NewsService
from services.tts_service import TTSService
from api.main import main as start_api


def setup_logging(level: str = "INFO"):
    """Logging setup"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/app.log', encoding='utf-8')
        ]
    )


def validate_system():
    """Sistem gereksinimlerini kontrol et"""
    print("Sistem kontrolleri...")
    
    # Config validation
    validation = config_manager.validate_config()
    
    issues = []
    for key, value in validation.items():
        if not value and not key.endswith('_error'):
            issues.append(f"- {key}")
    
    if issues:
        print("Sistem sorunları:")
        for issue in issues:
            print(issue)
        return False
    
    print("Sistem kontrolleri tamamlandı")
    return True


def cmd_update_agenda(args):
    """Gündem haberlerini güncelle ve TTS oluştur"""
    print("=" * 60)
    print("📰 GÜNDEM HABERLERİ GÜNCELLENİYOR")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Servisler
        news_service = NewsService(
            default_category="guncel",
            enable_scraping=True,
            max_workers=args.workers
        )
        tts_service = TTSService()
        
        print(f"🔄 Güncel kategorisinden {args.count} haber çekiliyor...")
        
        # RSS'den haberleri çek
        articles = news_service.get_latest_news(
            count=args.count,
            category="guncel",
            enable_scraping=True
        )
        
        if not articles:
            print("❌ Haber bulunamadı")
            return
        
        print(f"✅ {len(articles)} haber RSS'den çekildi")
        
        # Scraping kontrolü
        scraped_count = sum(1 for a in articles if a.scraping_successful)
        print(f"📄 Web scraping: {scraped_count}/{len(articles)} başarılı")
        
        # Filtreleme
        print(f"🔍 Haberler filtreleniyor...")
        filtered_articles = news_service.filter_articles(
            articles,
            min_chars=args.min_chars,
            max_chars=args.max_chars,
            require_scraping=True
        )
        
        if not filtered_articles:
            print("❌ Filtre sonrası uygun haber bulunamadı")
            print(f"   Min karakter: {args.min_chars}")
            print(f"   Max karakter: {args.max_chars}")
            return
        
        print(f"✅ {len(filtered_articles)} haber filtrelendi")
        
        # Maliyet hesaplama
        total_chars = sum(a.get_character_count() for a in filtered_articles)
        estimated_cost = (total_chars / 1_000_000) * 0.015  # tts-1 pricing
        
        print(f"\n💰 MALİYET TAHMİNİ:")
        print(f"   Toplam karakter: {total_chars:,}")
        print(f"   Tahmini maliyet: ${estimated_cost:.6f}")
        
        if not args.force:
            confirm = input(f"\n❓ {len(filtered_articles)} haber için TTS oluşturulsun mu? (e/h): ")
            if confirm.lower() != 'e':
                print("❌ İşlem iptal edildi")
                return
        
        # TTS dönüştürme
        print(f"\n🎵 TTS DÖNÜŞTÜRME BAŞLADI")
        print("-" * 40)
        
        successful_tts = 0
        failed_tts = 0
        total_cost = 0
        agenda_data = []
        
        for i, article in enumerate(filtered_articles, 1):
            title_short = article.get_title()[:50]
            print(f"\n[{i}/{len(filtered_articles)}] {title_short}...")
            
            # TTS için içerik hazırla
            tts_content = f"Başlık: {article.get_title()}"
            
            # Summary/description ekle
            summary = ""
            if article.scraped_data and article.scraped_data.meta_description:
                summary = article.scraped_data.meta_description
            elif article.rss_data.summary:
                summary = article.rss_data.summary
            elif article.rss_data.description:
                summary = article.rss_data.description
            
            if summary and len(summary.strip()) > 20:
                tts_content += f"\n\nÖzet: {summary}"
            
            print(f"   📝 TTS karakter: {len(tts_content)}")
            
            # TTS dönüştürme
            response = tts_service.convert_article_to_speech(
                article=article,
                voice=args.voice,
                model=args.model
            )
            
            if response.success:
                successful_tts += 1
                total_cost += response.estimated_cost
                
                filename = Path(response.audio_file_path).name
                print(f"   ✅ TTS başarılı: {filename}")
                print(f"   💰 Maliyet: ${response.estimated_cost:.6f}")
                
                # Agenda data oluştur
                agenda_item = {
                    "id": f"agenda_{i}_{int(time.time())}",
                    "title": article.get_title(),
                    "summary": summary,
                    "content": tts_content,
                    "category": "guncel",
                    "published": article.rss_data.published,
                    "url": article.rss_data.link,
                    "author": article.scraped_data.author if article.scraped_data else "",
                    "location": article.scraped_data.location if article.scraped_data else "Türkiye",
                    "character_count": len(tts_content),
                    "images": article.scraped_data.image_urls if article.scraped_data else [
                        f"https://picsum.photos/400/600?random={i + 100}",
                        f"https://picsum.photos/400/600?random={i + 200}"
                    ],
                    "main_image": (article.scraped_data.main_image_url if article.scraped_data and article.scraped_data.main_image_url else f"https://picsum.photos/400/600?random={i + 100}"),
                    "audio_url": f"/audio/{filename}",
                    "audio_filename": filename,
                    "subtitles": _generate_subtitle_timing(_split_into_sentences(tts_content)),
                    "estimated_duration": len(_split_into_sentences(tts_content)) * 2.5,
                    "tags": article.scraped_data.tags if article.scraped_data else ["güncel", "haber"],
                    "created_at": datetime.now().isoformat(),
                    "processing_time": response.processing_time_seconds
                }
                
                agenda_data.append(agenda_item)
                
            else:
                failed_tts += 1
                print(f"   ❌ TTS hatası: {response.error_message}")
        
        # Sonuçları kaydet
        if agenda_data and args.save_json:
            output_file = f"agenda_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'category': 'guncel',
                    'total_items': len(agenda_data),
                    'total_cost': total_cost,
                    'processing_time': time.time() - start_time,
                    'agenda_items': agenda_data
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Gündem verileri kaydedildi: {output_file}")
        
        # Özet
        elapsed_time = time.time() - start_time
        
        print(f"\n" + "=" * 60)
        print(f"📊 GÜNDEM GÜNCELLEMESİ TAMAMLANDI")
        print(f"=" * 60)
        print(f"⏱️  Toplam süre: {elapsed_time:.1f} saniye")
        print(f"📰 Toplam haber: {len(filtered_articles)}")
        print(f"✅ TTS başarılı: {successful_tts}")
        print(f"❌ TTS başarısız: {failed_tts}")
        print(f"💰 Toplam maliyet: ${total_cost:.6f}")
        print(f"📊 Başarı oranı: {(successful_tts/len(filtered_articles)*100):.1f}%")
        
        if successful_tts > 0:
            print(f"\n🎯 {successful_tts} gündem haberi mobile uygulamalara hazır!")
        
    except Exception as e:
        print(f"❌ Gündem güncelleme hatası: {e}")
        import traceback
        traceback.print_exc()


def _split_into_sentences(text: str):
    """Metni cümlelere böl"""
    import re
    sentences = re.split(r'[.!?]+', text)
    clean_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:
            clean_sentences.append(sentence)
    return clean_sentences


def _generate_subtitle_timing(sentences):
    """Cümleler için tahmini timing oluştur"""
    subtitles = []
    current_time = 0
    
    for sentence in sentences:
        word_count = len(sentence.split())
        duration = max(2, word_count * 0.4)
        
        subtitles.append({
            "start": round(current_time, 1),
            "end": round(current_time + duration, 1),
            "text": sentence.strip()
        })
        
        current_time += duration + 0.3
    
    return subtitles


def cmd_news(args):
    """Haber çekme komutu"""
    try:
        news_service = NewsService(
            default_category=args.category,
            enable_scraping=args.scraping
        )
        
        print(f"'{args.category}' kategorisinden {args.count} haber çekiliyor...")
        
        articles = news_service.get_latest_news(
            count=args.count,
            category=args.category,
            enable_scraping=args.scraping
        )
        
        if not articles:
            print("Haber bulunamadı")
            return
        
        # Filtreleme
        if args.min_chars or args.max_chars:
            filtered = news_service.filter_articles(
                articles, 
                min_chars=args.min_chars or 100,
                max_chars=args.max_chars or 10000
            )
            articles = filtered
        
        # Sonuçları göster
        print(f"\n{len(articles)} haber bulundu:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.get_title()}")
            print(f"   URL: {article.rss_data.link}")
            print(f"   Karakter: {article.get_character_count()}")
            print(f"   Scraping: {'✓' if article.scraping_successful else '✗'}")
        
        # JSON çıktısı
        if args.output:
            output_data = {
                'timestamp': articles[0].processed_at.isoformat(),
                'category': args.category,
                'count': len(articles),
                'articles': [article.to_dict() for article in articles]
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"\nSonuçlar kaydedildi: {args.output}")
        
        # Özet
        summary = news_service.get_articles_summary(articles)
        print(f"\nÖzet:")
        print(f"Toplam karakter: {summary['total_characters']:,}")
        print(f"Scraping başarı: {summary['scraping_success_rate']}")
        
    except Exception as e:
        print(f"Haber çekme hatası: {e}")


def cmd_tts(args):
    """TTS dönüştürme komutu"""
    try:
        tts_service = TTSService()
        
        if args.text:
            # Direkt metin
            from models.news_models import TTSRequest
            
            request = TTSRequest(
                text=args.text,
                voice=args.voice,
                model=args.model,
                speed=args.speed
            )
            
            print(f"TTS dönüştürme başlatılıyor...")
            print(f"Metin: {args.text[:100]}...")
            print(f"Karakter: {len(args.text)}")
            print(f"Tahmini maliyet: ${request.estimate_cost():.6f}")
            
            if not args.force:
                confirm = input("Devam edilsin mi? (e/h): ")
                if confirm.lower() != 'e':
                    print("İptal edildi")
                    return
            
            response = tts_service.text_to_speech(request)
            
            if response.success:
                print(f"Başarılı! Dosya: {response.audio_file_path}")
                print(f"Boyut: {response.file_size_bytes} bytes")
                print(f"Süre: {response.processing_time_seconds:.2f}s")
                print(f"Maliyet: ${response.estimated_cost:.6f}")
            else:
                print(f"Hata: {response.error_message}")
        
        elif args.url:
            # URL'den makale
            from services.news_service import NewsService
            
            news_service = NewsService()
            article = news_service.get_single_article(args.url, with_scraping=True)
            
            if not article:
                print("Makale çekilemedi")
                return
            
            print(f"Makale: {article.get_title()}")
            print(f"Karakter: {article.get_character_count()}")
            
            if not args.force:
                confirm = input("TTS'e dönüştürülsün mü? (e/h): ")
                if confirm.lower() != 'e':
                    print("İptal edildi")
                    return
            
            response = tts_service.convert_article_to_speech(
                article=article,
                voice=args.voice,
                model=args.model
            )
            
            if response.success:
                print(f"Başarılı! Dosya: {response.audio_file_path}")
                print(f"Maliyet: ${response.estimated_cost:.6f}")
            else:
                print(f"Hata: {response.error_message}")
        
        else:
            print("--text veya --url parametresi gerekli")
    
    except Exception as e:
        print(f"TTS hatası: {e}")


def cmd_batch(args):
    """Toplu işlem komutu"""
    try:
        news_service = NewsService(enable_scraping=True)
        tts_service = TTSService()
        
        print(f"Toplu işlem başlatılıyor...")
        print(f"Kategori: {args.category}")
        print(f"Haber sayısı: {args.count}")
        print(f"TTS Model: {args.model}")
        print(f"Ses: {args.voice}")
        
        # Haberleri al
        articles = news_service.get_latest_news(
            count=args.count,
            category=args.category,
            enable_scraping=True
        )
        
        if not articles:
            print("Haber bulunamadı")
            return
        
        # Filtrele
        filtered = news_service.filter_articles(
            articles,
            min_chars=args.min_chars,
            max_chars=args.max_chars,
            require_scraping=True
        )
        
        if not filtered:
            print("Filtre sonrası haber kalmadı")
            return
        
        print(f"{len(filtered)} makale TTS'e dönüştürülecek")
        
        # Maliyet tahmini
        total_chars = sum(a.get_character_count() for a in filtered)
        estimated_cost = (total_chars / 1_000_000) * 0.015  # tts-1 pricing
        
        print(f"Toplam karakter: {total_chars:,}")
        print(f"Tahmini maliyet: ${estimated_cost:.6f}")
        
        if not args.force:
            confirm = input("Devam edilsin mi? (e/h): ")
            if confirm.lower() != 'e':
                print("İptal edildi")
                return
        
        # TTS dönüştürme
        successful = 0
        total_cost = 0
        
        for i, article in enumerate(filtered, 1):
            print(f"\n[{i}/{len(filtered)}] {article.get_title()[:50]}...")
            
            response = tts_service.convert_article_to_speech(
                article=article,
                voice=args.voice,
                model=args.model
            )
            
            if response.success:
                successful += 1
                total_cost += response.estimated_cost
                print(f"  ✓ Başarılı: {Path(response.audio_file_path).name}")
            else:
                print(f"  ✗ Hata: {response.error_message}")
        
        print(f"\nToplu işlem tamamlandı:")
        print(f"Başarılı: {successful}/{len(filtered)}")
        print(f"Toplam maliyet: ${total_cost:.6f}")
        
    except Exception as e:
        print(f"Toplu işlem hatası: {e}")


def cmd_stats(args):
    """İstatistik komutu"""
    try:
        tts_service = TTSService()
        stats = tts_service.get_cost_statistics()
        
        print("TTS İstatistikleri:")
        print("=" * 40)
        print(f"Toplam istek: {stats['total_requests']}")
        print(f"Başarılı: {stats['successful_requests']}")
        print(f"Başarı oranı: {stats['success_rate']}")
        print(f"Toplam maliyet: ${stats['total_cost']:.6f}")
        print(f"Toplam karakter: {stats['total_characters']:,}")
        print(f"Ortalama maliyet/istek: ${stats['average_cost_per_request']:.6f}")
        print(f"En çok kullanılan ses: {stats['most_used_voice']}")
        print(f"En çok kullanılan model: {stats['most_used_model']}")
        
        # Ses dosyaları
        audio_files = tts_service.list_audio_files()
        print(f"\nSes dosyaları: {len(audio_files)}")
        
        if audio_files and args.verbose:
            print("\nSon 10 dosya:")
            for file_info in audio_files[:10]:
                print(f"  {file_info['filename']} ({file_info['size_mb']} MB)")
        
    except Exception as e:
        print(f"İstatistik hatası: {e}")


def cmd_config(args):
    """Konfigürasyon komutu"""
    if args.create_env:
        result = config_manager.create_sample_env()
        print(result)
        return
    
    # Konfigürasyon doğrulama
    validation = config_manager.validate_config()
    
    print("Konfigürasyon Durumu:")
    print("=" * 40)
    
    for key, value in validation.items():
        if not key.endswith('_error'):
            status = "✓" if value else "✗"
            print(f"{status} {key}")
        elif key.endswith('_error'):
            print(f"  Hata: {value}")
    
    if args.verbose:
        try:
            app_config = get_app_config()
            print(f"\nUygulama Ayarları:")
            print(f"  Output dir: {app_config.output_dir}")
            print(f"  Scraping: {app_config.enable_scraping}")
            print(f"  API port: {app_config.api_port}")
            print(f"  Workers: {app_config.scraping_max_workers}")
        except Exception as e:
            print(f"Config error: {e}")


def main():
    """Ana CLI fonksiyonu"""
    parser = argparse.ArgumentParser(
        description="AA News TTS - Anadolu Ajansı haberlerini sese dönüştürür"
    )
    
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log seviyesi'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Komutlar')
    
    # Update Agenda command - YENİ!
    agenda_parser = subparsers.add_parser('update-agenda', help='Gündem haberlerini güncelle ve TTS oluştur')
    agenda_parser.add_argument('--count', type=int, default=15, help='Çekilecek haber sayısı')
    agenda_parser.add_argument('--voice', default='alloy', choices=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], help='TTS ses')
    agenda_parser.add_argument('--model', default='tts-1', choices=['tts-1', 'tts-1-hd'], help='TTS model')
    agenda_parser.add_argument('--min-chars', type=int, default=300, help='Minimum karakter sayısı')
    agenda_parser.add_argument('--max-chars', type=int, default=2000, help='Maksimum karakter sayısı')
    agenda_parser.add_argument('--workers', type=int, default=3, help='Paralel worker sayısı')
    agenda_parser.add_argument('--force', action='store_true', help='Onay almadan çalıştır')
    agenda_parser.add_argument('--save-json', action='store_true', help='JSON dosyasına kaydet')
    
    # News command
    news_parser = subparsers.add_parser('news', help='Haber çekme')
    news_parser.add_argument('--category', default='guncel', help='Kategori')
    news_parser.add_argument('--count', type=int, default=10, help='Haber sayısı')
    news_parser.add_argument('--scraping', action='store_true', help='Web scraping aktif')
    news_parser.add_argument('--min-chars', type=int, help='Minimum karakter')
    news_parser.add_argument('--max-chars', type=int, help='Maksimum karakter')
    news_parser.add_argument('--output', help='JSON çıktı dosyası')
    
    # TTS command
    tts_parser = subparsers.add_parser('tts', help='TTS dönüştürme')
    tts_parser.add_argument('--text', help='Dönüştürülecek metin')
    tts_parser.add_argument('--url', help='Makale URL\'si')
    tts_parser.add_argument('--voice', default='alloy', help='Ses')
    tts_parser.add_argument('--model', default='tts-1', help='Model')
    tts_parser.add_argument('--speed', type=float, default=1.0, help='Hız')
    tts_parser.add_argument('--force', action='store_true', help='Onay almadan çalıştır')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Toplu işlem')
    batch_parser.add_argument('--category', default='guncel', help='Kategori')
    batch_parser.add_argument('--count', type=int, default=5, help='Haber sayısı')
    batch_parser.add_argument('--voice', default='alloy', help='Ses')
    batch_parser.add_argument('--model', default='tts-1', help='Model')
    batch_parser.add_argument('--min-chars', type=int, default=200, help='Min karakter')
    batch_parser.add_argument('--max-chars', type=int, default=8000, help='Max karakter')
    batch_parser.add_argument('--force', action='store_true', help='Onay almadan çalıştır')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='İstatistikler')
    stats_parser.add_argument('--verbose', action='store_true', help='Detaylı bilgi')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Konfigürasyon')
    config_parser.add_argument('--create-env', action='store_true', help='.env dosyası oluştur')
    config_parser.add_argument('--verbose', action='store_true', help='Detaylı bilgi')
    
    # API command
    api_parser = subparsers.add_parser('api', help='API serverını başlat')
    
    args = parser.parse_args()
    
    # Logging setup
    setup_logging(args.log_level)
    
    # Komut yok ise help göster
    if not args.command:
        parser.print_help()
        return
    
    # Sistem kontrolü (config hariç)
    if args.command != 'config':
        if not validate_system():
            print("\nSistem kontrollerinde sorun var!")
            print("Çözüm için: python main.py config --create-env")
            return
    
    # Komutları çalıştır
    try:
        if args.command == 'update-agenda':
            cmd_update_agenda(args)
        elif args.command == 'news':
            cmd_news(args)
        elif args.command == 'tts':
            cmd_tts(args)
        elif args.command == 'batch':
            cmd_batch(args)
        elif args.command == 'stats':
            cmd_stats(args)
        elif args.command == 'config':
            cmd_config(args)
        elif args.command == 'api':
            print("API server başlatılıyor...")
            start_api()
        else:
            print(f"Bilinmeyen komut: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nİşlem iptal edildi")
    except Exception as e:
        print(f"Hata: {e}")
        if args.log_level == 'DEBUG':
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()