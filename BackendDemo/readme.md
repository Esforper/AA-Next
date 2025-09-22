news_api/
├── models/
│   ├── __init__.py
│   ├── news_models.py
│   └── api_models.py
├── services/
│   ├── __init__.py
│   ├── rss_reader.py
│   ├── web_scraper.py
│   ├── tts_service.py
│   └── news_service.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── endpoints.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── helpers.py
├── requirements.txt
└── main.py


## Teknoloji Stack

RSS Parsing: feedparser
Web Scraping: requests + BeautifulSoup4
API Framework: FastAPI (modern, hızlı, otomatik docs)
TTS: OpenAI API
Config: python-dotenv
Data Validation: Pydantic


## news_models.py

Ne içeriyor:

RSSNewsItem: RSS'den gelen temel veri
ScrapedNewsContent: Web scraping ile elde edilen detaylı içerik
CompleteNewsArticle: İkisini birleştiren ana model
TTSRequest ve TTSResponse: TTS işlemleri için modeller

Özellikler:

Otomatik HTML temizleme
Karakter sayısı hesaplama
TTS için optimize edilmiş metin oluşturma
Veri doğrulama methodları
API response için dictionary dönüşümü


## services/rss_reader.py

Güvenli RSS çekme: Timeout, retry, hata yönetimi
Flexible parsing: Eksik alanları handle eder
Logging sistemi: Detaylı log kayıtları
Session yönetimi: HTTP bağlantılarını optimize eder
Veri doğrulama: Geçersiz verileri filtreler
Kategori desteği: Farklı RSS kategorileri
Test fonksiyonları: Bağlantı kontrolü

Temel fonksiyonlar:

get_latest_news(count): Son haberleri çeker
get_news_by_category(category, count): Kategoriye göre haberler
test_connection(): RSS bağlantı durumu
get_feed_info(): Feed metadata bilgileri

16 farklı kategori desteği: guncel, ekonomi, spor, kultur, dunya, politika, teknoloji, bilim-teknoloji, saglik, egitim, yasam, analiz, portre, futbol, basketbol, dunyadan-spor
✅ Gelişmiş kategori yönetimi:

get_news_by_category(category, count): Belirli kategoriden haber
get_available_categories(): Mevcut kategoriler
get_category_info(): Kategori açıklamaları
get_news_from_multiple_categories(): Birden fazla kategoriden haber
search_in_category(): Kategori içinde arama

Kullanım örnekleri:
python
# Varsayılan güncel kategori
reader = RSSReader()

# Ekonomi kategorisi varsayılan
reader = RSSReader(default_category="ekonomi")

# Spor haberlerini çek
spor_haberleri = reader.get_news_by_category("spor", 10)

# Birden fazla kategori
results = reader.get_news_from_multiple_categories(["guncel", "ekonomi", "spor"], 5)



## services/web_scraper.py

scrape_article(url): Tek haber çeker
scrape_multiple_articles(urls): Toplu çekme
_extract_article_content(): Ana içerik
_extract_metadata(): Meta veriler

Çıkardığı veriler:

Tam makale metni
Yazar ve konum bilgisi
Ana görsel + tüm görseller
Etiketler ve kategori
Yayın tarihi




## services/news_service.py

Ana özellikler:

RSS + Scraping birleşimi: RSS'den hızlı liste, scraping'den zengin içerik
Paralel processing: ThreadPoolExecutor ile hızlı scraping
Flexible kategori: Tek/çoklu kategori desteği
Akıllı filtreleme: Karakter, anahtar kelime, scraping zorunluluğu
Summary analytics: Başarı oranları, kategori dağılımı

Ana metodlar:

get_latest_news(): Son haberler (tek kategori)
get_news_by_categories(): Çoklu kategori
get_single_article(): URL'den tek makale
search_articles(): Haber arama
filter_articles(): Gelişmiş filtreleme



## services/tts_service.py

Ana özellikler:

OpenAI TTS API entegrasyonu: Tam API desteği
Metin bölme: 4000 karakter limitini otomatik handle eder
Cost tracking: JSON tabanlı maliyet takibi
File management: Benzersiz dosya isimleri, organizasyon
Chunk support: Uzun metinler için çoklu dosya
Statistics: Detaylı kullanım istatistikleri

Ana metodlar:

text_to_speech(request): Temel TTS dönüştürme
convert_article_to_speech(article): Haber makalesini direkt dönüştür
get_cost_statistics(): Maliyet ve kullanım istatistikleri
list_audio_files(): Oluşturulan dosyaları listele

Cost tracking özellikleri:

Her API çağrısını kaydet
Toplam maliyet hesaplama
Başarı oranları
En çok kullanılan ses/model





## api/main.py

Ana özellikler:

Local network ready: CORS enabled, IP auto-detection
Full REST API: News + TTS + Audio serving
Static file serving: /audio/ endpoint ile ses dosyaları
Comprehensive endpoints: 12 farklı endpoint
Batch operations: Toplu haber-TTS dönüştürme
Auto documentation: Swagger UI /docs

API Endpoints:

GET / - Root info
GET /health - Health check
GET /api/news/latest - Son haberler
GET /api/news/categories - Kategori listesi
GET /api/news/category/{category} - Kategoriye göre haber
GET /api/news/search - Haber arama
POST /api/tts/convert - Text-to-speech
POST /api/tts/article - Article-to-speech
GET /api/tts/stats - TTS istatistikleri
GET /api/audio/list - Ses dosyaları listesi
GET /audio/{filename} - Ses dosyası serve
POST /api/batch/news-to-tts - Toplu dönüştürme

Local network features:

Auto IP detection
Mobile-friendly URLs
Direct audio streaming
CORS enabled

python api/main.py




## main.py

Ana komutlar:

python main.py news - Haber çekme
python main.py tts - TTS dönüştürme
python main.py batch - Toplu işlem
python main.py stats - İstatistikler
python main.py config - Konfigürasyon
python main.py api - API server başlat

Örnek kullanımlar:
bash# .env dosyası oluştur
python main.py config --create-env

# Son 5 ekonomi haberini çek
python main.py news --category ekonomi --count 5 --scraping

# Metni sese dönüştür
python main.py tts --text "Merhaba dünya" --voice alloy

# URL'den makaleyi TTS'e dönüştür
python main.py tts --url "https://aa.com.tr/tr/..." --force

# Toplu işlem - 10 haber
python main.py batch --category guncel --count 10 --voice nova

# İstatistikleri göster
python main.py stats --verbose

# API serverını başlat
python main.py api
CLI özellikleri:

Argparse ile professional CLI
Validation ve error handling
Progress feedback
Cost estimation ve confirmation
JSON output support
Verbose mode
Force mode (auto-confirm)














# Temel kullanım
python main.py update-agenda

# Özelleştirilmiş kullanım
python main.py update-agenda --count 20 --voice nova --force --save-json

# Parametreler:
--count 15          # Çekilecek haber sayısı
--voice alloy       # TTS ses (alloy, echo, fable, onyx, nova, shimmer)
--model tts-1       # TTS model (tts-1, tts-1-hd)
--min-chars 300     # Minimum karakter filtresi
--max-chars 2000    # Maksimum karakter filtresi
--workers 3         # Paralel işlem worker sayısı
--force             # Onay almadan çalıştır
--save-json         # JSON dosyasına kaydet

python main.py update-agenda --force --save-json