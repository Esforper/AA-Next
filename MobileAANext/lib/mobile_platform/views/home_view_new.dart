// lib/views/home_view.dart
// GÜNCELLEME: Progress bar'lar ve düğüm sistemi + Web responsive düzen

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/platform_utils.dart';
import '../../providers/gamification_provider.dart';
import '../../shared/widgets/gamification/daily_progress_card.dart';
import '../../shared/widgets/gamification/level_chain_display.dart';
import 'chat_rooms_view.dart';
import '../pages/game_menu_page.dart';

/// Home View - Ana Sayfa
/// Günlük ilerleme, level sistemi, oyun modları
class HomeView extends StatelessWidget {
  const HomeView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Web için özel düzen: Üstte AppBar ve iki sütunlu içerik (sol ana içerik, sağ yan panel)
    if (PlatformUtils.isWeb) {
      return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          elevation: 0,
          title: const Text(
            'AA - Next',
            style: TextStyle(
              color: Colors.blueAccent,
              fontWeight: FontWeight.bold,
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.menu, color: Colors.blueAccent),
              onPressed: () {},
            ),
          ],
        ),
        backgroundColor: Colors.grey[50],
        body: Row(
          children: [
            // Sol sütun: ana içerik
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      maxWidth: PlatformUtils.getMaxWidth(context),
                    ),
                    child: _buildMobileContent(context),
                  ),
                ),
              ),
            ),
            // Sağ sütun: sabit genişlikli yan panel
            Container(
              width: 300,
              padding: const EdgeInsets.all(16),
              color: Colors.grey[200],
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Öne Çıkanlar',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 16),
                  // Web'e özel yardımcı içerikler buraya eklenebilir
                ],
              ),
            ),
          ],
        ),
      );
    }

    // Mobil düzen (değişmeden)
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // App Bar
            SliverAppBar(
              floating: true,
              snap: true,
              elevation: 0,
              backgroundColor: Colors.white,
              title: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.blue[600]!, Colors.indigo[600]!],
                      ),
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
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
              actions: [
                // Level indicator
                Consumer<GamificationProvider>(
                  builder: (context, provider, _) {
                    return Container(
                      margin: const EdgeInsets.only(right: 16),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.amber[400]!, Colors.orange[500]!],
                        ),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            '⚡',
                            style: TextStyle(fontSize: 16),
                          ),
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
              child: _buildMobileContent(context),
            ),
          ],
        ),
      ),
    );
  }

  // Ortak içerik widget'ı (hem mobil hem web için)
  Widget _buildMobileContent(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Daily Progress Card
        Consumer<GamificationProvider>(
          builder: (context, provider, _) {
            return DailyProgressCard(
              currentXP: provider.state.xpEarnedToday,
              goalXP: provider.dailyXPGoal,
              streakDays: provider.currentStreak,
              percentile: provider.state.streakPercentile,
              goalCompleted: provider.dailyGoalCompleted,
            );
          },
        ),

        const SizedBox(height: 8),

        // Level & Chain Display
        Padding(
          padding: const EdgeInsets.all(16),
          child: Consumer<GamificationProvider>(
            builder: (context, provider, _) {
              return LevelChainDisplay(
                currentLevel: provider.currentLevel,
                currentNode: provider.currentNode,
                totalNodes: provider.state.nodesInLevel,
                currentXP: provider.currentXP,
              );
            },
          ),
        ),

        const SizedBox(height: 8),

        // Section: Oyun Modları
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
          child: Row(
            children: [
              const Text(
                '🎮',
                style: TextStyle(fontSize: 20),
              ),
              const SizedBox(width: 8),
              const Text(
                'Oyun Modları',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),

        // Game modes grid (responsive)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: PlatformUtils.getGridColumns(context),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.3,
            children: [
              _buildGameModeCard(
                context,
                icon: '⚔️',
                title: 'Haber Kapışması',
                subtitle: 'Bilgini konuştur',
                color: Colors.red,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const GameMenuPage()),
                  );
                },
              ),
              _buildGameModeCard(
                context,
                icon: '🔥',
                title: 'Streak Modu',
                subtitle: 'Seriyi devam ettir',
                color: Colors.orange,
                onTap: () {
                  // Navigate to reels
                },
              ),
              _buildGameModeCard(
                context,
                icon: '🏆',
                title: 'Liderlik',
                subtitle: 'Yakında',
                color: Colors.purple,
                isLocked: true,
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Bu özellik yakında eklenecek!'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
              ),
              _buildGameModeCard(
                context,
                icon: '💬',
                title: 'Sohbet Odaları',
                subtitle: 'Arkadaşlarla',
                color: Colors.green,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => const ChatRoomsView(),
                    ),
                  );
                },
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // Section: İstatistikler
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
          child: Row(
            children: [
              const Text(
                '📊',
                style: TextStyle(fontSize: 20),
              ),
              const SizedBox(width: 8),
              const Text(
                'Bugünkü Aktiviteler',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),

        // Stats cards
        Consumer<GamificationProvider>(
          builder: (context, provider, _) {
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                children: [
                  _buildStatCard(
                    icon: '👀',
                    label: 'İzlenen Haber',
                    value: '${provider.state.reelsWatchedToday}',
                    color: Colors.blue,
                  ),
                  const SizedBox(height: 8),
                  _buildStatCard(
                    icon: '❤️',
                    label: 'Atılan Emoji',
                    value: '${provider.state.emojisGivenToday}',
                    color: Colors.pink,
                  ),
                  const SizedBox(height: 8),
                  _buildStatCard(
                    icon: '📖',
                    label: 'Detay Okuma',
                    value: '${provider.state.detailsReadToday}',
                    color: Colors.purple,
                  ),
                  const SizedBox(height: 8),
                  _buildStatCard(
                    icon: '🔗',
                    label: 'Paylaşım',
                    value: '${provider.state.sharesGivenToday}',
                    color: Colors.green,
                  ),
                ],
              ),
            );
          },
        ),

        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildGameModeCard(
    BuildContext context, {
    required String icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
    bool isLocked = false,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      elevation: 2,
      shadowColor: color.withOpacity(0.1),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: color.withOpacity(0.2),
              width: 1.5,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    icon,
                    style: const TextStyle(fontSize: 32),
                  ),
                  if (isLocked)
                    Icon(
                      Icons.lock,
                      color: Colors.grey[400],
                      size: 20,
                    ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: color.withOpacity(isLocked ? 0.5 : 1.0),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required String icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1.5,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              icon,
              style: const TextStyle(fontSize: 24),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Colors.grey[800],
              ),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
