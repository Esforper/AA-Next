import json
import re

# AA Kategorileri
AA_CATEGORIES = [
    'Politika', 'Ekonomi', 'Teknoloji', 'Sağlık', 'Spor',
    'Guncel', 'Dünya', 'Kültür Sanat', 'Kültür', 'Bilim',
    'Eğitim', 'Yaşam', 'Çevre', 'Futbol',
    'Türkiye'
]

def parse_description(description):
    """
    Description field'ını parse eder ve sadece parse sonuçlarını döner
    Orijinal habere hiç dokunmaz
    """
    if not description:
        return {
            'parsed_category': None,
            'parsed_subcategory': None,
            'parsed_title': None,
            'parsed_summary': None,
            'parsed_author': None,
            'parsed_published_date': None,
            'parsed_updated_date': None
        }
    
    result = {
        'parsed_category': None,
        'parsed_subcategory': None,
        'parsed_title': None,
        'parsed_summary': None,
        'parsed_author': None,
        'parsed_published_date': None,
        'parsed_updated_date': None
    }
    
    text = description.strip()
    
    # 1. TARİH (en sonda)
    date_pattern = r'(\d{2}\.\d{2}\.\d{4})(?:\s*-\s*Güncelleme\s*:\s*(\d{2}\.\d{2}\.\d{4}))?$'
    date_match = re.search(date_pattern, text)
    
    if date_match:
        result['parsed_published_date'] = date_match.group(1)
        result['parsed_updated_date'] = date_match.group(2)
        text = text[:date_match.start()].strip()
    
    # 2. YAZAR (tarihten önce " |" ile biter)
    author_pattern = r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+){1,3})\s+\|$'
    author_match = re.search(author_pattern, text)
    
    if author_match:
        result['parsed_author'] = author_match.group(1).strip()
        text = text[:author_match.start()].strip()
    
    # 3. KATEGORİ (başta, en uzun eşleşmeyi bul)
    sorted_cats = sorted(AA_CATEGORIES, key=len, reverse=True)
    
    for cat in sorted_cats:
        if text.startswith(cat):
            result['parsed_category'] = cat.lower()
            text = text[len(cat):].strip()
            
            # Alt kategori kontrol et
            if text.startswith(','):
                text = text[1:].strip()
                for subcat in sorted_cats:
                    if text.startswith(subcat):
                        result['parsed_subcategory'] = subcat.lower()
                        text = text[len(subcat):].strip()
                        break
            else:
                for subcat in sorted_cats:
                    if cat != subcat and text.startswith(subcat):
                        result['parsed_subcategory'] = subcat.lower()
                        text = text[len(subcat):].strip()
                        break
            break
    
    # 4. BAŞLIK ve ÖZET (kalan metin)
    if len(text) > 150:
        # Uzun metin - nokta, iki nokta üst üste ile ayır
        potential_breaks = [
            text.find('.', 50, 150),
            text.find(':', 50, 150),
            text.find('?', 50, 150),
        ]
        potential_breaks = [x for x in potential_breaks if x > 0]
        
        if potential_breaks:
            break_point = min(potential_breaks) + 1
            result['parsed_title'] = text[:break_point].strip()
            result['parsed_summary'] = text[break_point:].strip()
        else:
            words = text.split()
            char_count = 0
            title_words = []
            for word in words:
                char_count += len(word) + 1
                if char_count > 150:
                    break
                title_words.append(word)
            result['parsed_title'] = ' '.join(title_words)
            result['parsed_summary'] = ' '.join(words[len(title_words):])
    else:
        result['parsed_title'] = text
        result['parsed_summary'] = None
    
    return result

def main():
    print("=" * 80)
    print("AA HABERLERİ DESCRIPTION PARSE")
    print("=" * 80)
    
    # JSON'u oku
    print("\nJSON dosyası okunuyor...")
    with open('aa_news_scraped_last.json', 'r', encoding='utf-8') as f:
        all_news = json.load(f)
    
    print(f"Toplam {len(all_news)} haber bulundu")
    
    # Her haberin description'ını parse et ve ekle
    print("\nDescription'lar parse ediliyor...")
    
    for i, news in enumerate(all_news, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(all_news)} haber işlendi...")
        
        # Description'ı parse et
        desc = news.get('description', '')
        parsed = parse_description(desc)
        
        # Parse sonuçlarını habere ekle
        news['description_parsed'] = parsed
    
    print(f"\nToplam {len(all_news)} haberin description'ı parse edildi")
    
    # Kaydet
    output_file = 'aa_news_with_parsed_descriptions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\nSonuç '{output_file}' dosyasına kaydedildi")
    
    # İstatistikler
    print("\n" + "=" * 80)
    print("İSTATİSTİKLER")
    print("=" * 80)
    
    categories = {}
    with_author = 0
    with_date = 0
    
    for news in all_news:
        parsed = news['description_parsed']
        
        cat = parsed.get('parsed_category') or 'uncategorized'
        categories[cat] = categories.get(cat, 0) + 1
        
        if parsed.get('parsed_author'):
            with_author += 1
        if parsed.get('parsed_published_date'):
            with_date += 1
    
    print(f"Toplam haber: {len(all_news)}")
    print(f"Parse edilen yazar: {with_author}")
    print(f"Parse edilen tarih: {with_date}")
    
    print("\nParse edilen kategoriler:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {cat}: {count} haber")
    
    print("\n" + "=" * 80)
    print("TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()