import 'package:flutter/material.dart';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'game_matchmaking_page.dart';

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
          if (eligibility.eligible)
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
            )
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
}