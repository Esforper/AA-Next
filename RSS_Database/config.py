"""
Keyword-based scraper için ayarlar
"""

# Dosya yolları (aynı dizinde)
RSS_NEWS_FILE = 'aa_news_data.json'
SCRAPED_NEWS_FILE = 'aa_news_scraped_data.json'

# Scraping ayarları
REQUEST_DELAY = 2  # Requestler arası bekleme süresi (saniye)
MAX_KEYWORDS_PER_NEWS = 10  # Her haberden kaç keyword takip edilecek
MAX_NEWS_PER_KEYWORD = 30  # Her keyword arama sayfasından kaç haber alınacak

# Anadolu Ajansı
AA_BASE_URL = 'https://www.aa.com.tr'