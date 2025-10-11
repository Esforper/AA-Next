// lib/web_platform/pages/web_reels_feed_page.dart
// WEB İÇİN PROFESYONEL REELS FEED SAYFASI
// Sol: Görsel | Sağ: Bilgiler

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../providers/reels_provider.dart';
import '../../providers/saved_reels_provider.dart';
import '../../models/reel_model.dart';
import '../../shared/widgets/image_carousel.dart';
import '../../shared/widgets/gamification/reels_xp_overlay.dart';
import '../widgets/web_article_detail_panel.dart';



import '../../services/audio_service.dart';
import '../widgets/web_audio_player.dart';
import '../widgets/web_gamification_sidebar.dart';

class WebReelsFeedPage extends StatefulWidget {
  final int? currentIndex;
  final Function(int)? onNavigate;
  
  const WebReelsFeedPage({
    super.key,
    this.currentIndex,
    this.onNavigate,
  });

  @override
  State<WebReelsFeedPage> createState() => _WebReelsFeedPageState();
}

class _WebReelsFeedPageState extends State<WebReelsFeedPage> {
  int _currentReelIndex = 0;
  int _currentImageIndex = 0;
  bool _showDetailPanel = false;
  
  // Scroll controller
  final ScrollController _scrollController = ScrollController();

@override
void initState() {
  super.initState();
  
  // İlk yükleme
  WidgetsBinding.instance.addPostFrameCallback((_) {
    final provider = context.read<ReelsProvider>();
    provider.loadReels();
    
    // ✅ YENİ: İlk reel'in sesini başlat
    if (provider.reels.isNotEmpty) {
      final audioService = context.read<AudioService>();
      final firstReel = provider.reels[0];
      
      if (firstReel.audioUrl.isNotEmpty) {
        debugPrint('🎵 Auto-starting audio for first reel');
        audioService.play(firstReel.audioUrl, firstReel.id);
      }
    }
  });

  // Infinite scroll listener
  _scrollController.addListener(_onScroll);
}

  void _onScroll() {
    if (_scrollController.position.pixels >= 
        _scrollController.position.maxScrollExtent * 0.8) {
      final provider = context.read<ReelsProvider>();
      if (!provider.isLoadingMore && provider.hasMore) {
        provider.loadMore(); // ✅ loadMoreReels değil, loadMore
      }
    }
  }

  // Klavye navigasyonu
  void _handleKeyPress(RawKeyEvent event) {
    if (event is! RawKeyDownEvent) return;

    final provider = context.read<ReelsProvider>();
    final reelsCount = provider.reels.length;
    if (reelsCount == 0) return;

    final currentReel = provider.reels[_currentReelIndex];

if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
  // Sonraki haber
  if (_currentReelIndex < reelsCount - 1) {
    _onReelChanged(_currentReelIndex + 1); // ✅ setState yerine bu
  }
} else if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
  // Önceki haber
  if (_currentReelIndex > 0) {
    _onReelChanged(_currentReelIndex - 1); // ✅ setState yerine bu
  }
} else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
      // Sonraki resim
      if (_currentImageIndex < currentReel.imageUrls.length - 1) {
        setState(() => _currentImageIndex++);
      }
    } else if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
      // Önceki resim
      if (_currentImageIndex > 0) {
        setState(() => _currentImageIndex--);
      }
    } else if (event.logicalKey == LogicalKeyboardKey.escape) {
      // Detay panelini kapat
      if (_showDetailPanel) {
        setState(() => _showDetailPanel = false);
      }
    }
  }

  void _scrollToCurrentReel() {
    // Smooth scroll animasyonu
    final position = _currentReelIndex * 120.0; // Card height
    _scrollController.animateTo(
      position,
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return RawKeyboardListener(
      focusNode: FocusNode()..requestFocus(),
      onKey: _handleKeyPress,
      child: Scaffold(
        backgroundColor: const Color(0xFFF8F9FA),
        appBar: _buildAppBar(),
        body: Consumer<ReelsProvider>(
          builder: (context, provider, _) {
            // Loading state
            if (provider.status == FeedStatus.loading) {
              return const Center(child: CircularProgressIndicator());
            }

            // Error state
            if (provider.status == FeedStatus.error) {
              return _buildErrorState(provider);
            }

            // Empty state
            if (provider.reels.isEmpty) {
              return const Center(
                child: Text('Henüz haber yok', style: TextStyle(fontSize: 16)),
              );
            }

            // Main content
            return _buildMainContent(provider);
          },
        ),
      ),
    );
  }

  PreferredSizeWidget? _buildAppBar() {
    // ✅ Eğer onNavigate null ise, main.dart'tan AppBar gelir
    // Bu durumda burada AppBar göstermeye gerek yok
    return null;
  }

  Widget _buildErrorState(ReelsProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          const Text('Haberler yüklenirken hata oluştu'),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => provider.loadReels(),
            icon: const Icon(Icons.refresh),
            label: const Text('Tekrar Dene'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF003D82),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

Widget _buildMainContent(ReelsProvider provider) {
  return Stack(
    children: [
      // Ana içerik
      Row(
        children: [
          // SOL: Haber listesi (thumbnail preview)
          _buildReelsList(provider),
          
          // ORTA: Ana görsel ve bilgi paneli
          Expanded(
            child: _buildReelDetailView(provider),
          ),
          
          // SAĞ: Gamification Sidebar
          const WebGamificationSidebar(),
        ],
      ),

      // SAĞ ÜSTTE: Detay paneli (conditional)
      if (_showDetailPanel)
        WebArticleDetailPanel(
          reel: provider.reels[_currentReelIndex],
          onClose: () => setState(() => _showDetailPanel = false),
        ),
    ],
  );
}

Widget _buildReelsList(ReelsProvider provider) {
  return Container(
    width: 280, // 320 → 280 (sidebar için yer açtık)
    decoration: BoxDecoration(
      color: Colors.white,
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.05),
          blurRadius: 10,
          offset: const Offset(2, 0),
        ),
      ],
    ),
      child: ListView.builder(
        controller: _scrollController,
        itemCount: provider.reels.length + (provider.isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          // Loading indicator
          if (index == provider.reels.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ),
            );
          }

          final reel = provider.reels[index];
          final isSelected = index == _currentReelIndex;

          return _buildReelListItem(reel, index, isSelected);
        },
      ),
    );
  }

  Widget _buildReelListItem(Reel reel, int index, bool isSelected) {
  return InkWell(
    onTap: () => _onReelChanged(index), // ✅ Yeni fonksiyon kullan
    child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF003D82).withOpacity(0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? const Color(0xFF003D82) : Colors.transparent,
            width: 2,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Thumbnail
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                reel.imageUrls.first,
                width: 80,
                height: 60,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  width: 80,
                  height: 60,
                  color: Colors.grey[300],
                  child: const Icon(Icons.image, color: Colors.grey),
                ),
              ),
            ),
            const SizedBox(width: 12),
            
            // Başlık
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    reel.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                      color: const Color(0xFF1F2937),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    reel.category.toUpperCase(),
                    style: TextStyle(
                      fontSize: 11,
                      color: isSelected ? const Color(0xFF003D82) : Colors.grey[600],
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

Widget _buildReelDetailView(ReelsProvider provider) {
  if (provider.reels.isEmpty) return const SizedBox();
  
  final reel = provider.reels[_currentReelIndex];

  return Container(
    color: const Color(0xFFF8F9FA),
    child: Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 900), // 1200 → 900 (sidebar için yer)
        padding: const EdgeInsets.all(32),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // SOL: Görsel
                  Expanded(
                    flex: 4,
                    child: _buildImageSection(reel),
                  ),
                  
                  const SizedBox(width: 32),
                  
                  // SAĞ: Bilgiler
                  Expanded(
                    flex: 6,
                    child: _buildInfoSection(reel),
                  ),
                ],
              ),
              
              const SizedBox(height: 32),
              
              // ✅ YENİ: Audio Player (alt kısımda, tam genişlik)
              WebAudioPlayer(reel: reel),
            ],
          ),
        ),
      ),
    ),
  );
}

  Widget _buildImageSection(Reel reel) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Ana görsel
        AspectRatio(
          aspectRatio: 4 / 3,
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: GestureDetector(
                onTap: () {
                  // Resme tıkla → sonraki resim
                  if (_currentImageIndex < reel.imageUrls.length - 1) {
                    setState(() => _currentImageIndex++);
                  } else {
                    setState(() => _currentImageIndex = 0);
                  }
                },
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: Image.network(
                    reel.imageUrls[_currentImageIndex],
                    key: ValueKey(_currentImageIndex),
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      color: Colors.grey[300],
                      child: const Icon(Icons.image, size: 64),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Resim navigasyon butonları
        if (reel.imageUrls.length > 1)
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed: _currentImageIndex > 0
                    ? () => setState(() => _currentImageIndex--)
                    : null,
                icon: const Icon(Icons.arrow_back_ios_rounded),
                color: const Color(0xFF003D82),
              ),
              const SizedBox(width: 16),
              
              // Dot indicators
              ...List.generate(reel.imageUrls.length, (index) {
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: index == _currentImageIndex ? 24 : 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: index == _currentImageIndex
                        ? const Color(0xFF003D82)
                        : Colors.grey[300],
                    borderRadius: BorderRadius.circular(4),
                  ),
                );
              }),
              
              const SizedBox(width: 16),
              IconButton(
                onPressed: _currentImageIndex < reel.imageUrls.length - 1
                    ? () => setState(() => _currentImageIndex++)
                    : null,
                icon: const Icon(Icons.arrow_forward_ios_rounded),
                color: const Color(0xFF003D82),
              ),
            ],
          ),
      ],
    );
  }


void _onReelChanged(int newIndex) {
  if (_currentReelIndex == newIndex) return;
  
  setState(() {
    _currentReelIndex = newIndex;
    _currentImageIndex = 0;
  });
  
  // ✅ Ses değiştir
  final provider = context.read<ReelsProvider>();
  final newReel = provider.reels[newIndex];
  
  if (newReel.audioUrl.isNotEmpty) {
    final audioService = context.read<AudioService>();
    debugPrint('🎵 Changing audio to: ${newReel.id}');
    audioService.play(newReel.audioUrl, newReel.id);
  }
  
  _scrollToCurrentReel();
}


  Widget _buildInfoSection(Reel reel) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Kategori + Tarih
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF003D82).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  reel.category.toUpperCase(),
                  style: const TextStyle(
                    color: Color(0xFF003D82),
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 4),
              Text(
                _formatDate(reel.publishedAt),
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 13,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Başlık
          Text(
            reel.title,
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
              height: 1.3,
              letterSpacing: -0.5,
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Özet
          Text(
            reel.summary,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[700],
              height: 1.6,
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Aksiyon butonları
          Row(
            children: [
              // Devamını Oku butonu
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => setState(() => _showDetailPanel = true),
                  icon: const Icon(Icons.article_outlined),
                  label: const Text('Devamını Oku'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF003D82),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 12),
              
              // Kaydet butonu
              Consumer<SavedReelsProvider>(
                builder: (context, savedProvider, _) {
                  final isSaved = savedProvider.isSaved(reel.id);
                  return IconButton(
                    onPressed: () async {
                      if (isSaved) {
                        savedProvider.unsaveReel(reel.id);
                      } else {
                        savedProvider.saveReel(
                          reelId: reel.id,
                          title: reel.title,
                          imageUrl: reel.imageUrls.first,
                          content: reel.summary,
                        );
                      }
                    },
                    icon: Icon(
                      isSaved ? Icons.bookmark : Icons.bookmark_border,
                      color: const Color(0xFF003D82),
                    ),
                    iconSize: 28,
                    tooltip: isSaved ? 'Kaydedildi' : 'Kaydet',
                  );
                },
              ),
              
              // Paylaş butonu
              IconButton(
                onPressed: () {
                  // Share functionality
                  print('Share: ${reel.title}');
                },
                icon: const Icon(Icons.share_outlined),
                color: const Color(0xFF003D82),
                iconSize: 28,
                tooltip: 'Paylaş',
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    
    if (diff.inMinutes < 60) {
      return '${diff.inMinutes} dakika önce';
    } else if (diff.inHours < 24) {
      return '${diff.inHours} saat önce';
    } else if (diff.inDays < 7) {
      return '${diff.inDays} gün önce';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

@override
void dispose() {
  _scrollController.dispose();
  
  // ✅ YENİ: Ses durdur
  final audioService = context.read<AudioService>();
  audioService.stop();
  
  super.dispose();
}
}