// lib/main.dart
// ✅ WEB/MOBILE ROUTING ENTEGRASYONU
// Platform-aware: Web için WebReelsFeedPage, Mobile için ReelsFeedPage

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

// Providers
import 'providers/auth_provider.dart';
import 'providers/reels_provider.dart';
import 'providers/gamification_provider.dart';
import 'providers/saved_reels_provider.dart';
import 'providers/chat_provider.dart';
import 'services/audio_service.dart';

// Core
import 'core/theme/app_theme.dart';
import 'core/theme/web_theme.dart';
import 'core/constants/app_constants.dart';
import 'core/utils/platform_utils.dart';

// Mobile Platform Pages & Views
import 'mobile_platform/pages/splash_page.dart';
import 'mobile_platform/pages/home_page_redesigned.dart';
import 'mobile_platform/pages/game_menu_page.dart';
import 'mobile_platform/pages/login_page.dart';
import 'mobile_platform/views/home_view.dart';
import 'mobile_platform/views/profile_view.dart';

// ✅ YENİ: Web Platform Pages
import 'web_platform/pages/web_reels_feed_page.dart';
import 'web_platform/widgets/web_category_dropdown.dart';

// Shared widgets
import 'shared/widgets/reels/category_reel_feed.dart';
import 'mobile_platform/pages/reels_feed_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  
  print('🚀 App starting...');
  print('📱 Platform: ${PlatformUtils.isWeb ? "WEB" : "MOBILE"}');
  
  runApp(const AanextApp());
}

class AanextApp extends StatelessWidget {
  const AanextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Auth Provider
        ChangeNotifierProvider<AuthProvider>(
          create: (_) => AuthProvider(),
        ),
        
        // Audio Service Provider
        ChangeNotifierProvider<AudioService>(
          create: (_) => AudioService(),
        ),
        
        // Reels Provider
        ChangeNotifierProvider<ReelsProvider>(
          create: (_) => ReelsProvider()..loadReels(),
        ),
        
        // Gamification Provider
        ChangeNotifierProvider<GamificationProvider>(
          create: (_) => GamificationProvider()..init(),
        ),
        
        // Saved Reels Provider
        ChangeNotifierProvider<SavedReelsProvider>(
          create: (_) => SavedReelsProvider()..init(),
        ),
        
        // Chat Provider
        ChangeNotifierProvider<ChatProvider>(
          create: (_) => ChatProvider()..init(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'AA-Next',
        theme: PlatformUtils.isWeb ? WebTheme.theme : AppTheme.theme,
        home: const SplashPage(),
      ),
    );
  }
}

// Main Navigator - Auth'dan sonra gelinen sayfa
class MainNavigator extends StatefulWidget {
  const MainNavigator({super.key});

  @override
  State<MainNavigator> createState() => _MainNavigatorState();
}

class _MainNavigatorState extends State<MainNavigator> {
  int _currentIndex = 0;

  // ✅ PLATFORM-AWARE SCREENS
  List<Widget> get _screens => [
    const HomePageRedesigned(),
    // Web ve mobile için farklı sayfalar
    PlatformUtils.isWeb 
        ? const WebReelsFeedPage()  // 🆕 WEB
        : const ReelsFeedPage(),     // 📱 MOBILE
    const GameMenuPage(),
    const ProfileView(),
  ];

  @override
  Widget build(BuildContext context) {
    // Web (PC/tablet) için üstte butonlar, altta nav yok
    final screenSize = PlatformUtils.getScreenSize(context);
    final bool isWebWide = PlatformUtils.isWeb && 
        (screenSize == ScreenSize.desktop || screenSize == ScreenSize.tablet);

    return Scaffold(
      // ✅ Web'de AppBar yok - her sayfa kendi bar'ını yönetir
      body: isWebWide 
          ? _buildWebLayout()
          : IndexedStack(
              index: _currentIndex,
              children: _screens,
            ),
      bottomNavigationBar: isWebWide ? null : _buildMobileBottomNav(),
    );
  }

  // ✅ Web için layout - tüm sayfalar için birleşik navigasyon
  Widget _buildWebLayout() {
    return Scaffold(
      appBar: _buildWebAppBar(),
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
    );
  }

  // ✅ Web için üst navigasyon - birleşik bar
  PreferredSizeWidget _buildWebAppBar() {
    return AppBar(
      automaticallyImplyLeading: false,
      backgroundColor: AppColors.primary, // ✅ Mavi arka plan
      elevation: 0,
      title: Row(
        children: [
          // ✅ Sol: Logo/Başlık
          const Text(
            'AA Next',
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const Spacer(),
          
          // ✅ Orta: Navigasyon Butonları (Centered)
          _TopNavButton(
            label: 'Ana Sayfa',
            icon: Icons.home_outlined,
            selected: _currentIndex == 0,
            onTap: () => setState(() => _currentIndex = 0),
          ),
          const SizedBox(width: 8),
          _TopNavButton(
            label: 'Reels',
            icon: Icons.play_circle_outline,
            selected: _currentIndex == 1,
            onTap: () => setState(() => _currentIndex = 1),
          ),
          const SizedBox(width: 8),
          _TopNavButton(
            label: 'Oyunlar',
            icon: Icons.sports_esports_outlined,
            selected: _currentIndex == 2,
            onTap: () => setState(() => _currentIndex = 2),
          ),
          const SizedBox(width: 8),
          
          // ✅ Kategoriler Dropdown (Oyunlar ve Profil arasında)
          WebCategoryDropdown(
            onCategorySelected: (categoryId, categoryName, categoryIcon, categoryColor) {
              // Kategori seçildiğinde CategoryReelFeed sayfasına git
              CategoryReelFeed.navigateTo(
                context,
                categoryId: categoryId,
                categoryName: categoryName,
                categoryIcon: categoryIcon,
                categoryColor: categoryColor,
              );
            },
          ),
          const SizedBox(width: 8),
          
          _TopNavButton(
            label: 'Profil',
            icon: Icons.person_outline,
            selected: _currentIndex == 3,
            onTap: () => setState(() => _currentIndex = 3),
          ),
          
          const Spacer(),
        ],
      ),
    );
  }

  // Mobile için alt navigasyon
  Widget _buildMobileBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.primary, // ✅ Mavi arka plan
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        backgroundColor: AppColors.primary, // ✅ Mavi arka plan
        selectedItemColor: Colors.white, // ✅ Seçili renk beyaz
        unselectedItemColor: Colors.white.withOpacity(0.6), // ✅ Seçili olmayan beyaz şeffaf
        selectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
        unselectedLabelStyle: const TextStyle(
          fontSize: 11,
        ),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Ana Sayfa',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.play_circle_outline),
            activeIcon: Icon(Icons.play_circle),
            label: 'Reels',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.sports_esports_outlined),
            activeIcon: Icon(Icons.sports_esports),
            label: 'Oyunlar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profil',
          ),
        ],
      ),
    );
  }
}

// ✅ Navigasyon butonu widget
class _TopNavButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _TopNavButton({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = selected ? Colors.white : Colors.white.withOpacity(0.7);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: TextButton.icon(
        onPressed: onTap,
        style: TextButton.styleFrom(
          foregroundColor: color,
          backgroundColor: selected 
              ? Colors.white.withOpacity(0.15) 
              : Colors.transparent,
          overlayColor: Colors.white.withOpacity(0.1),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        icon: Icon(icon, color: color, size: 20),
        label: Text(
          label,
          style: TextStyle(
            color: color,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}

// Placeholder View - Henüz geliştirilmemiş sayfalar için
class PlaceholderView extends StatelessWidget {
  final String title;
  final String icon;

  const PlaceholderView({
    super.key,
    required this.title,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              icon,
              style: const TextStyle(fontSize: 80),
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Yakında geliyor...',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}