// lib/pages/reels_feed_page.dart
// GÜNCELLEME: Navigasyon ortada + Görsel kırpma düzenlemesi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';

import '../providers/reels_provider.dart';
import '../providers/saved_reels_provider.dart';
import '../providers/gamification_provider.dart';
import '../models/reel_model.dart';
import '../widgets/image_carousel.dart';
import '../widgets/article_overlay.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../widgets/popup_bar.dart';
import '../widgets/gamification/reels_xp_overlay.dart';
import '../widgets/gamification/floating_xp.dart';
import '../services/api_service.dart';

class ReelsFeedPage extends StatefulWidget {
  const ReelsFeedPage({super.key});

  @override
  State<ReelsFeedPage> createState() => _ReelsFeedPageState();
}

class _ReelsFeedPageState extends State<ReelsFeedPage> {
  DateTime? _reelStartTime;
  DateTime? _detailOpenTime;
  bool _hasEarnedWatchXP = false;
  String? _currentReelId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ReelsProvider>();
      if (provider.reels.isNotEmpty) {
        _startReelTracking(provider.current!.id);
      }
    });
  }

  void _startReelTracking(String reelId) {
    _reelStartTime = DateTime.now();
    _hasEarnedWatchXP = false;
    _currentReelId = reelId;
  }

  void _onPageChanged(int index) {
    final reelsProvider = context.read<ReelsProvider>();
    
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
      _startReelTracking(reelsProvider.current!.id);
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
      appBar: const PopupBar(),
      body: Stack(
        children: [
          _buildBody(context, provider),

          // XP Overlay (üstte)
          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: ReelsXPOverlay(),
            ),
          ),

          // ✅ NAVİGASYON BARI ORTADA (Positioned yerine Align kullanıyoruz)
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
                      debugPrint('[Handle] UP - Article Detail');
                      _openArticle(context, reel);
                      break;
                    
                    case HandleAction.right:
                      debugPrint('[Handle] RIGHT - Emoji Panel');
                      _openEmojis(context, reel);
                      break;
                    
                    case HandleAction.down:
                      debugPrint('[Handle] DOWN - Share');
                      _onShareTap(context, reel);
                      break;
                    
                    case HandleAction.left:
                      debugPrint('[Handle] LEFT - Save');
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
        return const Center(
          child: CircularProgressIndicator(),
        );

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
        final reels = provider.reels;
        if (reels.isEmpty) {
          return const Center(
            child: Text('Gösterilecek içerik yok.'),
          );
        }
        
        return PageView.builder(
          scrollDirection: Axis.vertical,
          physics: const PageScrollPhysics(),
          allowImplicitScrolling: true,
          itemCount: reels.length,
          onPageChanged: _onPageChanged,
          itemBuilder: (context, i) {
            final reel = reels[i];
            return KeyedSubtree(
              key: ValueKey(reel.id),
              child: _ReelView(reel: reel),
            );
          },
        );
    }
  }

  void _openArticle(BuildContext context, Reel reel) {
    _detailOpenTime = DateTime.now();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ArticleOverlay(
        title: reel.title,
        body: reel.fullText,
        onClose: () {
          Navigator.pop(context);
          _onDetailClose(reel);
        },
      ),
    );
  }

  void _onDetailClose(Reel reel) {
    if (_detailOpenTime != null) {
      final duration = DateTime.now().difference(_detailOpenTime!);
      
      if (duration.inSeconds >= 10) {
        final gamificationProvider = context.read<GamificationProvider>();
        gamificationProvider.onDetailRead(reel.id);
        
        ApiService().trackDetailView(
          reelId: reel.id,
          durationMs: duration.inMilliseconds,
        );
        
        _showFloatingXP(5, 'detail_read');
      }
      
      _detailOpenTime = null;
    }
  }

  void _openEmojis(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      barrierColor: Colors.black.withOpacity(0.2),
      builder: (_) => EmojiPanel(
        publicEmojis: const ['👍', '❤️', '🔥', '⭐', '👏'],
        premiumEmojis: const ['😍', '🤔', '😮', '🎉', '💎'],
        onPick: (emoji) async {
          Navigator.pop(context);
          
          final gamificationProvider = context.read<GamificationProvider>();
          final success = gamificationProvider.onEmojiGiven(reel.id);
          
          if (success) {
            await ApiService().trackEmoji(
              reelId: reel.id,
              emoji: emoji,
              category: reel.category,
            );
            
            _showFloatingXP(5, 'emoji_given');
            
            if (!context.mounted) return;
            ScaffoldMessenger.of(context)
              ..hideCurrentSnackBar()
              ..showSnackBar(
                SnackBar(
                  content: Text('Tepkiniz gönderildi: $emoji +5 XP'),
                  duration: const Duration(seconds: 2),
                  behavior: SnackBarBehavior.floating,
                  backgroundColor: Colors.pink[600],
                ),
              );
          } else {
            if (!context.mounted) return;
            ScaffoldMessenger.of(context)
              ..hideCurrentSnackBar()
              ..showSnackBar(
                SnackBar(
                  content: const Text('Bu habere zaten emoji attın!'),
                  duration: const Duration(seconds: 2),
                  behavior: SnackBarBehavior.floating,
                  backgroundColor: Colors.orange[700],
                ),
              );
          }
        },
        onTapPremium: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context)
            ..hideCurrentSnackBar()
            ..showSnackBar(
              const SnackBar(
                content: Text('Premium emojiler şimdilik kilitli.'),
                duration: Duration(seconds: 2),
              ),
            );
        },
      ),
    );
  }

  void _onShareTap(BuildContext context, Reel reel) async {
    // Paylaşma işlemi
    await Share.share(
      '${reel.title}\n\n${reel.summary}',
      subject: reel.title,
    );
    
    // Şimdilik XP yok, ileride eklenebilir
    if (!context.mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(
          content: Text('Paylaşıldı!'),
          duration: Duration(seconds: 1),
        ),
      );
  }

  void _saveReel(BuildContext context, Reel reel) async {
    final savedProvider = context.read<SavedReelsProvider>();
    
    if (savedProvider.isSaved(reel.id)) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Bu haber zaten kayıtlı!'),
            duration: Duration(seconds: 2),
          ),
        );
      return;
    }
    
    savedProvider.saveReel(  // ✅ await kaldırıldı
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
    FloatingXPOverlay.remove();
    super.dispose();
  }
}

// ✅ REEL GÖRÜNÜMÜ - GÖRSEL KIRPMA DÜZENLENDİ
class _ReelView extends StatelessWidget {
  final Reel reel;
  const _ReelView({required this.reel});

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // ✅ GÖRSEL - Daha kareye yakın, dikey biraz daha büyük
        Positioned.fill(
          top: 0,
          bottom: 160,  // ✅ 120 → 80 (reels daha uzun olsun)
          child: Center(
            child: AspectRatio(
              aspectRatio: 4 / 3,  // ✅ 16/9 → 4/3 (daha kare)
              child: ClipRect(
                child: SizedBox.expand(
                  child: ImageCarousel(urls: reel.imageUrls),
                ),
              ),
            ),
          ),
        ),

        // ✅ Başlık ve özet - Navigasyon üstünde
        Positioned(
          left: 0,
          right: 0,
          bottom: 10,  // ✅ Navigasyon için boşluk (24 bottom + 56 button + 20 padding = ~100)
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
                // ✅ BAŞLIK - Marker/Highlight efekti
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.9),  // Sarı marker
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
                      color: Colors.black87,  // Siyah yazı
                      height: 1.2,
                    ),
                  ),
                ),
                const SizedBox(height: 120),
                // Özet
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