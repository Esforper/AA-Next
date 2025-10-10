// lib/views/home_view.dart
// AA Haber Ana Sayfa - Haber kartları ve günlük ilerleme

import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../core/utils/platform_utils.dart';
import '../../core/constants/app_constants.dart';
import '../../models/reel_model.dart';
import '../../providers/gamification_provider.dart';
import '../../providers/saved_reels_provider.dart';
import '../../viewmodels/news_home_viewmodel.dart';
import '../../shared/widgets/gamification/daily_progress_card.dart';
import '../../shared/widgets/news_card.dart';
import '../pages/reels_feed_page.dart';

/// Home View - AA Haber Ana Sayfa
/// Günlük ilerleme + Haber kartları (AA.com.tr tarzı)
class HomeView extends StatefulWidget {
  const HomeView({Key? key}) : super(key: key);

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  late NewsHomeViewModel _viewModel;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _viewModel = NewsHomeViewModel();
    _viewModel.loadNews();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _viewModel.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= 
        _scrollController.position.maxScrollExtent - 200) {
      _viewModel.loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _viewModel,
      child: Scaffold(
        backgroundColor: AppColors.background,
        body: RefreshIndicator(
          onRefresh: _viewModel.refresh,
          color: AppColors.primary,
        child: CustomScrollView(
            controller: _scrollController,
          slivers: [
              // Mobil için AppBar
              if (!PlatformUtils.isWeb || 
                  PlatformUtils.getScreenSize(context) == ScreenSize.mobile)
            SliverAppBar(
              floating: true,
              snap: true,
              elevation: 0,
                  backgroundColor: AppColors.primary,
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      '📰',
                      style: TextStyle(fontSize: 20),
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'AA Haber',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                          color: Colors.white,
                    ),
                  ),
                ],
              ),
              actions: [
                Consumer<GamificationProvider>(
                  builder: (context, provider, _) {
                    return Container(
                      margin: const EdgeInsets.only(right: 16),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                            color: AppColors.accent,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                              const Text('⚡', style: TextStyle(fontSize: 16)),
                          const SizedBox(width: 4),
                          Text(
                            'Lv ${provider.currentLevel}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),

            // Content
            SliverToBoxAdapter(
                child: _buildContent(context),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Ana içerik
  Widget _buildContent(BuildContext context) {
    final screenSize = PlatformUtils.getScreenSize(context);
    final isWebWide = PlatformUtils.isWeb && 
                      (screenSize == ScreenSize.desktop || screenSize == ScreenSize.tablet);
    
    return Padding(
      padding: isWebWide 
          ? const EdgeInsets.symmetric(horizontal: 48, vertical: 24)
          : const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
          // Kategori filtresi - Responsive (Mobilde wrap, web'de horizontal scroll)
          Consumer<NewsHomeViewModel>(
            builder: (context, vm, _) {
              final screenSize = PlatformUtils.getScreenSize(context);
              final isMobile = screenSize == ScreenSize.mobile;
              
              // Mobil: Wrap layout (2 satır)
              if (isMobile) {
                return Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: vm.categories.map((category) {
                    final isSelected = vm.selectedCategory == category;
                    return FilterChip(
                      label: Text(category),
                      selected: isSelected,
                      onSelected: (_) => vm.selectCategory(category),
                      backgroundColor: AppColors.surface,
                      selectedColor: AppColors.primary,
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : AppColors.textPrimary,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                      side: BorderSide(
                        color: isSelected ? AppColors.primary : AppColors.border,
                      ),
                    );
                  }).toList(),
                );
              }
              
              // Web: Horizontal scroll
              return SizedBox(
                height: 40,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: vm.categories.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final category = vm.categories[index];
                    final isSelected = vm.selectedCategory == category;
                    
                    return FilterChip(
                      label: Text(category),
                      selected: isSelected,
                      onSelected: (_) => vm.selectCategory(category),
                      backgroundColor: AppColors.surface,
                      selectedColor: AppColors.primary,
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : AppColors.textPrimary,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                      side: BorderSide(
                        color: isSelected ? AppColors.primary : AppColors.border,
                      ),
                    );
                  },
                ),
              );
            },
          ),

                  const SizedBox(height: 24),

          // Haber listesi
          Consumer<NewsHomeViewModel>(
            builder: (context, vm, _) {
              if (vm.isLoading && vm.news.isEmpty) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(48),
                    child: CircularProgressIndicator(),
                  ),
                );
              }

              if (vm.error != null && vm.news.isEmpty) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(48),
                        child: Column(
                          children: [
                        const Icon(Icons.error_outline, size: 64, color: AppColors.error),
                        const SizedBox(height: 16),
                        Text(
                          'Haberler yüklenemedi',
                          style: AppTextStyles.h4,
                            ),
                            const SizedBox(height: 8),
                        Text(
                          vm.error!,
                          style: AppTextStyles.bodySmall,
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: vm.refresh,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Tekrar Dene'),
            ),
          ],
        ),
      ),
    );
  }

              if (vm.isEmpty) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(48),
                    child: Text('Henüz haber yok'),
      ),
    );
  }

              final filteredNews = vm.filteredNews;

              // Responsive grid düzeni
              return _buildNewsGrid(context, filteredNews, isWebWide);
            },
          ),

          // Loading indicator (daha fazla yüklenirken)
          Consumer<NewsHomeViewModel>(
            builder: (context, vm, _) {
              if (vm.isLoading && vm.news.isNotEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              return const SizedBox.shrink();
            },
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  // Haber grid düzeni - Responsive: Web'de küçük, mobilde orta boy kartlar
  Widget _buildNewsGrid(BuildContext context, List<Reel> news, bool isWebWide) {
    final crossAxisCount = isWebWide ? 5 : 2; // Web'de 5 sütun (daha küçük), mobilde 2 sütun
    // Web'de 0.75 = daha küçük kartlar (1/3 oranında küçültülmüş)
    // Mobilde 0.85 = orta boy kartlar
    final aspectRatio = isWebWide ? 0.75 : 0.85;
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: aspectRatio, // 📐 Responsive aspect ratio
      ),
      itemCount: news.length,
      itemBuilder: (context, index) {
        return NewsCard(
          news: news[index],
          onTap: () => _showNewsDetailModal(context, news[index]),
        );
      },
    );
  }

  // Haber detayına git (Reels sayfasına yönlendir)
  void _openNewsDetail(Reel news) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const ReelsFeedPage(),
      ),
    );
  }

  // 🆕 YENİ: Modal detay kartı göster
  void _showNewsDetailModal(BuildContext context, Reel news) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _NewsDetailModal(news: news),
    );
  }
}

// 🆕 YENİ: Detay Modal Widget
class _NewsDetailModal extends StatelessWidget {
  final Reel news;

  const _NewsDetailModal({required this.news});

  @override
  Widget build(BuildContext context) {
    final hasImage = news.imageUrls.isNotEmpty;
    final screenHeight = MediaQuery.of(context).size.height;
    
    return BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5), // 🌫️ Arka plan bulanık
      child: Container(
        height: screenHeight * 0.9,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            // Handle bar
            Container(
              margin: const EdgeInsets.symmetric(vertical: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Üst butonlar (Geri, Paylaş, Beğen)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Geri butonu
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.grey[100],
                    ),
                  ),
                  
                  // Sağ taraf butonlar
                  Row(
                    children: [
                      // Beğen butonu
                      Consumer<SavedReelsProvider>(
                        builder: (context, savedProvider, _) {
                          final isSaved = savedProvider.isSaved(news.id);
                          return IconButton(
                            onPressed: () => _toggleSave(context, news, isSaved),
                            icon: Icon(
                              isSaved ? Icons.bookmark : Icons.bookmark_border,
                              color: isSaved ? AppColors.primary : Colors.grey[700],
                            ),
                            style: IconButton.styleFrom(
                              backgroundColor: Colors.grey[100],
                            ),
                          );
                        },
                      ),
                      const SizedBox(width: 8),
                      // Paylaş butonu
                      IconButton(
                        onPressed: () => _shareNews(news),
                        icon: const Icon(Icons.share),
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.grey[100],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // İçerik
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Resim
                    if (hasImage)
                      ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: CachedNetworkImage(
                          imageUrl: news.imageUrls.first,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          placeholder: (context, url) => Container(
                            height: 250,
                            color: AppColors.surfaceVariant,
                            child: const Center(
                              child: CircularProgressIndicator(),
                            ),
                          ),
                          errorWidget: (context, url, error) => Container(
                            height: 250,
                            color: AppColors.surfaceVariant,
                            child: const Icon(Icons.image_not_supported, size: 64),
                          ),
                        ),
                      ),
                    
                    const SizedBox(height: 20),
                    
                    // Kategori ve zaman
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: AppColors.primary,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            news.category.toUpperCase(),
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          _formatTime(news.publishedAt),
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Başlık
                    Text(
                      news.title,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                        height: 1.3,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Özet
                    Text(
                      news.summary,
                      style: const TextStyle(
                        fontSize: 16,
                        color: AppColors.textSecondary,
                        height: 1.6,
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Tam içerik
                    if (news.fullContent.isNotEmpty)
                      ...news.fullContent.map((paragraph) => Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Text(
                          paragraph,
                          style: const TextStyle(
                            fontSize: 15,
                            color: AppColors.textPrimary,
                            height: 1.7,
                          ),
                        ),
                      )),
                    
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _toggleSave(BuildContext context, Reel news, bool isSaved) {
    final savedProvider = context.read<SavedReelsProvider>();
    
    if (isSaved) {
      savedProvider.unsaveReel(news.id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Kaydedilenlerden çıkarıldı'),
          duration: Duration(seconds: 2),
        ),
      );
    } else {
      savedProvider.saveReel(
        reelId: news.id,
        title: news.title,
        imageUrl: news.imageUrls.isNotEmpty ? news.imageUrls.first : '',
        content: news.fullContent.join('\n\n'),
      );
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Kaydedilenlere eklendi 💾'),
          duration: Duration(seconds: 2),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  void _shareNews(Reel news) {
    Share.share(
      '${news.title}\n\n${news.summary}\n\nAA Haber uygulamasından paylaşıldı.',
      subject: news.title,
    );
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes} dk önce';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} saat önce';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} gün önce';
    } else {
      return '${dateTime.day}.${dateTime.month}.${dateTime.year}';
    }
  }
}

