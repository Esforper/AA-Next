#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AA RSS Haber Botu - Sonsuz Çalışma Garantili
Anadolu Ajansı RSS feed'lerinden haberleri toplar ve JSON'a kaydeder
Her türlü hata durumunda kendini toparlar ve çalışmaya devam eder
"""

import feedparser
import json
import time
from datetime import datetime
import socket
import traceback
import sys

# TIMEOUT AYARI - Kritik!
socket.setdefaulttimeout(30)  # 30 saniye timeout

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
LOG_FILE = 'aa_bot_errors.log'
CHECK_INTERVAL = 900  # 15 dakika
MAX_RETRIES = 3  # Maksimum yeniden deneme sayısı
FEED_TIMEOUT = 45  # Her feed için maksimum bekleme süresi

def log_error(message):
    """Hataları log dosyasına yaz"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except:
        pass  # Log yazılamasa bile devam et

def load_data():
    """Mevcut haberleri yükle - Hata durumunda boş dict döner"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Veri yükleme hatası: {e}")
        return {}

def save_data(data):
    """Haberleri kaydet - Hata durumunda log'a yaz ve devam et"""
    try:
        # Önce geçici dosyaya yaz
        temp_file = f"{DATA_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Başarılıysa asıl dosyayı değiştir
        import os
        if os.path.exists(DATA_FILE):
            os.replace(temp_file, DATA_FILE)
        else:
            os.rename(temp_file, DATA_FILE)
            
    except Exception as e:
        log_error(f"Veri kaydetme hatası: {e}")
        print(f"⚠️ Veri kaydedilemedi: {e}")

def fetch_feed_with_timeout(url, category, timeout=FEED_TIMEOUT):
    """Tek bir feed'i timeout ile çek"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Feed timeout: {category}")
    
    # Unix sistemlerde SIGALRM kullan
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
    
    try:
        news_list = []
        feed = feedparser.parse(url)
        
        # Feed parse edilemedi mi kontrol et
        if hasattr(feed, 'bozo') and feed.bozo and not feed.entries:
            raise Exception(f"Feed parse hatası")
        
        for entry in feed.entries:
            # Görsel URL'ini al
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
        
        return news_list
        
    finally:
        # Alarm'ı iptal et
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

def fetch_feed(url, category):
    """RSS feed'den haberleri çek - Tam korumalı versiyon"""
    for attempt in range(MAX_RETRIES):
        try:
            news_list = fetch_feed_with_timeout(url, category)
            return news_list
            
        except TimeoutError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⏱️ Timeout (deneme {attempt + 1}/{MAX_RETRIES})...", end=' ')
                time.sleep(2)
            else:
                log_error(f"Timeout [{category}]: {url}")
                print(f"❌ Timeout - atlandı")
                return []
                
        except socket.timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"⏱️ Socket timeout (deneme {attempt + 1}/{MAX_RETRIES})...", end=' ')
                time.sleep(2)
            else:
                log_error(f"Socket timeout [{category}]: {url}")
                print(f"❌ Socket timeout - atlandı")
                return []
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"⚠️ Hata (deneme {attempt + 1}/{MAX_RETRIES})...", end=' ')
                time.sleep(2)
            else:
                error_msg = f"Feed hatası [{category}]: {str(e)[:100]}"
                log_error(error_msg)
                print(f"❌ {str(e)[:30]}")
                return []
    
    return []

def process_all_feeds():
    """Tüm feed'leri işle - Hata korumalı"""
    try:
        # Mevcut verileri yükle
        news_data = load_data()
        old_count = len(news_data)
        new_count = 0
        failed_feeds = []
        successful_feeds = 0
        
        # Her kategoriyi tara
        for category, url in FEEDS.items():
            try:
                print(f"📡 {category:20s} kontrol ediliyor...", end=' ')
                sys.stdout.flush()  # Hemen yazdır
                
                news_list = fetch_feed(url, category)
                
                if news_list is None or len(news_list) == 0:
                    print("⚪ Sonuç yok")
                    continue
                
                successful_feeds += 1
                feed_new = 0
                
                for news in news_list:
                    guid = news.get('guid', '')
                    if guid and guid not in news_data:
                        news_data[guid] = news
                        new_count += 1
                        feed_new += 1
                
                if feed_new > 0:
                    print(f"✅ {feed_new} yeni haber!")
                else:
                    print(f"⚪ Yeni haber yok")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                failed_feeds.append(category)
                error_msg = f"Kategori işleme hatası [{category}]: {str(e)[:100]}"
                log_error(error_msg)
                print(f"❌ Hata: {str(e)[:30]}")
                continue  # Bir feed hata verse bile devam et
        
        # Verileri kaydet
        save_data(news_data)
        
        return {
            'total': len(news_data),
            'old': old_count,
            'new': new_count,
            'failed': failed_feeds,
            'successful': successful_feeds
        }
        
    except Exception as e:
        # En dış katman hata yakalama
        error_msg = f"DÖNGÜ HATASI: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg)
        print(f"\n❌ KRİTİK HATA: {str(e)}")
        print("⚠️ Hata loglandı, devam ediliyor...")
        return None

def main():
    print("=" * 60)
    print("🚀 AA RSS HABER BOTU - SONSUZ ÇALIŞMA MODU")
    print("=" * 60)
    print(f"📁 Veri dosyası: {DATA_FILE}")
    print(f"📋 Log dosyası: {LOG_FILE}")
    print(f"⏱️  Kontrol aralığı: {CHECK_INTERVAL} saniye ({CHECK_INTERVAL//60} dakika)")
    print(f"🔌 Socket timeout: 30 saniye")
    print(f"⏰ Feed timeout: {FEED_TIMEOUT} saniye")
    print(f"🔄 Maksimum retry: {MAX_RETRIES}")
    print(f"📂 Toplam kategori: {len(FEEDS)}")
    print("=" * 60)
    print("✅ Herhangi bir hata durumunda otomatik toparlanır")
    print("🛑 Ctrl+C ile durdurun\n")
    
    cycle = 0
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 5
    
    try:
        while True:
            try:
                cycle += 1
                print(f"\n{'='*60}")
                print(f"🔄 DÖNGÜ #{cycle} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"{'='*60}")
                
                # Feed'leri işle
                stats = process_all_feeds()
                
                if stats is None:
                    # Kritik hata oldu
                    consecutive_errors += 1
                    print(f"⚠️ Ardışık hata sayısı: {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}")
                    
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        print(f"🚨 Çok fazla ardışık hata! 5 dakika bekleniyor...")
                        time.sleep(300)  # 5 dakika bekle
                        consecutive_errors = 0
                    else:
                        time.sleep(30)  # Kısa bir ara ver
                    continue
                
                # Başarılı döngü
                consecutive_errors = 0
                
                # İstatistikler
                print(f"\n{'='*60}")
                print(f"📊 İSTATİSTİKLER")
                print(f"{'='*60}")
                print(f"📰 Toplam haber sayısı: {stats['total']:,}")
                print(f"🆕 Bu döngüde yeni: {stats['new']}")
                print(f"📈 Önceki toplam: {stats['old']:,}")
                print(f"✅ Başarılı feed: {stats['successful']}/{len(FEEDS)}")
                
                if stats['failed']:
                    print(f"⚠️  Başarısız: {', '.join(stats['failed'])}")
                
                # Kategori dağılımı
                try:
                    news_data = load_data()
                    categories = {}
                    for news in news_data.values():
                        cat = news.get('category', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    print(f"\n📂 KATEGORİ DAĞILIMI (İlk 10):")
                    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"   {cat:25s}: {count:5,}")
                except:
                    pass  # İstatistik hatası önemli değil
                
                # Bekle
                print(f"\n⏳ {CHECK_INTERVAL} saniye bekleniyor...")
                next_time = datetime.fromtimestamp(time.time() + CHECK_INTERVAL).strftime('%H:%M:%S')
                print(f"   Sonraki döngü: {next_time}")
                print(f"{'='*60}\n")
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                raise  # Ctrl+C'yi üst katmana gönder
                
            except Exception as e:
                # İç döngü hatası
                consecutive_errors += 1
                error_msg = f"İÇ DÖNGÜ HATASI #{cycle}: {str(e)}\n{traceback.format_exc()}"
                log_error(error_msg)
                print(f"\n❌ Döngü hatası: {str(e)}")
                print(f"⚠️ Ardışık hata: {consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}")
                print("🔄 30 saniye sonra yeniden denenecek...\n")
                time.sleep(30)
                continue
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot durduruldu!")
        try:
            news_data = load_data()
            print(f"💾 Toplam {len(news_data):,} haber kaydedildi")
        except:
            print("💾 Veri kaydedildi")
        print(f"📋 Hata logları: {LOG_FILE}")

if __name__ == "__main__":
    main()