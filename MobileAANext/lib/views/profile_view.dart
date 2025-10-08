// lib/views/profile_view.dart
// Auth entegrasyonu + Logout butonu eklendi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/gamification_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/gamification/level_chain_display.dart';
import '../widgets/gamification/streak_display.dart';
import '../pages/login_page.dart';
import 'saved_reels_view.dart';

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
                            child: Consumer<AuthProvider>(
                              builder: (context, auth, _) {
                                // Avatar gösterimi
                                if (auth.user?.avatarUrl != null) {
                                  return ClipOval(
                                    child: Image.network(
                                      auth.user!.avatarUrl!,
                                      width: 80,
                                      height: 80,
                                      fit: BoxFit.cover,
                                      errorBuilder: (_, __, ___) => const Text(
                                        '👤',
                                        style: TextStyle(fontSize: 40),
                                      ),
                                    ),
                                  );
                                }
                                return const Text(
                                  '👤',
                                  style: TextStyle(fontSize: 40),
                                );
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        
                        // Kullanıcı adı
                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            final displayName = auth.user?.fullName ?? 
                                               auth.user?.username ?? 
                                               'Kullanıcı';
                            return Text(
                              displayName,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 4),
                        
                        // Level & XP
                        Consumer2<GamificationProvider, AuthProvider>(
                          builder: (context, gamification, auth, _) {
                            return Column(
                              children: [
                                Text(
                                  'Level ${gamification.currentLevel} • ${gamification.state.totalXP} XP',
                                  style: TextStyle(
                                    color: Colors.white.withOpacity(0.9),
                                    fontSize: 14,
                                  ),
                                ),
                                if (auth.user?.email != null)
                                  Text(
                                    auth.user!.email,
                                    style: TextStyle(
                                      color: Colors.white.withOpacity(0.7),
                                      fontSize: 12,
                                    ),
                                  ),
                              ],
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
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Level Chain Display
                  Consumer<GamificationProvider>(
                    builder: (context, provider, _) {
                      return LevelChainDisplay(
                        currentLevel: provider.currentLevel,
                        currentChain: provider.state.currentChain,
                        totalChains: provider.state.chainsInLevel,
                      );
                    },
                  ),

                  const SizedBox(height: 24),

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

                  // Today's Stats
                  _buildSectionHeader('📊', 'Bugünün İstatistikleri'),

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

                  // Achievements Section
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
                          icon: Icons.bookmark_outline,
                          title: 'Kaydedilenler',
                          subtitle: 'Kaydettiğiniz haberler',
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => const SavedReelsView(),
                              ),
                            );
                          },
                        ),
                        Divider(height: 1, color: Colors.grey[200]),
                        _buildSettingTile(
                          icon: Icons.notifications,
                          title: 'Bildirimler',
                          subtitle: 'Streak hatırlatmaları',
                          onTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Bildirim ayarları çok yakında!'),
                              ),
                            );
                          },
                        ),
                        Divider(height: 1, color: Colors.grey[200]),
                        _buildSettingTile(
                          icon: Icons.person_outline,
                          title: 'Profil Düzenle',
                          subtitle: 'İsim, avatar değiştir',
                          onTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Profil düzenleme çok yakında!'),
                              ),
                            );
                          },
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
                        Divider(height: 1, color: Colors.grey[200]),
                        // 🆕 LOGOUT BUTONU
                        Consumer<AuthProvider>(
                          builder: (context, auth, _) {
                            return _buildSettingTile(
                              icon: Icons.logout,
                              title: 'Çıkış Yap',
                              subtitle: 'Hesaptan çıkış yap',
                              onTap: () {
                                _showLogoutDialog(context, auth);
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
              ? Colors.red.withOpacity(0.1)
              : Colors.blue.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          color: isDestructive ? Colors.red[600] : Colors.blue[600],
          size: 22,
        ),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: isDestructive ? Colors.red[600] : Colors.black87,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          fontSize: 13,
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

  // Reset Dialog
  void _showResetDialog(BuildContext context, GamificationProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('⚠️ İlerlemeyi Sıfırla'),
        content: const Text(
          'Tüm seviye, XP ve streak ilerlemeniz sıfırlanacak. Bu işlem geri alınamaz!\n\nEmin misiniz?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton(
            onPressed: () {
              // İlerlemeyi sıfırla - state'i manuel olarak sıfırla
              // Eğer GamificationProvider'da bu metod yoksa, state'i manuel reset et
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('İlerleme sıfırlama özelliği yakında eklenecek'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Sıfırla'),
          ),
        ],
      ),
    );
  }

  // 🆕 LOGOUT DIALOG
  void _showLogoutDialog(BuildContext context, AuthProvider auth) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('🚪 Çıkış Yap'),
        content: const Text(
          'Hesaptan çıkış yapmak istediğinize emin misiniz?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context); // Dialog kapat
              
              // Logout işlemi
              await auth.logout();
              
              // Login sayfasına yönlendir
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginPage()),
                  (route) => false,
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Çıkış Yap'),
          ),
        ],
      ),
    );
  }
}