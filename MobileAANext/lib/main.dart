// lib/main.dart
// GÜNCELLEME: SavedReelsProvider + ChatProvider eklendi

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/reels_provider.dart';
import 'providers/gamification_provider.dart';
import 'providers/saved_reels_provider.dart'; // 🆕
import 'providers/chat_provider.dart'; // 🆕
import 'pages/reels_feed_page.dart';
import 'views/home_view.dart';
import 'views/profile_view.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AanextApp());
}

class AanextApp extends StatelessWidget {
  const AanextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<ReelsProvider>(
          create: (_) => ReelsProvider()..loadReels(),
        ),
        ChangeNotifierProvider<GamificationProvider>(
          create: (_) => GamificationProvider()..init(),
        ),
        // 🆕 Saved Reels Provider
        ChangeNotifierProvider<SavedReelsProvider>(
          create: (_) => SavedReelsProvider()..init(),
        ),
        // 🆕 Chat Provider
        ChangeNotifierProvider<ChatProvider>(
          create: (_) => ChatProvider()..init(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'AA-Next',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
          useMaterial3: true,
        ),
        home: const MainNavigator(),
      ),
    );
  }
}

// Main Navigator
class MainNavigator extends StatefulWidget {
  const MainNavigator({super.key});

  @override
  State<MainNavigator> createState() => _MainNavigatorState();
}

class _MainNavigatorState extends State<MainNavigator> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeView(),
    const ReelsFeedPage(),
    const PlaceholderView(title: 'Oyunlar', icon: '🎮'),
    const ProfileView(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
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
          backgroundColor: Colors.white,
          selectedItemColor: Colors.indigo[600],
          unselectedItemColor: Colors.grey[400],
          selectedLabelStyle: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 12,
          ),
          unselectedLabelStyle: const TextStyle(
            fontWeight: FontWeight.w500,
            fontSize: 11,
          ),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined, size: 26),
              activeIcon: Icon(Icons.home, size: 26),
              label: 'Ana Sayfa',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.play_circle_outline, size: 26),
              activeIcon: Icon(Icons.play_circle, size: 26),
              label: 'Reels',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.gamepad_outlined, size: 26),
              activeIcon: Icon(Icons.gamepad, size: 26),
              label: 'Oyunlar',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline, size: 26),
              activeIcon: Icon(Icons.person, size: 26),
              label: 'Profil',
            ),
          ],
        ),
      ),
    );
  }
}

// Placeholder View
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
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text(title),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
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
              '$title çok yakında!',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Bu özellik üzerinde çalışıyoruz',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      ),
    );
  }
}