"""
🔥 Streak Mockup Data Generator
Kullanıcı email'ine göre gerçekçi 90 günlük aktivite verisi oluşturur
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, date
import random

# Path ayarları
SCRIPT_DIR = Path(__file__).parent  # src/scripts/
SRC_DIR = SCRIPT_DIR.parent  # src/
BACKEND_DIR = SRC_DIR.parent  # BackendAPIDemo/ ✅ BU DOĞRU BACKEND ROOT

# ✅ Backend config'deki storage_base_path = "outputs"
STORAGE_DIR = BACKEND_DIR / "outputs"  # outputs/ klasörü (backend default)
USERS_FILE = BACKEND_DIR / "storage" / "users" / "users.json"  # users ayrı yerde
DATA_DIR = STORAGE_DIR / "gamification"  # outputs/gamification/
STREAK_DIR = BACKEND_DIR / "data" / "streaks"

# Dizinleri oluştur
DATA_DIR.mkdir(parents=True, exist_ok=True)
STREAK_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("🔥 STREAK MOCKUP DATA GENERATOR")
print("=" * 60)
print(f"\n📂 Çalışma Dizinleri:")
print(f"   ├─ Script: {SCRIPT_DIR}")
print(f"   ├─ Backend: {BACKEND_DIR}")
print(f"   ├─ Storage: {STORAGE_DIR}")
print(f"   └─ Users: {USERS_FILE}")
print()

# ============ KULLANICI PROFİLLERİ ============

PROFILES = {
    "aktif": {
        "name": "Aktif Kullanıcı",
        "desc": "Hemen her gün giriş yapar, yüksek XP kazanır",
        "daily_activity_chance": 0.90,  # %90 günlerde aktif
        "xp_range": (150, 400),
        "streak_breaks": 1,  # Kaç kere streak kırılır
    },
    "orta": {
        "name": "Orta Düzey Kullanıcı", 
        "desc": "Haftada 4-5 gün aktif, orta XP",
        "daily_activity_chance": 0.60,
        "xp_range": (100, 250),
        "streak_breaks": 2,
    },
    "yeni": {
        "name": "Yeni Kullanıcı",
        "desc": "Son 2 haftadır aktif, tutarlı değil",
        "daily_activity_chance": 0.40,
        "xp_range": (50, 180),
        "streak_breaks": 3,
    },
}


# ============ USER LOOKUP ============

def find_user_by_email(email: str) -> dict | None:
    """Email'e göre kullanıcıyı bul"""
    
    if not USERS_FILE.exists():
        print(f"❌ Kullanıcı veritabanı bulunamadı: {USERS_FILE}")
        print(f"   Beklenen konum: {USERS_FILE.absolute()}")
        return None
    
    print(f"📂 Kullanıcı dosyası okunuyor: {USERS_FILE}")
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        # ✅ Direkt liste formatı (yeni yapı)
        if isinstance(users_data, list):
            user_list = users_data
            print(f"   └─ Format: Direkt liste")
        # Eski format: {"users": [...]}
        elif isinstance(users_data, dict) and 'users' in users_data:
            user_list = users_data['users']
            print(f"   └─ Format: Dict wrapper")
        else:
            print(f"❌ Beklenmeyen format: {type(users_data)}")
            return None
        
        print(f"   └─ Toplam {len(user_list)} kullanıcı bulundu")
        
        # Email arama
        for user in user_list:
            if user.get('email', '').lower() == email.lower():
                return user
        
        return None
        
    except Exception as e:
        print(f"❌ Dosya okuma hatası: {e}")
        return None


# ============ XP HISTORY GENERATOR ============

def generate_xp_history(user_id: str, profile_type: str, days: int = 90):
    """Gerçekçi XP history oluştur"""
    profile = PROFILES[profile_type]
    
    print(f"\n📊 Profil: {profile['name']}")
    print(f"   └─ {profile['desc']}")
    print(f"\n⏳ Son {days} gün için veri oluşturuluyor...\n")
    
    xp_history = []
    today = date.today()
    
    # Streak kırılma günleri belirle
    break_days = set()
    if profile['streak_breaks'] > 0:
        break_intervals = days // (profile['streak_breaks'] + 1)
        for i in range(1, profile['streak_breaks'] + 1):
            break_day = break_intervals * i
            # 2-3 gün boşluk bırak
            for j in range(random.randint(2, 3)):
                break_days.add(break_day + j)
    
    total_xp = 0
    active_days = 0
    
    # Geriye doğru tarihler oluştur
    for i in range(days - 1, -1, -1):
        target_date = today - timedelta(days=i)
        
        # Bu gün aktif mi?
        is_active = random.random() < profile['daily_activity_chance']
        is_break_day = i in break_days
        
        if is_active and not is_break_day:
            # XP kazanımı oluştur
            daily_xp = random.randint(*profile['xp_range'])
            
            # Reel izleme (10 XP/reel)
            reels_watched = daily_xp // 10
            for _ in range(reels_watched):
                xp_history.append({
                    'timestamp': (datetime.combine(target_date, datetime.min.time()) + 
                                timedelta(hours=random.randint(8, 22), 
                                        minutes=random.randint(0, 59))).isoformat(),
                    'xp_amount': 10,
                    'source': 'reel_watch',
                    'metadata': {'reel_id': f'reel_{random.randint(1000, 9999)}'},
                    'total_xp_after': 0  # Sonra hesaplanacak
                })
                total_xp += 10
            
            # Emoji verme (5 XP, bazı reellerde)
            emojis_given = random.randint(1, min(3, reels_watched))
            for _ in range(emojis_given):
                xp_history.append({
                    'timestamp': (datetime.combine(target_date, datetime.min.time()) + 
                                timedelta(hours=random.randint(8, 22), 
                                        minutes=random.randint(0, 59))).isoformat(),
                    'xp_amount': 5,
                    'source': 'emoji_given',
                    'metadata': {},
                    'total_xp_after': 0
                })
                total_xp += 5
            
            # Detay okuma (15 XP, bazı reellerde)
            details_read = random.randint(0, min(2, reels_watched))
            for _ in range(details_read):
                xp_history.append({
                    'timestamp': (datetime.combine(target_date, datetime.min.time()) + 
                                timedelta(hours=random.randint(8, 22), 
                                        minutes=random.randint(0, 59))).isoformat(),
                    'xp_amount': 15,
                    'source': 'detail_read',
                    'metadata': {},
                    'total_xp_after': 0
                })
                total_xp += 15
            
            active_days += 1
            print(f"  ✅ {target_date.isoformat()}: {daily_xp} XP")
        else:
            print(f"  ⚪ {target_date.isoformat()}: Aktivite yok")
    
    # total_xp_after değerlerini güncelle
    cumulative_xp = 0
    for entry in sorted(xp_history, key=lambda x: x['timestamp']):
        cumulative_xp += entry['xp_amount']
        entry['total_xp_after'] = cumulative_xp
    
    print(f"\n📈 Özet:")
    print(f"   ├─ Toplam XP: {total_xp}")
    print(f"   ├─ Aktif gün: {active_days}/{days}")
    print(f"   └─ XP kayıt sayısı: {len(xp_history)}")
    
    return xp_history, total_xp


# ============ LEVEL CALCULATION ============

def calculate_level_from_xp(total_xp: int) -> tuple[int, int, int]:
    """Total XP'den level, node, current_xp hesapla"""
    
    def get_nodes_in_level(level: int) -> int:
        """Her levelda kaç node var"""
        tier = level // 5
        return min(2 + (tier * 2), 10)
    
    current_level = 0
    current_node = 0
    remaining_xp = total_xp
    
    while True:
        nodes_in_level = get_nodes_in_level(current_level)
        xp_for_this_level = nodes_in_level * 100
        
        if remaining_xp >= xp_for_this_level:
            # Level tamamlandı
            remaining_xp -= xp_for_this_level
            current_level += 1
            current_node = 0
        else:
            # Bu level içinde
            current_node = remaining_xp // 100
            current_xp = remaining_xp % 100
            return current_level, current_node, current_xp
    

# ============ STREAK CALCULATION ============

def calculate_streak(xp_history: list) -> tuple[int, str | None]:
    """XP history'den streak hesapla"""
    if not xp_history:
        return 0, None
    
    # Günlere göre XP grupla
    daily_xp = {}
    for entry in xp_history:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        date_str = entry_date.isoformat()
        daily_xp[date_str] = daily_xp.get(date_str, 0) + entry['xp_amount']
    
    # Bugünden geriye streak say
    today = date.today()
    current_streak = 0
    last_activity = None
    
    for i in range(100):  # Max 100 gün geriye
        check_date = today - timedelta(days=i)
        date_str = check_date.isoformat()
        
        if date_str in daily_xp and daily_xp[date_str] >= 100:
            # Minimum karşılandı
            current_streak += 1
            if last_activity is None:
                last_activity = date_str
        else:
            # Streak kırıldı
            break
    
    return current_streak, last_activity


# ============ SAVE DATA ============

def save_gamification_data(user_id: str, xp_history: list, total_xp: int):
    """Gamification data'yı kaydet"""
    
    gamification_file = DATA_DIR / "user_gamification.json"
    
    print(f"\n💾 Gamification dosyası: {gamification_file}")
    print(f"   └─ Tam yol: {gamification_file.absolute()}")
    
    # Mevcut data'yı oku
    if gamification_file.exists():
        print(f"   ├─ Mevcut dosya okunuyor...")
        with open(gamification_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        print(f"   └─ {len(all_data)} kullanıcı mevcut")
    else:
        print(f"   └─ Yeni dosya oluşturuluyor...")
        all_data = {}
    
    # Level hesapla
    level, node, current_xp = calculate_level_from_xp(total_xp)
    
    # Streak hesapla
    streak, last_activity = calculate_streak(xp_history)
    
    # User data oluştur
    user_data = {
        'user_id': user_id,
        'total_xp': total_xp,
        'current_level': level,
        'current_node': node,
        'current_xp': current_xp,
        'current_streak': streak,
        'last_activity_date': last_activity,
        'daily_xp_goal': 300,
        'xp_earned_today': 0,
        'reels_watched_today': 0,
        'emojis_given_today': 0,
        'details_read_today': 0,
        'shares_given_today': 0,
        'xp_history': xp_history,
        'level_history': [],
        'unlocked_achievements': [],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }
    
    # Kaydet
    all_data[user_id] = user_data
    
    with open(gamification_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Data kaydedildi!")
    print(f"   ├─ Kullanıcı ID: {user_id[:16]}...")
    print(f"   ├─ Level: {level}")
    print(f"   ├─ Node: {node}/{2 + (level // 5) * 2}")
    print(f"   ├─ Current XP: {current_xp}/100")
    print(f"   ├─ Streak: {streak} gün")
    print(f"   └─ Toplam kayıt: {len(all_data)} kullanıcı")


# ============ MAIN ============

def main():
    # Email sor
    print("📧 Kullanıcı email'ini girin:")
    email = input("   └─> ").strip()
    
    if not email:
        print("❌ Email boş olamaz!")
        sys.exit(1)
    
    print()
    
    # Kullanıcıyı bul
    print(f"🔍 Kullanıcı aranıyor: {email}")
    user = find_user_by_email(email)
    
    if not user:
        print(f"❌ Kullanıcı bulunamadı: {email}")
        print("\n💡 İpucu: Önce register endpoint'ini kullanarak kullanıcı oluşturun")
        sys.exit(1)
    
    user_id = user.get('id')
    username = user.get('username', 'Unknown')
    
    print(f"✅ Kullanıcı bulundu!")
    print(f"   ├─ ID: {user_id}")
    print(f"   └─ Username: {username}")
    
    # Profil seç
    print("\n📋 Profil Seçin:")
    for i, (key, profile) in enumerate(PROFILES.items(), 1):
        print(f"   {i}. {profile['name']} - {profile['desc']}")
    
    try:
        choice = int(input("\n   └─> Seçim (1-3): ").strip())
        profile_key = list(PROFILES.keys())[choice - 1]
    except (ValueError, IndexError):
        print("❌ Geçersiz seçim!")
        sys.exit(1)
    
    # Gün sayısı sor
    print("\n📅 Kaç günlük veri oluşturulsun?")
    try:
        days = int(input("   └─> (varsayılan: 90): ").strip() or "90")
    except ValueError:
        days = 90
    
    # Data oluştur
    print("\n" + "=" * 60)
    xp_history, total_xp = generate_xp_history(user_id, profile_key, days)
    
    # Kaydet
    print("\n" + "=" * 60)
    save_gamification_data(user_id, xp_history, total_xp)
    
    print("\n" + "=" * 60)
    print("✅ İŞLEM TAMAMLANDI!")
    print("=" * 60)
    print("\n📂 Kaydedilen dosyalar:")
    print(f"   └─ {DATA_DIR / 'user_gamification.json'}")
    print("\n🚀 Test için:")
    print(f"   GET http://localhost:8000/api/gamification/stats/{user_id}")
    print(f"   GET http://localhost:8000/api/gamification/streak/{user_id}")
    print("\n💡 Frontend'de test etmek için:")
    print(f"   1. Backend'i başlat: python -m uvicorn src.main:app --reload")
    print(f"   2. Mobile app'i aç ve login ol")
    print(f"   3. Ana sayfada streak takvimini gör!")
    print()


if __name__ == "__main__":
    main()