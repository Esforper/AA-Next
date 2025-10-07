import json
import requests
from bs4 import BeautifulSoup
from typing import List
import time

# AA domains
AA_DOMAIN = 'https://www.aa.com.tr'
AA_CDN = 'https://cdnuploads.aa.com.tr'

# Session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def normalize_url(src: str) -> str:
    """URL normalize et"""
    if not src:
        return None
    if src.startswith('http://') or src.startswith('https://'):
        return src
    if src.startswith('//'):
        return 'https:' + src
    if src.startswith('/'):
        return AA_CDN + src if src.startswith('/uploads/') else AA_DOMAIN + src
    return None

def filter_aa_images(soup, base_url: str) -> List[str]:
    """
    BackendAPIDemo'daki filter_aa_images() fonksiyonunun aynısı
    AA görselleri filtrele
    """
    images = []
    main_image = None
    
    # Ana görsel
    main_img = soup.select_one('img.detay-buyukFoto, img[class*="detay-buyuk"]')
    if main_img and main_img.get('src'):
        src = normalize_url(main_img.get('src'))
        if src:
            main_image = src
            images.append(src)
    
    # İçerik görselleri
    content_div = soup.select_one('div.detay-icerik')
    if content_div:
        for img in content_div.find_all('img'):
            src = normalize_url(img.get('src'))
            if src and src != main_image:
                if any(k in src.lower() for k in ['/uploads/', 'cdnuploads.aa.com.tr', '/thumbs_']):
                    images.append(src)
    
    # Fallback: Tüm görselleri tara
    if not images:
        for img in soup.find_all('img'):
            src = normalize_url(img.get('src'))
            if src:
                if not any(p in src.lower() for p in ['logo', 'icon', 'button', 'social', 'facebook', 'twitter', 'instagram']):
                    images.append(src)
    
    # Deduplicate
    return list(dict.fromkeys(images))

def scrape_images_from_url(url: str) -> List[str]:
    """Verilen URL'den resimleri scrape et"""
    try:
        print(f"  Scraping: {url}")
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images = filter_aa_images(soup, url)
        
        print(f"    ✓ {len(images)} resim bulundu")
        return images
        
    except Exception as e:
        print(f"    ✗ Hata: {e}")
        return []
import json
import requests
from bs4 import BeautifulSoup
from typing import List
import time
import os

# ... (normalize_url, filter_aa_images, scrape_images_from_url fonksiyonları aynı)

def main():
    print("=" * 80)
    print("EKSİK RESİMLERİ SCRAPE ETME")
    print("=" * 80)
    
    # Önce final_data var mı kontrol et
    final_file = 'aa_news_final_data.json'
    input_file = 'aa_news_selected_with_keywords.json'
    
    if os.path.exists(final_file):
        print(f"\n✓ '{final_file}' bulundu, devam ediliyor...")
        input_file = final_file
    else:
        print(f"\n'{final_file}' yok, '{input_file}' kullanılıyor...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tüm haberleri topla
    all_news = []
    
    # Seçilen haberler
    for category, news_list in data.get('selected_news_by_category', {}).items():
        all_news.extend(news_list)
    
    # Keyword'lere göre haberler
    for keyword, news_list in data.get('news_by_keyword', {}).items():
        all_news.extend(news_list)
    
    # Deduplicate
    seen_guids = set()
    unique_news = []
    for news in all_news:
        guid = news.get('guid')
        if guid and guid not in seen_guids:
            seen_guids.add(guid)
            unique_news.append(news)
    
    print(f"Toplam {len(unique_news)} benzersiz haber bulundu")
    
    # İstatistik: Kaç tanesinde resim var
    news_with_images = sum(
        1 for news in unique_news 
        if news.get('scraped_content', {}).get('images')
    )
    print(f"Resimli haber: {news_with_images}")
    print(f"Resimsiz haber: {len(unique_news) - news_with_images}")
    
    # Eksik resim olanları bul - SADECE BOŞ OLANLAR
    news_without_images = []
    for news in unique_news:
        scraped = news.get('scraped_content', {})
        images = scraped.get('images', [])
        
        if not images:
            news_without_images.append(news)
    
    if len(news_without_images) == 0:
        print("\n✓ Tüm haberlerde resim var!")
        return
    
    # Eksik resimleri scrape et
    print(f"\n{len(news_without_images)} haberin resimleri scrape ediliyor...")
    print("=" * 80)
    
    updated_count = 0
    failed_count = 0
    
    for i, news in enumerate(news_without_images, 1):
        url = news.get('link') or news.get('scraped_content', {}).get('url')
        
        if not url:
            print(f"{i}/{len(news_without_images)} - URL yok, atlanıyor")
            failed_count += 1
            continue
        
        # Title kontrolü
        title = news.get('title') or news.get('scraped_content', {}).get('full_title') or 'Başlıksız'
        title_display = title[:60] if isinstance(title, str) else 'Başlıksız'
        
        print(f"{i}/{len(news_without_images)} - {title_display}...", end=' ')
        
        # Resimleri scrape et
        images = scrape_images_from_url(url)
        
        # Habere ekle
        if images:
            if 'scraped_content' not in news:
                news['scraped_content'] = {}
            news['scraped_content']['images'] = images
            updated_count += 1
            print(f"✓ {len(images)} resim")
        else:
            failed_count += 1
            print("✗ Resim bulunamadı")
        
        # Rate limiting
        time.sleep(0.5)
        
        # Her 50 haberde bir ara kayıt yap
        if i % 50 == 0:
            print(f"\n--- Ara kayıt yapılıyor ({i}/{len(news_without_images)}) ---")
            save_progress(data, unique_news, final_file)
            print("--- Devam ediliyor ---\n")
    
    print("\n" + "=" * 80)
    print(f"✓ {updated_count} habere resim eklendi")
    print(f"✗ {failed_count} haberde resim bulunamadı")
    
    # Final kayıt
    print(f"\nFinal data '{final_file}' dosyasına kaydediliyor...")
    save_progress(data, unique_news, final_file)
    print(f"✓ Kaydedildi!")
    
    # İstatistikler
    print("\n" + "=" * 80)
    print("FINAL İSTATİSTİKLER")
    print("=" * 80)
    
    total_with_images = sum(
        1 for news in unique_news 
        if news.get('scraped_content', {}).get('images')
    )
    
    print(f"Toplam haber: {len(unique_news)}")
    print(f"Resimli haber: {total_with_images} (%{total_with_images/len(unique_news)*100:.1f})")
    print(f"Resimsiz haber: {len(unique_news) - total_with_images}")
    print(f"Bu çalıştırmada eklenen: {updated_count}")
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI")
    print("=" * 80)

def save_progress(data, unique_news, output_file):
    """Progress'i kaydet"""
    guid_to_news = {n.get('guid'): n for n in unique_news}
    final_data = data.copy()
    
    # Seçilen haberleri güncelle
    for category in final_data.get('selected_news_by_category', {}):
        for i, news in enumerate(final_data['selected_news_by_category'][category]):
            guid = news.get('guid')
            if guid in guid_to_news:
                final_data['selected_news_by_category'][category][i] = guid_to_news[guid]
    
    # Keyword haberleri güncelle
    for keyword in final_data.get('news_by_keyword', {}):
        for i, news in enumerate(final_data['news_by_keyword'][keyword]):
            guid = news.get('guid')
            if guid in guid_to_news:
                final_data['news_by_keyword'][keyword][i] = guid_to_news[guid]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()