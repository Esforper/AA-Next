// lib/main.dart
// Auth entegrasyonu + Splash ekranı + Audio Service eklendi

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

// Core (Yeni eklenenler)
import 'core/theme/app_theme.dart';
import 'core/theme/web_theme.dart';
import 'core/constants/app_constants.dart';
import 'core/utils/platform_utils.dart';

// Mobile Platform Pages & Views (Doğru path'ler)
import 'mobile_platform/pages/splash_page.dart';
import 'mobile_platform/pages/reels_feed_page.dart';
import 'mobile_platform/pages/login_page.dart';
import 'mobile_platform/pages/game_menu_page.dart';
import 'mobile_platform/views/home_view.dart';
import 'mobile_platform/views/profile_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(const AanextApp());
}

class AanextApp extends StatelessWidget {
  const AanextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Auth Provider - İlk sırada
        ChangeNotifierProvider<AuthProvider>(
          create: (_) => AuthProvider(),
        ),
        
        // Audio Service Provider (ReelsProvider'dan ÖNCE!)
        ChangeNotifierProvider<AudioService>(
          create: (_) => AudioService(),
        ),
        
        // Reels Provider - Audio service'i kullanıyor
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
        // Platform-aware theme
        theme: PlatformUtils.isWeb ? WebTheme.theme : AppTheme.theme,
        // ⚠️ ÖNEMLİ: SplashPage ile başla (auth kontrolü için)
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

  // 🔽 DEĞİŞİKLİK BURADA 🔽
  final List<Widget> _screens = [
    const HomeView(),
    const ReelsFeedPage(),
    const GameMenuPage(), // ✅ Placeholder yerine GameMenuPage geldi
    const ProfileView(),
  ];
  // 🔼 DEĞİŞİKLİK BURADA 🔼

  @override
  Widget build(BuildContext context) {
    // Web (PC/tablet) için üstte butonlar, altta nav yok
    final screenSize = PlatformUtils.getScreenSize(context);
    final bool isWebWide = PlatformUtils.isWeb && (screenSize == ScreenSize.desktop || screenSize == ScreenSize.tablet);

    return Scaffold(
      appBar: isWebWide
          ? AppBar(
              automaticallyImplyLeading: false,
              centerTitle: true,
              title: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
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
                  _TopNavButton(
                    label: 'Profil',
                    icon: Icons.person_outline,
                    selected: _currentIndex == 3,
                    onTap: () => setState(() => _currentIndex = 3),
                  ),
                ],
              ),
            )
          : null,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: isWebWide ? null : Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: AppColors.surface,
          selectedItemColor: AppColors.primary,
          unselectedItemColor: AppColors.textTertiary,
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
      ),
    );
  }
}

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
    final color = selected ? Colors.white : Colors.white.withValues(alpha: 0.8);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 6),
      child: TextButton.icon(
        onPressed: onTap,
        style: TextButton.styleFrom(
          foregroundColor: color,
          overlayColor: Colors.white.withValues(alpha: 0.1),
        ),
        icon: Icon(icon, color: color, size: 20),
        label: Text(
          label,
          style: TextStyle(
            color: color,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
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