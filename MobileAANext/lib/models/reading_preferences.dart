// lib/models/reading_preferences.dart

import 'package:flutter/material.dart';

/// Okuma ekranı için font boyutu seçenekleri
enum AppFontSize { small, medium, large }

/// Okuma ekranı için font ailesi seçenekleri
enum AppFontFamily { system, serif, sansSerif }

/// Okuma ekranı için satır yüksekliği seçenekleri
enum AppLineHeight { compact, normal, relaxed }

/// Kullanıcının okuma tercihlerini bir arada tutan model sınıfı.
class ReadingPreferences {
  final AppFontSize fontSize;
  final AppFontFamily fontFamily;
  final AppLineHeight lineHeight;

  // Varsayılan ayarlar
  ReadingPreferences({
    this.fontSize = AppFontSize.medium,
    this.fontFamily = AppFontFamily.system,
    this.lineHeight = AppLineHeight.normal,
  });

  /// Mevcut ayarları kopyalayıp sadece istenenleri değiştirerek yeni bir nesne oluşturur.
  ReadingPreferences copyWith({
    AppFontSize? fontSize,
    AppFontFamily? fontFamily,
    AppLineHeight? lineHeight,
  }) {
    return ReadingPreferences(
      fontSize: fontSize ?? this.fontSize,
      fontFamily: fontFamily ?? this.fontFamily,
      lineHeight: lineHeight ?? this.lineHeight,
    );
  }
}