// lib/core/constants/emoji_constants.dart
// Emoji listeleri - Uygulama genelinde kullanılan sabit emoji setleri

/// Emoji kategorileri
class EmojiConstants {
  // ✅ Public Emojiler (Herkes kullanabilir)
  static const List<String> publicEmojis = [
    '👍', // Beğendim
    '❤️', // Sevdim
    '🔥', // Çok iyi
    '⭐', // Harika
    '👏', // Alkış
  ];

  // ✅ Premium Emojiler (Kilitli - ileride premium özellik)
  static const List<String> premiumEmojis = [
    '😍', // Bayıldım
    '🤔', // Düşündürücü
    '😮', // Şaşırdım
    '🎉', // Kutlama
    '💎', // Değerli
  ];

  // ✅ Haber kategorilerine özel emoji setleri (opsiyonel)
  static const Map<String, List<String>> categoryEmojis = {
    'Gündem': ['👍', '😮', '🤔', '❤️', '🔥'],
    'Spor': ['⚽', '🏆', '💪', '🔥', '👏'],
    'Ekonomi': ['💰', '📈', '💼', '🤔', '👍'],
    'Teknoloji': ['💻', '🚀', '⚡', '🔥', '🤖'],
    'Sağlık': ['🏥', '💊', '❤️', '👍', '🙏'],
    'Kültür': ['🎭', '🎨', '📚', '⭐', '👏'],
  };

  // ✅ Tüm emojileri al (public + premium)
  static List<String> get allEmojis => [...publicEmojis, ...premiumEmojis];

  // ✅ Kategoriye göre emoji listesi döndür
  static List<String> getEmojisForCategory(String category) {
    return categoryEmojis[category] ?? publicEmojis;
  }

  // ✅ Emoji validasyonu
  static bool isPublicEmoji(String emoji) {
    return publicEmojis.contains(emoji);
  }

  static bool isPremiumEmoji(String emoji) {
    return premiumEmojis.contains(emoji);
  }

  static bool isValidEmoji(String emoji) {
    return allEmojis.contains(emoji);
  }
}