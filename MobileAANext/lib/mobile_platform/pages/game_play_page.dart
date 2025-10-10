import 'package:flutter/material.dart';
import 'dart:async';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'game_result_page.dart';
import '../../services/auth_service.dart';
class GamePlayPage extends StatefulWidget {
  final String gameId;
  const GamePlayPage({super.key, required this.gameId});

  @override
  State<GamePlayPage> createState() => _GamePlayPageState();
}

class _GamePlayPageState extends State<GamePlayPage> {
  final GameService _gameService = GameService();
  final AuthService _authService = AuthService();

  bool _isLoading = true;
  String? _errorMessage;
  GameSession? _session;
  GameQuestion? _currentQuestion;
  String? _selectedOption;
  int _currentRound = 0;

  @override
  void initState() {
    super.initState();
    _initializeGame();
  }

  Future<void> _initializeGame() async {
    try {
      // 🔥 UPDATED: setUserId() çağrısı KALDIRILDI
      // GameService artık otomatik olarak AuthService'den user ID alıyor
      
      final session = await _gameService.getGameStatus(widget.gameId);
      if (!mounted) return;
      setState(() {
        _session = session;
      });
      _fetchQuestion(0);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = "Oyun yüklenemedi: $e";
      });
    }
  }

  Future<void> _fetchQuestion(int round) async {
    if (round >= (_session?.totalRounds ?? 8)) {
      _endGame();
      return;
    }
    setState(() {
      _isLoading = true;
      _selectedOption = null;
    });
    try {
      final question = await _gameService.getQuestion(widget.gameId, round);
      if (!mounted) return;
      setState(() {
        _currentQuestion = question;
        _currentRound = round;
        _isLoading = false;
      });
    } catch (e) {
       if (!mounted) return;
       setState(() {
        _isLoading = false;
        _errorMessage = "Soru yüklenemedi: $e";
      });
    }
  }

  Future<void> _submitAnswer(String selectedOption) async {
    if (_selectedOption != null || _currentQuestion == null) return;

    setState(() {
      _isLoading = true;
      _selectedOption = selectedOption;
    });

    try {
      // Seçilen string'in index'ini bulup gönder
      final selectedIndex = _currentQuestion!.options.indexOf(selectedOption);
      if (selectedIndex == -1) throw Exception("Seçenek bulunamadı!");

      final response = await _gameService.answerQuestion(
          widget.gameId, 
          _currentRound, 
          selectedIndex: selectedIndex,
      );
      if (!mounted) return;
      
      // 🔥 FIXED: Doğru player'ın skorunu güncelle
      final myUserId = await _authService.getUser();
      final amIPlayer1 = _session!.player1Id == myUserId;
      
      setState(() {
        if (_session != null) {
          _session = GameSession(
            success: _session!.success,
            gameId: _session!.gameId,
            status: _session!.status,
            player1Id: _session!.player1Id,
            player2Id: _session!.player2Id,
            // Doğru player'ın skorunu güncelle
            player1Score: amIPlayer1 ? response.currentScore : _session!.player1Score,
            player2Score: !amIPlayer1 ? response.currentScore : _session!.player2Score,
            currentRound: _currentRound + 1,
            totalRounds: _session!.totalRounds,
            createdAt: _session!.createdAt,
          );
        }
        _isLoading = false;
      });

      // Kısa bir bekleme sonrası bir sonraki soruya geç
      await Future.delayed(const Duration(milliseconds: 800));
      if (!mounted) return;
      _fetchQuestion(_currentRound + 1);
      
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = "Cevap gönderilemedi: $e";
      });
    }
  }

  void _endGame() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => GameResultPage(gameId: widget.gameId),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_errorMessage != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Oyun')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.red),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Geri Dön'),
              ),
            ],
          ),
        ),
      );
    }

    if (_isLoading || _session == null || _currentQuestion == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Oyun Yükleniyor...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Tur ${_currentRound + 1}/${_session!.totalRounds}'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Skor göstergesi
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildScoreCard(
                  'Sen',
                  _session!.player1Score,
                  Colors.blue,
                ),
                const Text('VS', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                _buildScoreCard(
                  'Rakip',
                  _session!.player2Score,
                  Colors.red,
                ),
              ],
            ),
            const SizedBox(height: 30),
            
            // Soru
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  _currentQuestion!.questionText,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            const SizedBox(height: 20),
            
            // Haber başlığı
            Text(
              'Haber: ${_currentQuestion!.newsTitle}',
              style: const TextStyle(fontSize: 14, fontStyle: FontStyle.italic),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 30),
            
            // Seçenekler
            ..._currentQuestion!.options.map((option) {
              final isSelected = _selectedOption == option;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: ElevatedButton(
                  onPressed: _selectedOption == null ? () => _submitAnswer(option) : null,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                    backgroundColor: isSelected ? Colors.blue : null,
                    foregroundColor: isSelected ? Colors.white : null,
                  ),
                  child: Text(
                    option,
                    style: const TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreCard(String label, int score, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(fontSize: 16, color: color, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            border: Border.all(color: color, width: 2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '$score',
            style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: color),
          ),
        ),
      ],
    );
  }
}