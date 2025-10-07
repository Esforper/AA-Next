// lib/views/profile_view.dart
// Profil sayfası - Level, streak, stats gösterimi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/gamification_provider.dart';
import '../widgets/gamification/level_chain_display.dart';
import '../widgets/gamification/streak_display.dart';

/// Profile View - Kullanıcı profili ve istatistikler
class ProfileView extends StatelessWidget {
  const ProfileView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: CustomScrollView(
        slivers: [
          // App Bar with user info
          SliverAppBar(
            expandedHeight: 200,
            floating: false,
            pinned: true,
            elevation: 0,
            backgroundColor: Colors.blue[600],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Colors.blue[600]!, Colors.indigo[700]!],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        // Avatar
                        Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 3),
                          ),
                          child: CircleAvatar(
                            radius: 40,
                            backgroundColor: Colors.white,
                            child: Text(
                              '👤',
                              style: TextStyle(fontSize: 40),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Kullanıcı',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Consumer<GamificationProvider>(
                          builder: (context, provider, _) {
                            return Text(
                              'Level ${provider.currentLevel} • ${provider.state.totalXP} XP',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.9),
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Level Progress
                  Consumer<GamificationProvider>(
                    builder: (context, provider, _) {
                      return LevelChainDisplay(
                        currentLevel: provider.currentLevel,
                        currentChain: provider.state.currentChain,
                        totalChains: provider.state.chainsInLevel,
                      );
                    },
                  ),

                  const SizedBox(height: 16),

                  // Streak Display
                  Consumer<GamificationProvider>(
                    builder: (context, provider, _) {
                      return StreakDisplay(
                        streakDays: provider.currentStreak,
                        percentile: provider.state.streakPercentile,
                      );
                    },
                  ),

                  const SizedBox(height: 24),

                  // Stats Section
                  _buildSectionHeader('📊', 'İstatistikler'),

                  const SizedBox(height: 12),

                  Consumer<GamificationProvider>(
                    builder: (context, provider, _) {
                      return Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            _buildStatRow(
                              '🎯',
                              'Bugün İzlenen',
                              '${provider.state.reelsWatchedToday} haber',
                            ),
                            const Divider(height: 24),
                            _buildStatRow(
                              '💬',
                              'Bugün Emoji',
                              '${provider.state.emojisGivenToday} adet',
                            ),
                            const Divider(height: 24),
                            _buildStatRow(
                              '📖',
                              'Detay Okunan',
                              '${provider.state.detailsReadToday} haber',
                            ),
                            const Divider(height: 24),
                            _buildStatRow(
                              '⭐',
                              'Toplam XP',
                              '${provider.state.totalXP} puan',
                            ),
                            const Divider(height: 24),
                            _buildStatRow(
                              '🏆',
                              'Günlük Hedef',
                              provider.dailyGoalCompleted
                                  ? 'Tamamlandı! ✅'
                                  : '${provider.state.xpEarnedToday}/${provider.dailyXPGoal}',
                            ),
                          ],
                        ),
                      );
                    },
                  ),

                  const SizedBox(height: 24),

                  // Achievements Section (Placeholder)
                  _buildSectionHeader('🏆', 'Başarımlar'),

                  const SizedBox(height: 12),

                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        const Text(
                          '🎖️',
                          style: TextStyle(fontSize: 48),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Başarımlar çok yakında!',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Colors.grey[700],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Rozetler, madalyalar ve daha fazlası',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Settings Section
                  _buildSectionHeader('⚙️', 'Ayarlar'),

                  const SizedBox(height: 12),

                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        _buildSettingTile(
                          icon: Icons.notifications_outlined,
                          title: 'Bildirimler',
                          subtitle: 'Streak hatırlatmaları',
                          onTap: () {},
                        ),
                        Divider(height: 1, color: Colors.grey[200]),
                        _buildSettingTile(
                          icon: Icons.person_outline,
                          title: 'Profil Düzenle',
                          subtitle: 'İsim, avatar değiştir',
                          onTap: () {},
                        ),
                        Divider(height: 1, color: Colors.grey[200]),
                        Consumer<GamificationProvider>(
                          builder: (context, provider, _) {
                            return _buildSettingTile(
                              icon: Icons.refresh,
                              title: 'İlerlemeyi Sıfırla',
                              subtitle: 'Test için (dikkatli kullan)',
                              onTap: () {
                                _showResetDialog(context, provider);
                              },
                              isDestructive: true,
                            );
                          },
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String icon, String title) {
    return Row(
      children: [
        Text(
          icon,
          style: const TextStyle(fontSize: 20),
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Widget _buildStatRow(String icon, String label, String value) {
    return Row(
      children: [
        Text(
          icon,
          style: const TextStyle(fontSize: 24),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w500,
              color: Colors.grey[700],
            ),
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Widget _buildSettingTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    bool isDestructive = false,
  }) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: isDestructive
              ? Colors.red[50]
              : Colors.blue[50],
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          color: isDestructive ? Colors.red[600] : Colors.blue[600],
          size: 20,
        ),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: isDestructive ? Colors.red[700] : Colors.black87,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          fontSize: 12,
          color: Colors.grey[600],
        ),
      ),
      trailing: Icon(
        Icons.chevron_right,
        color: Colors.grey[400],
      ),
      onTap: onTap,
    );
  }

  void _showResetDialog(BuildContext context, GamificationProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('İlerlemeyi Sıfırla'),
        content: const Text(
          'Tüm XP, level ve streak verilerin silinecek. '
          'Bu işlem geri alınamaz. Emin misin?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () {
              provider.resetAll();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('İlerleme sıfırlandı'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: TextButton.styleFrom(
              foregroundColor: Colors.red,
            ),
            child: const Text('Sıfırla'),
          ),
        ],
      ),
    );
  }
}