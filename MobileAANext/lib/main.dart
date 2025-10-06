// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/reels_provider.dart';
import 'pages/reels_feed_page.dart';

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
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'AA-Next Reels',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
          useMaterial3: true,
        ),
        home: const ReelsFeedPage(),
      ),
    );
  }
}
