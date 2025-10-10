import 'dart:async';
import 'package:flutter/material.dart';
import '../models/game_models.dart';
import '../services/game_service.dart';
import '../pages/game_play_page.dart'; // Dosya yolu projenize göre güncellenecek

class GameMatchmakingPage extends StatefulWidget {
  const GameMatchmakingPage({Key? key}) : super(key: key);

  @override
  _GameMatchmakingPageState createState() => _GameMatchmakingPageState();
}

class _GameMatchmakingPageState extends State<GameMatchmakingPage> with TickerProviderStateMixin {
  final GameService _gameService = GameService();
  late AnimationController _controller;
  String _statusText = "Rakip aranıyor...";
  Timer? _statusTimer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();

    _startStatusUpdates();
    _findMatch();
  }
  
  void _startStatusUpdates() {
    const statuses = [
      "Rakip aranıyor...",
      "En dişli rakipler taranıyor...",
      "Haber arşivleri karşılaştırılıyor...",
      "Neredeyse hazır!"
    ];
    int currentIndex = 0;
    _statusTimer = Timer.periodic(const Duration(seconds: 4), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      setState(() {
        currentIndex = (currentIndex + 1) % statuses.length;
        _statusText = statuses[currentIndex];
      });
    });
  }

  Future<void> _findMatch() async {
    try {
      final response = await _gameService.startMatchmaking();
      if (mounted && response.matched) {
        // Eşleşme bulundu! Oyun ekranına yönlendir.
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => GamePlayPage(gameId: response.gameId!),
          ),
        );
      } else if (mounted) {
        // Eşleşme bulunamadı veya bir sorun oldu.
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response.message)),
        );
        Navigator.pop(context); // Menüye geri dön
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Eşleşme sırasında bir hata oluştu: $e')),
        );
        Navigator.pop(context); // Menüye geri dön
      }
    }
  }

  Future<void> _cancelSearch() async {
    // TODO: game_service'e cancelMatchmaking API çağrısı eklenecek
    // await _gameService.cancelMatchmaking(); 
    if (mounted) {
      Navigator.pop(context);
    }
  }
  
  @override
  void dispose() {
    _controller.dispose();
    _statusTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: WillPopScope(
        onWillPop: () async {
          // Geri tuşuna basıldığında aramayı iptal et
          await _cancelSearch();
          return true;
        },
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              RotationTransition(
                turns: _controller,
                child: Icon(
                  Icons.sync,
                  size: 80,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const SizedBox(height: 40),
              Text(
                _statusText,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 20),
              const Text(
                'Bu işlem birkaç saniye sürebilir.',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 60),
              TextButton(
                onPressed: _cancelSearch,
                child: const Text('Aramayı İptal Et'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}