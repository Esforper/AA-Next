// lib/pages/reels_feed_page.dart
// GÜNCELLEME: Mevcut sistem + XP gamification entegrasyonu

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
  // XP tracking için state'ler
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
    
    // Önceki reel için XP ver (3+ saniye izlendiyse)
    if (!_hasEarnedWatchXP && _reelStartTime != null && _currentReelId != null) {
      final duration = DateTime.now().difference(_reelStartTime!);
      if (duration.inSeconds >= 3) {
        final gamificationProvider = context.read<GamificationProvider>();
        gamificationProvider.onReelWatched(_currentReelId!);
        _showFloatingXP(10, 'reel_watched');
        _hasEarnedWatchXP = true;
      }
    }

    // Yeni reel için tracking
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

          // Read Handle (sağ-alt)
          Positioned(
            right: 16,
            bottom: 24,
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

  // Article detail modal (10+ saniye okuma = 5 XP)
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
      
      // 10+ saniye okuduysa XP ver
      if (duration.inSeconds >= 10) {
        final gamificationProvider = context.read<GamificationProvider>();
        gamificationProvider.onDetailRead(reel.id);
        
        // Backend'e tracking gönder
        ApiService().trackDetailView(
          reelId: reel.id,
          durationMs: duration.inMilliseconds,
        );
        
        _showFloatingXP(5, 'detail_read');
      }
      
      _detailOpenTime = null;
    }
  }

  // Emoji panel (her reels'e 1 emoji = 5 XP)
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
            // Backend'e tracking
            await ApiService().trackEmoji(
              reelId: reel.id,
              emoji: emoji,
              category: reel.category,
            );
            
            // XP animasyonu
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
            // Zaten emoji atılmış
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

  // Paylaş (ilk paylaşma = 5 XP)
  void _onShareTap(BuildContext context, Reel reel) async {
    final gamificationProvider = context.read<GamificationProvider>();
    
    // Daha önce paylaşılmış mı?
    if (gamificationProvider.hasShareGiven(reel.id)) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: const Text('Bu haberi zaten paylaştın!'),
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
            backgroundColor: Colors.orange[700],
          ),
        );
      return;
    }
    
    try {
      final result = await Share.shareWithResult(
        '${reel.title}\n\n${reel.summary}\n\nAA Haber uygulamasından paylaşıldı.',
        subject: reel.title,
      );
      
      if (result.status == ShareResultStatus.success) {
        final success = gamificationProvider.onShareGiven(reel.id);
        if (success) {
          _showFloatingXP(5, 'share_given');
        }
      }
    } catch (e) {
      debugPrint('Paylaşım hatası: $e');
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Paylaşım özelliği yakında...'),
            duration: Duration(seconds: 2),
          ),
        );
    }
  }

  // Save reel
  void _saveReel(BuildContext context, Reel reel) {
    final savedProv = context.read<SavedReelsProvider>();
    
    if (savedProv.isSaved(reel.id)) {
      // Zaten kayıtlı, kaldır
      savedProv.unsaveReel(reel.id);
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.bookmark_remove, color: Colors.white),
                SizedBox(width: 8),
                Text('Kayıt kaldırıldı'),
              ],
            ),
            backgroundColor: Colors.orange[700],
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        );
    } else {
      // Kaydet
      savedProv.saveReel(
        reelId: reel.id,
        title: reel.title,
        imageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls.first : '',
      );
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
  }

  @override
  void dispose() {
    FloatingXPOverlay.remove();
    super.dispose();
  }
}

// Reel görünümü widget'ı
class _ReelView extends StatelessWidget {
  final Reel reel;
  const _ReelView({required this.reel});

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        Positioned.fill(
          bottom: 90,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 8),
              Expanded(child: ImageCarousel(urls: reel.imageUrls)),
              const SizedBox(height: 12),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  reel.title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  reel.summary,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    height: 1.4,
                    color: Colors.black87,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}