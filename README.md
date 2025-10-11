<div align="center">

# 📰 AA Next - Akıllı Haber Deneyimi

<img src="https://img.shields.io/badge/Flutter-3.35.6-02569B?style=for-the-badge&logo=flutter&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/React-18.0-61DAFB?style=for-the-badge&logo=react&logoColor=black" />

**Modern, Gamified ve AI Destekli Haber Platformu**

*Anadolu Ajansı haberlerini kısa, ilgi çekici reels formatında keşfedin*

[Özellikler](#-özellikler) • [Teknolojiler](#-teknoloji-stack) • [Kurulum](#-kurulum) • [Ekran Görüntüleri](#-ekran-görüntüleri)

</div>

---

## ✨ Özellikler

### 🎮 Gamification Sistemi - Level Up!

**AA Next**'i kullanan her dakika deneyim puanı (XP) kazanın!

- **📊 Dinamik Level Sistemi**
  - 100+ seviye ile sonsuz ilerleme
  - Her düğüm 100 XP (Level 1-5: 2 düğüm, Level 6-10: 4 düğüm, vs.)
  - Gerçek zamanlı XP animasyonları ve level atlama kutlamaları
  
- **🔥 Streak (Seri) Sistemi**
  - Günlük hedef: 300 XP
  - Streak koruyan kullanıcılar için özel rozetler
  - Kullanıcıların %95'inden iyi olun! (30+ gün streak)

- **🎯 XP Kazanma Yolları**
  ```
  📱 Reel İzle (3+ saniye)     → +10 XP
  😊 Emoji Reaksiyonu Ver      → +5 XP
  📖 Detaylı Okuma (10+ saniye) → +50 XP
  🔗 Paylaş                     → +10 XP
  ```

- **🏆 Görsel İlerleme**
  - Zincir tabanlı level gösterimi
  - Günlük progress bar
  - Floating XP animasyonları

---

### 📱 Reels Sistemi - TikTok Tarzı Haber Deneyimi

Haberleri **kısa, eğlenceli ve akıcı** formatta tüketin!

- **🎬 Akıcı Swipe Deneyimi**
  - Dikey scroll ile haber keşfi
  - Otomatik oynatma ve sesli anlatım
  - Alt yazı desteği (kaydırılabilir)

- **🎙️ AI Destekli TTS (Text-to-Speech)**
  - OpenAI TTS entegrasyonu
  - 6 farklı ses seçeneği (Alloy, Echo, Fable, Nova, Onyx, Shimmer)
  - Doğal Türkçe telaffuz

- **🤖 Kişiselleştirilmiş Feed**
  - AI tabanlı öneri algoritması
  - İzleme geçmişinize göre öneriler
  - Kategori bazlı filtreleme (Ekonomi, Spor, Teknoloji, vb.)

- **💬 Etkileşimli Özellikler**
  - Emoji reaksiyonları (6 farklı emoji)
  - Paylaşım butonu
  - Kaydetme özelliği
  - Detaylı okuma modu

---

### 🎯 Responsive & Modern UI

**Her cihazda mükemmel deneyim**

- **📱 Mobil Optimizasyonu**
  - iOS ve Android desteği
  - Hızlı performans (cached images)
  - Offline mode desteği

- **🖥️ Web Desteği**
  - Responsive grid düzeni
  - Desktop için optimize edilmiş kartlar
  - Chrome, Firefox, Safari uyumlu

- **🎨 Modern Tasarım**
  - AA Mavi teması (#0078D2)
  - Glassmorphism efektleri
  - Smooth animasyonlar
  - Dark mode ready

---

### 🎲 Multiplayer Quiz Oyunları

**Arkadaşlarınızla yarışın!**

- **⚔️ Gerçek Zamanlı Multiplayer**
  - WebSocket tabanlı canlı oyun
  - Matchmaking sistemi
  - 2-4 oyuncu desteği

- **📚 Haber Bilgi Yarışması**
  - Güncel haberlerden sorular
  - 4 seçenekli sorular
  - Zamanlayıcı ile heyecan

- **🏅 Sıralama ve Rozetler**
  - Oyun geçmişi
  - Kazanma istatistikleri
  - Arkadaş sıralaması

---

### 👥 Sosyal Özellikler

- **👫 Arkadaş Sistemi**
  - Arkadaş ekleme/çıkarma
  - Friend requests
  - Arkadaş aktivitelerini görme

- **💬 Paylaşım**
  - Haberleri sosyal medyada paylaşın
  - Doğrudan link paylaşımı
  - Screenshot alma

---

### 🔐 Güvenlik & Auth

- **🔒 JWT Token Tabanlı Kimlik Doğrulama**
  - Güvenli login/register
  - Token refresh mekanizması
  - Bcrypt password hashing

- **👤 Profil Yönetimi**
  - Avatar desteği
  - Bio ve kullanıcı bilgileri
  - İstatistikler ve başarılar

---

## 🛠️ Teknoloji Stack

### Frontend

<table>
<tr>
<td width="50%">

**📱 Mobile App (Flutter)**
- Flutter 3.35.6
- Provider (State Management)
- MVVM Architecture
- Cached Network Images
- Audio Players
- WebSocket Support

</td>
<td width="50%">

**🌐 Web App (React)**
- React 18.0
- TypeScript
- Tailwind CSS
- React Router
- Axios HTTP Client
- MSW (Mock Service Worker)

</td>
</tr>
</table>

### Backend

**🐍 FastAPI Backend**
- Python 3.13
- FastAPI (Async)
- Pydantic Models
- JWT Authentication
- WebSocket Support
- OpenAI Integration

**📰 News Processing**
- RSS Feed Scraper (AA.com.tr)
- Beautiful Soup Parsing
- AI Text Summarization
- TTS Audio Generation
- JSON Storage

### Database & Storage

- JSON File Storage (Lightweight)
- Shared Preferences (Mobile)
- Flutter Secure Storage
- Local Caching

---

## 🚀 Kurulum

### Gereksinimler

- **Flutter SDK**: 3.35.6+
- **Python**: 3.13+
- **Node.js**: 18.0+ (Web için)
- **OpenAI API Key**: TTS için gerekli

### 1️⃣ Backend Kurulumu

```bash
# Backend klasörüne git
cd BackendAPIDemo

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyası oluştur
cp .env.example .env
# OPENAI_API_KEY'i ekle

# API'yi başlat
python main.py api
# → http://localhost:8000/docs
```

### 2️⃣ Mobile App Kurulumu

```bash
# Flutter uygulamasına git
cd MobileAANext

# Bağımlılıkları yükle
flutter pub get

# .env dosyası oluştur
echo "API_URL=http://localhost:8000" > .env
echo "BACKEND_PORT=8000" >> .env

# Uygulamayı çalıştır
flutter run -d chrome  # Web için
flutter run -d <device>  # Mobil için
```

### 3️⃣ Web App Kurulumu (Opsiyonel)

```bash
# React uygulamasına git
cd web_aa_next

# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm start
# → http://localhost:3000
```

### 4️⃣ Haber Feed'i Oluşturma

```bash
cd BackendAPIDemo

# RSS'den 50 haber çek ve TTS oluştur
python main.py batch --category guncel --count 50 --voice alloy

# Farklı kategoriler için
python main.py batch --category ekonomi --count 20 --voice nova
python main.py batch --category spor --count 20 --voice shimmer
```

---

## 📱 Ekran Görüntüleri

<table>
<tr>
<td width="33%">

### 🏠 Ana Sayfa
<img src="https://via.placeholder.com/300x600/0078D2/FFFFFF?text=Haber+Grid" alt="Ana Sayfa" />

*Responsive haber kartları ve kategori filtreleme*

</td>
<td width="33%">

### 📱 Reels Feed
<img src="https://via.placeholder.com/300x600/C30019/FFFFFF?text=Reels+Feed" alt="Reels" />

*TikTok tarzı dikey scroll haber deneyimi*

</td>
<td width="33%">

### 🎮 Gamification
<img src="https://via.placeholder.com/300x600/FBBf24/000000?text=Level+Progress" alt="Level" />

*Level zinciri ve günlük ilerleme*

</td>
</tr>
</table>

---

## 📂 Proje Yapısı

```
AA-Next/
│
├── 📱 MobileAANext/          # Flutter Mobil/Web App
│   ├── lib/
│   │   ├── core/             # Tema, constants, utils
│   │   ├── models/           # Data models
│   │   ├── viewmodels/       # MVVM ViewModels
│   │   ├── providers/        # State management
│   │   ├── services/         # API, Auth services
│   │   ├── mobile_platform/  # Mobil UI
│   │   └── shared/           # Shared widgets
│   └── pubspec.yaml
│
├── 🐍 BackendAPIDemo/        # FastAPI Backend
│   ├── src/
│   │   ├── api/             # REST endpoints
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   └── providers/       # External APIs
│   ├── outputs/             # Generated content
│   │   └── reels_data/      # Audio files
│   └── main.py
│
├── 🌐 web_aa_next/          # React Web App
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── viewmodels/      # Business logic
│   │   ├── api/             # API clients
│   │   └── views/           # Pages
│   └── package.json
│
├── 📰 RSS_Database/         # News Scraper
│   ├── aa_rss_bot.py       # RSS feed scraper
│   ├── aa_scraper.py       # Content parser
│   └── generate_tts_for_reels.py
│
└── 📊 Dashboard_AA_Next/   # Admin Dashboard
    ├── dashboard.py        # Flask dashboard
    └── templates/          # HTML templates
```

---

## 🎯 Kullanım Senaryoları

### 📚 Günlük Haber Okuma

```
1. Uygulamayı açın
2. Ana sayfada kategori seçin (Ekonomi, Spor, vb.)
3. İlginizi çeken haberin kartına tıklayın
4. Detaylı okuma için modal açılır
5. +50 XP kazanın! 🎉
```

### 🎬 Reels Keşfi

```
1. Alt menüden "Reels" sekmesine gidin
2. Yukarı kaydırarak haberleri keşfedin
3. Emoji ile reaksiyon verin (+5 XP)
4. Beğendiğinizi kaydedin
5. Detaylı okumak için tıklayın (+50 XP)
```

### 🎮 Oyun Oynama

```
1. "Oyunlar" sekmesine gidin
2. "Hızlı Oyun" ile rastgele eşleşin
3. Soruları cevaplayın (15 saniye süre)
4. Sonuçları görün ve XP kazanın!
```

---

## 🔥 Öne Çıkan Özellikler

### 🚀 Performans

- ⚡ **Hızlı Yükleme**: Cached images ile anında görüntü
- 📦 **Offline Mode**: Okunmuş haberlere offline erişim
- 🎯 **Lazy Loading**: İhtiyaç anında yükleme
- 🔄 **Smooth Animations**: 60 FPS akıcılık

### 🎨 Tasarım Detayları

- 🌈 **AA Mavi Teması**: Profesyonel ve tanıdık
- 💫 **Glassmorphism**: Modern cam efekti
- 🎭 **Micro-interactions**: Butona bastığınızda hissediyorsunuz
- 📱 **Bottom Sheets**: Mobil-first tasarım

### 🤖 AI & Akıllı Özellikler

- 🧠 **Personalization Engine**: İlgi alanlarınızı öğrenir
- 📊 **Analytics**: Okuma alışkanlıklarınızı analiz eder
- 🎯 **Smart Feed**: Size özel haber önerileri
- 🔮 **Predictive Loading**: Sonraki haberi önceden yükler

---

## 🎮 XP Sistemi Detayları

### XP Kaynakları

| Aktivite | XP | Açıklama |
|----------|-----|----------|
| 📱 Reel İzleme | +10 XP | 3+ saniye izleme |
| 😊 Emoji Reaksiyonu | +5 XP | Her reel için 1 kez |
| 📖 Detaylı Okuma | +50 XP | 10+ saniye okuma |
| 🔗 Paylaşım | +10 XP | Sosyal medyada paylaş |
| 🎮 Oyun Kazanma | +100 XP | Multiplayer quiz |
| 🔥 Streak Bonusu | +25 XP | Günlük hedef tutturma |

### Level Formülü

```
Level 1-5:    2 düğüm  (200 XP/level)
Level 6-10:   4 düğüm  (400 XP/level)
Level 11-15:  6 düğüm  (600 XP/level)
Level 16-20:  8 düğüm  (800 XP/level)
Level 20+:   10 düğüm (1000 XP/level)
```

**Örnek İlerleme:**
- Level 1 → 2: 200 XP (2 düğüm × 100 XP)
- Level 5 → 6: 200 XP son, sonra 400 XP'lik level
- Level 10 → 11: 400 XP son, sonra 600 XP'lik level

---

## 🌟 Gelecek Özellikler (Roadmap)

- [ ] 📲 Push Notifications (Breaking news)
- [ ] 🌙 Dark Mode
- [ ] 📊 Gelişmiş Analytics Dashboard
- [ ] 🎙️ Podcast Modu (Uzun format)
- [ ] 📝 Kullanıcı Yorumları
- [ ] 🏆 Global Leaderboard
- [ ] 💎 Premium Özellikler
- [ ] 🌍 Çoklu Dil Desteği
- [ ] 📱 Widget Desteği

---

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak isterseniz:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 📞 İletişim & Destek

- 📧 Email: [support@aanext.com](mailto:support@aanext.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourrepo/AA-Next/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourrepo/AA-Next/discussions)

---

## 🙏 Teşekkürler

- **Anadolu Ajansı** - Haber kaynağı için
- **OpenAI** - TTS servisi için
- **Flutter Team** - Harika framework için
- **Tüm Katkıda Bulunanlar** ❤️

---

<div align="center">

### ⭐ Projeyi Beğendiyseniz Yıldız Vermeyi Unutmayın!

**AA Next ile haberleri keşfetmenin yeni yolunu deneyimleyin** 🚀

[🏠 Ana Sayfa](#-aa-next---akıllı-haber-deneyimi) • [📱 İndir](#-kurulum) • [🤝 Katkıda Bulun](#-katkıda-bulunma)

---

Made with ❤️ and ☕

*"Haberler hiç bu kadar eğlenceli olmamıştı!"*

</div>
