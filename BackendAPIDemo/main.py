# ================================
# main.py - Universal Application Entry Point
# ================================

"""
AA Universal API - Main Entry Point
- CLI Commands
- API Server  
- System Management
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
import json

# Local imports
from src.config import settings
from src.api import create_app
from src.api.content import router as content_router
from src.api.processing import router as processing_router

def setup_logging():
    """Basic logging setup"""
    import logging
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)

def validate_system():
    """System requirements check"""
    print("🔍 System validation...")
    
    issues = []
    
    # Check OpenAI API key
    if not settings.openai_api_key:
        issues.append("❌ OpenAI API key not set (OPENAI_API_KEY)")
    else:
        print("✅ OpenAI API key configured")
    
    # Check storage directory
    storage_path = Path(settings.storage_base_path)
    try:
        storage_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Storage directory: {storage_path}")
    except Exception as e:
        issues.append(f"❌ Storage directory issue: {e}")
    
    # Check providers
    from src.providers import PROVIDERS
    print(f"✅ Providers loaded: {list(PROVIDERS.keys())}")
    
    if issues:
        print("\n⚠️  System issues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before running the system.")
        return False
    
    print("✅ System validation passed")
    return True

# ================================
# CLI COMMANDS
# ================================

async def cmd_news(args):
    """News command - fetch and display news"""
    print("📰 Fetching news...")
    
    try:
        from src.services.content import content_service
        
        result = await content_service.get_latest_news(
            count=args.count,
            category=args.category,
            enable_scraping=args.scraping
        )
        
        if result.success:
            print(f"✅ Found {len(result.articles)} articles")
            
            for i, article in enumerate(result.articles, 1):
                print(f"\n{i}. {article.title}")
                print(f"   📍 {article.location or 'Unknown'} | 👤 {article.author or 'Unknown'}")
                print(f"   🔗 {article.url}")
                print(f"   📊 {len(article.content)} characters")
                if args.verbose and article.summary:
                    print(f"   📝 {article.summary[:100]}...")
        else:
            print(f"❌ Failed to fetch news: {result.message}")
            
    except Exception as e:
        print(f"❌ News command error: {e}")

async def cmd_tts(args):
    """TTS command - convert text to speech"""
    print("🎵 Converting text to speech...")
    
    try:
        from src.services.processing import processing_service
        from src.models.tts import TTSRequest
        
        if args.text:
            # Direct text conversion
            text = args.text
        elif args.url:
            # Convert article from URL
            from src.services.content import content_service
            article = await content_service.get_article_by_url(args.url, enable_scraping=True)
            if not article:
                print("❌ Could not fetch article from URL")
                return
            text = article.to_tts_content()
            print(f"📰 Article: {article.title}")
        else:
            print("❌ Please provide either --text or --url")
            return
        
        print(f"📝 Text length: {len(text)} characters")
        print(f"🎙️  Voice: {args.voice}")
        print(f"🤖 Model: {args.model}")
        
        # Estimate cost
        estimated_cost = (len(text) / 1_000_000) * 0.015
        print(f"💰 Estimated cost: ${estimated_cost:.6f}")
        
        if not args.force:
            confirm = input("Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ Cancelled")
                return
        
        # Convert to speech
        request = TTSRequest(
            text=text,
            voice=args.voice,
            model=args.model,
            speed=args.speed
        )
        
        result = await processing_service.text_to_speech(request)
        
        if result.success:
            print(f"✅ TTS successful!")
            print(f"📁 File: {result.result.file_path}")
            print(f"🌐 URL: {result.result.file_url}")
            print(f"📊 Size: {result.result.file_size_bytes} bytes")
            print(f"💰 Cost: ${result.result.estimated_cost:.6f}")
        else:
            print(f"❌ TTS failed: {result.message}")
            
    except Exception as e:
        print(f"❌ TTS command error: {e}")

async def cmd_batch(args):
    """Batch command - process multiple items"""
    print("⚡ Starting batch processing...")
    
    try:
        from src.services.content import content_service
        from src.services.processing import processing_service
        
        # Get news articles
        print(f"📰 Fetching {args.count} articles from '{args.category}'...")
        news_result = await content_service.get_latest_news(
            count=args.count,
            category=args.category,
            enable_scraping=True
        )
        
        if not news_result.success:
            print(f"❌ Failed to fetch news: {news_result.message}")
            return
        
        articles = news_result.articles
        print(f"✅ Got {len(articles)} articles")
        
        # Filter articles
        filtered_articles = [a for a in articles 
                           if args.min_chars <= len(a.content) <= args.max_chars]
        
        print(f"🔍 Filtered to {len(filtered_articles)} articles ({args.min_chars}-{args.max_chars} chars)")
        
        if not filtered_articles:
            print("❌ No articles match the criteria")
            return
        
        # Calculate total cost
        total_chars = sum(len(a.to_tts_content()) for a in filtered_articles)
        total_cost = (total_chars / 1_000_000) * 0.015
        
        print(f"📊 Total characters: {total_chars:,}")
        print(f"💰 Estimated total cost: ${total_cost:.6f}")
        
        if not args.force:
            confirm = input(f"Process {len(filtered_articles)} articles? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ Cancelled")
                return
        
        # Process articles
        successful = 0
        failed = 0
        actual_cost = 0.0
        
        for i, article in enumerate(filtered_articles, 1):
            print(f"\n🔄 [{i}/{len(filtered_articles)}] {article.title[:50]}...")
            
            result = await processing_service.article_to_speech(
                article=article,
                voice=args.voice,
                model=args.model
            )
            
            if result.success:
                successful += 1
                actual_cost += result.result.estimated_cost
                filename = Path(result.result.file_path).name if result.result.file_path else "unknown"
                print(f"   ✅ Success: {filename}")
            else:
                failed += 1
                print(f"   ❌ Failed: {result.message}")
        
        # Summary
        print(f"\n📊 Batch processing completed:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💰 Total cost: ${actual_cost:.6f}")
        print(f"   📈 Success rate: {(successful/len(filtered_articles)*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Batch command error: {e}")

async def cmd_stats(args):
    """Stats command - show system statistics"""
    print("📊 System Statistics")
    print("=" * 50)
    
    try:
        from src.services.processing import processing_service
        
        # TTS stats
        tts_stats = await processing_service.get_tts_stats()
        print("🎵 TTS Statistics:")
        for key, value in tts_stats.items():
            print(f"   {key}: {value}")
        
        # Audio files
        audio_files = await processing_service.list_audio_files()
        print(f"\n📁 Audio Files: {len(audio_files)}")
        
        if args.verbose and audio_files:
            print("   Recent files:")
            for file_info in audio_files[:5]:
                print(f"   - {file_info['filename']} ({file_info['size_mb']} MB)")
        
        # Storage info
        storage_path = Path(settings.storage_base_path)
        if storage_path.exists():
            total_size = sum(f.stat().st_size for f in storage_path.glob("*") if f.is_file())
            print(f"\n💾 Storage: {total_size / (1024*1024):.1f} MB in {storage_path}")
        
        # Provider status
        from src.providers import PROVIDERS
        print(f"\n🔌 Providers: {len(PROVIDERS)}")
        for provider_type, providers in PROVIDERS.items():
            print(f"   {provider_type}: {list(providers.keys())}")
        
    except Exception as e:
        print(f"❌ Stats error: {e}")

async def cmd_test(args):
    """Test command - system health check"""
    print("🧪 Running system tests...")
    
    try:
        # Test news provider
        print("\n📰 Testing news provider...")
        from src.services.content import content_service
        news_result = await content_service.get_latest_news(count=2, enable_scraping=False)
        
        if news_result.success:
            print(f"   ✅ News: Got {len(news_result.articles)} articles")
        else:
            print(f"   ❌ News: {news_result.message}")
        
        # Test TTS provider (if not disabled)
        if not args.skip_tts:
            print("\n🎵 Testing TTS provider...")
            from src.services.processing import processing_service
            from src.models.tts import TTSRequest
            
            test_request = TTSRequest(text="Test message for TTS system")
            tts_result = await processing_service.text_to_speech(test_request)
            
            if tts_result.success:
                print(f"   ✅ TTS: File created successfully")
                # Clean up test file
                test_file = Path(tts_result.result.file_path)
                if test_file.exists():
                    test_file.unlink()
                    print(f"   🗑️  Test file cleaned up")
            else:
                print(f"   ❌ TTS: {tts_result.message}")
        
        print("\n✅ System tests completed")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def cmd_api(args):
    """API command - start web server"""
    print("🌐 Starting API server...")
    
    # Create FastAPI app
    app = create_app()
    
    # Add routers
    app.include_router(content_router)
    app.include_router(processing_router)
    
    # Add any new routers here:
    # app.include_router(game_router)
    # app.include_router(chat_router)
    
    print(f"🚀 Server starting on {settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🏥 Health Check: http://{settings.host}:{settings.port}/health")
    
    # Start server
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info" if not settings.debug else "debug",
        reload=settings.debug
    )

# ================================
# CLI SETUP
# ================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AA Universal API - News, TTS and more",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py news --count 5 --category spor
  python main.py tts --text "Hello world" --voice alloy
  python main.py tts --url "https://aa.com.tr/..." --force
  python main.py batch --category guncel --count 10 --voice nova
  python main.py api
  python main.py test
        """
    )
    
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # News command
    news_parser = subparsers.add_parser('news', help='Fetch and display news')
    news_parser.add_argument('--count', type=int, default=10, help='Number of articles')
    news_parser.add_argument('--category', default='guncel', help='News category')
    news_parser.add_argument('--scraping', action='store_true', help='Enable web scraping')
    news_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # TTS command
    tts_parser = subparsers.add_parser('tts', help='Convert text to speech')
    tts_parser.add_argument('--text', help='Text to convert')
    tts_parser.add_argument('--url', help='Article URL to convert')
    tts_parser.add_argument('--voice', default='alloy', help='Voice to use')
    tts_parser.add_argument('--model', default='tts-1', help='TTS model')
    tts_parser.add_argument('--speed', type=float, default=1.0, help='Speech speed')
    tts_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process articles to speech')
    batch_parser.add_argument('--count', type=int, default=5, help='Number of articles')
    batch_parser.add_argument('--category', default='guncel', help='News category')
    batch_parser.add_argument('--voice', default='alloy', help='TTS voice')
    batch_parser.add_argument('--model', default='tts-1', help='TTS model')
    batch_parser.add_argument('--min-chars', type=int, default=200, help='Minimum characters')
    batch_parser.add_argument('--max-chars', type=int, default=8000, help='Maximum characters')
    batch_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    stats_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run system tests')
    test_parser.add_argument('--skip-tts', action='store_true', help='Skip TTS tests')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start API server')
    
    # Parse args
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        settings.debug = True
    
    # Setup logging
    setup_logging()
    
    # Validate system (except for some commands)
    if args.command not in ['test']:
        if not validate_system():
            sys.exit(1)
    
    # Execute command
    if args.command == 'news':
        asyncio.run(cmd_news(args))
    elif args.command == 'tts':
        asyncio.run(cmd_tts(args))
    elif args.command == 'batch':
        asyncio.run(cmd_batch(args))
    elif args.command == 'stats':
        asyncio.run(cmd_stats(args))
    elif args.command == 'test':
        asyncio.run(cmd_test(args))
    elif args.command == 'api':
        cmd_api(args)
    else:
        parser.print_help()

# ================================
# QUICK START FUNCTIONS
# ================================

def quick_start():
    """Quick start for development"""
    print("🚀 Quick Start Mode")
    
    # Validate system
    if not validate_system():
        print("❌ System validation failed")
        return
    
    print("\nChoose an option:")
    print("1. Start API server")
    print("2. Test news fetching")
    print("3. Test TTS conversion")
    print("4. Show system stats")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        print("Starting API server...")
        import uvicorn
        app = create_app()
        app.include_router(content_router)
        app.include_router(processing_router)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    elif choice == '2':
        async def test_news():
            from src.services.content import content_service
            result = await content_service.get_latest_news(count=3)
            print(f"News test: {len(result.articles)} articles")
            for article in result.articles:
                print(f"- {article.title}")
        asyncio.run(test_news())
    
    elif choice == '3':
        async def test_tts():
            from src.services.processing import processing_service
            from src.models.tts import TTSRequest
            request = TTSRequest(text="Hello, this is a test message")
            result = await processing_service.text_to_speech(request)
            print(f"TTS test: {'Success' if result.success else 'Failed'}")
        asyncio.run(test_tts())
    
    elif choice == '4':
        async def show_stats():
            from src.services.processing import processing_service
            stats = await processing_service.get_tts_stats()
            print("System stats:", stats)
        asyncio.run(show_stats())
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    # Check if running without arguments for quick start
    if len(sys.argv) == 1:
        try:
            quick_start()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        main()

# ================================
# YENİ KOMUT EKLEYİN
# ================================

"""
Yeni CLI komutu eklemek için:

1. async def cmd_yeni_komut(args) fonksiyonu yaz
2. main() fonksiyonunda subparser ekle:
   yeni_parser = subparsers.add_parser('yeni-komut', help='Açıklama')
   yeni_parser.add_argument('--param', help='Parameter')
3. Execute kısmında elif ekle:
   elif args.command == 'yeni-komut':
       asyncio.run(cmd_yeni_komut(args))

Örnek:
async def cmd_game(args):
    print("🎮 Starting game server...")
    # Game logic here

# Parser'da:
game_parser = subparsers.add_parser('game', help='Start game server')
game_parser.add_argument('--players', type=int, default=10)

# Execute'da:
elif args.command == 'game':
    asyncio.run(cmd_game(args))
"""