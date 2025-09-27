# ================================
# src/api/endpoints/reels_mockup.py - Detailed Mockup Reels API
# ================================

"""
Reels Mockup API - Web scraping'den gelmiş gibi detaylı test verisi
Gerçek API'ye geçmeden önce test için kullanılacak
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
import hashlib

# Router oluştur
router = APIRouter(prefix="/api/reels/mockup", tags=["reels-mockup"])

# ============ DETAILED MODELS ============

class ScrapedNewsItem(BaseModel):
    """Web scraping'den gelmiş gibi detaylı haber modeli"""
    
    # Basic info
    title: str
    summary: str
    full_content: str
    url: HttpUrl
    
    # Metadata
    category: str
    author: Optional[str] = None
    location: Optional[str] = None
    published_date: str
    scraped_date: str
    
    # Media
    main_image: Optional[str] = None
    images: List[str] = []
    videos: List[str] = []
    
    # SEO & Tags
    tags: List[str] = []
    keywords: List[str] = []
    meta_description: Optional[str] = None
    
    # Metrics
    word_count: int
    character_count: int
    estimated_reading_time: int  # minutes
    
    # Technical
    source: str = "aa"
    scraping_quality: str = "high"  # high, medium, low
    content_language: str = "tr"

class MockupReelOutput(BaseModel):
    """Mockup reel output model"""
    id: str
    news_data: ScrapedNewsItem
    
    # TTS info
    tts_content: str  # Başlık + özet kombinasyonu
    voice_used: str
    model_used: str
    
    # Audio simulation
    audio_url: str
    duration_seconds: int
    file_size_mb: float
    
    # Cost & metrics
    character_count: int
    estimated_cost: float
    processing_time_seconds: float
    
    # Status
    status: str = "completed"
    created_at: str

# ============ DETAILED MOCKUP DATA ============

DETAILED_MOCKUP_NEWS = [
    {
        "title": "Engelsiz Gazze projesi kapsamında sanatla dayanışma etkinliği düzenlendi",
        "summary": "Uluslararası Doktorlar Derneği (AID) ve ÖNDER Ankara İmam Hatipliler Derneği tarafından Gazzelilere protez desteği sağlamak amacıyla başlatılan 'Engelsiz Gazze' projesi kapsamında sanat etkinlikleri düzenlendi.",
        "full_content": """Uluslararası Doktorlar Derneği (AID) ve ÖNDER Ankara İmam Hatipliler Derneği tarafından Gazzelilere protez desteği sağlamak amacıyla başlatılan "Engelsiz Gazze" projesi kapsamında sanat etkinlikleri düzenlendi.

Ankara'da düzenlenen etkinlikte, Gazze'deki insanlık dramına dikkat çekmek ve protez ihtiyacı olan kişilere destek sağlamak amacıyla çeşitli sanat gösterileri yapıldı. 

Etkinlikte konuşan AID Genel Başkanı Dr. Mehmet Akif Çelik, Gazze'deki durumun insanlık açısından utanç verici olduğunu belirterek, "Bu proje ile hem farkındalık yaratmak hem de somut yardım sağlamak istiyoruz" dedi.

ÖNDER Ankara İmam Hatipliler Derneği Başkanı Hasan Özdemir ise projenin toplumsal dayanışmanın güzel bir örneği olduğunu vurgulayarak, "Sanat ve dayanışmanın gücü ile Gazze'deki kardeşlerimize umut olmaya çalışıyoruz" şeklinde konuştu.

Proje kapsamında toplanan bağışlar doğrudan protez üretimi ve dağıtımı için kullanılacak. Etkinlikte ayrıca Gazze'deki çocukların çizimleri de sergilendi.""",
        "url": "https://www.aa.com.tr/tr/guncel/engelsiz-gazze-projesi-kapsaminda-sanatla-dayanisma-etkinligi-duzenlendi/3700959",
        "category": "guncel",
        "author": "Mehmet Yalçın",
        "location": "Ankara",
        "published_date": "2024-09-27T14:30:00Z",
        "main_image": "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/thumbs_b_c_1234567890.jpg",
        "images": [
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/gazze_etkinlik_1.jpg",
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/gazze_etkinlik_2.jpg"
        ],
        "tags": ["Gazze", "protez", "dayanışma", "sanat", "AID", "ÖNDER"],
        "keywords": ["engelsiz gazze", "protez desteği", "sanat etkinliği", "uluslararası doktorlar derneği"],
        "meta_description": "Engelsiz Gazze projesi kapsamında Ankara'da sanat etkinliği düzenlendi"
    },
    {
        "title": "Troya'da çıkartılan 4 bin 500 yıllık altın broş antik kentteki önemli buluntular arasına girdi",
        "summary": "Troya Antik Kenti Kazı Başkan Yardımcısı Prof. Dr. Reyhan Körpe, Çanakkale'de 160 yılı aşkın süredir devam eden Troya kazılarında 4 bin 500 yıllık altın halkalı broş ile son derece ender bir yeşim taşının bulunmasına ilişkin açıklama yaptı.",
        "full_content": """Çanakkale'de 160 yılı aşkın süredir devam eden Troya Antik Kenti kazılarında tarihi öneme sahip yeni buluntular gün yüzüne çıkarıldı.

Troya Antik Kenti Kazı Başkan Yardımcısı Prof. Dr. Reyhan Körpe, kazı çalışmaları sırasında bulunan 4 bin 500 yıllık altın halkalı broş ve ender yeşim taşının, antik kentteki en önemli buluntular arasında yer aldığını belirtti.

Prof. Dr. Körpe, "Bu broş, Erken Tunç Çağı'na ait olup, o dönemin işçilik teknikleri ve estetik anlayışı hakkında önemli bilgiler veriyor. Altın halkalı yapısı ve üzerindeki motifler, dönemin sanat anlayışını yansıtıyor" şeklinde konuştu.

Yeşim taşının ise Anadolu'da çok nadir bulunan türden olduğunu kaydeden Körpe, "Bu taş, muhtemelen uzak coğrafyalardan ticaret yolu ile gelmiş. Troya'nın o dönemki ticari önemini ve uluslararası bağlantılarını gösteren çok değerli bir buluntu" dedi.

Kazı çalışmaları kapsamında bu yıl toplamda 2 bin 500'ün üzerinde eser gün yüzüne çıkarıldı. Buluntular Troya Müzesi'nde ziyaretçilere sunulacak.""",
        "url": "https://www.aa.com.tr/tr/guncel/troyada-cikartilan-4-bin-500-yillik-altin-bros-antik-kentteki-onemli-buluntular-arasina-girdi/3700953",
        "category": "kultur",
        "author": "Ayşe Demir",
        "location": "Çanakkale",
        "published_date": "2024-09-27T13:45:00Z",
        "main_image": "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/thumbs_b_c_9876543210.jpg",
        "images": [
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/troya_bros_1.jpg",
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/troya_kazi_1.jpg",
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/troya_yesim_tas.jpg"
        ],
        "tags": ["Troya", "altın broş", "arkeoloji", "antik kent", "kazı", "yeşim taşı"],
        "keywords": ["troya antik kenti", "4 bin 500 yıllık", "altın broş", "arkeolojik buluntu"],
        "meta_description": "Troya'da 4 bin 500 yıllık altın broş ve ender yeşim taşı bulundu"
    },
    {
        "title": "Mavi vatan'a milli uzun menzil hava savunma yeteneği geliyor",
        "summary": "Türk savunma sanayisinin 'mavi vatan'da milli hava savunma kabiliyetini artırma çalışmaları, uzun menzilli SİPER füzesiyle güçleniyor.",
        "full_content": """Türkiye'nin savunma sanayisinde önemli bir gelişme yaşanıyor. Milli uzun menzil hava savunma sistemi SİPER, "mavi vatan" olarak adlandırılan deniz alanlarında Türkiye'nin savunma kabiliyetini önemli ölçüde artıracak.

Savunma Sanayii Başkanlığı yetkilileri, SİPER füze sisteminin test aşamalarının başarıyla tamamlandığını ve yakında operasyonel kullanıma hazır hale geleceğini açıkladı.

SİPER sistemi, 100 kilometreye kadar menzile sahip olup, çok çeşitli hava tehdidine karşı etkili koruma sağlayacak. Sistem, özellikle Doğu Akdeniz ve Ege Denizi'ndeki kritik bölgelerde konuşlandırılması planlanan gemilerde kullanılacak.

Türk Silahlı Kuvvetleri Komutanı, "Bu sistem ile mavi vatanımızdaki hava sahası güvenliğimizi tamamen milli imkanlarla sağlayacağız. Bu, hem stratejik bağımsızlığımız hem de caydırıcılığımız açısından çok önemli" şeklinde konuştu.

SİPER sisteminin seri üretimine 2025 yılında başlanması ve ilk teslimatların 2026 yılında yapılması planlanıyor. Proje kapsamında toplam 12 adet fırkateyn ve destroyer sınıfı gemiye sistem entegre edilecek.""",
        "url": "https://www.aa.com.tr/tr/guncel/mavi-vatana-milli-uzun-menzil-hava-savunma-yetenegi-geliyor/3700952",
        "category": "savunma",
        "author": "Kemal Özkan",
        "location": "Ankara",
        "published_date": "2024-09-27T12:15:00Z",
        "main_image": "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/thumbs_b_c_1122334455.jpg",
        "images": [
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/siper_fuze_1.jpg",
            "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/mavi_vatan_1.jpg"
        ],
        "videos": [
            "https://cdnuploads.aa.com.tr/uploads/Videos/2024/09/27/siper_test_video.mp4"
        ],
        "tags": ["SİPER", "mavi vatan", "hava savunma", "milli savunma", "deniz kuvvetleri"],
        "keywords": ["siper füze sistemi", "uzun menzil hava savunma", "mavi vatan", "türk savunma sanayi"],
        "meta_description": "SİPER füze sistemi ile Türkiye'nin mavi vatandaki hava savunma kabiliyeti artıyor"
    }
]

# ============ HELPER FUNCTIONS ============

def create_scraped_news_item(raw_data: dict) -> ScrapedNewsItem:
    """Raw data'dan ScrapedNewsItem oluştur"""
    
    # Character ve word count hesapla
    full_text = f"{raw_data['title']} {raw_data['summary']} {raw_data['full_content']}"
    word_count = len(full_text.split())
    char_count = len(full_text)
    reading_time = max(1, word_count // 200)  # 200 kelime/dakika
    
    return ScrapedNewsItem(
        title=raw_data["title"],
        summary=raw_data["summary"],
        full_content=raw_data["full_content"],
        url=raw_data["url"],
        category=raw_data["category"],
        author=raw_data["author"],
        location=raw_data["location"],
        published_date=raw_data["published_date"],
        scraped_date=datetime.now().isoformat(),
        main_image=raw_data.get("main_image"),
        images=raw_data.get("images", []),
        videos=raw_data.get("videos", []),
        tags=raw_data["tags"],
        keywords=raw_data["keywords"],
        meta_description=raw_data["meta_description"],
        word_count=word_count,
        character_count=char_count,
        estimated_reading_time=reading_time
    )

def create_mockup_reel_from_news(news_item: ScrapedNewsItem, voice: str = "alloy") -> MockupReelOutput:
    """ScrapedNewsItem'dan MockupReelOutput oluştur"""
    
    # TTS content: Sadece başlık + özet (reel için)
    tts_content = f"{news_item.title}. {news_item.summary}"
    tts_char_count = len(tts_content)
    
    # Simulated metrics
    duration = max(15, len(tts_content.split()) // 150 * 60)  # Minimum 15 saniye
    file_size_mb = duration * 0.5  # Rough estimate
    processing_time = 2.5  # Simulated processing time
    
    # Cost calculation
    estimated_cost = (tts_char_count / 1_000_000) * 0.015
    
    # Generate unique ID
    reel_id = hashlib.md5(f"{news_item.title}{voice}".encode()).hexdigest()[:12]
    
    # Audio URL simulation
    audio_filename = f"reel_{reel_id}_{voice}.mp3"
    
    return MockupReelOutput(
        id=reel_id,
        news_data=news_item,
        tts_content=tts_content,
        voice_used=voice,
        model_used="tts-1",
        audio_url=f"/audio/{audio_filename}",
        duration_seconds=duration,
        file_size_mb=round(file_size_mb, 2),
        character_count=tts_char_count,
        estimated_cost=round(estimated_cost, 6),
        processing_time_seconds=processing_time,
        created_at=datetime.now().isoformat()
    )

# ============ MOCKUP ENDPOINTS ============

@router.get("/scraped-news")
async def get_scraped_news_mockup(
    count: int = Query(3, ge=1, le=10, description="Number of news items"),
    category: Optional[str] = Query(None, description="Category filter")
):
    """
    Web scraping'den gelmiş gibi detaylı haber verisi
    """
    try:
        # Filter by category if provided
        filtered_news = DETAILED_MOCKUP_NEWS
        if category:
            filtered_news = [news for news in DETAILED_MOCKUP_NEWS if news["category"] == category]
        
        if not filtered_news:
            raise HTTPException(status_code=404, detail=f"No news found for category: {category}")
        
        # Limit results
        selected_news = filtered_news[:count]
        
        # Convert to ScrapedNewsItem objects
        scraped_items = [create_scraped_news_item(news) for news in selected_news]
        
        return {
            "success": True,
            "message": f"Retrieved {len(scraped_items)} scraped news items",
            "news_items": scraped_items,
            "total_count": len(scraped_items),
            "scraping_info": {
                "scraping_time": "2024-09-27T15:30:45Z",
                "source": "aa.com.tr",
                "quality": "high",
                "errors": 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraped news error: {str(e)}")

@router.get("/generate-reels")
async def generate_reels_from_scraped_mockup(
    count: int = Query(3, ge=1, le=10, description="Number of reels to generate"),
    voice: str = Query("alloy", description="TTS voice"),
    category: Optional[str] = Query(None, description="Category filter")
):
    """
    Scraped news'dan reel generate et (mockup)
    """
    try:
        # Get scraped news first
        filtered_news = DETAILED_MOCKUP_NEWS
        if category:
            filtered_news = [news for news in DETAILED_MOCKUP_NEWS if news["category"] == category]
        
        selected_news = filtered_news[:count]
        
        # Generate reels
        reels = []
        for news_data in selected_news:
            news_item = create_scraped_news_item(news_data)
            reel = create_mockup_reel_from_news(news_item, voice)
            reels.append(reel)
        
        # Summary stats
        total_chars = sum(reel.character_count for reel in reels)
        total_cost = sum(reel.estimated_cost for reel in reels)
        total_duration = sum(reel.duration_seconds for reel in reels)
        
        return {
            "success": True,
            "message": f"Generated {len(reels)} reels from scraped news",
            "reels": reels,
            "summary": {
                "total_reels": len(reels),
                "total_characters": total_chars,
                "total_estimated_cost": round(total_cost, 6),
                "total_duration_seconds": total_duration,
                "average_duration": round(total_duration / len(reels), 1),
                "voice_used": voice
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reel generation error: {str(e)}")

@router.get("/news-detail/{news_id}")
async def get_news_detail_mockup(news_id: int):
    """
    Specific news item detayı (mockup)
    """
    try:
        if news_id < 0 or news_id >= len(DETAILED_MOCKUP_NEWS):
            raise HTTPException(status_code=404, detail="News not found")
        
        raw_news = DETAILED_MOCKUP_NEWS[news_id]
        news_item = create_scraped_news_item(raw_news)
        
        # TTS preview
        tts_preview = f"{news_item.title}. {news_item.summary}"
        
        return {
            "success": True,
            "news_item": news_item,
            "tts_preview": {
                "content": tts_preview,
                "character_count": len(tts_preview),
                "estimated_duration": len(tts_preview.split()) // 150 * 60,
                "estimated_cost": (len(tts_preview) / 1_000_000) * 0.015
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News detail error: {str(e)}")

@router.get("/categories")
async def get_mockup_categories():
    """
    Mockup data'daki kategoriler
    """
    categories = {}
    for news in DETAILED_MOCKUP_NEWS:
        cat = news["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    return {
        "success": True,
        "categories": categories,
        "available_categories": list(categories.keys()),
        "total_news": len(DETAILED_MOCKUP_NEWS)
    }

@router.get("/stats")
async def get_mockup_stats():
    """
    Mockup data istatistikleri
    """
    try:
        total_chars = 0
        total_words = 0
        categories = {}
        authors = {}
        
        for news in DETAILED_MOCKUP_NEWS:
            # Content analysis
            full_text = f"{news['title']} {news['summary']} {news['full_content']}"
            total_chars += len(full_text)
            total_words += len(full_text.split())
            
            # Category count
            cat = news["category"]
            categories[cat] = categories.get(cat, 0) + 1
            
            # Author count
            author = news["author"]
            authors[author] = authors.get(author, 0) + 1
        
        # TTS estimations
        tts_chars = sum(len(f"{news['title']}. {news['summary']}") for news in DETAILED_MOCKUP_NEWS)
        total_tts_cost = (tts_chars / 1_000_000) * 0.015
        
        return {
            "success": True,
            "mockup_statistics": {
                "total_news_items": len(DETAILED_MOCKUP_NEWS),
                "content_stats": {
                    "total_characters": total_chars,
                    "total_words": total_words,
                    "average_words_per_article": round(total_words / len(DETAILED_MOCKUP_NEWS))
                },
                "tts_stats": {
                    "total_tts_characters": tts_chars,
                    "estimated_total_cost": round(total_tts_cost, 6),
                    "average_cost_per_reel": round(total_tts_cost / len(DETAILED_MOCKUP_NEWS), 6)
                },
                "categories": categories,
                "authors": authors
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")
    
    
    
    
    
"""

Endpoint'ler:

GET /api/reels/mockup/scraped-news - Web scraping verisi
GET /api/reels/mockup/generate-reels - Reel generation
GET /api/reels/mockup/news-detail/{id} - Detaylı haber
GET /api/reels/mockup/categories - Kategoriler
GET /api/reels/mockup/stats - İstatistikler

GET /api/reels/mockup/generate-reels?count=3&voice=nova&category=guncel

"""