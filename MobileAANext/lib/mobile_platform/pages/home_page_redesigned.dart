// lib/mobile_platform/pages/home_page_redesigned.dart
// 🏠 Ana Sayfa - YENİ TASARIM

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/aa_colors.dart';
import '../../core/utils/platform_utils.dart'; // ✅ Responsive için
import '../../providers/gamification_provider.dart';
import '../../shared/widgets/home/streak_github_calendar.dart';
import '../../shared/widgets/home/level_progress_card.dart';
import '../../shared/widgets/home/daily_goal_ring.dart';
import '../../shared/widgets/home/category_bubble_menu.dart';
import '../../shared/widgets/reels/category_reel_feed.dart';

class HomePageRedesigned extends StatefulWidget {
  const HomePageRedesigned({Key? key}) : super(key: key);

  @override
  State<HomePageRedesigned> createState() => _HomePageRedesignedState();
}

class _HomePageRedesignedState extends State<HomePageRedesigned> {
  bool _showCategoryMenu = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final gamification = context.read<GamificationProvider>();
    await gamification.init();
    // TODO: Streak data yükle (backend entegrasyonu)
    debugPrint('✅ Home page data loaded');
  }

  void _onCategorySelected(String categoryId) {
    debugPrint('📂 Category selected: $categoryId');

    // Kategori bilgilerini al
    final categoryMap = _getCategoryInfo(categoryId);

    // Kategori feed sayfasına git
    CategoryReelFeed.navigateTo(
      context,
      categoryId: categoryId,
      categoryName: categoryMap['name'],
      categoryIcon: categoryMap['icon'],
      categoryColor: categoryMap['color'],
    );
  }

  Map<String, dynamic> _getCategoryInfo(String categoryId) {
    final categories = {
      'guncel': {'name': 'Güncel', 'icon': '📰', 'color': AAColors.catGuncel},
      'ekonomi': {'name': 'Ekonomi', 'icon': '💰', 'color': AAColors.catEkonomi},
      'spor': {'name': 'Spor', 'icon': '⚽', 'color': AAColors.catSpor},
      'teknoloji': {'name': 'Teknoloji', 'icon': '💻', 'color': AAColors.catTeknoloji},
      'kultur': {'name': 'Kültür', 'icon': '🎨', 'color': AAColors.catKultur},
      'dunya': {'name': 'Dünya', 'icon': '🌍', 'color': AAColors.catDunya},
      'politika': {'name': 'Politika', 'icon': '🏛️', 'color': AAColors.catPolitika},
      'saglik': {'name': 'Sağlık', 'icon': '🏥', 'color': AAColors.catSaglik},
    };
    return categories[categoryId] ?? categories['guncel']!;
  }

  @override
  Widget build(BuildContext context) {
    // ✅ Responsive layout kontrolü
    final screenSize = PlatformUtils.getScreenSize(context);
    final isDesktop = screenSize == ScreenSize.desktop;
    final isTablet = screenSize == ScreenSize.tablet;
    final isWideScreen = isDesktop || isTablet;
    
    // ✅ Responsive padding
    final padding = isDesktop ? 32.0 : (isTablet ? 24.0 : 16.0);
    
    // ✅ Web desktop'ta AppBar main.dart'tan gelir
    final showAppBar = !PlatformUtils.isWeb || !(isDesktop || isTablet);
    
    return Scaffold(
      backgroundColor: AAColors.grey50,
      appBar: showAppBar ? _buildAppBar() : null,
      body: Stack(
        children: [
          // Ana içerik - ✅ Responsive center layout
          Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: isDesktop ? 1400 : double.infinity,
              ),
              child: RefreshIndicator(
                onRefresh: _loadData,
                color: AAColors.aaRed, // ✅ Artık mavi
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Padding(
                    padding: EdgeInsets.all(padding),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Hoşgeldin
                        _buildWelcomeSection(),

                        const SizedBox(height: 24),

                        // ✅ RESPONSIVE LAYOUT: Web PC için yan yana
                        if (isWideScreen)
                          Consumer<GamificationProvider>(
                            builder: (context, gamification, _) {
                              final mockCalendarData = <String, dynamic>{};
                              return Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Sol: Streak Calendar
                                  Expanded(
                                    flex: 2,
                                    child: StreakGithubCalendar(
                                      calendarData: mockCalendarData,
                                      currentStreak: gamification.currentStreak,
                                      longestStreak: 30,
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  // Sağ: Daily Goal Ring
                                  Expanded(
                                    flex: 1,
                                    child: DailyGoalRing(
                                      xpEarnedToday: gamification.state.xpEarnedToday,
                                      dailyGoal: gamification.dailyXPGoal,
                                      goalCompleted: gamification.dailyGoalCompleted,
                                    ),
                                  ),
                                ],
                              );
                            },
                          )
                        else
                          // ✅ Mobile Layout: Dikey
                          Consumer<GamificationProvider>(
                            builder: (context, gamification, _) {
                              final mockCalendarData = <String, dynamic>{};
                              return Column(
                                children: [
                                  // Streak Calendar
                                  StreakGithubCalendar(
                                    calendarData: mockCalendarData,
                                    currentStreak: gamification.currentStreak,
                                    longestStreak: 30,
                                  ),
                                  const SizedBox(height: 16),
                                  // Daily Goal Ring
                                  DailyGoalRing(
                                    xpEarnedToday: gamification.state.xpEarnedToday,
                                    dailyGoal: gamification.dailyXPGoal,
                                    goalCompleted: gamification.dailyGoalCompleted,
                                  ),
                                ],
                              );
                            },
                          ),

                        const SizedBox(height: 16),

                        // Level Progress
                        Consumer<GamificationProvider>(
                          builder: (context, gamification, _) {
                            return LevelProgressCard(
                              currentLevel: gamification.currentLevel,
                              currentNode: gamification.currentNode,
                              nodesInLevel: gamification.state.nodesInLevel,
                              currentXP: gamification.currentXP,
                              totalXP: gamification.state.totalXP,
                            );
                          },
                        ),

                        const SizedBox(height: 24),

                        // Kategori Buton - Sadece mobilde göster (Web'de üst barda)
                        if (!isWideScreen)
                          _buildCategoryButton(),

                        const SizedBox(height: 100), // Alt navigasyon için boşluk
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),

          // Kategori Bubble Menu (Overlay)
          if (_showCategoryMenu)
            CategoryBubbleMenu(
              onCategorySelected: (categoryId) {
                setState(() => _showCategoryMenu = false);
                _onCategorySelected(categoryId);
              },
            ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      title: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: const BoxDecoration(
              gradient: AAColors.redGradient,
              shape: BoxShape.circle,
            ),
            child: const Center(
              child: Text(
                'AA',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          const Text(
            'AA Next',
            style: TextStyle(
              color: Color(0xFF1A1A1A),
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: Icon(Icons.notifications_outlined, color: AAColors.grey700),
          onPressed: () {
            // TODO: Bildirimler
          },
        ),
      ],
    );
  }

  Widget _buildWelcomeSection() {
    final hour = DateTime.now().hour;
    String greeting = 'Merhaba';
    if (hour < 12) {
      greeting = 'Günaydın';
    } else if (hour < 18) {
      greeting = 'İyi günler';
    } else {
      greeting = 'İyi akşamlar';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          greeting,
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: AAColors.black,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Günlük hedeflerini tamamla, seviye atla! 🚀',
          style: TextStyle(
            fontSize: 14,
            color: AAColors.grey500,
          ),
        ),
      ],
    );
  }

  Widget _buildCategoryButton() {
    return GestureDetector(
      onTap: () {
        setState(() => _showCategoryMenu = true);
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: AAColors.redGradient,
          borderRadius: BorderRadius.circular(16),
          boxShadow: AAColors.buttonShadow,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.apps, color: Colors.white, size: 28),
            SizedBox(width: 12),
            Text(
              'Kategorilere Göz At',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Spacer(),
            Icon(Icons.arrow_forward_ios, color: Colors.white, size: 20),
          ],
        ),
      ),
    );
  }
}