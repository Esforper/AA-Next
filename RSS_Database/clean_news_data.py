import json
import os
import argparse
from collections import defaultdict
import copy

def is_news_item_valid(news_item: dict) -> bool:
    """
    Bir haberin geçerli olup olmadığını kontrol eder.
    - Başlığı boş veya null ise geçersizdir.
    - Link'i '/podcast/' içeriyorsa geçersizdir.
    """
    # 'title' anahtarının değeri None olabilir, önce bunu kontrol etmeliyiz.
    title = news_item.get('title')
    if not title or not title.strip():
        return False  # Başlık None, boş veya sadece boşluk karakteri içeriyor

    # Podcast Kontrolü
    link = news_item.get('link', '')
    if '/podcast/' in link:
        return False

    return True

def clean_news_file(input_path: str, output_path: str):
    """
    JSON dosyasını okur, geçersiz haberleri temizler ve yeni bir dosyaya yazar.
    """
    print(f"📂 '{input_path}' dosyası okunuyor...")
    if not os.path.exists(input_path):
        print(f"❌ HATA: Girdi dosyası bulunamadı: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = copy.deepcopy(data)
    
    all_news = data.get('all_unique_news', {})
    if not all_news:
        print("⚠️ 'all_unique_news' içinde haber bulunamadı. İşlem durduruldu.")
        return

    initial_count = len(all_news)
    print(f"🔎 {initial_count} adet benzersiz haber bulundu. Temizleme başlıyor...")
    
    cleaned_unique_news = {}
    removed_guids = set()
    stats = defaultdict(int)

    for guid, news_item in all_news.items():
        if is_news_item_valid(news_item):
            cleaned_unique_news[guid] = news_item
        else:
            removed_guids.add(guid)
            
            # === BURASI TAMAMEN DÜZELTİLDİ ===
            # Hatanın oluştuğu yer burasıydı. 'title' None olabileceği için
            # önce değeri alıp, sonra kontrol ediyoruz.
            title_value = news_item.get('title')
            if not title_value or not title_value.strip():
                stats['basliksiz_silindi'] += 1
            elif '/podcast/' in news_item.get('link', ''):
                stats['podcast_silindi'] += 1
            else:
                stats['diger_nedenle_silindi'] += 1
            # ==================================
    
    cleaned_data['all_unique_news'] = cleaned_unique_news
    
    if 'selected_news_by_category' in cleaned_data:
        cleaned_selection = {}
        for category, news_list in cleaned_data['selected_news_by_category'].items():
            filtered_list = [news for news in news_list if news.get('guid') not in removed_guids]
            if filtered_list:
                cleaned_selection[category] = filtered_list
        cleaned_data['selected_news_by_category'] = cleaned_selection
    
    if 'metadata' in cleaned_data:
        new_total = len(cleaned_unique_news)
        print(f"\n📊 Metadata güncelleniyor...")
        cleaned_data['metadata']['original_total_news'] = initial_count
        cleaned_data['metadata']['final_unique_news'] = new_total
        category_dist = defaultdict(int)
        for news in cleaned_unique_news.values():
            scraped_content = news.get('scraped_content') or {}
            category = scraped_content.get('category') or news.get('category') or 'diger'
            category_dist[category] += 1
        cleaned_data['metadata']['category_distribution'] = dict(category_dist)
        
    print("\n--- Temizleme Raporu ---")
    print(f"Başlangıçtaki haber sayısı : {initial_count}")
    print(f"Başlıksız olduğu için silinen: {stats['basliksiz_silindi']}")
    print(f"Podcast olduğu için silinen  : {stats['podcast_silindi']}")
    print(f"Toplam silinen haber       : {len(removed_guids)}")
    print(f"Kalan haber sayısı         : {len(cleaned_unique_news)}")
    print("--------------------------\n")

    print(f"💾 Temizlenmiş veri '{output_path}' dosyasına kaydediliyor...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"✅ İşlem başarıyla tamamlandı!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AA Haber JSON dosyasını istenmeyen içeriklerden (podcast, başlıksız) temizler."
    )
    parser.add_argument(
        "--input",
        default="aa_news_selected_final.json",
        help="Temizlenecek girdi JSON dosyasının yolu."
    )
    parser.add_argument(
        "--output",
        default="aa_news_cleaned.json",
        help="Temizlenmiş verinin kaydedileceği çıktı JSON dosyasının yolu."
    )
    args = parser.parse_args()

    clean_news_file(args.input, args.output)