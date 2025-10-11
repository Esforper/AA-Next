// lib/core/theme/aa_colors.dart
// 🎨 Anadolu Ajansı Resmi Renk Paleti

import 'package:flutter/material.dart';

class AAColors {
  AAColors._(); // Private constructor
  
  // ============ ANA RENKLER ============
  static const Color aaRed = Color(0xFFE30613);        // AA Logo Kırmızı
  static const Color aaNavy = Color(0xFF003D82);       // AA Logo Lacivert
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF1A1A1A);
  
  // ============ YARDIMCI RENKLER ============
  static const Color redLight = Color(0xFFFF2D3B);     // Hover/Active
  static const Color redDark = Color(0xFFC00510);      // Pressed
  static const Color navyMid = Color(0xFF0052AD);      // Secondary actions
  static const Color navyLight = Color(0xFF1E5FA8);
  
  // ============ GRİ TONLARI ============
  static const Color grey50 = Color(0xFFFAFAFA);       // Background
  static const Color grey100 = Color(0xFFF5F5F5);      // Card background
  static const Color grey200 = Color(0xFFEEEEEE);
  static const Color grey300 = Color(0xFFE0E0E0);      // Borders
  static const Color grey400 = Color(0xFFBDBDBD);
  static const Color grey500 = Color(0xFF9E9E9E);      // Secondary text
  static const Color grey700 = Color(0xFF616161);
  static const Color grey900 = Color(0xFF212121);
  
  // ============ STREAK COLORS (GitHub style) ============
  static const Color streakNone = Color(0xFFEBEDF0);   // Aktivite yok
  static const Color streakLow = Color(0xFFFFCDD2);    // 100-199 XP (açık kırmızı)
  static const Color streakMed = Color(0xFFEF5350);    // 200-299 XP (orta kırmızı)
  static const Color streakHigh = Color(0xFFE30613);   // 300+ XP (AA kırmızı)
  
  // ============ KATEGORİ RENKLERİ ============
  static const Color catGuncel = Color(0xFFE30613);    // Güncel - Kırmızı
  static const Color catEkonomi = Color(0xFF0052AD);   // Ekonomi - Mavi
  static const Color catSpor = Color(0xFF00C853);      // Spor - Yeşil
  static const Color catTeknoloji = Color(0xFF6200EA); // Teknoloji - Mor
  static const Color catKultur = Color(0xFFFF6D00);    // Kültür - Turuncu
  static const Color catDunya = Color(0xFF00B8D4);     // Dünya - Cyan
  static const Color catPolitika = Color(0xFF003D82);  // Politika - Lacivert
  static const Color catSaglik = Color(0xFF00E676);    // Sağlık - Açık yeşil
  
  // ============ SEMANTIC COLORS ============
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  // ============ GRADIENTS ============
  static const LinearGradient redGradient = LinearGradient(
    colors: [aaRed, redLight],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient navyGradient = LinearGradient(
    colors: [aaNavy, navyMid],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // ============ SHADOWS ============
  static List<BoxShadow> cardShadow = [
    BoxShadow(
      color: black.withOpacity(0.08),
      blurRadius: 12,
      offset: const Offset(0, 4),
    ),
  ];
  
  static List<BoxShadow> buttonShadow = [
    BoxShadow(
      color: aaRed.withOpacity(0.3),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];
}