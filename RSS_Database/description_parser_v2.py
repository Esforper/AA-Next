import re
from datetime import datetime
from typing import Dict, Optional, List

# AA'nın kullandığı sabit kategori listesi
AA_CATEGORIES = [
    'Politika',
    'Ekonomi', 
    'Teknoloji',
    'Sağlık',
    'Spor',
    'Güncel',
    'Dünya',
    'Kültür Sanat',
    'Bilim',
    'Eğitim',
    'Yaşam',
    'Çevre', 
    'turkiye',
    'kultur',
]

def parse_aa_description_advanced(description: str) -> Dict[str, Optional[str]]:
    """
    AA RSS feed description'ını parse eder
    
    Format: [Kategori][Başlık][Özet][Yazar][Tarih]
    
    Örnekler:
    - "PolitikaBakan Memişoğlu: Şehir hastanelerimiz...Başak Akbulut Yazar  |17.05.2025"
    - "Spor,BasketbolKadın basketbolunda 46. sezon...Salih Ulaş Şahan  |03.10.2025"
    
    Returns:
        dict: Tüm parse edilmiş metadata
    """
    
    if not description:
        return None
    
    result = {
        'category': None,
        'subcategory': None,
        'title': None,
        'summary': None,
        'author': None,
        'published_date': None,
        'updated_date': None,
        'raw_description': description
    }
    
    working_text = description.strip()
    
    # 1. TARİH - En sonda (DD.MM.YYYY formatında)
    date_pattern = r'(\d{2}\.\d{2}\.\d{4})(?:\s*-\s*Güncelleme\s*:\s*(\d{2}\.\d{2}\.\d{4}))?$'
    date_match = re.search(date_pattern, working_text)
    
    if date_match:
        result['published_date'] = date_match.group(1)
        result['updated_date'] = date_match.group(2)
        working_text = working_text[:date_match.start()].strip()
    
    # 2. YAZAR - Tarihten önce, " |" ile biter
    # Türkçe karakterlere izin ver, 2-3 kelimelik isimler
    author_pattern = r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+){1,3})\s+\|$'
    author_match = re.search(author_pattern, working_text)
    
    if author_match:
        result['author'] = author_match.group(1).strip()
        working_text = working_text[:author_match.start()].strip()
    
    # 3. KATEGORİ - Sabit listeden eşleştirme
    # En uzun kategoriyi önce kontrol et (örn: "Kültür Sanat" önce, "Kültür" sonra)
    sorted_categories = sorted(AA_CATEGORIES, key=len, reverse=True)
    
    category_found = None
    subcategory_found = None
    
    for cat in sorted_categories:
        # Kategori başta mı kontrol et
        if working_text.startswith(cat):
            category_found = cat
            working_text = working_text[len(cat):].strip()
            
            # Alt kategori var mı kontrol et (virgül veya başka kategori)
            # Örnek: "Spor,Basketbol" veya "SporBasketbol"
            if working_text.startswith(','):
                working_text = working_text[1:].strip()
                # Virgülden sonra başka kategori varsa alt kategori
                for subcat in sorted_categories:
                    if working_text.startswith(subcat):
                        subcategory_found = subcat
                        working_text = working_text[len(subcat):].strip()
                        break
            else:
                # Virgül yoksa, direkt başka kategori olabilir
                for subcat in sorted_categories:
                    if subcat != category_found and working_text.startswith(subcat):
                        subcategory_found = subcat
                        working_text = working_text[len(subcat):].strip()
                        break
            
            break
    
    result['category'] = category_found.lower() if category_found else None
    result['subcategory'] = subcategory_found.lower() if subcategory_found else None
    
    # 4. BAŞLIK ve ÖZET
    # Kalan metin: Başlık + Özet
    # Başlık: Genellikle büyük harfle başlar, kısa bir ifade
    # Özet: Büyük harfle devam eder, daha uzun açıklama
    
    # Strateji: İki büyük harfli cümle varsa, ilki başlık, ikincisi özet
    # Pattern: Büyük harfle başlayan cümleler
    
    # Büyük harfle başlayan kısımları bul
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])', working_text)
    
    if len(sentences) >= 2:
        # İlk cümle başlık, geri kalanı özet
        result['title'] = sentences[0].strip()
        result['summary'] = ' '.join(sentences[1:]).strip()
    elif len(sentences) == 1:
        # Tek cümle varsa, büyük harfli ilk kısmı başlık yap
        # Eğer çok uzunsa (150+ karakter), bir yerde kes
        text = sentences[0]
        
        # Uzun mu kontrol et
        if len(text) > 150:
            # İlk 150 karakterde nokta, soru işareti veya iki nokta üst üste varsa kes
            potential_breaks = [
                text.find('.', 50, 150),
                text.find(':', 50, 150),
                text.find('?', 50, 150),
            ]
            potential_breaks = [x for x in potential_breaks if x > 0]
            
            if potential_breaks:
                break_point = min(potential_breaks) + 1
                result['title'] = text[:break_point].strip()
                result['summary'] = text[break_point:].strip()
            else:
                # Kelime sınırında kes (150. karaktere yakın)
                words = text.split()
                char_count = 0
                title_words = []
                
                for word in words:
                    char_count += len(word) + 1
                    if char_count > 150:
                        break
                    title_words.append(word)
                
                result['title'] = ' '.join(title_words)
                result['summary'] = ' '.join(words[len(title_words):])
        else:
            result['title'] = text.strip()
    else:
        result['title'] = working_text.strip()
    
    return result


def extract_metadata_from_news(news_item: dict) -> dict:
    """
    Tam bir news item'dan metadata çıkarır
    
    Öncelik sırası:
    1. scraped_content içindeki veriler (en güvenilir)
    2. URL'den parse
    3. Description'dan parse
    4. Üst seviye fields
    """
    
    result = {
        'category': None,
        'subcategory': None,
        'title': None,
        'summary': None,
        'author': None,
        'published_date': None,
        'updated_date': None,
        'url': None,
        'images': [],
        'keywords': [],
        'paragraphs': []
    }
    
    # 1. Scraped content'ten al (en güvenilir)
    scraped = news_item.get('scraped_content', {})
    
    result['title'] = scraped.get('full_title') or news_item.get('title')
    result['summary'] = scraped.get('summary')
    result['author'] = scraped.get('author')
    result['images'] = scraped.get('images', [])
    result['keywords'] = scraped.get('keywords', [])
    result['paragraphs'] = scraped.get('paragraphs', [])
    
    # 2. URL
    result['url'] = news_item.get('link')
    
    # 3. URL'den kategori parse et
    url = news_item.get('link', '')
    if '/tr/' in url:
        parts = url.split('/tr/')
        if len(parts) > 1:
            url_category = parts[1].split('/')[0]
            result['category'] = url_category
    
    # 4. Tarih bilgisi
    result['published_date'] = news_item.get('pubDate') or news_item.get('collected_at')
    
    # 5. Description'dan eksik bilgileri tamamla
    desc = news_item.get('description', '')
    if desc:
        parsed_desc = parse_aa_description_advanced(desc)
        
        # Kategori - description'dakini URL'den olanla kombine et
        if not result['category'] and parsed_desc.get('category'):
            result['category'] = parsed_desc.get('category')
        
        # Alt kategori sadece description'dan gelir
        if parsed_desc.get('subcategory'):
            result['subcategory'] = parsed_desc.get('subcategory')
        
        # Yazar
        if not result['author'] and parsed_desc.get('author'):
            result['author'] = parsed_desc.get('author')
        
        # Summary eğer scraped'de boşsa description'dan al
        if not result['summary'] and parsed_desc.get('summary'):
            result['summary'] = parsed_desc.get('summary')
        
        # Tarih bilgisi description'dan daha detaylı olabilir
        if parsed_desc.get('published_date'):
            result['published_date'] = parsed_desc.get('published_date')
        if parsed_desc.get('updated_date'):
            result['updated_date'] = parsed_desc.get('updated_date')
    
    # 6. image field'ını kontrol et
    if not result['images']:
        img = news_item.get('image', '')
        if img:
            result['images'] = [img]
    
    return result


def test_parser():
    """Test cases"""
    
    test_cases = [
        {
            'name': 'Politika - Normal',
            'text': "PolitikaBakan Memişoğlu: Şehir hastanelerimiz, birer bilim ve teknoloji üssü haline gelmiştirSağlık Bakanı Kemal Memişoğlu, bugün Türkiye'nin dünyanın en gelişmiş sağlık altyapısına sahip ülkelerinden biri olduğunu belirterek, \"Sağlık alanında pek çok temel göstergede dünya ortalamasının üzerine çıkılmıştır.\" dedi.Başak Akbulut Yazar  |17.05.2025 - Güncelleme : 17.05.2025"
        },
        {
            'name': 'Spor - Alt kategori virgüllü',
            'text': "Spor,BasketbolKadın basketbolunda 46. sezon başlıyorHalkbank Kadınlar Basketbol Süper Ligi'nde 46. sezon bugün oynanacak maçlarla başlayacak.Salih Ulaş Şahan  |03.10.2025 - Güncelleme : 04.10.2025"
        },
        {
            'name': 'Ekonomi - Normal',
            'text': "EkonomiTCMB Başkanı Karahan: Sıkı para politikası duruşumuzu sürdüreceğizTürkiye Cumhuriyet Merkez Bankası (TCMB) Başkanı Fatih Karahan, sıkı para politikası duruşunun enflasyonda kalıcı düşüş ve fiyat istikrarı sağlanana kadar süreceğini belirtti.Uğur Aslanhan  |10.05.2025 - Güncelleme : 11.05.2025"
        },
        {
            'name': 'Teknoloji - Uzun başlık',
            'text': "TeknolojiTürkiye ve ABD'de keşfedilen 6 sülük türü dünya bilim literatürüne kazandırıldıTürk ve Amerikalı bilim insanları tarafından yapılan saha ve laboratuvar çalışmaları sonucu keşfedilen 6 sülük türü, dünya literatürüne kazandırıldı.İsmail Şen  |02.05.2025 - Güncelleme : 02.05.2025"
        },
        {
            'name': 'Sağlık - Normal',
            'text': "SağlıkSülük salgısıyla iltihaplı ve otoimmün hastalıklarda alternatif tedaviTürk bilim insanları tıbbi sülük salgısındaki doğal bileşenlerin biyoteknolojik ilaç adayı olarak kullanılabilmesine yönelik çalışmada başarılı sonuçlar elde etti.Zeynep Rakipoğlu  |17.02.2025 - Güncelleme : 17.02.2025"
        }
    ]
    
    print("=" * 100)
    print("AA DESCRIPTION PARSER TEST")
    print("=" * 100)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*100}")
        print(f"RAW: {test['text'][:80]}...\n")
        
        result = parse_aa_description_advanced(test['text'])
        
        print(f"📁 Kategori: {result['category']}")
        print(f"📁 Alt Kategori: {result['subcategory']}")
        print(f"📰 Başlık: {result['title']}")
        print(f"📝 Özet: {result['summary'][:80] if result['summary'] else None}...")
        print(f"✍️  Yazar: {result['author']}")
        print(f"📅 Yayın Tarihi: {result['published_date']}")
        print(f"🔄 Güncelleme: {result['updated_date']}")


def test_full_extraction():
    """Gerçek news item testi"""
    
    sample = {
        "guid": "3706901",
        "title": "Sağlık Bakanı Memişoğlu: DSÖ İşbirliği Merkezi'nin Türkiye'de açılması için resmi süreci başlattık",
        "link": "https://www.aa.com.tr/tr/saglik/saglik-bakani-memisoglu-dso-isbirligi-merkezinin-turkiyede-acilmasi-icin-resmi-sureci-baslattik/3706901",
        "description": "SağlıkSağlık Bakanı Memişoğlu: DSÖ İşbirliği Merkezi'nin Türkiye'de açılması için resmi süreci başlattıkSağlık Bakanı Kemal Memişoğlu, \"DSÖ ile yürüttüğümüz görüşmeler sonucunda, GETAT alanında bir DSÖ İşbirliği Merkezi'nin Türkiye'de açılması için resmi süreci başlattık.\" dedi.Hikmet Faruk Başer  |03.10.2025 - Güncelleme : 03.10.2025",
        "pubDate": "03.10.2025",
        "category": None,
        "image": "",
        "scraped_content": {
            "url": "https://www.aa.com.tr/tr/saglik/saglik-bakani-memisoglu-dso-isbirligi-merkezinin-turkiyede-acilmasi-icin-resmi-sureci-baslattik/3706901",
            "full_title": "Sağlık Bakanı Memişoğlu: DSÖ İşbirliği Merkezi'nin Türkiye'de açılması için resmi süreci başlattık",
            "summary": "...",
            "keywords": ["3. Geleneksel ve Tamamlayıcı Tıp Kongresi", "Sağlık Bakanı Kemal Memişoğlu"],
            "images": [],
            "author": None
        }
    }
    
    print("\n" + "=" * 100)
    print("FULL NEWS EXTRACTION TEST")
    print("=" * 100)
    
    result = extract_metadata_from_news(sample)
    
    print(f"\n📁 Kategori: {result['category']}")
    print(f"📁 Alt Kategori: {result['subcategory']}")
    print(f"📰 Başlık: {result['title']}")
    print(f"📝 Özet: {result['summary'][:80] if result['summary'] else None}...")
    print(f"✍️  Yazar: {result['author']}")
    print(f"📅 Tarih: {result['published_date']}")
    print(f"🔗 URL: {result['url']}")
    print(f"🖼️  Resimler: {len(result['images'])} adet")
    print(f"🔑 Keywords: {result['keywords']}")


if __name__ == "__main__":
    test_parser()
    print("\n\n")
    test_full_extraction()