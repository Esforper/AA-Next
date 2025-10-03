#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AA RSS Haber Botu
Anadolu Ajansı RSS feed'lerinden haberleri toplar ve JSON'a kaydeder
"""

import feedparser
import json
import time
from datetime import datetime

# RSS Feed Listesi
FEEDS = {
    # Türkçe Ana Kategoriler
    'guncel': 'https://www.aa.com.tr/tr/rss/default?cat=guncel',
    'dunya': 'https://www.aa.com.tr/tr/rss/default?cat=dunya',
    'turkiye': 'https://www.aa.com.tr/tr/rss/default?cat=turkiye',
    'ekonomi': 'https://www.aa.com.tr/tr/rss/default?cat=ekonomi',
    'spor': 'https://www.aa.com.tr/tr/rss/default?cat=spor',
    'saglik': 'https://www.aa.com.tr/tr/rss/default?cat=saglik',
    'teknoloji': 'https://www.aa.com.tr/tr/rss/default?cat=teknoloji',
    'kultur': 'https://www.aa.com.tr/tr/rss/default?cat=kultur',
    'egitim': 'https://www.aa.com.tr/tr/rss/default?cat=egitim',
    'politika': 'https://www.aa.com.tr/tr/rss/default?cat=politika',
    'yasam': 'https://www.aa.com.tr/tr/rss/default?cat=yasam',
    
    # Teyit Hattı
    'teyit_gazze': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=gazze',
    'teyit_politika': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=politika',
    'teyit_aktuel': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=aktuel',
    'teyit_kultur': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=kultur-sanat',
    'teyit_bilim': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=bilim-teknoloji',
    'teyit_blog': 'https://www.aa.com.tr/tr/teyithatti/rss/news?cat=blog',
    'teyit_video': 'https://www.aa.com.tr/tr/teyithatti/rss/video',
    
    # İngilizce
    'en_general': 'https://www.aa.com.tr/en/rss/default?cat=general',
    'en_world': 'https://www.aa.com.tr/en/rss/default?cat=world',
    'en_turkey': 'https://www.aa.com.tr/en/rss/default?cat=turkey',
    'en_economy': 'https://www.aa.com.tr/en/rss/default?cat=economy',
    'en_sports': 'https://www.aa.com.tr/en/rss/default?cat=sports',
    
    # Diğer Diller
    'ar_genel': 'https://www.aa.com.tr/ar/rss/default',
    'ru_genel': 'https://www.aa.com.tr/ru/rss/default',
    'fr_genel': 'https://www.aa.com.tr/fr/rss/default',
    'es_genel': 'https://www.aa.com.tr/es/rss/default',
}

DATA_FILE = 'aa_news_data.json'
CHECK_INTERVAL = 900  # 30 dakika

def load_data():
    """Mevcut haberleri yükle"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    """Haberleri kaydet"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_feed(url, category):
    """RSS feed'den haberleri çek"""
    news_list = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Görsel URL'ini al (AA RSS'inde <image> etiketi var)
            image_url = ''
            if hasattr(entry, 'image'):
                image_url = entry.image
            elif hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url', '')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image_url = entry.enclosures[0].get('href', '')
            
            news = {
                'guid': entry.get('id', entry.get('link', '')),
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'description': entry.get('description', entry.get('summary', '')),
                'pubDate': entry.get('published', entry.get('updated', '')),
                'category': category,
                'image': image_url,
                'collected_at': datetime.now().isoformat()
            }
            
            news_list.append(news)
    except Exception as e:
        print(f"❌ Hata [{category}]: {e}")
    
    return news_list

def main():
    print("=" * 60)
    print("🚀 AA RSS HABER BOTU BAŞLATILDI")
    print("=" * 60)
    print(f"📁 Veri dosyası: {DATA_FILE}")
    print(f"⏱️  Kontrol aralığı: {CHECK_INTERVAL} saniye ({CHECK_INTERVAL//60} dakika)")
    print(f"📂 Toplam kategori: {len(FEEDS)}")
    print("=" * 60)
    print("Ctrl+C ile durdurun\n")
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n{'='*60}")
            print(f"🔄 DÖNGÜ #{cycle} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Mevcut verileri yükle
            news_data = load_data()
            old_count = len(news_data)
            new_count = 0
            
            # Her kategoriyi tara
            for category, url in FEEDS.items():
                print(f"📡 {category:20s} kontrol ediliyor...", end=' ')
                
                news_list = fetch_feed(url, category)
                feed_new = 0
                
                for news in news_list:
                    guid = news['guid']
                    if guid not in news_data:
                        news_data[guid] = news
                        new_count += 1
                        feed_new += 1
                
                if feed_new > 0:
                    print(f"✅ {feed_new} yeni haber!")
                else:
                    print(f"⚪ Yeni haber yok")
                
                time.sleep(0.5)  # Rate limiting
            
            # Verileri kaydet
            save_data(news_data)
            
            # İstatistikler
            print(f"\n{'='*60}")
            print(f"📊 İSTATİSTİKLER")
            print(f"{'='*60}")
            print(f"📰 Toplam haber sayısı: {len(news_data):,}")
            print(f"🆕 Bu döngüde yeni: {new_count}")
            print(f"📈 Önceki toplam: {old_count:,}")
            
            # Kategori dağılımı
            categories = {}
            for news in news_data.values():
                cat = news['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📂 KATEGORİ DAĞILIMI (İlk 10):")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {cat:25s}: {count:5,}")
            
            # Bekle
            print(f"\n⏳ {CHECK_INTERVAL} saniye bekleniyor...")
            print(f"{'='*60}\n")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot durduruldu!")
        print(f"💾 Toplam {len(news_data):,} haber kaydedildi")
        save_data(news_data)

if __name__ == "__main__":
    main()