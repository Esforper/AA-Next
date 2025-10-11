import json
import sys

def analyze_news_summaries(file_path):
    """
    Verilen JSON dosyasını analiz eder ve 'summary' alanı boş, null veya
    eksik olan haberleri bulur.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"HATA: '{file_path}' dosyası bulunamadı.")
        return
    except json.JSONDecodeError:
        print(f"HATA: '{file_path}' dosyası geçerli bir JSON formatında değil.")
        return

    all_news = []
    if 'all_unique_news' in data and isinstance(data['all_unique_news'], dict):
        all_news.extend(data['all_unique_news'].values())
    elif 'selected_news_by_category' in data and isinstance(data['selected_news_by_category'], dict):
        for category_news in data['selected_news_by_category'].values():
            all_news.extend(category_news)
    else:
        print("HATA: Desteklenen bir haber yapısı ('all_unique_news' veya 'selected_news_by_category') bulunamadı.")
        return

    if not all_news:
        print("Hiç haber bulunamadı.")
        return

    print(f"Toplam {len(all_news)} haber inceleniyor...\n")

    missing_summary_news = []
    for news in all_news:
        scraped_content = news.get('scraped_content', {})
        if not isinstance(scraped_content, dict):
            scraped_content = {}
            
        summary = scraped_content.get('summary', '')

        if not summary or not summary.strip():
            missing_summary_news.append(news)
            
    if not missing_summary_news:
        print("✓ Tüm haberlerin 'summary' alanı dolu görünüyor.")
    else:
        print(f"🚨 {len(missing_summary_news)} haberde 'summary' alanı boş veya eksik bulundu:\n")
        for i, news in enumerate(missing_summary_news, 1):
            guid = news.get('guid') or 'GUID YOK'
            
            # --- DÜZELTME BURADA ---
            # 'title' None olabileceğinden, 'or' ile yedek bir değer atıyoruz.
            title = news.get('title') or 'Başlık Yok'
            # -----------------------
            
            print(f"{i:3}. GUID: {guid:<10} | Başlık: {title[:70]}...")
            
    print(f"\nAnaliz tamamlandı. Toplam {len(all_news)} haberden {len(missing_summary_news)} tanesinde summary eksik.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        analyze_news_summaries(json_file)
    else:
        print("Kullanım: python check_summaries.py <dosya_adi.json>")
        default_file = 'aa_news_selected_final.json'
        print(f"\nVarsayılan dosya '{default_file}' deneniyor...")
        analyze_news_summaries(default_file)