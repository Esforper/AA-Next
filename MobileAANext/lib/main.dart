// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'providers/reels_provider.dart';
import 'pages/splash_page.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

void main() async {
  await dotenv.load(fileName: ".env");
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AanextApp());
}
class AanextApp extends StatelessWidget {
  const AanextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // Auth Provider - İlk sırada (diğer provider'lar buna bağımlı olabilir)
        ChangeNotifierProvider<AuthProvider>(
          create: (_) => AuthProvider(),
        ),
        
        // Reels Provider
        ChangeNotifierProvider<ReelsProvider>(
          create: (_) => ReelsProvider()..loadReels(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'AA-Next Reels',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
          useMaterial3: true,
          // Input decoration theme (tüm app için)
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        // İlk ekran: SplashPage (token kontrolü yapar)
        home: const SplashPage(),
      ),
    );
  }
}