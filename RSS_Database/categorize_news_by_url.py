import json
from collections import defaultdict

def extract_category_from_url(url):
    """
    URL'den kategori çıkarır
    Örnek: https://www.aa.com.tr/tr/saglik/... -> 'saglik'
    """
    if not url:
        return None
    
    # /tr/ ile başlayan path'i bul
    if '/tr/' in url:
        parts = url.split('/tr/')
        if len(parts) > 1:
            # tr'den sonraki ilk segment kategoridir
            category = parts[1].split('/')[0]
            return category
    
    return None

def main():
    print("=" * 80)
    print("AA HABERLERİ URL'DEN KATEGORİZE ETME")
    print("=" * 80)
    
    # JSON'u oku
    print("\nJSON dosyası okunuyor...")
    with open('aa_news_scraped_last.json', 'r', encoding='utf-8') as f:
        all_news = json.load(f)
    
    print(f"Toplam {len(all_news)} haber bulundu")
    
    # Kategorilere ayır
    print("\nHaberler kategorilere ayrılıyor...")
    categorized = defaultdict(list)
    uncategorized = []
    
    for news in all_news:
        url = news.get('link') or news.get('scraped_content', {}).get('url')
        category = extract_category_from_url(url)
        
        if category:
            categorized[category].append(news)
        else:
            uncategorized.append(news)
    
    print(f"Kategorilere ayrıldı: {len(categorized)} kategori")
    print(f"Kategorize edilemeyen: {len(uncategorized)} haber")
    
    # Kategorileri dict'e çevir
    categorized = dict(categorized)
    
    # Sonuçları kaydet
    output = {
        'metadata': {
            'total_news': len(all_news),
            'categorized': len(all_news) - len(uncategorized),
            'uncategorized': len(uncategorized),
            'categories': list(categorized.keys())
        },
        'by_category': categorized,
        'uncategorized': uncategorized
    }
    
    output_file = 'aa_news_categorized.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nSonuç '{output_file}' dosyasına kaydedildi")
    
    # İstatistikler
    print("\n" + "=" * 80)
    print("KATEGORİ DAĞILIMI")
    print("=" * 80)
    
    for cat in sorted(categorized.keys()):
        count = len(categorized[cat])
        print(f"{cat:20s}: {count:5d} haber")
    
    if uncategorized:
        print(f"\n{'uncategorized':20s}: {len(uncategorized):5d} haber")
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI")
    print("=" * 80)
    
    return output

if __name__ == "__main__":
    main()