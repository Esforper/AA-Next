// lib/services/reading_preferences_service.dart

import 'package:shared_preferences/shared_preferences.dart';
import '../models/reading_preferences.dart';

/// Kullanıcının okuma tercihlerini (font ayarları vb.) cihaza kaydeder ve okur.
/// Singleton pattern ile uygulama genelinde tek bir instance olmasını sağlar.
class ReadingPreferencesService {
  // SharedPreferences için anahtar (key) tanımları
  static const String _fontSizeKey = 'reading_font_size';
  static const String _fontFamilyKey = 'reading_font_family';
  static const String _lineHeightKey = 'reading_line_height';

  // Singleton instance
  ReadingPreferencesService._privateConstructor();
  static final ReadingPreferencesService instance =
      ReadingPreferencesService._privateConstructor();

  /// Kaydedilmiş tercihleri cihazdan yükler.
  /// Eğer daha önce kaydedilmiş bir ayar yoksa, varsayılan değerleri döner.
  Future<ReadingPreferences> loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();

    final fontSizeIndex = prefs.getInt(_fontSizeKey) ?? AppFontSize.medium.index;
    final fontFamilyIndex = prefs.getInt(_fontFamilyKey) ?? AppFontFamily.system.index;
    final lineHeightIndex = prefs.getInt(_lineHeightKey) ?? AppLineHeight.normal.index;

    return ReadingPreferences(
      fontSize: AppFontSize.values[fontSizeIndex],
      fontFamily: AppFontFamily.values[fontFamilyIndex],
      lineHeight: AppLineHeight.values[lineHeightIndex],
    );
  }

  /// Verilen tercihleri cihaza kaydeder.
  Future<void> savePreferences(ReadingPreferences preferences) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setInt(_fontSizeKey, preferences.fontSize.index);
    await prefs.setInt(_fontFamilyKey, preferences.fontFamily.index);
    await prefs.setInt(_lineHeightKey, preferences.lineHeight.index);
  }
}