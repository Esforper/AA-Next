// lib/views/reels_view.dart
// GÜNCELLEME: Gamification tracking eklendi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/gamification_provider.dart';
import '../widgets/gamification/xp_progress_bar.dart';
import '../widgets/gamification/streak_display.dart';
import '../widgets/gamification/level_chain_display.dart';
import '../widgets/gamification/floating_xp.dart';

/// Reels View - Gamification entegrasyonlu
class ReelsView extends StatefulWidget {
  const ReelsView({Key? key}) : super(key: key);

  @override
  State<ReelsView> createState() => _ReelsViewState();
}

class _ReelsViewState extends State<ReelsView> {
  int _currentReelIndex = 0;
  DateTime? _reelStartTime;
  DateTime? _detailOpenTime;
  bool _hasEarnedWatchXP = false;

  final List<Map<String, dynamic>> _mockReels = [
    {
      'id': 'reel_1',
      'title': 'Dolar kuru rekor kırdı',
      'image': 'https://picsum.photos/400/700?random=1',
    },
    {
      'id': 'reel_2',
      'title': 'Merkez Bankası faiz kararı',
      'image': 'https://picsum.photos/400/700?random=2',
    },
    {
      'id': 'reel_3',
      'title': 'Teknoloji şirketleri istihdam artırdı',
      'image': 'https://picsum.photos/400/700?random=3',
    },
  ];

  @override
  void initState() {
    super.initState();
    _startReelTracking();
  }

  void _startReelTracking() {
    _reelStartTime = DateTime.now();
    _hasEarnedWatchXP = false;
  }

  void _onReelChange(int index) {
    // Önceki reel için XP ver (eğer henüz verilmediyse)
    if (!_hasEarnedWatchXP && _reelStartTime != null) {
      final duration = DateTime.now().difference(_reelStartTime!);
      if (duration.inSeconds >= 3) {
        _awardXP(10, 'reel_watched');
        _hasEarnedWatchXP = true;
      }
    }

    setState(() {
      _currentReelIndex = index;
      _startReelTracking();
    });
  }

  void _onEmojiTap(String emoji) {
    _awardXP(5, 'emoji_given');
    
    // Emoji feedback
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$emoji +5 XP'),
        duration: const Duration(seconds: 1),
        behavior: SnackBarBehavior.floating,
        backgroundColor: Colors.blue[600],
      ),
    );
  }

  void _onDetailOpen() {
    _detailOpenTime = DateTime.now();
  }

  void _onDetailClose() {
    if (_detailOpenTime != null) {
      final duration = DateTime.now().difference(_detailOpenTime!);
      if (duration.inSeconds >= 15) {
        _awardXP(10, 'detail_read');
      }
      _detailOpenTime = null;
    }
  }

  void _awardXP(int amount, String source) {
    final provider = context.read<GamificationProvider>();
    provider.addXP(amount, source);

    // Floating XP animation
    FloatingXPOverlay.show(
      context,
      xpAmount: amount,
      position: Offset(
        MediaQuery.of(context).size.width / 2 - 50,
        MediaQuery.of(context).size.height / 2 - 100,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Reels content
          PageView.builder(
            scrollDirection: Axis.vertical,
            onPageChanged: _onReelChange,
            itemCount: _mockReels.length,
            itemBuilder: (context, index) {
              final reel = _mockReels[index];
              return _buildReelItem(reel);
            },
          ),

          // Top overlay - Gamification info
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.black.withOpacity(0.6),
                      Colors.transparent,
                    ],
                  ),
                ),
                child: Consumer<GamificationProvider>(
                  builder: (context, provider, _) {
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // XP Progress (compact)
                        Expanded(
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.6),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '${provider.state.xpEarnedToday}/${provider.dailyXPGoal} XP',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                XPProgressBar(
                                  currentXP: provider.state.xpEarnedToday,
                                  goalXP: provider.dailyXPGoal,
                                  compact: true,
                                ),
                              ],
                            ),
                          ),
                        ),

                        const SizedBox(width: 8),

                        // Streak (compact)
                        StreakDisplay(
                          streakDays: provider.currentStreak,
                          compact: true,
                        ),

                        const SizedBox(width: 8),

                        // Level (compact)
                        LevelChainDisplay(
                          currentLevel: provider.currentLevel,
                          currentChain: provider.state.currentChain,
                          totalChains: provider.state.chainsInLevel,
                          compact: true,
                        ),
                      ],
                    );
                  },
                ),
              ),
            ),
          ),

          // Bottom actions
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Reel title
                    Text(
                      _mockReels[_currentReelIndex]['title'],
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        shadows: [
                          Shadow(
                            color: Colors.black54,
                            blurRadius: 8,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Action buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildActionButton(
                          icon: '❤️',
                          label: '+5 XP',
                          onTap: () => _onEmojiTap('❤️'),
                        ),
                        _buildActionButton(
                          icon: '😮',
                          label: '+5 XP',
                          onTap: () => _onEmojiTap('😮'),
                        ),
                        _buildActionButton(
                          icon: '🔥',
                          label: '+5 XP',
                          onTap: () => _onEmojiTap('🔥'),
                        ),
                        _buildActionButton(
                          icon: '📖',
                          label: 'Detay',
                          onTap: () {
                            _onDetailOpen();
                            _showDetailModal();
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildReelItem(Map<String, dynamic> reel) {
    return Container(
      decoration: BoxDecoration(
        image: DecorationImage(
          image: NetworkImage(reel['image']),
          fit: BoxFit.cover,
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.transparent,
              Colors.black.withOpacity(0.7),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required String icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
              border: Border.all(
                color: Colors.white.withOpacity(0.5),
                width: 2,
              ),
            ),
            child: Text(
              icon,
              style: const TextStyle(fontSize: 24),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.w600,
              shadows: [
                Shadow(
                  color: Colors.black54,
                  blurRadius: 4,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showDetailModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
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
                    padding: const EdgeInsets.all(20),
                    children: [
                      Text(
                        _mockReels[_currentReelIndex]['title'],
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Bu haber hakkında detaylı bilgi burada yer alacak. '
                        '15+ saniye okursan +10 XP kazanırsın! 🎉\n\n'
                        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
                        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                        'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.',
                        style: TextStyle(
                          fontSize: 15,
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
    ).whenComplete(_onDetailClose);
  }

  @override
  void dispose() {
    FloatingXPOverlay.remove();
    super.dispose();
  }
}