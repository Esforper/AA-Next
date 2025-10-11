"""
AA Haberlerini Kategori ve Keyword'lere Göre Seçme
- Her kategoriden 20 haber seç (fazla haberi olan kategorilerden)
- Seçilen haberlerin keyword'lerindeki tüm benzersiz haberleri topla
- Tamamen benzersiz GUID'li haberler oluştur
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
import os

class NewsCategoryKeywordSelector:
    def __init__(self, input_file='aa_news_scraped_last.json', output_file='aa_news_selected_final.json'):
        self.input_file = input_file
        self.output_file = output_file
        self.all_news = []
        self.categorized_news = defaultdict(list)
        self.selected_by_category = {}
        self.keywords_from_selected = set()
        self.news_by_keyword = defaultdict(list)
        self.final_unique_news = {}
        
    def load_news(self):
        """Scraped haberleri yükle"""
        print(f"\n📂 {self.input_file} dosyası yükleniyor...")
        
        if not os.path.exists(self.input_file):
            print(f"❌ HATA: {self.input_file} dosyası bulunamadı!")
            return False
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.all_news = json.load(f)
        
        print(f"✓ {len(self.all_news)} haber yüklendi")
        return True
    
    def extract_category_from_news(self, news):
        """Haberden kategori bilgisini çıkar"""
        # Öncelik sırası:
        # 1. scraped_content içindeki category_full
        # 2. scraped_content içindeki category
        # 3. Ana seviyedeki category
        # 4. URL'den çıkarma
        
        scraped = news.get('scraped_content', {})
        
        # category_full tercih edilir (daha doğru)
        category = scraped.get('category_full')
        if category:
            return category
        
        # Normal category
        category = scraped.get('category') or news.get('category')
        if category:
            return category
        
        # URL'den çıkar
        url = news.get('link') or scraped.get('url', '')
        if '/tr/' in url:
            parts = url.split('/tr/')
            if len(parts) > 1:
                category = parts[1].split('/')[0]
                if category:
                    return category
        
        return 'diger'  # Kategorisiz haberler için
    
    def categorize_all_news(self):
        """Tüm haberleri kategorilere ayır"""
        print("\n📊 Haberler kategorilere ayrılıyor...")
        
        for news in self.all_news:
            category = self.extract_category_from_news(news)
            self.categorized_news[category].append(news)
        
        # Kategori istatistikleri
        print(f"\n{'='*60}")
        print("KATEGORİ DAĞILIMI:")
        print(f"{'='*60}")
        
        sorted_categories = sorted(
            self.categorized_news.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        for category, news_list in sorted_categories:
            count = len(news_list)
            status = "✓" if count >= 20 else "○"
            print(f"{status} {category:20s}: {count:5d} haber")
        
        print(f"{'='*60}")
        print(f"Toplam kategori sayısı: {len(self.categorized_news)}")
        
        
    def select_top_news_per_category(self, select_count=20):
            """Her kategoriden en yeni ve benzersiz 'select_count' kadar haber seçer."""
            print(f"\n🎯 Her kategoriden en yeni ve benzersiz {select_count} haber seçiliyor...")
            
            final_selected_news = {}
            
            # Kategorileri haber sayısına göre sıralayarak işleme alalım (isteğe bağlı ama loglar için güzel)
            sorted_categories = sorted(
                self.categorized_news.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )

            for category, news_list in sorted_categories:
                # 1. Haberleri tarihe göre sırala (en yeni olanlar en başta)
                sorted_by_date = sorted(
                    news_list,
                    key=lambda x: self.get_news_date(x),
                    reverse=True
                )
                
                # 2. GUID bazında tekilleştirme yap
                unique_news = []
                seen_guids = set()
                for news in sorted_by_date:
                    guid = news.get('guid')
                    if guid and guid not in seen_guids:
                        seen_guids.add(guid)
                        unique_news.append(news)
                
                # 3. Belirlenen sayıda haberi seç
                selection = unique_news[:select_count]
                
                if selection: # Eğer kategoride haber varsa ekle
                    final_selected_news[category] = selection
                    print(f"  ✓ {category:25s}: {len(selection):2d} haber seçildi")
            
            # Sonucu sınıfın `selected_by_category` özelliğine atayalım
            self.selected_by_category = final_selected_news        
        
        
        
        
    def select_news_from_major_categories(self, min_news_count=20, select_count=20):
        """Yeterli haberi olan kategorilerden belirli sayıda haber seç"""
        print(f"\n🎯 {min_news_count}+ haberi olan kategorilerden {select_count}'er haber seçiliyor...")
        
        # Yeterli haberi olan kategorileri bul
        major_categories = {
            cat: news_list 
            for cat, news_list in self.categorized_news.items() 
            if len(news_list) >= min_news_count
        }
        
        print(f"✓ {len(major_categories)} kategori kriterleri karşılıyor")
        
        for category, news_list in major_categories.items():
            # Tarihe göre sırala (en yeni önce)
            sorted_news = sorted(
                news_list,
                key=lambda x: self.get_news_date(x),
                reverse=True
            )
            
            # Duplicate kontrolü yap (GUID bazlı)
            unique_news = []
            seen_guids = set()
            
            for news in sorted_news:
                guid = news.get('guid')
                if guid and guid not in seen_guids:
                    seen_guids.add(guid)
                    unique_news.append(news)
                    if len(unique_news) >= select_count:
                        break
            
            self.selected_by_category[category] = unique_news
            print(f"  {category:20s}: {len(unique_news)} haber seçildi")
    
    def get_news_date(self, news):
        """Haberin tarihini datetime objesi olarak al"""
        try:
            # Öncelik sırası
            date_str = (
                news.get('scraped_content', {}).get('published_date') or
                news.get('pubDate') or
                news.get('collected_at') or
                datetime.now().isoformat()
            )
            
            # ISO format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # DD.MM.YYYY format
            if '.' in date_str and len(date_str.split('.')) == 3:
                return datetime.strptime(date_str.split()[0], '%d.%m.%Y')
            
            return datetime.now()
        except:
            return datetime.now()
    
    def extract_keywords_from_selected(self):
        """Seçilen haberlerden keyword'leri çıkar"""
        print("\n🔍 Seçilen haberlerdeki keyword'ler toplanıyor...")
        
        category_keywords = {}
        
        for category, news_list in self.selected_by_category.items():
            keywords_in_category = set()
            
            for news in news_list:
                keywords = news.get('scraped_content', {}).get('keywords', [])
                
                # Generic keyword'leri filtrele
                filtered = [
                    kw for kw in keywords 
                    if kw and kw.lower() not in ['anadolu ajansı', 'aa', '']
                ]
                
                keywords_in_category.update(filtered)
                self.keywords_from_selected.update(filtered)
            
            category_keywords[category] = list(keywords_in_category)
            print(f"  {category:20s}: {len(keywords_in_category)} benzersiz keyword")
        
        print(f"\n✓ Toplam benzersiz keyword: {len(self.keywords_from_selected)}")
        return category_keywords
    
    def find_news_by_keywords(self):
        """Her keyword için TÜM haberleri bul"""
        print("\n🔎 Keyword'lere göre ilgili haberler bulunuyor...")
        
        # Tüm haberleri tara
        for news in self.all_news:
            keywords = news.get('scraped_content', {}).get('keywords', [])
            
            for kw in keywords:
                if kw in self.keywords_from_selected:
                    # Bu haberi keyword listesine ekle
                    self.news_by_keyword[kw].append(news)
        
        # İstatistikler
        keyword_stats = sorted(
            [(kw, len(news_list)) for kw, news_list in self.news_by_keyword.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        print(f"\n📈 En popüler keyword'ler:")
        for kw, count in keyword_stats[:15]:  # İlk 15 keyword
            print(f"  {kw:40s}: {count:3d} haber")
    
    def create_unique_news_collection(self):
            """Tüm seçilen haberleri birleştirerek final koleksiyonu oluşturur."""
            print("\n🔄 Benzersiz haber koleksiyonu oluşturuluyor...")
            
            self.final_unique_news = {}
            
            # Kategorilerden seçilen tüm haberleri topla
            for category, news_list in self.selected_by_category.items():
                for news in news_list:
                    guid = news.get('guid')
                    if guid and guid not in self.final_unique_news:
                        # Habere hangi kategoriden seçildiğini ekleyelim
                        news['_selected_category'] = category
                        self.final_unique_news[guid] = news
            
            total_selected = sum(len(v) for v in self.selected_by_category.values())
            print(f"  Kategori seçimlerinden: {total_selected} haber")
            print(f"\n✓ TOPLAM BENZERSİZ HABER: {len(self.final_unique_news)}")
    
    def generate_statistics(self):
        """Detaylı istatistikler oluştur"""
        stats = {
            'generated_at': datetime.now().isoformat(),
            'input_file': self.input_file,
            'total_input_news': len(self.all_news),
            'categories_found': len(self.categorized_news),
            'categories_selected': len(self.selected_by_category),
            'total_selected_by_category': sum(len(v) for v in self.selected_by_category.values()),
            'unique_keywords': len(self.keywords_from_selected),
            'keyword_matches': sum(len(v) for v in self.news_by_keyword.values()),
            'final_unique_news': len(self.final_unique_news),
            'sources': {
                'from_category_selection': sum(
                    1 for n in self.final_unique_news.values() 
                    if n.get('_source') == 'category_selection'
                ),
                'from_keyword_match': sum(
                    1 for n in self.final_unique_news.values() 
                    if n.get('_source') == 'keyword_match'
                )
            }
        }
        
        # Kategori bazlı dağılım
        category_distribution = defaultdict(int)
        for news in self.final_unique_news.values():
            category = self.extract_category_from_news(news)
            category_distribution[category] += 1
        
        stats['category_distribution'] = dict(category_distribution)
        
        return stats
    
    def save_results(self):
        """Sonuçları JSON'a kaydet"""
        print(f"\n💾 Sonuçlar {self.output_file} dosyasına kaydediliyor...")
        
        # _source ve _matched_keyword gibi geçici alanları temizle
        clean_news = {}
        for guid, news in self.final_unique_news.items():
            clean_news[guid] = {
                k: v for k, v in news.items() 
                if not k.startswith('_')
            }
        
        output_data = {
            'metadata': self.generate_statistics(),
            'selected_news_by_category': {
                cat: [
                    {k: v for k, v in n.items() if not k.startswith('_')} 
                    for n in news_list
                ]
                for cat, news_list in self.selected_by_category.items()
            },
            'news_by_keyword': {
                kw: news_list
                for kw, news_list in self.news_by_keyword.items()
            },
            'all_unique_news': clean_news
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Kaydedildi!")
    
    def print_final_summary(self):
        """Final özet istatistikleri yazdır"""
        stats = self.generate_statistics()
        
        print("\n" + "=" * 60)
        print("ÖZET İSTATİSTİKLER")
        print("=" * 60)
        print(f"Girdi dosyası          : {self.input_file}")
        print(f"Toplam haber (girdi)   : {stats['total_input_news']:,}")
        print(f"Bulunan kategori       : {stats['categories_found']}")
        print(f"Seçilen kategori       : {stats['categories_selected']}")
        print(f"Kategoriden seçilen    : {stats['total_selected_by_category']:,}")
        print(f"Benzersiz keyword      : {stats['unique_keywords']:,}")
        print(f"Keyword eşleşmeleri    : {stats['keyword_matches']:,}")
        print(f"Final benzersiz haber  : {stats['final_unique_news']:,}")
        print("-" * 60)
        print(f"Kategori seçiminden    : {stats['sources']['from_category_selection']:,}")
        print(f"Keyword eşleşmesinden  : {stats['sources']['from_keyword_match']:,}")
        print("=" * 60)
        
        # En çok haber içeren kategoriler
        print("\n📊 Final Kategori Dağılımı (İlk 10):")
        sorted_cats = sorted(
            stats['category_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for cat, count in sorted_cats[:10]:
            print(f"  {cat:20s}: {count:4d} haber")
    
    def run(self):
            """Ana işlem akışı"""
            print("=" * 60)
            print("AA HABERLERİ KATEGORİ VE KEYWORD SEÇİCİ")
            print("=" * 60)
            
            # 1. Haberleri yükle
            if not self.load_news():
                return
            
            # 2. Kategorilere ayır
            self.categorize_all_news()
            
            # 3. HER KATEGORİDEN EN YENİ 20 HABERİ SEÇ (YENİ ADIM)
            self.select_top_news_per_category(select_count=20)
            
            # --- ESKİ ADIMLAR KALDIRILDI ---
            # self.select_news_from_major_categories(min_news_count=20, select_count=20)
            # self.extract_keywords_from_selected()
            # self.find_news_by_keywords()
            # ---------------------------------

            # 4. Benzersiz koleksiyon oluştur (BASİTLEŞTİRİLMİŞ ADIM)
            self.create_unique_news_collection()
            
            # 5. Kaydet
            self.save_results()
            
            # 6. Özet göster
            self.print_final_summary()
            
            print("\n✅ İşlem tamamlandı!")
            print(f"📁 Çıktı dosyası: {self.output_file}")


if __name__ == "__main__":
    # Varsayılan ayarlarla çalıştır
    selector = NewsCategoryKeywordSelector(
        input_file='aa_news_scraped_last.json',
        output_file='aa_news_selected_final.json'
    )
    selector.run()
    
    # Veya özel ayarlarla:
    # selector = NewsCategoryKeywordSelector(
    #     input_file='custom_input.json',
    #     output_file='custom_output.json'
    # )
    # selector.run()