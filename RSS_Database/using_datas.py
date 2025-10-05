import json
from datetime import datetime, timedelta
from collections import defaultdict

def filter_and_select_news():
    """
    1. 100+ haber olan kategorilerden 20'şer haber seç
    2. Seçilen haberlerin tüm keywords'lerini topla
    3. Her keyword için tüm ilgili haberleri bul
    """
    
    print("=" * 80)
    print("AA HABERLERİ FİLTRELEME VE SEÇME")
    print("=" * 80)
    
    # Kategorize edilmiş JSON'u oku
    print("\nKategorize edilmiş haberler okunuyor...")
    with open('aa_news_categorized.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categorized = data['by_category']
    
    # 100+ haber olan kategorileri bul
    major_categories = {
        cat: news_list 
        for cat, news_list in categorized.items() 
        if len(news_list) >= 100
    }
    
    print(f"\n100+ haber olan kategoriler:")
    for cat, news_list in major_categories.items():
        print(f"  {cat}: {len(news_list)} haber")
    
    # Her kategoriden son 3 günde yayınlanan 20 haber seç
    print("\n" + "=" * 80)
    print("HER KATEGORİDEN 20 HABER SEÇİLİYOR (SON 3 GÜN)")
    print("=" * 80)
    
    cutoff_date = datetime.now() - timedelta(days=3)
    selected_news = {}
    
    for category, news_list in major_categories.items():
        # Tarihe göre filtrele ve sırala
        recent_news = []
        
        for news in news_list:
            try:
                date_str = news.get('pubDate') or news.get('collected_at')
                if date_str:
                    if 'T' in date_str:
                        news_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        news_date = datetime.strptime(date_str, '%d.%m.%Y')
                    
                    if news_date >= cutoff_date:
                        recent_news.append(news)
            except:
                continue
        
        # En yeni 20 tanesini seç
        recent_news.sort(
            key=lambda x: x.get('pubDate') or x.get('collected_at') or '',
            reverse=True
        )
        
        selected = recent_news[:20]
        selected_news[category] = selected
        
        print(f"{category:20s}: {len(recent_news):4d} recent -> {len(selected):2d} seçildi")
    
    # Seçilen haberlerdeki tüm keywords'leri topla
    print("\n" + "=" * 80)
    print("KEYWORDS TOPLANIYOR")
    print("=" * 80)
    
    all_keywords = set()
    category_keywords = {}
    
    for category, news_list in selected_news.items():
        keywords_in_category = set()
        
        for news in news_list:
            keywords = news.get('scraped_content', {}).get('keywords', [])
            # "Anadolu Ajansı" gibi generic keyword'leri filtrele
            filtered = [kw for kw in keywords if kw.lower() not in ['anadolu ajansı', 'aa']]
            keywords_in_category.update(filtered)
            all_keywords.update(filtered)
        
        category_keywords[category] = list(keywords_in_category)
        print(f"{category:20s}: {len(keywords_in_category)} benzersiz keyword")
    
    print(f"\nTOPLAM BENZERSIZ KEYWORD: {len(all_keywords)}")
    
    # Her keyword için TÜM kategorilerdeki ilgili haberleri bul
    print("\n" + "=" * 80)
    print("KEYWORD'LERE GÖRE TÜM HABERLERİ BULMA")
    print("=" * 80)
    
    keyword_news_map = defaultdict(list)
    
    # Tüm kategorilerdeki tüm haberleri tara
    for category, news_list in categorized.items():
        for news in news_list:
            keywords = news.get('scraped_content', {}).get('keywords', [])
            
            for kw in keywords:
                if kw in all_keywords:
                    # Bu haberi keyword listesine ekle (eğer yoksa)
                    news_guid = news.get('guid')
                    if not any(n.get('guid') == news_guid for n in keyword_news_map[kw]):
                        keyword_news_map[kw].append(news)
    
    print(f"\nKeyword bazlı haber eşleştirmeleri:")
    for kw in sorted(keyword_news_map.keys())[:20]:  # İlk 20'sini göster
        print(f"  {kw:30s}: {len(keyword_news_map[kw])} haber")
    
    # Sonuçları hazırla
    result = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'filter_days': 3,
            'major_categories': list(major_categories.keys()),
            'total_selected_news': sum(len(v) for v in selected_news.values()),
            'total_keywords': len(all_keywords),
            'total_keyword_matches': sum(len(v) for v in keyword_news_map.values())
        },
        'selected_news_by_category': selected_news,
        'keywords_by_category': category_keywords,
        'news_by_keyword': dict(keyword_news_map)
    }
    
    # Kaydet
    output_file = 'aa_news_selected_with_keywords.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{output_file} dosyasına kaydedildi")
    
    # Final istatistikler
    print("\n" + "=" * 80)
    print("ÖZET İSTATİSTİKLER")
    print("=" * 80)
    print(f"Seçilen kategori sayısı: {len(selected_news)}")
    print(f"Toplam seçilen haber: {sum(len(v) for v in selected_news.values())}")
    print(f"Toplam benzersiz keyword: {len(all_keywords)}")
    print(f"Keyword'lere göre eşleşen toplam haber: {sum(len(v) for v in keyword_news_map.values())}")
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    filter_and_select_news()