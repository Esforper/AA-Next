# ================================
# main.py - Universal Application Entry Point (Updated)
# ================================

"""
AA Universal API - Main Entry Point
- CLI Commands (Updated with RSS-Reels)
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
    """Batch command - process multiple items (Updated)"""
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
        
        # Use updated batch processing (with RSS optimization)
        print("🔄 Using enhanced RSS-optimized batch processing...")
        results = await processing_service.batch_articles_to_speech(
            articles=filtered_articles,
            voice=args.voice,
            model=args.model,
            create_reels=True,  # Auto-create reels
            rss_optimized=True  # Use RSS optimization
        )
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        actual_cost = sum(r.result.estimated_cost for r in results if r.success)
        
        print(f"\n📊 Batch processing completed:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💰 Total cost: ${actual_cost:.6f}")
        print(f"   📈 Success rate: {(successful/len(filtered_articles)*100):.1f}%")
        print(f"   🎬 Reels created: {successful} (auto-generated)")
        
    except Exception as e:
        print(f"❌ Batch command error: {e}")

async def cmd_rss_reels(args):
    """RSS-Reels command - Create reels from latest RSS news (NEW)"""
    print("🎬 Creating reels from latest RSS news...")
    
    try:
        from src.services.processing import processing_service
        
        # RSS-specific parameters
        voice = args.voice or "mini_default"
        category = args.category or "guncel"
        count = args.count or 10
        
        print(f"📰 Category: {category}")
        print(f"🎙️  Voice: {voice}")
        print(f"📊 Count: {count}")
        print(f"🎯 Mode: {'Test Feed' if args.test_feed else 'Production'}")
        
        if args.test_feed:
            print("🧪 Test feed mode - creating sample reels for testing...")
        
        # Execute RSS → TTS → Reel pipeline
        result = await processing_service.create_reels_from_latest_news(
            category=category,
            count=count,
            voice=voice,
            min_chars=args.min_chars or 50
        )
        
        if result["success"]:
            print(f"\n✅ RSS-Reels pipeline completed!")
            print(f"   🎬 Reels created: {result['reels_created']}")
            print(f"   📰 Articles processed: {result['total_articles_processed']}")
            print(f"   📈 Success rate: {result['success_rate']}%")
            print(f"   💰 Total cost: ${result['total_cost']:.6f}")
            print(f"   🎙️  Voice used: {result['voice_used']}")
            
            if args.test_feed:
                print(f"\n🎯 Test feed ready! Access via:")
                print(f"   📱 API: GET /api/reels/feed")
                print(f"   🌐 Web: http://localhost:8000/api/reels/feed")
                
                # Show sample reels info
                try:
                    from src.services.reels_analytics import reels_analytics
                    latest_reels = await reels_analytics.get_all_published_reels()
                    recent_reels = sorted(latest_reels, key=lambda r: r.published_at, reverse=True)[:3]
                    
                    print(f"\n📋 Sample reels created:")
                    for i, reel in enumerate(recent_reels, 1):
                        print(f"   {i}. {reel.news_data.title[:50]}...")
                        print(f"      🎵 {reel.duration_seconds}s | 📁 {reel.audio_url}")
                except Exception as e:
                    print(f"   ⚠️ Could not fetch reel details: {e}")
                    
        else:
            print(f"❌ RSS-Reels pipeline failed: {result['message']}")
            print(f"   🎬 Reels created: {result.get('reels_created', 0)}")
            
    except Exception as e:
        print(f"❌ RSS-Reels command error: {e}")

async def cmd_worker(args):
    """Worker command - RSS worker management (NEW)"""
    
    try:
        from src.services.rss_worker import rss_worker
        
        if args.action == 'start':
            print("🤖 Starting RSS Worker...")
            
            # Check if worker is already running
            status = rss_worker.get_worker_status()
            if status["is_running"]:
                print("❌ Worker is already running")
                print(f"   Started: {status['start_time']}")
                print(f"   Uptime: {status['uptime_minutes']:.1f} minutes")
                return
            
            print(f"⚙️  Settings:")
            print(f"   Interval: {rss_worker.worker_settings['interval_minutes']} minutes")
            print(f"   Categories: {', '.join(rss_worker.worker_settings['categories'])}")
            print(f"   Voice: {rss_worker.worker_settings['voice']}")
            print(f"   Max articles per run: {rss_worker.worker_settings['max_articles_per_run']}")
            
            if not args.force:
                confirm = input("\nStart worker? (y/n): ")
                if confirm.lower() != 'y':
                    print("❌ Cancelled")
                    return
            
            # Start worker (blocking call)
            print("🚀 Worker starting... Press Ctrl+C to stop")
            await rss_worker.start_worker()
        
        elif args.action == 'stop':
            print("🛑 Stopping RSS Worker...")
            
            status = rss_worker.get_worker_status()
            if not status["is_running"]:
                print("❌ Worker is not running")
                return
            
            await rss_worker.stop_worker()
            print("✅ Worker stopped")
        
        elif args.action == 'status':
            print("📊 RSS Worker Status")
            print("=" * 50)
            
            status = rss_worker.get_worker_status()
            
            # Basic status
            print(f"🔄 Running: {'Yes' if status['is_running'] else 'No'}")
            
            if status['start_time']:
                print(f"⏰ Started: {status['start_time']}")
                print(f"⏱️  Uptime: {status['uptime_minutes']:.1f} minutes")
            
            if status['last_check_time']:
                print(f"🔍 Last check: {status['last_check_time']}")
            
            # Statistics
            print(f"\n📈 Statistics:")
            print(f"   Total runs: {status['total_runs']}")
            print(f"   Successful: {status['successful_runs']}")
            print(f"   Failed: {status['failed_runs']}")
            print(f"   Success rate: {status['success_rate']:.1f}%")
            print(f"   Consecutive failures: {status['consecutive_failures']}")
            
            print(f"\n🎬 Production:")
            print(f"   Articles processed: {status['total_articles_processed']}")
            print(f"   Reels created: {status['total_reels_created']}")
            print(f"   Total cost: ${status['total_cost']:.6f}")
            
            print(f"\n📂 Categories: {', '.join(status['categories_tracked'])}")
            
            if status['next_check_in_minutes']:
                print(f"⏳ Next check: {status['next_check_in_minutes']} minutes")
            
            if status['last_error']:
                print(f"❌ Last error: {status['last_error']}")
        
        elif args.action == 'restart':
            print("🔄 Restarting RSS Worker...")
            
            # Stop if running
            status = rss_worker.get_worker_status()
            if status["is_running"]:
                print("🛑 Stopping current worker...")
                await rss_worker.stop_worker()
                
                # Wait a moment
                await asyncio.sleep(2)
            
            # Start
            print("🚀 Starting worker...")
            await rss_worker.start_worker()
        
        elif args.action == 'test':
            print("🧪 Testing RSS Worker (single iteration)...")
            
            status = rss_worker.get_worker_status()
            if status["is_running"]:
                print("❌ Cannot test while worker is running. Stop worker first.")
                return
            
            # Run single iteration
            try:
                await rss_worker._worker_iteration()
                print("✅ Test iteration completed successfully")
            except Exception as e:
                print(f"❌ Test iteration failed: {e}")
        
        else:
            print(f"❌ Unknown worker action: {args.action}")
            
    except ImportError as e:
        print(f"❌ Worker service not available: {e}")
    except Exception as e:
        print(f"❌ Worker command error: {e}")

async def cmd_test_feed(args):
    """Test Feed command - Show current feed status"""
    print("🧪 Testing current feed status...")
    
    try:
        from src.services.reels_analytics import reels_analytics
        
        # Get all published reels
        all_reels = await reels_analytics.get_all_published_reels()
        print(f"📊 Total published reels: {len(all_reels)}")
        
        if not all_reels:
            print("❌ No reels found. Run 'rss-reels --test-feed' first to create test data.")
            return
        
        # Recent reels (last 24 hours)
        from datetime import timedelta
        now = datetime.now()
        recent_reels = [r for r in all_reels if (now - r.published_at).total_seconds() < 86400]
        print(f"🕐 Recent reels (24h): {len(recent_reels)}")
        
        # Category breakdown
        categories = {}
        for reel in all_reels:
            cat = reel.news_data.category
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"📂 Categories: {dict(categories)}")
        
        # Sample feed generation
        print(f"\n🎯 Generating sample feed...")
        feed_response = await reels_analytics.generate_user_feed("test_user", limit=5)
        
        if feed_response.success:
            print(f"✅ Feed generated successfully!")
            print(f"   📱 Reels in feed: {len(feed_response.reels)}")
            print(f"   🔥 Trending: {feed_response.feed_metadata.trending_count}")
            print(f"   🆕 Fresh: {feed_response.feed_metadata.fresh_count}")
            print(f"   👤 Personalized: {feed_response.feed_metadata.personalized_count}")
            
            print(f"\n📋 Sample feed items:")
            for i, reel in enumerate(feed_response.reels[:3], 1):
                flags = []
                if reel.is_trending: flags.append("🔥 Trending")
                if reel.is_fresh: flags.append("🆕 Fresh")
                if reel.is_watched: flags.append("👁️ Watched")
                
                print(f"   {i}. {reel.news_data.title[:60]}...")
                print(f"      📂 {reel.news_data.category} | 🎵 {reel.duration_seconds}s | {' | '.join(flags)}")
        
        print(f"\n🌐 API Endpoints to test:")
        print(f"   📱 Main feed: GET /api/reels/feed?limit=20")
        print(f"   🔥 Trending: GET /api/reels/trending")
        print(f"   📊 Analytics: GET /api/reels/analytics/overview")
        
    except Exception as e:
        print(f"❌ Test feed error: {e}")

async def cmd_stats(args):
    """Stats command - show system statistics (Updated)"""
    print("📊 System Statistics")
    print("=" * 50)
    
    try:
        from src.services.processing import processing_service
        
        # TTS stats (enhanced)
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
        
        # Reels stats (NEW)
        try:
            from src.services.reels_analytics import reels_analytics
            all_reels = await reels_analytics.get_all_published_reels()
            
            print(f"\n🎬 Reels Statistics:")
            print(f"   Total published reels: {len(all_reels)}")
            
            if all_reels:
                total_duration = sum(reel.duration_seconds for reel in all_reels)
                total_views = sum(reel.total_views for reel in all_reels)
                avg_duration = total_duration / len(all_reels)
                
                print(f"   Total duration: {total_duration} seconds ({total_duration/60:.1f} minutes)")
                print(f"   Average duration: {avg_duration:.1f} seconds")
                print(f"   Total views: {total_views}")
                print(f"   Average views per reel: {total_views/len(all_reels):.1f}")
                
                # Category breakdown
                categories = {}
                for reel in all_reels:
                    cat = reel.news_data.category
                    categories[cat] = categories.get(cat, 0) + 1
                print(f"   Categories: {dict(categories)}")
                
        except Exception as e:
            print(f"   ⚠️ Could not get reel stats: {e}")
        
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
        
        # Test RSS-Reels pipeline (NEW)
        if args.test_pipeline:
            print("\n🎬 Testing RSS-Reels pipeline...")
            from src.services.processing import processing_service
            
            pipeline_result = await processing_service.create_reels_from_latest_news(
                category="guncel",
                count=1,  # Only 1 for testing
                voice="mini_default"
            )
            
            if pipeline_result["success"]:
                print(f"   ✅ Pipeline: Created {pipeline_result['reels_created']} reel(s)")
            else:
                print(f"   ❌ Pipeline: {pipeline_result['message']}")
        
        print("\n✅ System tests completed")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

def cmd_api(args):
    """API command - start web server"""
    print("🌐 Starting API server...")
    
    # Create FastAPI app
    app = create_app()
    
    print(f"🚀 Server starting on {settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🏥 Health Check: http://{settings.host}:{settings.port}/health")
    print(f"📰 News API: http://{settings.host}:{settings.port}/api/news/latest")
    print(f"🎵 TTS API: http://{settings.host}:{settings.port}/api/tts/voices")
    print(f"🎬 Reels Feed: http://{settings.host}:{settings.port}/api/reels/feed")
    print(f"🔥 Trending: http://{settings.host}:{settings.port}/api/reels/trending")
    print(f"⚙️  System API: http://{settings.host}:{settings.port}/api/system/health")
    
    # Start server
    import uvicorn
    uvicorn.run(
        "src.api:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=settings.debug,
        access_log=True
    )

# ================================
# CLI SETUP
# ================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AA Universal API - News, TTS, Reels and more",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # News
  python main.py news --count 5 --category spor
  
  # TTS
  python main.py tts --text "Hello world" --voice alloy
  python main.py tts --url "https://aa.com.tr/..." --force
  
  # Batch (Updated)
  python main.py batch --category guncel --count 10 --voice nova
  
  # RSS-Reels (NEW)
  python main.py rss-reels --count 10 --category guncel --voice mini_default
  python main.py rss-reels --test-feed  # Create test feed
  
  # Testing
  python main.py test-feed  # Check current feed
  python main.py test --test-pipeline  # Test full pipeline
  
  # Server
  python main.py api
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
    
    # Batch command (Updated)
    batch_parser = subparsers.add_parser('batch', help='Batch process articles to speech with reels')
    batch_parser.add_argument('--count', type=int, default=5, help='Number of articles')
    batch_parser.add_argument('--category', default='guncel', help='News category')
    batch_parser.add_argument('--voice', default='alloy', help='TTS voice')
    batch_parser.add_argument('--model', default='tts-1', help='TTS model')
    batch_parser.add_argument('--min-chars', type=int, default=200, help='Minimum characters')
    batch_parser.add_argument('--max-chars', type=int, default=8000, help='Maximum characters')
    batch_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # RSS-Reels command (NEW)
    rss_reels_parser = subparsers.add_parser('rss-reels', help='Create reels from latest RSS news')
    rss_reels_parser.add_argument('--count', type=int, default=10, help='Number of articles to process')
    rss_reels_parser.add_argument('--category', default='guncel', help='News category')
    rss_reels_parser.add_argument('--voice', default='nova', help='TTS voice (fixed default)')
    rss_reels_parser.add_argument('--min-chars', type=int, default=50, help='Minimum characters')
    rss_reels_parser.add_argument('--test-feed', action='store_true', help='Create test feed for development')
    
    # Worker command (NEW)
    worker_parser = subparsers.add_parser('worker', help='RSS Worker management')
    worker_parser.add_argument('action', choices=['start', 'stop', 'status', 'restart', 'test'], 
                              help='Worker action')
    worker_parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    
    # Test Feed command (NEW)
    test_feed_parser = subparsers.add_parser('test-feed', help='Show current feed status and generate sample')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    stats_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # Test command (Updated)
    test_parser = subparsers.add_parser('test', help='Run system tests')
    test_parser.add_argument('--skip-tts', action='store_true', help='Skip TTS tests')
    test_parser.add_argument('--test-pipeline', action='store_true', help='Test RSS-Reels pipeline')
    
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
    elif args.command == 'rss-reels':
        asyncio.run(cmd_rss_reels(args))
    elif args.command == 'worker':
        asyncio.run(cmd_worker(args))
    elif args.command == 'test-feed':
        asyncio.run(cmd_test_feed(args))
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
    print("2. Create test reels feed")
    print("3. Test RSS-Reels pipeline")
    print("4. Show system stats")
    print("5. Test current feed")
    print("6. Start RSS Worker")
    print("7. Check worker status")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    if choice == '1':
        print("Starting API server...")
        import uvicorn
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    elif choice == '2':
        async def create_test_feed():
            from src.services.processing import processing_service
            result = await processing_service.create_reels_from_latest_news(
                category="guncel", count=5, voice="mini_default"
            )
            print(f"Test feed result: {result}")
        asyncio.run(create_test_feed())
    
    elif choice == '3':
        async def test_pipeline():
            from src.services.processing import processing_service
            result = await processing_service.create_reels_from_latest_news(
                category="guncel", count=3, voice="mini_default"
            )
            print(f"Pipeline test: {result}")
        asyncio.run(test_pipeline())
    
    elif choice == '4':
        async def show_stats():
            from src.services.processing import processing_service
            stats = await processing_service.get_tts_stats()
            print("System stats:", stats)
        asyncio.run(show_stats())
    
    elif choice == '5':
        async def test_current_feed():
            from src.services.reels_analytics import reels_analytics
            feed = await reels_analytics.generate_user_feed("test_user", 5)
            print(f"Current feed: {len(feed.reels)} reels available")
        asyncio.run(test_current_feed())
    
    elif choice == '6':
        async def start_worker():
            from src.services.rss_worker import rss_worker
            print("Starting RSS Worker...")
            await rss_worker.start_worker()
        asyncio.run(start_worker())
    
    elif choice == '7':
        async def check_worker():
            from src.services.rss_worker import rss_worker
            status = rss_worker.get_worker_status()
            print(f"Worker running: {status['is_running']}")
            print(f"Total reels created: {status['total_reels_created']}")
        asyncio.run(check_worker())
    
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
# YENİ KOMUT ÖRNEKLERİ
# ================================

"""
RSS-Reels Pipeline Examples:

# Create 10 reels from latest news
python main.py rss-reels --count 10 --category guncel

# Create test feed for development
python main.py rss-reels --test-feed

# Create sports reels with specific voice
python main.py rss-reels --count 5 --category spor --voice nova

# Create reels with minimum character filter
python main.py rss-reels --count 15 --min-chars 100 --voice mini_default

# Test current feed status
python main.py test-feed

# Enhanced batch processing (creates reels automatically)
python main.py batch --count 8 --category ekonomi --voice alloy

# Test full pipeline
python main.py test --test-pipeline

# Show enhanced stats (includes reels)
python main.py stats --verbose

Quick Development Workflow:

1. Create test data:
   python main.py rss-reels --test-feed

2. Start API server:
   python main.py api

3. Check feed in browser:
   http://localhost:8000/api/reels/feed

4. Test specific endpoints:
   http://localhost:8000/api/reels/trending
   http://localhost:8000/api/reels/analytics/overview

Production Workflow:

1. Daily reel generation:
   python main.py rss-reels --count 20 --category guncel

2. Category-specific reels:
   python main.py rss-reels --count 10 --category spor
   python main.py rss-reels --count 10 --category ekonomi

3. Monitor system:
   python main.py stats
   python main.py test-feed
"""