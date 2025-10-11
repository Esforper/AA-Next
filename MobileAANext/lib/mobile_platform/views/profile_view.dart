// lib/views/profile_view.dart
// Auth entegrasyonu + Logout butonu eklendi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/utils/platform_utils.dart';
import '../../providers/gamification_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/saved_reels_provider.dart';
import '../../shared/widgets/gamification/level_chain_display.dart';
import '../../shared/widgets/gamification/streak_display.dart';
import '../../shared/widgets/gamification/daily_progress_card.dart';
import '../pages/login_page.dart';
import 'saved_reels_view.dart';

/// Profile View - Kullanıcı profili ve istatistikler
class ProfileView extends StatelessWidget {
  const ProfileView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // ✅ Platform ve ekran boyutu kontrolü
    final screenSize = PlatformUtils.getScreenSize(context);
    final isWebWide = PlatformUtils.isWeb && 
        (screenSize == ScreenSize.desktop || screenSize == ScreenSize.tablet);
    
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: CustomScrollView(
        slivers: [
          // ✅ Mobil: SliverAppBar ile profil
          if (!isWebWide)
          SliverAppBar(
            expandedHeight: 200,
            floating: false,
            pinned: true,
            elevation: 0,
            backgroundColor: Colors.blue[600],
            flexibleSpace: FlexibleSpaceBar(
                background: _buildMobileProfileHeader(context),
              ),
            ),

          // ✅ Content - Responsive ve ortalanmış
          SliverToBoxAdapter(
            child: Center(
              child: Container(
                constraints: BoxConstraints(
                  maxWidth: isWebWide ? 1200 : double.infinity,
                ),
                padding: EdgeInsets.all(isWebWide ? 32 : 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // ✅ Web: Profil kartı (üstte)
                    if (isWebWide) ...[
                      _buildWebProfileCard(context),
                      const SizedBox(height: 32),
                    ],
                    // ✅ Level ve Streak Display - Responsive ve ortalanmış
                    Consumer<GamificationProvider>(
                      builder: (context, provider, _) {
                        return _buildLevelAndStreakSection(provider, isWebWide);
                      },
                    ),


                    const SizedBox(height: 24),

                    // ✅ Günlük İlerleme + Bugünün İstatistikleri
                    Consumer<GamificationProvider>(
                      builder: (context, provider, _) {
                        return _buildDailyStatsSection(provider, isWebWide);
                      },
                    ),


                    const SizedBox(height: 24),

                    // ✅ Settings Section
                    _buildSectionHeader('⚙️', 'Ayarlar'),
                    const SizedBox(height: 12),
                    _buildSettingsSection(context),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ✅ Mobil: Profil header
  Widget _buildMobileProfileHeader(BuildContext context) {
    return Container(
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
    );
  }

  // ✅ Web: Profil kartı (kullanıcı dostu ve işlevsel)
  Widget _buildWebProfileCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.blue[50]!,
            Colors.white,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.blue[100]!,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.1),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Consumer2<AuthProvider, GamificationProvider>(
        builder: (context, auth, gamification, _) {
          final displayName = auth.user?.fullName ?? 
                             auth.user?.username ?? 
                             'Kullanıcı';
          
          return Row(
            children: [
              // Avatar with edit button
              Stack(
                children: [
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.blue[600]!,
                        width: 3,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.blue.withOpacity(0.3),
                          blurRadius: 16,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: CircleAvatar(
                      radius: 50,
                      backgroundColor: Colors.grey[200],
                      child: auth.user?.avatarUrl != null
                          ? ClipOval(
                              child: Image.network(
                                auth.user!.avatarUrl!,
                                width: 100,
                                height: 100,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) => const Text(
                                  '👤',
                                  style: TextStyle(fontSize: 50),
                                ),
                              ),
                            )
                          : const Text(
                              '👤',
                              style: TextStyle(fontSize: 50),
                            ),
                    ),
                  ),
                  // Edit avatar button
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Material(
                      color: Colors.blue[600],
                      borderRadius: BorderRadius.circular(20),
                      elevation: 4,
                      child: InkWell(
                        onTap: () => _showAvatarPickerDialog(context),
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          child: const Icon(
                            Icons.camera_alt,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 32),
              
              // Bilgiler
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            displayName,
                            style: const TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                              letterSpacing: -0.5,
                            ),
                          ),
                        ),
                        // Edit profile button
                        ElevatedButton.icon(
                          onPressed: () => _showEditProfileDialog(context, auth),
                          icon: const Icon(Icons.edit, size: 18),
                          label: const Text('Profili Düzenle'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue[600],
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 12,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            elevation: 2,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (auth.user?.email != null)
                      Row(
                        children: [
                          Icon(Icons.email_outlined, 
                            size: 16, 
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 6),
                          Text(
                            auth.user!.email,
                            style: TextStyle(
                              fontSize: 15,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _buildAnimatedInfoChip(
                          icon: Icons.bolt,
                          label: 'Level ${gamification.currentLevel}',
                          value: '${gamification.currentNode}/${gamification.state.nodesInLevel} node',
                          color: Colors.amber,
                        ),
                        _buildAnimatedInfoChip(
                          icon: Icons.stars,
                          label: '${gamification.state.totalXP} XP',
                          value: 'Toplam',
                          color: Colors.purple,
                        ),
                        _buildAnimatedInfoChip(
                          icon: Icons.local_fire_department,
                          label: '${gamification.currentStreak} gün',
                          value: 'Seri',
                          color: Colors.orange,
                        ),
                        _buildAnimatedInfoChip(
                          icon: Icons.emoji_events,
                          label: '${gamification.state.reelsWatchedToday} haber',
                          value: 'Bugün',
                          color: Colors.green,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  // ✅ Animasyonlu info chip (web için)
  Widget _buildAnimatedInfoChip({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    final darkColor = Color.fromRGBO(
      (color.red * 0.7).toInt(),
      (color.green * 0.7).toInt(),
      (color.blue * 0.7).toInt(),
      1,
    );
    
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              color.withOpacity(0.15),
              color.withOpacity(0.08),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: color.withOpacity(0.4),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.2),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, size: 20, color: darkColor),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: darkColor,
                      ),
                    ),
                    Text(
                      value,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ✅ Avatar picker dialog (frontend only)
  void _showAvatarPickerDialog(BuildContext context) {
    // Mock avatar listesi
    final avatars = [
      '👤', '😊', '😎', '🤓', '🥳', '🤩',
      '😇', '🤗', '🥰', '😁', '🙂', '🤔',
      '👨‍💼', '👩‍💼', '👨‍🎓', '👩‍🎓', '👨‍💻', '👩‍💻',
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.face, color: Colors.blue[600]),
            const SizedBox(width: 12),
            const Text('Avatar Seç'),
          ],
        ),
        content: SizedBox(
          width: 400,
          height: 300,
          child: GridView.builder(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 6,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
            ),
            itemCount: avatars.length,
            itemBuilder: (context, index) {
              return InkWell(
                onTap: () {
                  // Frontend only - sadece görsel güncelleme
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Avatar seçildi: ${avatars[index]}'),
                      backgroundColor: Colors.green,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                  Navigator.pop(context);
                },
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.blue[200]!,
                      width: 2,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      avatars[index],
                      style: const TextStyle(fontSize: 32),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
        ],
      ),
    );
  }

  // ✅ Profil düzenleme dialog (frontend only)
  void _showEditProfileDialog(BuildContext context, AuthProvider auth) {
    final nameController = TextEditingController(
      text: auth.user?.fullName ?? auth.user?.username ?? '',
    );
    final usernameController = TextEditingController(
      text: auth.user?.username ?? '',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.edit, color: Colors.blue[600]),
            const SizedBox(width: 12),
            const Text('Profili Düzenle'),
          ],
        ),
        content: SizedBox(
          width: 500,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Ad Soyad',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: nameController,
                decoration: InputDecoration(
                  hintText: 'Adınız ve soyadınız',
                  prefixIcon: const Icon(Icons.person),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey[50],
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Kullanıcı Adı',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: usernameController,
                decoration: InputDecoration(
                  hintText: 'Kullanıcı adınız',
                  prefixIcon: const Icon(Icons.alternate_email),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey[50],
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.blue[200]!,
                    width: 1,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, 
                      color: Colors.blue[700], 
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Değişiklikler sadece bu oturumda geçerlidir (Frontend demo)',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              // Frontend only - sadece görsel güncelleme
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Profil güncellendi: ${nameController.text}',
                  ),
                  backgroundColor: Colors.green,
                  behavior: SnackBarBehavior.floating,
                  action: SnackBarAction(
                    label: 'Tamam',
                    textColor: Colors.white,
                    onPressed: () {},
                  ),
                ),
              );
              Navigator.pop(context);
            },
            icon: const Icon(Icons.check),
            label: const Text('Kaydet'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[600],
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  // ✅ Level ve Streak Section
  Widget _buildLevelAndStreakSection(GamificationProvider provider, bool isWebWide) {
    if (isWebWide) {
      // Web: Yan yana, ortalanmış - 4/5 ve 1/5 oranında
      return IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
            // Level Display - 4/5 oran
                            Expanded(
              flex: 4,
                              child: LevelChainDisplay(
                                currentLevel: provider.currentLevel,
                                currentNode: provider.currentNode,
                                totalNodes: provider.state.nodesInLevel,
                                currentXP: provider.currentXP,
                              ),
                            ),
                            const SizedBox(width: 16),
            // Streak Display - 1/5 oran
                            Expanded(
              flex: 1,
                              child: StreakDisplay(
                                streakDays: provider.currentStreak,
                                percentile: provider.state.streakPercentile,
                              ),
                            ),
                          ],
        ),
                        );
                      }
                      
    // Mobil: Alt alta
                      return Column(
                        children: [
                          LevelChainDisplay(
                            currentLevel: provider.currentLevel,
                            currentNode: provider.currentNode,
                            totalNodes: provider.state.nodesInLevel,
                            currentXP: provider.currentXP,
                          ),
                          const SizedBox(height: 24),
                          StreakDisplay(
                            streakDays: provider.currentStreak,
                            percentile: provider.state.streakPercentile,
                          ),
                        ],
                      );
  }

  // ✅ Günlük stats section
  Widget _buildDailyStatsSection(GamificationProvider provider, bool isWebWide) {
    if (isWebWide) {
      // Web: Yan yana
                        return Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: DailyProgressCard(
                                currentXP: provider.state.xpEarnedToday,
                                goalXP: provider.dailyXPGoal,
                                streakDays: provider.currentStreak,
                                percentile: provider.state.streakPercentile,
                                goalCompleted: provider.dailyGoalCompleted,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  _buildSectionHeader('📊', 'Bugünün İstatistikleri'),
                                  const SizedBox(height: 12),
                                  _buildTodayStatsCard(provider),
                                ],
                              ),
                            ),
                          ],
                        );
                      }
                      
                      // Mobil: Alt alta
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          DailyProgressCard(
                            currentXP: provider.state.xpEarnedToday,
                            goalXP: provider.dailyXPGoal,
                            streakDays: provider.currentStreak,
                            percentile: provider.state.streakPercentile,
                            goalCompleted: provider.dailyGoalCompleted,
                          ),
                          const SizedBox(height: 24),
                          _buildSectionHeader('📊', 'Bugünün İstatistikleri'),
                          const SizedBox(height: 12),
                          _buildTodayStatsCard(provider),
                        ],
                      );
  }

  // ✅ Settings section
  Widget _buildSettingsSection(BuildContext context) {
    return Container(
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
      child: Consumer<SavedReelsProvider>(
        builder: (context, savedProvider, _) {
          return Column(
            children: [
              _buildSettingTile(
                icon: Icons.bookmark,
                title: 'Kaydedilenler',
                subtitle: '${savedProvider.savedReels.length} kayıtlı haber',
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
                icon: Icons.notifications_active,
                title: 'Bildirimler',
                subtitle: 'Streak hatırlatmaları',
                onTap: () => _showNotificationSettingsDialog(context),
              ),
              Divider(height: 1, color: Colors.grey[200]),
              Consumer<AuthProvider>(
                builder: (context, auth, _) {
                  return _buildSettingTile(
                    icon: Icons.person,
                    title: 'Profil Düzenle',
                    subtitle: 'İsim ve avatar değiştir',
                    onTap: () => _showEditProfileDialog(context, auth),
                  );
                },
              ),
              Divider(height: 1, color: Colors.grey[200]),
              _buildSettingTile(
                icon: Icons.palette,
                title: 'Tema Ayarları',
                subtitle: 'Görünüm ve renkler',
                onTap: () => _showThemeSettingsDialog(context),
              ),
              Divider(height: 1, color: Colors.grey[200]),
              Consumer<GamificationProvider>(
                builder: (context, provider, _) {
                  return _buildSettingTile(
                    icon: Icons.restore,
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
          );
        },
      ),
    );
  }

  // ✅ Bildirim ayarları dialog (frontend only)
  void _showNotificationSettingsDialog(BuildContext context) {
    bool dailyReminder = true;
    bool streakAlert = true;
    bool newsAlert = false;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Row(
            children: [
              Icon(Icons.notifications, color: Colors.blue[600]),
              const SizedBox(width: 12),
              const Text('Bildirim Ayarları'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SwitchListTile(
                value: dailyReminder,
                onChanged: (value) => setState(() => dailyReminder = value),
                title: const Text('Günlük Hatırlatma'),
                subtitle: const Text('Her gün saat 20:00\'de'),
                activeColor: Colors.blue[600],
              ),
              SwitchListTile(
                value: streakAlert,
                onChanged: (value) => setState(() => streakAlert = value),
                title: const Text('Streak Uyarısı'),
                subtitle: const Text('Serini kaybetmeden önce'),
                activeColor: Colors.orange,
              ),
              SwitchListTile(
                value: newsAlert,
                onChanged: (value) => setState(() => newsAlert = value),
                title: const Text('Yeni Haber Bildirimleri'),
                subtitle: const Text('Yeni haberler eklendiğinde'),
                activeColor: Colors.green,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('İptal'),
            ),
            ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Bildirim ayarları kaydedildi! (Frontend demo)'),
                    backgroundColor: Colors.green,
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                Navigator.pop(context);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[600],
              ),
              child: const Text('Kaydet'),
            ),
          ],
        ),
      ),
    );
  }

  // ✅ Tema ayarları dialog (frontend only)
  void _showThemeSettingsDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.palette, color: Colors.blue[600]),
            const SizedBox(width: 12),
            const Text('Tema Ayarları'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildThemeOption(
              context,
              'Açık Tema',
              Icons.light_mode,
              Colors.orange,
              () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Açık tema seçildi (Frontend demo)'),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                Navigator.pop(context);
              },
            ),
            const SizedBox(height: 12),
            _buildThemeOption(
              context,
              'Koyu Tema',
              Icons.dark_mode,
              Colors.purple,
              () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Koyu tema yakında gelecek!'),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                Navigator.pop(context);
              },
            ),
            const SizedBox(height: 12),
            _buildThemeOption(
              context,
              'Sistem Teması',
              Icons.settings_suggest,
              Colors.blue,
              () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Sistem teması seçildi (Frontend demo)'),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildThemeOption(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
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

  // 🆕 YENİ: Bugünün istatistikleri kartı
  Widget _buildTodayStatsCard(GamificationProvider provider) {
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
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: isDestructive
                        ? [
                            Colors.red.withOpacity(0.15),
                            Colors.red.withOpacity(0.08),
                          ]
                        : [
                            Colors.blue.withOpacity(0.15),
                            Colors.blue.withOpacity(0.08),
                          ],
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isDestructive
                        ? Colors.red.withOpacity(0.3)
                        : Colors.blue.withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
                child: Icon(
                  icon,
                  color: isDestructive ? Colors.red[700] : Colors.blue[700],
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: isDestructive ? Colors.red[700] : Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right_rounded,
                color: Colors.grey[400],
                size: 24,
              ),
            ],
          ),
        ),
      ),
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