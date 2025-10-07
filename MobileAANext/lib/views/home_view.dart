// lib/views/home_view.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/gamification_provider.dart';
import '../widgets/gamification/daily_progress_card.dart';
import 'chat_rooms_view.dart';

/// Home View - Ana Sayfa
/// Günlük ilerleme, oyun modları, arkadaşlar
class HomeView extends StatelessWidget {
  const HomeView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
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
              child: Column(
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
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Game Modes Grid
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 1.1,
                      children: [
                        _buildGameModeCard(
                          context,
                          icon: '📚',
                          title: 'Kategori\nTakipçisi',
                          subtitle: 'Çok yakında',
                          gradient: [Colors.purple[400]!, Colors.purple[600]!],
                          enabled: false,
                        ),
                        _buildGameModeCard(
                          context,
                          icon: '🎯',
                          title: 'Gündem\nQuiz',
                          subtitle: 'Çok yakında',
                          gradient: [Colors.blue[400]!, Colors.blue[600]!],
                          enabled: false,
                        ),
                        _buildGameModeCard(
                          context,
                          icon: '💬',
                          title: 'Sohbet\nOyunu',
                          subtitle: 'Yakında aktif',
                          gradient: [Colors.green[400]!, Colors.green[600]!],
                          enabled: false,
                        ),
                        _buildGameModeCard(
                          context,
                          icon: '🏆',
                          title: 'Haftalık\nYarış',
                          subtitle: 'Çok yakında',
                          gradient: [Colors.orange[400]!, Colors.orange[600]!],
                          enabled: false,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Section: Arkadaşlar (Placeholder)
// Section: Sohbet Odaları
Padding(
  padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
  child: Row(
    children: [
      const Text('💬', style: TextStyle(fontSize: 20)),
      const SizedBox(width: 8),
      const Text(
        'Sohbet Odaları',
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.black87,
        ),
      ),
    ],
  ),
),

// Chat rooms button
Padding(
  padding: const EdgeInsets.symmetric(horizontal: 16),
  child: GestureDetector(
    onTap: () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const ChatRoomsView()),
      );
    },
    child: Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.purple[400]!, Colors.purple[600]!],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.purple.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Text('💬', style: TextStyle(fontSize: 40)),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Sohbet Odaları',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Arkadaşlarınla haber paylaş',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),
          const Icon(
            Icons.arrow_forward_ios,
            color: Colors.white,
            size: 20,
          ),
        ],
      ),
    ),
  ),
),











                  const SizedBox(height: 32),
                ],
              ),
            ),
          ],
        ),
      ),

      // Floating Action Button - Reels'e git
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // Navigate to reels
          Navigator.pushNamed(context, '/reels');
        },
        backgroundColor: Colors.blue[600],
        icon: const Icon(Icons.play_circle_filled, size: 28),
        label: const Text(
          'Reels İzle',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        elevation: 4,
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }

  Widget _buildGameModeCard(
    BuildContext context, {
    required String icon,
    required String title,
    required String subtitle,
    required List<Color> gradient,
    bool enabled = false,
  }) {
    return Opacity(
      opacity: enabled ? 1.0 : 0.6,
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: gradient,
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: enabled
              ? [
                  BoxShadow(
                    color: gradient[0].withOpacity(0.3),
                    blurRadius: 12,
                    spreadRadius: 1,
                    offset: const Offset(0, 4),
                  ),
                ]
              : null,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: enabled ? () {} : null,
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    icon,
                    style: const TextStyle(fontSize: 36),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.white.withOpacity(0.9),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}