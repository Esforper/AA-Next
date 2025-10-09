// lib/pages/reels_feed_page.dart
// ESKİ ARAYÜZ + YENİ İNFİNİTE SCROLL
import '../services/audio_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import '../widgets/article_reader_sheet.dart'; 
import '../providers/reels_provider.dart';
import '../providers/saved_reels_provider.dart';
import '../providers/gamification_provider.dart';
import '../models/reel_model.dart';
import '../widgets/image_carousel.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../widgets/gamification/reels_xp_overlay.dart';
import '../widgets/gamification/floating_xp.dart';
import '../widgets/subtitle_widget.dart';

class ReelsFeedPage extends StatefulWidget {
  const ReelsFeedPage({super.key});

  @override
  State<ReelsFeedPage> createState() => _ReelsFeedPageState();
}

class _ReelsFeedPageState extends State<ReelsFeedPage> with WidgetsBindingObserver {
  DateTime? _reelStartTime;
  bool _hasEarnedWatchXP = false;
  String? _currentReelId;
  bool _subtitlesEnabled = true;
  
  // 🆕 PageController
  late PageController _pageController;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _pageController = PageController();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ReelsProvider>();
      if (provider.reels.isNotEmpty && !_isInitialized) {
        _isInitialized = true;
        _startReelTracking(provider.current!.id);
        final audioService = context.read<AudioService>();
        final firstReel = provider.current!;
        if (firstReel.audioUrl.isNotEmpty) {
          audioService.play(firstReel.audioUrl, firstReel.id);
        }
      }
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final audioService = context.read<AudioService>();
    if (state == AppLifecycleState.paused) {
      if (!audioService.isPlaying) {
        audioService.resume();
      }
    }
  }

  void _startReelTracking(String reelId) {
    _reelStartTime = DateTime.now();
    _hasEarnedWatchXP = false;
    _currentReelId = reelId;
  }

  void _onPageChanged(int index) {
    final reelsProvider = context.read<ReelsProvider>();
    final audioService = context.read<AudioService>();
    
    if (!_hasEarnedWatchXP && _reelStartTime != null && _currentReelId != null) {
      final duration = DateTime.now().difference(_reelStartTime!);
      if (duration.inSeconds >= 3) {
        final gamificationProvider = context.read<GamificationProvider>();
        gamificationProvider.onReelWatched(_currentReelId!);
        _showFloatingXP(10, 'reel_watched');
        _hasEarnedWatchXP = true;
      }
    }

    reelsProvider.setIndex(index);
    
    if (reelsProvider.current != null) {
      final reel = reelsProvider.current!;
      _startReelTracking(reel.id);
      
      if (reel.audioUrl.isNotEmpty) {
        audioService.play(reel.audioUrl, reel.id);
      } else {
        audioService.stop();
      }
    }
  }

  void _showFloatingXP(int amount, String source) {
    FloatingXPOverlay.show(
      context,
      xpAmount: amount,
      source: source,
      position: Offset(
        MediaQuery.of(context).size.width / 2 - 60,
        MediaQuery.of(context).size.height / 2 - 100,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ReelsProvider>();

    if (provider.status == FeedStatus.initial) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final p = context.read<ReelsProvider>();
        if (p.status == FeedStatus.initial) {
          p.loadReels();
        }
      });
    }

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Reels', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: Icon(
              _subtitlesEnabled ? Icons.closed_caption : Icons.closed_caption_disabled,
              color: Colors.white,
            ),
            onPressed: () => setState(() => _subtitlesEnabled = !_subtitlesEnabled),
            tooltip: _subtitlesEnabled ? 'Alt yazıları gizle' : 'Alt yazıları göster',
          ),
        ],
      ),
      body: Stack(
        children: [
          _buildBody(context, provider),

          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(child: ReelsXPOverlay()),
          ),

          Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: ReadHandle(
                threshold: 35,
                onAction: (action) {
                  final reels = provider.reels;
                  if (reels.isEmpty) return;
                  final reel = reels[provider.currentIndex];

                  switch (action) {
                    case HandleAction.up:
                      _openArticle(context, reel);
                      break;
                    case HandleAction.right:
                      _openEmojis(context, reel);
                      break;
                    case HandleAction.down:
                      _onShareTap(context, reel);
                      break;
                    case HandleAction.left:
                      _saveReel(context, reel);
                      break;
                    case HandleAction.none:
                      break;
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context, ReelsProvider provider) {
    switch (provider.status) {
      case FeedStatus.initial:
      case FeedStatus.loading:
        return const Center(child: CircularProgressIndicator());

      case FeedStatus.error:
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text('Yükleme hatası'),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => context.read<ReelsProvider>().loadReels(),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        );

      case FeedStatus.loaded:
      case FeedStatus.loadingMore:
        final reels = provider.reels;
        if (reels.isEmpty) {
          return const Center(child: Text('Gösterilecek içerik yok.'));
        }

        return RefreshIndicator(
          onRefresh: () => provider.refresh(),
          child: Stack(
            children: [
              PageView.builder(
                controller: _pageController,
                scrollDirection: Axis.vertical,
                onPageChanged: _onPageChanged,
                itemCount: reels.length,
                itemBuilder: (context, index) {
                  final reel = reels[index];
                  return _buildReelItem(reel);
                },
              ),

              // 🆕 Loading indicator
              if (provider.status == FeedStatus.loadingMore)
                Positioned(
                  bottom: 80,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                          SizedBox(width: 8),
                          Text('Daha fazla yükleniyor...', style: TextStyle(color: Colors.white, fontSize: 12)),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
    }
  }

  // ✅ ESKİ TASARIM KORUNDU
  Widget _buildReelItem(Reel reel) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // ✅ ESKİ: Görsel (top: 0, bottom: 160)
        Positioned.fill(
          top: 0,
          bottom: 160,
          child: Center(
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: ClipRect(
                child: SizedBox.expand(
                  child: ImageCarousel(urls: reel.imageUrls),
                ),
              ),
            ),
          ),
        ),

        // ✅ ESKİ: Alt yazı (bottom: 240)
        if (_subtitlesEnabled && reel.subtitles != null && reel.subtitles!.isNotEmpty)
          Positioned(
            left: 0,
            right: 0,
            bottom: 240,
            child: Consumer<AudioService>(
              builder: (context, audioService, _) {
                return SubtitleWidget(
                  subtitles: reel.subtitles!,
                  currentPosition: audioService.position,
                  isVisible: _subtitlesEnabled,
                );
              },
            ),
          ),

        // ✅ ESKİ: Başlık ve özet (bottom: 10)
        Positioned(
          left: 0,
          right: 0,
          bottom: 10,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withOpacity(0.8),
                  Colors.transparent,
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                // ✅ ESKİ: Sarı kutu başlık
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Text(
                    reel.title,
                    maxLines: 4,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                      height: 1.2,
                    ),
                  ),
                ),
                const SizedBox(height: 120),
                // ✅ ESKİ: Özet
                Text(
                  reel.summary,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    height: 1.4,
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.95),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _openArticle(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ArticleReaderSheet(
        articleId: reel.id,
        title: reel.title,
        body: reel.fullText,
        imageUrls: reel.imageUrls,
        category: reel.category,
        onClose: () => Navigator.pop(context),
        onBookmark: () => _saveReel(context, reel),
        onShare: () => _onShareTap(context, reel),
      ),
    );
  }

  void _openEmojis(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => EmojiPanel(
        publicEmojis: const ['👍', '❤️', '🔥', '⭐', '👏'],
        premiumEmojis: const ['😍', '🤔', '😮', '🎉', '💎'],
        onPick: (emoji) {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('$emoji emoji gönderildi!')),
          );
        },
        onTapPremium: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Premium emojiler şimdilik kilitli.')),
          );
        },
      ),
    );
  }

  void _onShareTap(BuildContext context, Reel reel) {
    Share.share(
      '${reel.title}\n\n${reel.summary}\n\nDaha fazlası için AANext uygulamasını indir!',
      subject: reel.title,
    );
  }

  void _saveReel(BuildContext context, Reel reel) {
    context.read<SavedReelsProvider>().saveReel(
      reelId: reel.id,
      title: reel.title,
      content: reel.summary,
      imageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls.first : '',
    );
    
    if (!context.mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.bookmark_added, color: Colors.white),
              SizedBox(width: 8),
              Text('Haber kaydedildi!'),
            ],
          ),
          backgroundColor: Colors.green[700],
          duration: const Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _pageController.dispose();
    FloatingXPOverlay.remove();
    super.dispose();
  }
}


// 6️⃣ _ReelView CLASS'I TAMAMEN DEĞİŞSİN (satır 485 civarı)
class _ReelView extends StatelessWidget {
  final Reel reel;
  final bool subtitlesEnabled;
  // ❌ KALDIRILAN: final dynamic audioService;

  const _ReelView({
    required this.reel,
    required this.subtitlesEnabled,
    // ❌ KALDIRILAN: required this.audioService,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // GÖRSEL
        Positioned.fill(
          top: 0,
          bottom: 160,
          child: Center(
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: ClipRect(
                child: SizedBox.expand(
                  child: ImageCarousel(urls: reel.imageUrls),
                ),
              ),
            ),
          ),
        ),

        // ALT YAZI (Ses ile senkronize)
        if (reel.subtitles != null && reel.subtitles!.isNotEmpty && subtitlesEnabled)
          Positioned(
            left: 0,
            right: 0,
            bottom: 240,
            // ❌ KALDIRILAN: AnimatedBuilder(animation: audioService,...)
            // ✅ YENİ: Consumer kullan
            child: Consumer<AudioService>(
              builder: (context, audioService, _) {
                return SubtitleWidget(
                  subtitles: reel.subtitles!,
                  currentPosition: audioService.position,
                  isVisible: subtitlesEnabled,
                );
              },
            ),
          ),

        // Başlık ve özet (değişmedi, aynı kalacak)
        Positioned(
          left: 0,
          right: 0,
          bottom: 10,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withOpacity(0.8),
                  Colors.transparent,
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Text(
                    reel.title,
                    maxLines: 4,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                      height: 1.2,
                    ),
                  ),
                ),
                const SizedBox(height: 120),
                Text(
                  reel.summary,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    height: 1.4,
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.95),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}


String? _getCategoryFromReel(Reel reel) {
  // Reel modelinde category zaten var
  return reel.category;
}



/// Okuma süresini hesapla (kelime sayısından)
int _calculateReadingTime(String text) {
  // Ortalama okuma hızı: 200 kelime/dakika
  final wordCount = text.split(' ').length;
  final minutes = (wordCount / 200).ceil();
  return minutes < 1 ? 1 : minutes;
}


/// Yayın tarihini formatla
String? _formatPublishedDate(Reel reel) {
  // Reel modelinde publishedAt var
  final now = DateTime.now();
  final diff = now.difference(reel.publishedAt);
  
  if (diff.inMinutes < 60) {
    return '${diff.inMinutes} dakika önce';
  } else if (diff.inHours < 24) {
    return '${diff.inHours} saat önce';
  } else if (diff.inDays < 7) {
    return '${diff.inDays} gün önce';
  } else {
    return '${reel.publishedAt.day}.${reel.publishedAt.month}.${reel.publishedAt.year}';
  }
}