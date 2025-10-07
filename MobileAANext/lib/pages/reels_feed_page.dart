// lib/pages/reels_feed_page.dart
// GÜNCELLEME: 4 yön handle + paylaş + kaydet

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/reels_provider.dart';
import '../providers/gamification_provider.dart';
import '../providers/saved_reels_provider.dart';
import '../models/reel_model.dart';
import '../widgets/image_carousel.dart';
import '../widgets/article_overlay.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../widgets/popup_bar.dart';
import '../widgets/share_sheet.dart';
import '../widgets/gamification/xp_progress_bar.dart';
import '../widgets/gamification/streak_display.dart';
import '../widgets/gamification/level_chain_display.dart';
import '../widgets/gamification/floating_xp.dart';
import '../services/api_service.dart';

class ReelsFeedPage extends StatefulWidget {
  const ReelsFeedPage({super.key});

  @override
  State<ReelsFeedPage> createState() => _ReelsFeedPageState();
}

class _ReelsFeedPageState extends State<ReelsFeedPage> {
  DateTime? _reelStartTime;
  bool _hasEarnedWatchXP = false;
  DateTime? _detailOpenTime;

  @override
  void initState() {
    super.initState();
    _reelStartTime = DateTime.now();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ReelsProvider>();
    final reels = provider.reels;

    return Scaffold(
      appBar: const PopupBar(),
      body: Stack(
        children: [
          // Body
          reels.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : PageView.builder(
                  scrollDirection: Axis.vertical,
                  physics: const PageScrollPhysics(),
                  allowImplicitScrolling: true,
                  itemCount: reels.length,
                  onPageChanged: (i) {
                    // XP ver (3+ saniye izlenmişse)
                    if (!_hasEarnedWatchXP && _reelStartTime != null) {
                      final duration = DateTime.now().difference(_reelStartTime!);
                      if (duration.inSeconds >= 3) {
                        _awardXP(context, 10, 'reel_watched');
                      }
                    }

                    // Yeni reel tracking başlat
                    _reelStartTime = DateTime.now();
                    _hasEarnedWatchXP = false;

                    provider.setIndex(i);
                  },
                  itemBuilder: (context, i) {
                    final reel = reels[i];
                    return KeyedSubtree(
                      key: ValueKey(reel.id),
                      child: _ReelView(reel: reel),
                    );
                  },
                ),

          // Gamification Overlay (üstte)
          _buildGamificationOverlay(context),

          // Handle (orta-alt) - 4 YÖN
          Positioned(
            bottom: 120, // Daha yukarıda
            left: MediaQuery.of(context).size.width / 2 - 80, // Ortada
            child: ReadHandle(
              onAction: (action) {
                final reels = provider.reels;
                if (reels.isEmpty) return;
                final reel = reels[provider.currentIndex];

                switch (action) {
                  case HandleAction.up:
                    debugPrint('[Handle] UP - Detail');
                    _openArticle(context, reel);
                    break;
                    
                  case HandleAction.right:
                    debugPrint('[Handle] RIGHT - Emoji');
                    _openEmojis(context, reel);
                    break;
                    
                  case HandleAction.down:
                    debugPrint('[Handle] DOWN - Share');
                    _openShare(context, reel);
                    break;
                    
                  case HandleAction.left:
                    debugPrint('[Handle] LEFT - Save');
                    _toggleSave(context, reel);
                    break;
                    
                  case HandleAction.none:
                    debugPrint('[Handle] NONE');
                    break;
                }
              },
            ),
          ),

          // Kaydedilmiş göstergesi (sol üst köşe)
          Positioned(
            top: 80,
            left: 16,
            child: Consumer<SavedReelsProvider>(
              builder: (context, savedProv, _) {
                if (reels.isEmpty) return const SizedBox.shrink();
                final currentReel = reels[provider.currentIndex];
                final isSaved = savedProv.isSaved(currentReel.id);
                
                if (!isSaved) return const SizedBox.shrink();
                
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.bookmark, size: 16, color: Colors.white),
                      SizedBox(width: 4),
                      Text(
                        'Kaydedildi',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  // Gamification Overlay
  Widget _buildGamificationOverlay(BuildContext context) {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black.withOpacity(0.5),
                Colors.transparent,
              ],
            ),
          ),
          child: Consumer<GamificationProvider>(
            builder: (context, gameProv, _) {
              return Row(
                children: [
                  // XP Progress
                  Expanded(
                    flex: 3,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.6),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            '${gameProv.state.xpEarnedToday}/${gameProv.dailyXPGoal} XP',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 3),
                          XPProgressBar(
                            currentXP: gameProv.state.xpEarnedToday,
                            goalXP: gameProv.dailyXPGoal,
                            compact: true,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  StreakDisplay(streakDays: gameProv.currentStreak, compact: true),
                  const SizedBox(width: 6),
                  LevelChainDisplay(
                    currentLevel: gameProv.currentLevel,
                    currentChain: gameProv.state.currentChain,
                    totalChains: gameProv.state.chainsInLevel,
                    compact: true,
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  // Detail aç
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
          _onDetailClose(context);
        },
      ),
    );
  }

  // Emoji panel aç
  void _openEmojis(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => EmojiPanel(
        publicEmojis: const ['❤️', '😮', '🔥', '👍', '😂'],
        premiumEmojis: const ['💎', '🏆', '⚡', '🌟'],
        onPick: (emoji) {
          debugPrint('[Emoji] picked: $emoji');
          Navigator.pop(context);
          _awardXP(context, 5, 'emoji_given');
          
          ApiService.trackEmoji(
            reelId: reel.id,
            emoji: emoji,
            category: reel.category,
          );
        },
        onTapPremium: () {
          debugPrint('[Premium] tapped');
        },
      ),
    );
  }

  // Paylaş sheet aç
  void _openShare(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ShareSheet(
        newsId: reel.id,
        newsTitle: reel.title,
        newsImageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls[0] : '',
      ),
    );
  }

  // Kaydet/Çıkar toggle
  void _toggleSave(BuildContext context, Reel reel) {
    final savedProv = context.read<SavedReelsProvider>();
    
    savedProv.toggleSave(
      reelId: reel.id,
      title: reel.title,
      imageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls[0] : '',
    );

    final isSaved = savedProv.isSaved(reel.id);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          isSaved ? '✅ Haber kaydedildi!' : '❌ Kayıt kaldırıldı',
        ),
        duration: const Duration(seconds: 1),
        backgroundColor: isSaved ? Colors.green : Colors.grey[700],
      ),
    );
  }

  // XP ver
  void _awardXP(BuildContext context, int amount, String source) {
    final gameProv = context.read<GamificationProvider>();
    gameProv.addXP(amount, source);

    FloatingXPOverlay.show(
      context,
      xpAmount: amount,
      position: Offset(
        MediaQuery.of(context).size.width / 2 - 50,
        MediaQuery.of(context).size.height / 2,
      ),
    );
  }

  // Detail kapatıldığında
  void _onDetailClose(BuildContext context) {
    if (_detailOpenTime != null) {
      final duration = DateTime.now().difference(_detailOpenTime!);
      if (duration.inSeconds >= 15) {
        _awardXP(context, 10, 'detail_read');
      }
      _detailOpenTime = null;
    }
  }

  @override
  void dispose() {
    FloatingXPOverlay.remove();
    super.dispose();
  }
}

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
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  reel.summary,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(height: 1.4, color: Colors.black87),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}