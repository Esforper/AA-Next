// lib/core/constants/breakpoints.dart
// Responsive breakpoint değerleri ve yardımcı fonksiyonlar

import 'package:flutter/material.dart';

/// Cihaz tipi
enum DeviceType {
  mobile,
  tablet,
  desktop,
}

/// Responsive breakpoint değerleri
class Breakpoints {
  // Breakpoint değerleri (piksel)
  static const double mobile = 600;
  static const double tablet = 1024;
  static const double desktop = 1440;
  static const double largeDesktop = 1920;
  
  /// Mevcut ekran genişliğine göre cihaz tipini döndürür
  static DeviceType getDeviceType(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width < mobile) return DeviceType.mobile;
    if (width < tablet) return DeviceType.tablet;
    return DeviceType.desktop;
  }
  
  /// Ekran mobile boyutta mı?
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < mobile;
  }
  
  /// Ekran tablet boyutta mı?
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobile && width < tablet;
  }
  
  /// Ekran desktop boyutta mı?
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= tablet;
  }
  
  /// Ekran large desktop boyutta mı?
  static bool isLargeDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= largeDesktop;
  }
}

/// Responsive değer seçici
class ResponsiveValue<T> {
  final T mobile;
  final T? tablet;
  final T? desktop;
  final T? largeDesktop;
  
  const ResponsiveValue({
    required this.mobile,
    this.tablet,
    this.desktop,
    this.largeDesktop,
  });
  
  /// Mevcut ekran boyutuna göre değer döndürür
  T getValue(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    
    if (width >= Breakpoints.largeDesktop && largeDesktop != null) {
      return largeDesktop!;
    }
    if (width >= Breakpoints.tablet && desktop != null) {
      return desktop!;
    }
    if (width >= Breakpoints.mobile && tablet != null) {
      return tablet!;
    }
    return mobile;
  }
}

/// Grid column sayısı için responsive değerler
class ResponsiveGrid {
  static int getColumns(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 2;
      case DeviceType.tablet:
        return 3;
      case DeviceType.desktop:
        return 4;
    }
  }
  
  static double getCrossAxisSpacing(BuildContext context) {
    return Breakpoints.isDesktop(context) ? 24 : 16;
  }
  
  static double getMainAxisSpacing(BuildContext context) {
    return Breakpoints.isDesktop(context) ? 24 : 16;
  }
}

/// Padding değerleri için responsive değerler
class ResponsivePadding {
  static EdgeInsets getPagePadding(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return const EdgeInsets.all(16);
      case DeviceType.tablet:
        return const EdgeInsets.all(24);
      case DeviceType.desktop:
        return const EdgeInsets.symmetric(horizontal: 48, vertical: 32);
    }
  }
  
  static EdgeInsets getCardPadding(BuildContext context) {
    return Breakpoints.isMobile(context)
        ? const EdgeInsets.all(12)
        : const EdgeInsets.all(16);
  }
  
  static EdgeInsets getHorizontalPadding(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return const EdgeInsets.symmetric(horizontal: 16);
      case DeviceType.tablet:
        return const EdgeInsets.symmetric(horizontal: 32);
      case DeviceType.desktop:
        return const EdgeInsets.symmetric(horizontal: 48);
    }
  }
}

/// Font size için responsive değerler
class ResponsiveFont {
  static double getHeadingSize(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 24;
      case DeviceType.tablet:
        return 28;
      case DeviceType.desktop:
        return 32;
    }
  }
  
  static double getBodySize(BuildContext context) {
    return Breakpoints.isDesktop(context) ? 16 : 14;
  }
  
  static double getScale(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 1.0;
      case DeviceType.tablet:
        return 1.1;
      case DeviceType.desktop:
        return 1.15;
    }
  }
}

/// Widget boyutları için responsive değerler
class ResponsiveSize {
  // Card heights
  static double getCardHeight(BuildContext context) {
    return Breakpoints.isMobile(context) ? 200 : 240;
  }
  
  // Icon sizes
  static double getIconSize(BuildContext context) {
    return Breakpoints.isMobile(context) ? 24 : 28;
  }
  
  // Avatar sizes
  static double getAvatarSize(BuildContext context) {
    final deviceType = Breakpoints.getDeviceType(context);
    
    switch (deviceType) {
      case DeviceType.mobile:
        return 40;
      case DeviceType.tablet:
        return 48;
      case DeviceType.desktop:
        return 56;
    }
  }
  
  // Button heights
  static double getButtonHeight(BuildContext context) {
    return Breakpoints.isMobile(context) ? 48 : 52;
  }
  
  // AppBar heights
  static double getAppBarHeight(BuildContext context) {
    return Breakpoints.isMobile(context) ? 56 : 64;
  }
  
  // Bottom nav height
  static double getBottomNavHeight(BuildContext context) {
    return Breakpoints.isMobile(context) ? 60 : 0; // Web'de bottom nav yok
  }
}

/// Responsive helper extension
extension ResponsiveContext on BuildContext {
  bool get isMobile => Breakpoints.isMobile(this);
  bool get isTablet => Breakpoints.isTablet(this);
  bool get isDesktop => Breakpoints.isDesktop(this);
  bool get isLargeDesktop => Breakpoints.isLargeDesktop(this);
  
  DeviceType get deviceType => Breakpoints.getDeviceType(this);
  
  double get screenWidth => MediaQuery.of(this).size.width;
  double get screenHeight => MediaQuery.of(this).size.height;
  
  EdgeInsets get pagePadding => ResponsivePadding.getPagePadding(this);
  EdgeInsets get cardPadding => ResponsivePadding.getCardPadding(this);
  
  int get gridColumns => ResponsiveGrid.getColumns(this);
  
  double get headingSize => ResponsiveFont.getHeadingSize(this);
  double get bodySize => ResponsiveFont.getBodySize(this);
}