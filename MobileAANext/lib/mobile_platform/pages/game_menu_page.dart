import 'package:flutter/material.dart';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'game_matchmaking_page.dart';
import 'game_history_page.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../services/auth_service.dart';
import 'game_play_page.dart';
import 'package:flutter/foundation.dart' show kIsWeb; // 🆕
import 'game_play_page.dart'; // 🆕
import '../../services/auth_service.dart'; // 🆕
import 'dart:io' show Platform; // 🆕

class GameMenuPage extends StatefulWidget {
  const GameMenuPage({Key? key}) : super(key: key);

  @override
  State<GameMenuPage> createState() => _GameMenuPageState();
}

class _GameMenuPageState extends State<GameMenuPage> {
  late Future<GameEligibility> _eligibilityFuture;
  final GameService _gameService = GameService();

  @override
  void initState() {
    super.initState();
    // 🔥 UPDATED: setUserId() çağrısı KALDIRILDI
    // GameService artık otomatik olarak AuthService'den user ID alıyor
    _eligibilityFuture = _gameService.checkEligibility();
  }

  void _findOpponent() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const GameMatchmakingPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Haber Kapışması'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: FutureBuilder<GameEligibility>(
          future: _eligibilityFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator();
            }
            if (snapshot.hasError) {
              return Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'Bir hata oluştu: ${snapshot.error}',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              );
            }
            if (snapshot.hasData) {
              final eligibility = snapshot.data!;
              return _buildContent(eligibility);
            }
            return const Text('Durum bilinmiyor.');
          },
        ),
      ),
    );
  }
Widget _buildContent(GameEligibility eligibility) {
  return Padding(
    padding: const EdgeInsets.symmetric(horizontal: 24.0),
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          eligibility.eligible ? Icons.gamepad_outlined : Icons.info_outline,
          size: 100,
          color: eligibility.eligible ? Colors.green : Colors.amber,
        ),
        const SizedBox(height: 24),
        Text(
          eligibility.eligible ? 'Oyuna Hazırsın!' : 'Henüz Hazır Değilsin',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Text(
          eligibility.message,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 40),
        
        // 🆕 TEST BUTONU (BOT İLE OYNA)
        if (eligibility.eligible) ...[
          ElevatedButton.icon(
            icon: const Icon(Icons.smart_toy),
            label: const Text('🤖 Test: Bot ile Oyna'),
            onPressed: _playWithBot,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30.0),
              ),
            ),
          ),
          const SizedBox(height: 12),
          
          // Mevcut "Rakip Bul" butonu
          ElevatedButton.icon(
            icon: const Icon(Icons.search),
            label: const Text('Rakip Bul'),
            onPressed: _findOpponent,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 18),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30.0),
              ),
            ),
          ),
        ]
        else
          ElevatedButton.icon(
            icon: const Icon(Icons.refresh),
            label: const Text('Tekrar Kontrol Et'),
            onPressed: () {
              setState(() {
                _eligibilityFuture = _gameService.checkEligibility();
              });
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 18),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30.0),
              ),
            ),
          ),
      ],
    ),
  );
}
void _playWithBot() async {
  try {
    // Loading göster
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );
    
    // 🔥 Platform-aware URL
    String baseUrl;
    if (kIsWeb) {
      baseUrl = 'http://localhost:8000'; // Web
    } else if (Platform.isAndroid) {
      baseUrl = 'http://10.0.2.2:8000'; // Android Emulator
    } else if (Platform.isIOS) {
      baseUrl = 'http://localhost:8000'; // iOS Simulator
    } else {
      baseUrl = 'http://localhost:8000'; // Fallback
    }
    
    // Bot match oluştur
    final response = await http.post(
      Uri.parse('$baseUrl/api/game/test/bot-match'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${(await AuthService().getToken())?.accessToken}',
      },
    );
    
    if (!mounted) return;
    
    // Loading kapat
    Navigator.pop(context);
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      
      // Oyun sayfasına git
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => GamePlayPage(gameId: data['game_id']),
        ),
      );
    } else {
      final error = jsonDecode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hata: ${error['detail']}')),
      );
    }
  } catch (e) {
    if (!mounted) return;
    Navigator.pop(context); // Loading kapat
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Hata: $e')),
    );
  }
}

}