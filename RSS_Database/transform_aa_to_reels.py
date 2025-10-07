import json
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional

# AA Kategori anahtarlarının (json'daki key) metin başındaki karşılıkları
# Buraya yeni kategoriler eklendikçe güncellemek gerekebilir.
AA_CATEGORY_PREFIXES = {
    'saglik': 'Sağlık',
    'ekonomi': 'Ekonomi',
    'politika': 'Politika',
    'gundem': 'Güncel', # Bazen Güncel bazen Gündem olabilir, veriye göre ayarlanmalı
    'dunya': 'Dünya',
    'egitim': 'Eğitim',
    'yasam': 'Yaşam',
    'kultur': 'KültürSanat', # Bazen birleşik yazılıyor
    'spor': 'Spor',
    'teknoloji': 'Teknoloji',
    'cevre': 'Çevre',
}

def clean_aa_garbage(dirty_text: str, category_hint: str = None) -> str:
    """
    AA description/summary metninin başındaki kategoriyi ve
    sonundaki 'Yazar | Tarih' çöpünü temizler.
    """
    if not dirty_text:
        return ""
    
    cleaned = dirty_text.strip()

    # 1. ADIM: SONDAKI GARBAGE'I TEMIZLE (Yazar | Tarih)
    # Örnekler:
    # "bilim ve teknoloji üssü haline gelmiştir.Başak Akbulut  |17.05.2025 - Güncelleme : 17.05.2025"
    # "...söyledi.Tezcan Ekizler  |25.09.2025 - Güncelleme : 25.09.2025"
    # Sadece tarih varsa: " |25.09.2025..."
    
    # Regex Mantığı: 
    # (?:\s+[A-ZÇĞİÖŞÜa-zçğıöşü\.\s]+)? -> Opsiyonel yazar ismi (boşlukla başlar)
    # \s*\|\s*                          -> Pipe işareti (|) ve etrafındaki boşluklar
    # \d{2}\.\d{2}\.\d{4}               -> Tarih formatı (DD.MM.YYYY)
    # .*$                               -> Satır sonuna kadar geri kalan her şey (Güncelleme vs.)
    
    footer_regex = r'(?:\s+[A-Za-zÇĞİÖŞÜçğıöşü\.\s]+)?\s*\|\s*\d{2}\.\d{2}\.\d{4}.*$'
    
    # Regex'i uygula ve sil
    cleaned = re.sub(footer_regex, '', cleaned, flags=re.IGNORECASE).strip()

    # 2. ADIM: BAŞTAKİ KATEGORİ EKİNİ TEMİZLE
    # Kategori hint (ipucu) varsa (örn: 'saglik'), karşılığını ('Sağlık') bul ve baştan sil.
    prefix_to_remove = None
    if category_hint and category_hint in AA_CATEGORY_PREFIXES:
        prefix_to_remove = AA_CATEGORY_PREFIXES[category_hint]
    
    if prefix_to_remove and cleaned.startswith(prefix_to_remove):
        # "SağlıkBakan..." gibi bitişikse kes.
        # Kestikten sonraki karakterin büyük harf olup olmadığını kontrol etmek
        # yanlışlıkla kelime kesmeyi önler (örn: kategori "Sanat", metin "Sanatçı...")
        potential_clean = cleaned[len(prefix_to_remove):]
        if potential_clean and (potential_clean[0].isupper() or potential_clean[0].isspace()):
             cleaned = potential_clean.strip()

    return cleaned

def calculate_metrics(paragraphs: List[str]) -> dict:
    """İçerik metriklerini hesapla"""
    full_text = ' '.join(paragraphs) if paragraphs else ''
    words = full_text.split()
    
    return {
        'word_count': len(words),
        'character_count': len(full_text),
        # TTS için ortalama okuma hızı (karakter/saniye veya kelime/dakika)
        # 150 kelime/dakika daha gerçekçi bir TTS hızıdır.
        'estimated_reading_time': max(1, len(words) // 150) 
    }

def generate_reel_id(title: str, guid: str) -> str:
    """Benzersiz reel ID oluştur"""
    unique_str = f"{title}{guid}"
    return "reel_" + hashlib.md5(unique_str.encode()).hexdigest()[:12]

def transform_news_to_reel(news_item: dict) -> dict:
    """Tek bir haberi reel formatına dönüştür"""
    
    scraped = news_item.get('scraped_content', {})
    
    # 1. Title Belirle
    title = (
        news_item.get('title') or 
        scraped.get('full_title') or 
        'Başlıksız Haber'
    ).strip()
    
    # 2. Category Belirle (Main'den gelen hint veya URL'den)
    category = news_item.get('_category_hint', 'guncel') # Main'den gelen ipucu
    
    # URL'den kategori yedek kontrolü (eğer hint yoksa)
    url = news_item.get('link') or scraped.get('url', '')
    if category == 'guncel' and '/tr/' in url:
        parts = url.split('/tr/')
        if len(parts) > 1:
            category_from_url = parts[1].split('/')[0]
            if category_from_url:
                category = category_from_url

    # 3. Summary Temizleme İşlemi
    # En dolu özeti bul (scraped summary veya description)
    dirty_summary = scraped.get('summary') or news_item.get('description') or ""
    
    # YENİ TEMİZLEME FONKSİYONU KULLANIMI
    # Kategori ipucunu vererek baştaki ve sondaki çöpleri temizle
    clean_summary = clean_aa_garbage(dirty_summary, category)

    # 4. Diğer Veriler
    paragraphs = scraped.get('paragraphs', [])
    full_content_text = '\n\n'.join(paragraphs) if paragraphs else ''
    
    images = scraped.get('images', [])
    # Kaliteli resim seçimi (logo vb. elemeye çalışılabilir, şimdilik ilkini alıyoruz)
    main_image = images[0] if images else None
    
    keywords = scraped.get('keywords', [])
    keywords = [k for k in keywords if k.lower() not in ['anadolu ajansı', 'aa']]
    
    # Yazar bilgisi scraped içinde daha temiz olabilir
    author = scraped.get('author')
    
    published_date = news_item.get('pubDate') or news_item.get('collected_at')
    metrics = calculate_metrics(paragraphs)
    
    # 5. TTS Content Hazırlama (Kritik Kısım)
    # Temizlenen özet genellikle başlığı da içerir.
    # TTS = "Başlık. [kısa duraksama] Özet" olmalı.
    
    final_summary_for_tts = clean_summary
    
    # Eğer temiz özet, başlığın aynısıyla başlıyorsa, başlığı özetten çıkaralım.
    # Böylece TTS'de "Başlık. Başlık Özet..." gibi tekrar olmaz.
    if clean_summary.startswith(title):
        final_summary_for_tts = clean_summary[len(title):].strip()
        # Başlıktan sonra gelen noktalama işaretlerini de temizleyelim (. : ,)
        final_summary_for_tts = re.sub(r'^[.:,;-\s]+', '', final_summary_for_tts).strip()

    # TTS için birleştir
    if final_summary_for_tts:
        tts_content = f"{title}. {final_summary_for_tts}"
    else:
        # Özet kurtarılamadıysa sadece başlık
        tts_content = title

    # Reel ID
    reel_id = generate_reel_id(title, news_item.get('guid', ''))
    
    # Reel objesi oluştur
    reel = {
        "id": reel_id,
        "news_data": {
            "title": title,
            "summary": clean_summary, # Veritabanı için temizlenmiş tam halini tutalım
            "url": url,
            "category": category,
            "author": author,
            "published_date": published_date,
            "main_image": main_image,
            "images": images,
            "keywords": keywords,
            "source": "aa",
            "content_language": "tr",
            "full_content_paragraphs": paragraphs
        },
        "tts_content": tts_content, # Seslendirilecek optimize metin
        "status": "pending",
        "published_at": published_date,
        "created_at": datetime.now().isoformat(),
        "character_count_tts": len(tts_content), # TTS maliyeti için önemli
        "is_fresh": True,
    }
    
    return reel_id, reel

def main():
    print("=" * 80)
    print("AA HABERLERİ REELS FORMATINA DÖNÜŞTÜRME VE TEMİZLEME")
    print("=" * 80)
    
    input_file = 'aa_news_final_data.json'
    print(f"\n{input_file} dosyası okunuyor...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"HATA: {input_file} bulunamadı. Lütfen dosyayı aynı dizine koyun.")
        return

    # Tüm haberleri topla
    all_news = []
    
    print("Haberler kategorilere göre toplanıyor...")
    # Kategori bazlı haberleri alırken KATEGORİ BİLGİSİNİ de ekliyoruz.
    # Bu, temizleme fonksiyonunun baştaki "Sağlık" vb. kaldırması için gerekli ipucu.
    categories_data = data.get('selected_news_by_category', {})
    for category_key, news_list in categories_data.items():
        for news_item in news_list:
            # Geçici olarak kategori bilgisini haberin içine gömüyoruz
            news_item['_temp_category_hint'] = category_key
            all_news.append(news_item)
            
    # Keyword bazlı haberler (eğer varsa ve yukarıdakilerden farklıysa)
    # Not: Keyword haberlerinde kategori garantisi olmayabilir, URL'den çıkarılacak.
    keyword_data = data.get('news_by_keyword', {})
    for keyword, news_list in keyword_data.items():
         for news_item in news_list:
             # Keyword'den gelenlerde kategori hint'i şimdilik boş bırakalım
             news_item['_temp_category_hint'] = None 
             all_news.append(news_item)
    
    print(f"Toplam işlenecek aday haber: {len(all_news)}")
    
    # Deduplicate (Tekilleştirme)
    seen_guids = set()
    unique_news = []
    for news in all_news:
        guid = news.get('guid')
        # Guid yoksa linki kullan
        if not guid:
            guid = news.get('link')
            
        if guid and guid not in seen_guids:
            seen_guids.add(guid)
            unique_news.append(news)
    
    print(f"Tekilleştirilmiş (Unique) haberler: {len(unique_news)}")
    
    # Reels formatına dönüştür
    print("\nTemizleniyor ve Reels formatına dönüştürülüyor...")
    reels_data = {}
    
    success_count = 0
    failed_count = 0
    
    # Örnek çıktıları görmek için birkaç tanesini yazdıralım
    print("\n--- Temizleme Örnekleri (İlk 3) ---")
    
    for i, news in enumerate(unique_news, 1):
        try:
            reel_id, reel = transform_news_to_reel(news)
            reels_data[reel_id] = reel
            success_count += 1
            
            # İlk 3 haberin dönüşümünü ekrana bas (Kontrol amaçlı)
            if i <= 3:
                print(f"\nÖrnek {i}:")
                print(f"Kategori: {reel['news_data']['category']}")
                print(f"Orijinal Başlık: {reel['news_data']['title']}")
                print(f"TTS İçeriği (Temizlenmiş): \n-> {reel['tts_content']}")
                print("-" * 30)

            if i % 50 == 0:
                print(f"  {i}/{len(unique_news)} haber işlendi...")
                
        except Exception as e:
            title_safe = news.get('title') or 'Başlıksız'
            print(f"  ✗ Hata: {title_safe[:30]}... - {e}")
            failed_count += 1
    
    print("--- Örnekler Sonu ---\n")
    print(f"✓ {success_count} haber başarıyla temizlendi ve dönüştürüldü.")
    if failed_count > 0:
        print(f"✗ {failed_count} haberde hata oluştu.")
    
    # Kaydet
    output_file = 'reels_data_ready_for_tts.json'
    print(f"\n{output_file} dosyasına kaydediliyor...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reels_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Kaydedildi! TTS aşamasına geçebilirsiniz.")

if __name__ == "__main__":
    main()