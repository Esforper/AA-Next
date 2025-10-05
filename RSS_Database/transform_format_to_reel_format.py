import json
import hashlib
import re # Regex kütüphanesini ekliyoruz
from datetime import datetime
from typing import List

# AA Kategori anahtarlarının metin başındaki karşılıkları
AA_CATEGORY_PREFIXES = {
    'saglik': 'Sağlık',
    'ekonomi': 'Ekonomi',
    'politika': 'Politika',
    'gundem': 'Güncel',
    'dunya': 'Dünya',
    'egitim': 'Eğitim',
    'yasam': 'Yaşam',
    'kultur': 'KültürSanat',
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
    
    footer_regex = r'(?:\s+[A-Za-zÇĞİÖŞÜçğıöşü\.\s]+)?\s*\|\s*\d{2}\.\d{2}\.\d{4}.*$'
    cleaned = re.sub(footer_regex, '', cleaned, flags=re.IGNORECASE).strip()

    prefix_to_remove = None
    if category_hint and category_hint in AA_CATEGORY_PREFIXES:
        prefix_to_remove = AA_CATEGORY_PREFIXES[category_hint]
    
    if prefix_to_remove and cleaned.startswith(prefix_to_remove):
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
        'estimated_reading_time': max(1, len(words) // 150)
    }

def generate_reel_id(title: str, guid: str) -> str:
    """Benzersiz reel ID oluştur"""
    unique_str = f"{title}{guid}"
    return "reel_" + hashlib.md5(unique_str.encode()).hexdigest()[:12]

def transform_news_to_reel(news_item: dict) -> dict:
    """Tek bir haberi reel formatına dönüştür"""
    
    scraped = news_item.get('scraped_content', {})
    
    title = (
        news_item.get('title') or 
        scraped.get('full_title') or 
        'Başlıksız Haber'
    ).strip()
    
    # DÜZELTME 2: Kategori hiçbir zaman None kalmayacak şekilde ayarlandı.
    category = news_item.get('_temp_category_hint') or 'guncel'
    url = news_item.get('link') or scraped.get('url', '')
    if '/tr/' in url: # URL'den kategori alma işlemi her zaman denenecek
        parts = url.split('/tr/')
        if len(parts) > 1:
            category_from_url = parts[1].split('/')[0]
            if category_from_url:
                category = category_from_url
    
    dirty_summary = scraped.get('summary') or news_item.get('description') or ""
    summary = clean_aa_garbage(dirty_summary, category)

    paragraphs = scraped.get('paragraphs', [])
    full_content_text = '\n\n'.join(paragraphs) if paragraphs else ''
    images = scraped.get('images', [])
    main_image = images[0] if images else None
    keywords = [k for k in scraped.get('keywords', []) if k.lower() not in ['anadolu ajansı', 'aa']]
    author = scraped.get('author')
    published_date = news_item.get('pubDate') or news_item.get('collected_at')
    metrics = calculate_metrics(paragraphs)
    
    final_summary_for_tts = summary
    if summary.startswith(title):
        final_summary_for_tts = summary[len(title):].strip()
        # DÜZELTME 1: Regex'teki tire (-) karakteri sona alındı.
        final_summary_for_tts = re.sub(r'^[.:,;\s-]+', '', final_summary_for_tts).strip()
    
    if final_summary_for_tts:
        tts_content = f"{title}. {final_summary_for_tts}"
    else:
        tts_content = title

    reel_id = generate_reel_id(title, news_item.get('guid', ''))
    reel = {
        "id": reel_id,
        "news_data": {
            "title": title,
            "summary": summary,
            "full_content": paragraphs,
            "url": url,
            "category": category,
            "author": author,
            "location": None,
            "published_date": published_date,
            "main_image": main_image,
            "images": images,
            "videos": [],
            "tags": scraped.get('tags', []),
            "keywords": keywords,
            "estimated_reading_time": metrics['estimated_reading_time'],
            "source": "aa",
            "word_count": metrics['word_count'],
            "character_count": metrics['character_count'],
            "content_language": "tr",
            "full_content_text": full_content_text,
            "full_content_paragraphs": paragraphs
        },
        "tts_content": tts_content,
        "status": "pending",
        "published_at": published_date,
        "created_at": datetime.now().isoformat(),
        # ... diğer alanlar
        "voice_used": None,
        "model_used": None,
        "audio_url": None,
        "duration_seconds": None,
        "file_size_mb": None,
        "total_views": 0,
        "total_screen_time_ms": 0,
        "completion_rate": 0.0,
        "trend_score": 0.0,
        "is_watched": False,
        "is_trending": False,
        "is_fresh": True,
        "is_recommended": False,
        "recommendation_score": 0.0,
        "recommendation_reason": None,
        "feed_reason": "latest_news",
        "trend_rank": None,
        "character_count": len(tts_content),
        "estimated_cost": None,
        "processing_time_seconds": None,
        "thumbnail_url": None
    }
    
    return reel_id, reel

def main():
    print("=" * 80)
    print("AA HABERLERİ REELS FORMATINA DÖNÜŞTÜRME (GELİŞMİŞ TEMİZLEME)")
    print("=" * 80)
    
    input_file = 'aa_news_final_data.json'
    print(f"\n{input_file} dosyası okunuyor...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"HATA: {input_file} bulunamadı!")
        return
    
    all_news = []
    
    for category, news_list in data.get('selected_news_by_category', {}).items():
        for news_item in news_list:
            news_item['_temp_category_hint'] = category
            all_news.append(news_item)
            
    for keyword, news_list in data.get('news_by_keyword', {}).items():
        for news_item in news_list:
            news_item['_temp_category_hint'] = None
            all_news.append(news_item)
    
    print(f"Toplam aday haber sayısı: {len(all_news)}")
    
    seen_guids = set()
    unique_news = []
    for news in all_news:
        guid = news.get('guid') or news.get('link')
        if guid and guid not in seen_guids:
            seen_guids.add(guid)
            unique_news.append(news)
    
    print(f"Tekilleştirilmiş (Unique) haberler: {len(unique_news)}")
    
    print("\nTemizleniyor ve Reels formatına dönüştürülüyor...")
    reels_data = {}
    
    success_count = 0
    failed_count = 0
    
    for i, news in enumerate(unique_news, 1):
        try:
            reel_id, reel = transform_news_to_reel(news)
            reels_data[reel_id] = reel
            success_count += 1
            
            if i > 0 and i % 50 == 0:
                print(f"  {i}/{len(unique_news)} haber dönüştürüldü...")
        except Exception as e:
            title_safe = news.get('title') or 'Başlıksız'
            print(f"  ✗ Hata: {title_safe[:50]} - {e}")
            failed_count += 1
    
    print(f"\n✓ {success_count} haber başarıyla dönüştürüldü")
    if failed_count > 0:
        print(f"✗ {failed_count} haber dönüştürülemedi")
    
    output_file = 'reels_data_ready_for_tts.json'
    print(f"\n{output_file} dosyasına kaydediliyor...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reels_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Kaydedildi!")
    
    print("\n" + "=" * 80)
    print("İSTATİSTİKLER")
    print("=" * 80)
    
    categories = {}
    with_images = 0
    without_images = 0
    
    for reel_id, reel in reels_data.items():
        cat = reel['news_data']['category']
        categories[cat] = categories.get(cat, 0) + 1
        
        if reel['news_data']['images']:
            with_images += 1
        else:
            without_images += 1
    
    print(f"Toplam reel: {len(reels_data)}")
    print(f"Resimli: {with_images}")
    print(f"Resimsiz: {without_images}")
    
    print("\nKategori dağılımı:")
    # Artık burada hata almayacaksın
    for cat in sorted(categories.keys()):
        print(f"  {cat:20s}: {categories[cat]:4d} reel")
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI")
    print("=" * 80)
    print(f"\nSonraki adım: TTS işlemi için '{output_file}' dosyasını kullan")

if __name__ == "__main__":
    main()