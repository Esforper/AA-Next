// lib/core/theme/web_theme.dart
// Web-specific theme overrides

import 'package:flutter/material.dart';
import '../constants/app_constants.dart';
import 'app_theme.dart';

class WebTheme {
  static ThemeData get theme => AppTheme.theme.copyWith(
    // Web için daha geniş padding'ler
    cardTheme: CardThemeData(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: AppRadius.large),
      color: Colors.white,
      shadowColor: Colors.black.withValues(alpha: 0.05),
    ),
    
    // Web için hover effect'leri
    hoverColor: AppColors.primary.withValues(alpha: 0.05),
    
    // Web için daha büyük butonlar
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: AppRadius.medium),
        textStyle: AppTextStyles.button.copyWith(fontSize: 15),
      ),
    ),
    
    // Web için scrollbar görünümü
    scrollbarTheme: ScrollbarThemeData(
      thumbColor: WidgetStateProperty.all(AppColors.textTertiary.withValues(alpha: 0.3)),
      thickness: WidgetStateProperty.all(8),
      radius: const Radius.circular(4),
    ),
  );
}