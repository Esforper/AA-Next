"""
AA News Keyword-Based Deep Scraper
aa_news_data.json'dan henüz scrape edilmemiş haberleri alır,
scrape eder ve keyword'lerinden bulduğu diğer haberleri de scrape eder.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# aa_scraper.py'den AANewsScraper class'ını import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from aa_scraper import AANewsScraper

# Config
from config import (
    RSS_NEWS_FILE,
    SCRAPED_NEWS_FILE,
    REQUEST_DELAY,
    MAX_KEYWORDS_PER_NEWS,
    MAX_NEWS_PER_KEYWORD,
    AA_BASE_URL
)


class KeywordSearchScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.processed_urls = set()
        self.session = requests.Session()
        
        # AANewsScraper instance'ı oluştur
        self.aa_scraper = AANewsScraper(input_file=RSS_NEWS_FILE, output_file=SCRAPED_NEWS_FILE)
        
    def load_json(self, filepath):
        """JSON dosyasını yükle"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_json(self, data, filepath):
        """JSON dosyasına kaydet"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_scraped_as_list(self):
        """aa_news_scraped.json'ı liste olarak yükle"""
        try:
            with open(SCRAPED_NEWS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return list(data.values())
                return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_scraped_as_list(self, data_list):
        """aa_news_scraped.json'a liste olarak kaydet"""
        with open(SCRAPED_NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)
    
    def get_unscraped_news(self):
        """aa_news_data.json'dan henüz scrape edilmemiş haberleri bul"""
        rss_data = self.load_json(RSS_NEWS_FILE)
        scraped_list = self.load_scraped_as_list()
        
        # Scraped olan guid'leri bul
        scraped_guids = set()
        for item in scraped_list:
            if item.get('guid'):
                scraped_guids.add(item['guid'])
        
        # Unscraped olanları bul
        unscraped = []
        for guid, news in rss_data.items():
            if guid not in scraped_guids:
                unscraped.append(news)
        
        return unscraped
    
    def is_valid_news_url(self, url):
        """Geçerli haber URL'si mi kontrol et"""
        # İnfografik, abonelik formu gibi sayfaları filtrele
        invalid_patterns = [
            '/info/infographic/',
            '/p/abonelik',
            '/p/',  # Statik sayfalar
            '/pgc/',  # Foto galeri
            '/vgc/',  # Video galeri
            '/cvg/',  # Video
            '/live',  # Canlı yayın
            '/search',  # Arama sayfası
        ]
        
        for pattern in invalid_patterns:
            if pattern in url:
                return False
        
        # Haber URL'si format kontrolü: /tr/kategori/haber-basligi/guid
        parts = url.split('/')
        if len(parts) >= 5:
            # Son kısım sayısal guid olmalı
            try:
                int(parts[-1])
                return True
            except ValueError:
                return False
        
        return False
    
    def extract_keywords_from_page(self, url):
        """Haber sayfasından keyword linklerini çıkar"""
        try:
            time.sleep(REQUEST_DELAY + 1)  # Ekstra 1 saniye bekle
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            keywords = []
            
            # Keyword linklerini bul
            keyword_links = soup.find_all('a', href=lambda x: x and '/tr/search/' in x and 's=' in x)
            
            for link in keyword_links[:MAX_KEYWORDS_PER_NEWS]:
                keyword_url = link.get('href')
                if keyword_url.startswith('/'):
                    keyword_url = AA_BASE_URL + keyword_url
                
                keyword_text = link.text.strip().replace('\xa0', ' ')  # Non-breaking space temizle
                
                if keyword_text:
                    keywords.append({
                        'text': keyword_text,
                        'url': keyword_url
                    })
            
            if keywords:
                print(f"  → {len(keywords)} keyword bulundu: {[k['text'] for k in keywords]}")
            return keywords
            
        except Exception as e:
            print(f"  ✗ Keyword çıkarma hatası: {e}")
            return []
   
   
   
    def scrape_keyword_search_page(self, keyword_url, keyword_text):
        """Keyword arama sayfasından haber linklerini çıkar (AJAX kullanarak)"""
        try:
            time.sleep(REQUEST_DELAY + 1)
            
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(keyword_url)
            params = parse_qs(parsed.query)
            keyword_search = params.get('s', [''])[0]
            
            ajax_url = 'https://www.aa.com.tr/tr/Search/Search'
            
            response = self.session.get(keyword_url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            token = token_input.get('value') if token_input else ''
            
            post_data = {
                'PageSize': 100,
                'Keywords': keyword_search,
                'CategoryId': '',
                'TypeId': 1,
                'Page': 1,
                '__RequestVerificationToken': token
            }
            
            ajax_response = self.session.post(
                ajax_url, 
                data=post_data, 
                headers={**self.headers, 'X-Requested-With': 'XMLHttpRequest'},
                timeout=30
            )
            
            ajax_data = ajax_response.json()
            
            news_items = []  # (url, pub_date) tuple'ları
            
            if ajax_data and 'Documents' in ajax_data:
                for doc in ajax_data['Documents'][:MAX_NEWS_PER_KEYWORD]:
                    if 'Route' in doc:
                        full_url = AA_BASE_URL + doc['Route'] if doc['Route'].startswith('/') else doc['Route']
                        
                        # Tarih bilgisini al
                        pub_date = doc.get('CreateDateString', '')
                        
                        if self.is_valid_news_url(full_url):
                            if full_url not in [item[0] for item in news_items] and full_url not in self.processed_urls:
                                news_items.append((full_url, pub_date))
            
            print(f"  → '{keyword_text}' için {len(news_items)} geçerli haber bulundu")
            return news_items
            
        except Exception as e:
            print(f"  ✗ Keyword arama scraping hatası: {e}")
            import traceback
            traceback.print_exc()
            return []

    def is_already_scraped(self, url):
        """Bu URL daha önce scrape edilmiş mi kontrol et"""
        scraped_list = self.load_scraped_as_list()
        for item in scraped_list:
            if item.get('link') == url:
                return True
        return False
 
 
    
    def scrape_and_save_news(self, url, guid=None, pub_date=None):
        """Bir haberi scrape et ve kaydet"""
        # Önce bellekte kontrol et
        if url in self.processed_urls:
            print(f"  ⊘ Bu oturumda zaten işlendi: {url}")
            return None
        
        # Dosyada var mı kontrol et
        if self.is_already_scraped(url):
            print(f"  ⊘ Daha önce kaydedilmiş: {url}")
            self.processed_urls.add(url)  # Bellekte de işaretle
            return None
        
        if not self.is_valid_news_url(url):
            print(f"  ⊘ Geçersiz URL: {url}")
            return None
        
        print(f"  ↓ Scraping: {url}")
        
        # AANewsScraper'ın scrape_article metodunu kullan
        scraped_content = self.aa_scraper.scrape_article(url)
        
        if scraped_content:
            if not guid:
                guid = url.split('/')[-1]
            
            # pubDate belirleme önceliği:
            # 1. Parametre olarak gelen (AJAX'dan)
            # 2. Scrape edilen sayfadan (published_date)
            # 3. Şu an
            final_pub_date = pub_date or scraped_content.get('published_date') or datetime.now().isoformat()
            
            news_data = {
                'guid': guid,
                'title': scraped_content.get('full_title', ''),
                'link': url,
                'description': scraped_content.get('summary', ''),
                'pubDate': final_pub_date,  # ← Burada kullanıyoruz
                'category': scraped_content.get('category_full', ''),
                'image': '',
                'collected_at': datetime.now().isoformat(),
                'scraped_content': scraped_content,
                'scraping_success': True
            }
            
            self.processed_urls.add(url)
            print(f"  ✓ Başarılı: {scraped_content.get('full_title', 'Başlıksız')}")
            
            # Hemen kaydet
            scraped_list = self.load_scraped_as_list()
            scraped_list.append(news_data)
            self.save_scraped_as_list(scraped_list)
            
            return news_data
        else:
            print(f"  ✗ Scraping başarısız")
            return None
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 60)
        print("AA News Keyword-Based Deep Scraper")
        print("=" * 60)
        
        # Henüz scrape edilmemiş haberleri al
        unscraped_news = self.get_unscraped_news()
        print(f"\n📰 {len(unscraped_news)} adet scrape edilmemiş haber bulundu\n")
        
        if not unscraped_news:
            print("Scrape edilecek haber yok!")
            return
        
        total_scraped = 0
        
        # Her haber için işlem yap
        for i, news in enumerate(unscraped_news, 1):
            print(f"\n[{i}/{len(unscraped_news)}] İşleniyor...")
            
            url = news.get('link')
            guid = news.get('guid')
            
            if not url:
                continue
            
            # Haberi scrape et
            scraped_news = self.scrape_and_save_news(url, guid)
            
            if scraped_news:
                total_scraped += 1
                
                # Keyword'leri çıkar
                keywords = self.extract_keywords_from_page(url)
                
                # Her keyword için arama sayfasını scrape et
                for keyword in keywords:
                    print(f"\n  🔍 Keyword: '{keyword['text']}'")
                    
                    # Keyword arama sayfasından haber linklerini al
                    keyword_news_urls = self.scrape_keyword_search_page(
                        keyword['url'], 
                        keyword['text']
                    )
                    
                    # Bulunan haberleri scrape et
                    for kw_url, kw_pub_date in keyword_news_urls:
                        kw_scraped = self.scrape_and_save_news(kw_url, pub_date=kw_pub_date)
                        if kw_scraped:
                            total_scraped += 1
        
        print("\n" + "=" * 60)
        print(f"✓ Tamamlandı! Toplam {total_scraped} haber scrape edildi")
        print("=" * 60)


if __name__ == "__main__":
    scraper = KeywordSearchScraper()
    scraper.run()