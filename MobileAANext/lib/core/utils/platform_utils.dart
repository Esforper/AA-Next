// lib/core/utils/platform_utils.dart
// Platform tespiti ve responsive breakpoint'ler

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';

/// Platform tipi
enum AppPlatform {
  mobileiOS,
  mobileAndroid,
  web,
  desktop,
}

/// Ekran boyutu kategorileri
enum ScreenSize {
  mobile,    // < 600px
  tablet,    // 600-1024px
  desktop,   // > 1024px
}

class PlatformUtils {
  /// Mevcut platform
  static AppPlatform get currentPlatform {
    if (kIsWeb) return AppPlatform.web;
    return AppPlatform.mobileAndroid; // Default mobile
  }

  /// Web platformunda mıyız?
  static bool get isWeb => kIsWeb;

  /// Mobile platformda mıyız?
  static bool get isMobile => !kIsWeb;

  /// Ekran boyutuna göre kategori
  static ScreenSize getScreenSize(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width < 600) return ScreenSize.mobile;
    if (width < 1024) return ScreenSize.tablet;
    return ScreenSize.desktop;
  }

  /// Responsive değer seçici
  static T responsive<T>(
    BuildContext context, {
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    final size = getScreenSize(context);
    
    switch (size) {
      case ScreenSize.mobile:
        return mobile;
      case ScreenSize.tablet:
        return tablet ?? mobile;
      case ScreenSize.desktop:
        return desktop ?? tablet ?? mobile;
    }
  }

  /// Web için maksimum genişlik limiti
  static double getMaxWidth(BuildContext context) {
    if (!isWeb) return double.infinity;
    
    final screenWidth = MediaQuery.of(context).size.width;
    return screenWidth > 1200 ? 1200 : screenWidth;
  }

  /// Padding değerleri (platform-aware)
  static EdgeInsets getScreenPadding(BuildContext context) {
    final size = getScreenSize(context);
    
    if (isWeb) {
      switch (size) {
        case ScreenSize.mobile:
          return const EdgeInsets.all(16);
        case ScreenSize.tablet:
          return const EdgeInsets.all(24);
        case ScreenSize.desktop:
          return const EdgeInsets.symmetric(horizontal: 48, vertical: 24);
      }
    }
    
    // Mobile için default
    return const EdgeInsets.all(16);
  }

  /// Grid column sayısı (responsive)
  static int getGridColumns(BuildContext context) {
    final size = getScreenSize(context);
    
    switch (size) {
      case ScreenSize.mobile:
        return 2;
      case ScreenSize.tablet:
        return 3;
      case ScreenSize.desktop:
        return 4;
    }
  }

  /// Font scale faktörü
  static double getFontScale(BuildContext context) {
    final size = getScreenSize(context);
    
    if (!isWeb) return 1.0;
    
    switch (size) {
      case ScreenSize.mobile:
        return 1.0;
      case ScreenSize.tablet:
        return 1.1;
      case ScreenSize.desktop:
        return 1.2;
    }
  }
}