// lib/mobile_platform/widgets/reels/category_reel_feed.dart
// 📱 Category-specific Reels Feed - WRAPPER

import 'package:flutter/material.dart';
import '../../../../mobile_platform/pages/reels_feed_page.dart';
import '../../../core/theme/aa_colors.dart';

/// Kategoriye özel reels göstermek için ReelsFeedPage wrapper'ı
/// Mevcut ReelsFeedPage'i kullanır, sadece kategoriye göre filtreler
class CategoryReelFeed {
  static void navigateTo(
    BuildContext context, {
    required String categoryId,
    required String categoryName,
    required String categoryIcon,
    required Color categoryColor,
  }) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => _CategoryReelWrapper(
          categoryId: categoryId,
          categoryName: categoryName,
          categoryIcon: categoryIcon,
          categoryColor: categoryColor,
        ),
      ),
    );
  }
}

class _CategoryReelWrapper extends StatelessWidget {
  final String categoryId;
  final String categoryName;
  final String categoryIcon;
  final Color categoryColor;

  const _CategoryReelWrapper({
    required this.categoryId,
    required this.categoryName,
    required this.categoryIcon,
    required this.categoryColor,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Mevcut ReelsFeedPage'i kullan
          // TODO: ReelsFeedPage'e categoryFilter parametresi ekle
          const ReelsFeedPage(),

          // Üstte kategori badge (overlay)
          Positioned(
            top: MediaQuery.of(context).padding.top + 8,
            left: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: categoryColor,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(categoryIcon, style: const TextStyle(fontSize: 18)),
                  const SizedBox(width: 8),
                  Text(
                    categoryName,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}