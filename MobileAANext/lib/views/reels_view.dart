// lib/views/reels_view.dart
// GÜNCELLEME: Mevcut API + Emoji sistemi + XP entegrasyonu
/*

bu dosya kullanılmıyor, bunun yerine rels_feed_page.dart kullanılıyor


*/

/*




import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import '../providers/gamification_provider.dart';
import '../providers/reels_provider.dart';
import '../widgets/gamification/reels_xp_overlay.dart';
import '../widgets/gamification/floating_xp.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../widgets/image_carousel.dart';
import '../models/reel_model.dart';
import '../services/api_service.dart';

/// Reels View - Mevcut sistem + XP gamification
class ReelsView extends StatefulWidget {
  const ReelsView({Key? key}) : super(key: key);

  @override
  State<ReelsView> createState() => _ReelsViewState();
}

class _ReelsViewState extends State<ReelsView> {
  DateTime? _reelStartTime;
  DateTime? _detailOpenTime;
  bool _hasEarnedWatchXP = false;
  String? _currentReelId;
  bool _showEmojis = false;
  
  final ApiService _apiService = ApiService();

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
    _showEmojis = false; // Yeni reel'e geçildiğinde emoji panelini kapat
  }

  void _onReelChange(int index) {
    final reelsProvider = context.read<ReelsProvider>();
    
    // Önceki reel için XP ver (3+ saniye izlendiyse)
    if (!_hasEarnedWatchXP && _reelStartTime != null && _currentReelId != null) {
      final duration = DateTime.now().difference(_reelStartTime!);
      if (duration.inSeconds >= 3) {
        _awardXP(10, 'reel_watched', _currentReelId!);
        _hasEarnedWatchXP = true;
      }
    }

    // Yeni reel için tracking
    reelsProvider.setIndex(index);
    if (reelsProvider.current != null) {
      _startReelTracking(reelsProvider.current!.id);
    }
  }

  void _onEmojiPick(String emoji, Reel reel) {
    final provider = context.read<GamificationProvider>();
    
    // Emoji daha önce atılmış mı?
    final success = provider.onEmojiGiven(reel.id);
    
    if (success) {
      // Backend'e emoji tracking
      _apiService.trackEmoji(
        reelId: reel.id,
        emoji: emoji,
        category: reel.category,
      );
      
      // XP ver ve animasyon
      _showFloatingXP(5, 'emoji_given');
      
      // Snackbar feedback
      if (mounted) {
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
      }
    } else {
      _showAlreadyGivenMessage('Bu habere zaten emoji attın!');
    }
    
    // Emoji panelini kapat
    setState(() => _showEmojis = false);
  }

  void _onDetailOpen() {
    _detailOpenTime = DateTime.now();
  }

  void _onDetailClose(Reel reel) {
    if (_detailOpenTime != null) {
      final duration = DateTime.now().difference(_detailOpenTime!);
      
      // 10+ saniye okuduysa XP ver
      if (duration.inSeconds >= 10) {
        final provider = context.read<GamificationProvider>();
        provider.onDetailRead(reel.id);
        
        // Backend'e detail tracking
        _apiService.trackDetailView(
          reelId: reel.id,
          durationMs: duration.inMilliseconds,
        );
        
        _showFloatingXP(5, 'detail_read');
      }
      
      _detailOpenTime = null;
    }
  }

  void _onShareTap(Reel reel) async {
    final provider = context.read<GamificationProvider>();
    
    // Paylaşım yapılmış mı?
    if (provider.hasShareGiven(reel.id)) {
      _showAlreadyGivenMessage('Bu haberi zaten paylaştın!');
      return;
    }
    
    try {
      final result = await Share.share(
        '${reel.title}\n\n${reel.summary}\n\nAA Haber uygulamasından paylaşıldı.',
        subject: reel.title,
      );
      
      if (result.status == ShareResultStatus.success) {
        final success = provider.onShareGiven(reel.id);
        if (success) {
          _showFloatingXP(5, 'share_given');
        }
      }
    } catch (e) {
      debugPrint('Paylaşım hatası: $e');
    }
  }

  void _awardXP(int amount, String source, String reelId) {
    final provider = context.read<GamificationProvider>();
    provider.onReelWatched(reelId);
    _showFloatingXP(amount, source);
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

  void _showAlreadyGivenMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Colors.orange[700],
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ReelsProvider>(
      builder: (context, reelsProvider, _) {
        // Loading
        if (reelsProvider.status == FeedStatus.loading) {
          return const Scaffold(
            backgroundColor: Colors.black,
            body: Center(
              child: CircularProgressIndicator(color: Colors.white),
            ),
          );
        }

        // Error
        if (reelsProvider.status == FeedStatus.error) {
          return Scaffold(
            backgroundColor: Colors.black,
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, color: Colors.white, size: 64),
                  const SizedBox(height: 16),
                  const Text(
                    'Haberler yüklenirken hata oluştu',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => reelsProvider.loadReels(),
                    child: const Text('Tekrar Dene'),
                  ),
                ],
              ),
            ),
          );
        }

        // Empty
        if (reelsProvider.reels.isEmpty) {
          return const Scaffold(
            backgroundColor: Colors.black,
            body: Center(
              child: Text(
                'Henüz haber yok',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
            ),
          );
        }

        // Main content
        final currentReel = reelsProvider.current;
        
        return Scaffold(
          backgroundColor: Colors.black,
          body: Stack(
            children: [
              // Reels PageView
              PageView.builder(
                scrollDirection: Axis.vertical,
                onPageChanged: _onReelChange,
                itemCount: reelsProvider.reels.length,
                controller: PageController(initialPage: reelsProvider.currentIndex),
                itemBuilder: (context, index) {
                  final reel = reelsProvider.reels[index];
                  return _buildReelItem(reel);
                },
              ),

              // Top overlay - XP Progress
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: SafeArea(
                  child: ReelsXPOverlay(),
                ),
              ),

              // Bottom content
              if (currentReel != null)
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: SafeArea(
                    child: _buildBottomContent(currentReel),
                  ),
                ),

              // Read Handle (sağ-alt)
              if (currentReel != null)
                Positioned(
                  right: 16,
                  bottom: 24,
                  child: ReadHandle(
                    threshold: 35,
                    onAction: (action) {
                      switch (action) {
                        case HandleAction.up:
                          // Detay aç
                          debugPrint('[Handle] UP - Article Detail');
                          _showDetailModal(currentReel);
                          break;
                        
                        case HandleAction.right:
                          // Emoji panel aç
                          debugPrint('[Handle] RIGHT - Emoji Panel');
                          setState(() => _showEmojis = true);
                          break;
                        
                        case HandleAction.down:
                          // Paylaş
                          debugPrint('[Handle] DOWN - Share');
                          _onShareTap(currentReel);
                          break;
                        
                        case HandleAction.left:
                          // Kaydet (şimdilik sadece mesaj)
                          debugPrint('[Handle] LEFT - Save');
                          ScaffoldMessenger.of(context)
                            ..hideCurrentSnackBar()
                            ..showSnackBar(
                              const SnackBar(
                                content: Text('İçerik kaydedildi! 📚'),
                                duration: Duration(seconds: 2),
                              ),
                            );
                          break;
                        
                        case HandleAction.none:
                          break;
                      }
                    },
                  ),
                ),

              // Emoji Panel (overlay)
              if (_showEmojis && currentReel != null)
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: EmojiPanel(
                    publicEmojis: const ['👍', '❤️', '🔥', '⭐', '👏'],
                    premiumEmojis: const ['😍', '🤔', '😮', '🎉', '💎'],
                    onPick: (emoji) => _onEmojiPick(emoji, currentReel),
                    onTapPremium: () {
                      setState(() => _showEmojis = false);
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
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildReelItem(Reel reel) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Images carousel (full screen)
        Positioned.fill(
          child: ImageCarousel(urls: reel.imageUrls),
        ),
        
        // Gradient overlay
        Positioned.fill(
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withOpacity(0.3),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBottomContent(Reel reel) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [
            Colors.black.withOpacity(0.8),
            Colors.black.withOpacity(0.4),
            Colors.transparent,
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Title
          Text(
            reel.title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
              height: 1.3,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          
          const SizedBox(height: 8),
          
          // Summary
          Text(
            reel.summary,
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
              height: 1.4,
            ),
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  void _showDetailModal(Reel reel) {
    _onDetailOpen();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.75,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            ),
            child: Column(
              children: [
                // Handle
                Container(
                  margin: const EdgeInsets.symmetric(vertical: 12),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),

                // Content
                Expanded(
                  child: ListView(
                    controller: scrollController,
                    padding: const EdgeInsets.all(24),
                    children: [
                      // Title
                      Text(
                        reel.title,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          height: 1.3,
                        ),
                      ),
                      
                      const SizedBox(height: 8),
                      
                      // XP badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.purple[50],
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.purple[200]!),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text('📖', style: TextStyle(fontSize: 16)),
                            const SizedBox(width: 6),
                            Text(
                              '10+ saniye oku, 5 XP kazan!',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: Colors.purple[700],
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // Full content
                      Text(
                        reel.fullText,
                        style: TextStyle(
                          fontSize: 16,
                          height: 1.6,
                          color: Colors.grey[800],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    ).whenComplete(() => _onDetailClose(reel));
  }

  @override
  void dispose() {
    FloatingXPOverlay.remove();
    super.dispose();
  }
}
*/