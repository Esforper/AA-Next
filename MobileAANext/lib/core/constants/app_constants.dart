// lib/core/constants/app_constants.dart
// Uygulama genelinde kullanılan sabit değerler

import 'package:flutter/material.dart';

/// Renk paleti - AA Sitesi renkleri
class AppColors {
  // Primary colors - AA Mavi
  static const primary = Color(0xFF0078D2); // AA Mavi
  static const primaryDark = Color(0xFF006BB8);
  static const primaryLight = Color(0xFF3D94DC);
  
  // Secondary colors - Koyu gri/mavi
  static const secondary = Color(0xFF36495A); // Koyu gri/mavi
  static const secondaryDark = Color(0xFF2A3844);
  static const secondaryLight = Color(0xFF4A5D70);
  
  // Accent colors - ✅ Mavi tonları (kırmızı yerine)
  static const accent = Color(0xFF0077CC); // ✅ Açık mavi (eski: kırmızı)
  static const accentDark = Color(0xFF005799); // ✅ Orta mavi
  static const accentLight = Color(0xFF3D94DC); // ✅ Açık mavi tonu
  
  // Gamification colors
  static const xpGold = Color(0xFFFBBF24);
  static const streakFire = Color(0xFF0077CC); // ✅ Mavi streak (eski: kırmızı)
  static const levelPurple = Color(0xFF0078D2); // AA Mavi level için
  
  // Neutral colors
  static const background = Color(0xFFFFFFFF); // Beyaz arka plan
  static const surface = Color(0xFFFFFFFF); // Beyaz yüzey
  static const surfaceVariant = Color(0xFF9DA6AB); // Açık gri
  
  // Text colors
  static const textPrimary = Color(0xFF131313); // Siyah/koyu ton
  static const textSecondary = Color(0xFF36495A); // Koyu gri/mavi
  static const textTertiary = Color(0xFF9DA6AB); // Açık gri
  
  // Status colors
  static const success = Color(0xFF10B981);
  static const error = Color(0xFF0077CC); // ✅ Mavi hata rengi (eski: kırmızı)
  static const warning = Color(0xFFF59E0B);
  static const info = Color(0xFF0078D2); // AA Mavi bilgi için
  
  // Borders
  static const border = Color(0xFF9DA6AB); // Açık gri
  static const borderDark = Color(0xFF36495A); // Koyu gri/mavi
  
  // Gradients
  static const primaryGradient = LinearGradient(
    colors: [primary, primaryDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const accentGradient = LinearGradient(
    colors: [accent, accentDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const gamificationGradient = LinearGradient(
    colors: [levelPurple, primary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

/// Spacing değerleri
class AppSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  
  // Sayfa padding'leri
  static const EdgeInsets pagePadding = EdgeInsets.all(md);
  static const EdgeInsets pagePaddingLarge = EdgeInsets.all(lg);
  
  // Card padding'leri
  static const EdgeInsets cardPadding = EdgeInsets.all(md);
  static const EdgeInsets cardPaddingSmall = EdgeInsets.all(sm);
}

/// Border radius değerleri
class AppRadius {
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  
  static const BorderRadius small = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius medium = BorderRadius.all(Radius.circular(md));
  static const BorderRadius large = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius extraLarge = BorderRadius.all(Radius.circular(xl));
  
  static const BorderRadius topLarge = BorderRadius.vertical(
    top: Radius.circular(lg),
  );
}

/// ✅ Text style'ları - Daha okunaklı ve modern
class AppTextStyles {
  // Heading styles - ✅ İyileştirilmiş okunabilirlik
  static const h1 = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    height: 1.3,
    letterSpacing: -0.5,
  );
  
  static const h2 = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    height: 1.3,
    letterSpacing: -0.4,
  );
  
  static const h3 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    height: 1.4,
    letterSpacing: -0.3,
  );
  
  static const h4 = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    height: 1.4,
    letterSpacing: -0.2,
  );
  
  // Body styles - ✅ Daha iyi satır yüksekliği
  static const bodyLarge = TextStyle(
    fontSize: 17,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.6,
    letterSpacing: -0.2,
  );
  
  static const body = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.6,
    letterSpacing: -0.1,
  );
  
  static const bodySmall = TextStyle(
    fontSize: 13,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.5,
    letterSpacing: 0,
  );
  
  // Label styles - ✅ Daha belirgin
  static const label = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    letterSpacing: -0.1,
  );
  
  static const labelSmall = TextStyle(
    fontSize: 13,
    fontWeight: FontWeight.w600,
    color: AppColors.textSecondary,
    letterSpacing: 0,
  );
  
  // Caption - ✅ Daha okunaklı
  static const caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AppColors.textTertiary,
    height: 1.4,
    letterSpacing: 0,
  );
  
  // Button text - ✅ Daha vurgulu
  static const button = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.1,
    height: 1.2,
  );
}

/// Shadow değerleri
class AppShadows {
  static final small = [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];
  
  static final medium = [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];
  
  static final large = [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];
}

/// Animation süreleri
class AppDurations {
  static const fast = Duration(milliseconds: 150);
  static const normal = Duration(milliseconds: 300);
  static const slow = Duration(milliseconds: 500);
}

/// App constants
class AppConstants {
  // App info
  static const String appName = 'AA Haber';
  static const String appVersion = '1.0.0';
  
  // API
  static const int apiTimeout = 30; // seconds
  
  // Pagination
  static const int pageSize = 20;
  static const int initialLoadCount = 10;
  
  // Cache
  static const int maxCacheSize = 100; // MB
  static const int cacheExpiry = 24; // hours
  
  // Gamification
  static const int dailyXPGoal = 100;
  static const int streakBonusXP = 25;
  static const int nodesPerLevel = 10;
  
  // Reels
  static const int minViewDurationForXP = 3000; // ms
  static const int detailReadXP = 50;
  static const int emojiXP = 5;
  
  // Web specific
  static const double webMaxWidth = 1200;
  static const double webSidebarWidth = 260;
  static const double webSidebarCollapsedWidth = 72;
}