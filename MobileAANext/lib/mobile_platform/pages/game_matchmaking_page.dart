import 'dart:async';
import 'package:flutter/material.dart';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'game_play_page.dart';

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
  Timer? _pollingTimer;
  int _elapsedSeconds = 0;
  bool _isSearching = true;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();

    _startStatusUpdates();
    _startMatchmaking();
  }
  
  // Matchmaking'i başlat
  Future<void> _startMatchmaking() async {
    try {
      print('🎮 Starting matchmaking...');
      
      // 1. Queue'ya katıl
      final response = await _gameService.joinMatchmaking(); // ✅ DOĞRU FONKSİYON
      
      if (!mounted) return;
      
      print('📡 Queue response: matched=${response.matched}, success=${response.success}');
      
      if (response.matched) {
        // ✅ Hemen eşleşme bulundu!
        print('✅ Immediate match found!');
        _navigateToGame(response.gameId!);
      } else if (response.success) {
        // ⏳ Queue'ya eklendi, polling başlat
        print('⏳ Added to queue, starting polling...');
        _startPolling();
      } else {
        // ❌ Hata
        print('❌ Error: ${response.message}');
        _showError(response.message);
      }
    } catch (e) {
      print('❌ Matchmaking start error: $e');
      if (mounted) {
        _showError('Eşleşme başlatılamadı: $e');
      }
    }
  }

  // Polling başlat (her 3 saniyede kontrol)
  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
      if (!mounted || !_isSearching) {
        timer.cancel();
        return;
      }
      
      _elapsedSeconds += 3;
      print('⏱️ Polling... elapsed: $_elapsedSeconds seconds');
      
      // 60 saniye timeout
      if (_elapsedSeconds >= 60) {
        timer.cancel();
        print('⏱️ Timeout reached!');
        if (mounted) {
          await _gameService.cancelMatchmaking();
          _showError('Rakip bulunamadı. Lütfen daha fazla haber izleyin.');
        }
        return;
      }
      
      try {
        // Backend'den durum kontrol et
        final status = await _gameService.getMatchmakingStatus(); // ✅ DOĞRU FONKSİYON
        
        if (!mounted) return;
        
        print('📊 Status check: matched=${status.matched}, in_queue=${status.inQueue}');
        
        if (status.matched) { // ✅ DOĞRU PROPERTY
          // ✅ Eşleşme bulundu!
          timer.cancel();
          print('🎉 Match found! Game ID: ${status.gameId}');
          _navigateToGame(status.gameId!); // ✅ DOĞRU PROPERTY
        }
        // Eşleşme yoksa devam et (polling devam eder)
        
      } catch (e) {
        print('❌ Polling error: $e');
        // Hata olsa da polling devam eder
      }
    });
  }

  // Oyun ekranına git
  void _navigateToGame(String gameId) {
    if (!mounted) return;
    _isSearching = false;
    _pollingTimer?.cancel();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => GamePlayPage(gameId: gameId),
      ),
    );
  }

  // Hata göster ve geri dön
  void _showError(String message) {
    if (!mounted) return;
    _isSearching = false;
    _pollingTimer?.cancel();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
    Navigator.pop(context);
  }

  // Aramayı iptal et
  Future<void> _cancelSearch() async {
    print('🛑 Cancelling search...');
    _isSearching = false;
    _pollingTimer?.cancel();
    
    try {
      await _gameService.cancelMatchmaking();
    } catch (e) {
      print('❌ Cancel error: $e');
    }
    
    if (mounted) {
      Navigator.pop(context);
    }
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

  // ❌ GEREKSİZ - SİLİNDİ
  // Future<void> _findMatch() async { ... }
  
  @override
  void dispose() {
    _controller.dispose();
    _statusTimer?.cancel();
    _pollingTimer?.cancel();
    _isSearching = false;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: WillPopScope(
        onWillPop: () async {
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
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              const Text(
                'Bu işlem 60 saniye sürebilir.',
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