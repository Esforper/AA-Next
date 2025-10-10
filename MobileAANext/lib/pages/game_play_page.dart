import 'package:flutter/material.dart';
import 'dart:async';
import '../models/game_models.dart';
import '../services/game_service.dart';
import 'game_result_page.dart';

class GamePlayPage extends StatefulWidget {
  final String gameId;
  const GamePlayPage({super.key, required this.gameId});

  @override
  State<GamePlayPage> createState() => _GamePlayPageState();
}

class _GamePlayPageState extends State<GamePlayPage> {
  final GameService _gameService = GameService();

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
      if (_gameService.userId == null) {
        // Bu ID Auth sisteminden gelmeli, şimdilik test için.
        _gameService.setUserId("test_user_1");
      }
      
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
      // ✅ BÜYÜK HATA DÜZELTİLDİ: 'answerQuestion' artık 'selectedIndex' istiyor.
      // Seçilen string'in index'ini bulup gönderiyoruz.
      final selectedIndex = _currentQuestion!.options.indexOf(selectedOption);
      if (selectedIndex == -1) throw Exception("Seçenek bulunamadı!");

      final response = await _gameService.answerQuestion(
          widget.gameId, 
          _currentRound, 
          selectedIndex: selectedIndex,
      );
      if (!mounted) return;
      
      // Skoru ve round'u manuel olarak güncelliyoruz.
      setState(() {
        // Backend'den gelen güncel skorları modele yansıt
        final amIPlayer1 = _session!.player1Id == _gameService.userId;
        _session = GameSession(
          success: _session!.success,
          gameId: _session!.gameId,
          status: _session!.status,
          player1Id: _session!.player1Id,
          player2Id: _session!.player2Id,
          // ✅ HATA DÜZELTİLDİ: Skorlar artık backend'den gelen güncel değerler
          player1Score: amIPlayer1 ? response.currentScore : _session!.player1Score,
          player2Score: !amIPlayer1 ? response.currentScore : _session!.player2Score,
          currentRound: _currentRound + 1, // Round'u manuel ilerlet
          totalRounds: _session!.totalRounds,
          createdAt: _session!.createdAt,
        );
        _isLoading = false;
      });

      Timer(const Duration(seconds: 2, milliseconds: 500), () {
        if (mounted) {
          _fetchQuestion(_currentRound + 1);
        }
      });

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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Haber Kapışması'),
        automaticallyImplyLeading: false,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_errorMessage != null) {
      return Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)));
    }
    if (_session == null || _currentQuestion == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return Column(
      children: [
        _buildScoreBoard(),
        const Divider(),
        Expanded(
          child: _isLoading && _selectedOption == null
              ? const Center(child: CircularProgressIndicator())
              : _buildQuestionArea(),
        ),
      ],
    );
  }
  
  Widget _buildScoreBoard() {
    // ✅ HATA DÜZELTİLDİ: Artık public 'userId' getter'ı var
    final bool amIPlayer1 = _session!.player1Id == _gameService.userId;
    final myScore = amIPlayer1 ? _session!.player1Score : _session!.player2Score;
    final opponentScore = amIPlayer1 ? _session!.player2Score : _session!.player1Score;
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _playerScoreColumn("Sen", myScore),
          Text("${_currentRound + 1}/${_session!.totalRounds}", style: Theme.of(context).textTheme.headlineSmall),
          _playerScoreColumn("Rakip", opponentScore),
        ],
      ),
    );
  }
  
  Widget _playerScoreColumn(String title, int score) {
    return Column(
      children: [
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        Text(score.toString(), style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildQuestionArea() {
    bool isMyTurnToAnswer = _currentQuestion!.askerId != _gameService.userId;
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blueGrey.shade800,
              borderRadius: BorderRadius.circular(16)
            ),
            child: Text(
              _currentQuestion!.questionText,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white),
            ),
          ),
          const SizedBox(height: 30),
          ..._currentQuestion!.options.map((option) {
              return _buildOptionButton(option, isMyTurnToAnswer);
          }).toList(),
          const SizedBox(height: 20),
          if (!isMyTurnToAnswer && _selectedOption == null)
            const Text("Rakibin cevabı bekleniyor..."),
        ],
      ),
    );
  }
  
  Widget _buildOptionButton(String option, bool isMyTurnToAnswer) {
    Color? buttonColor;
    IconData? icon;

    if (_selectedOption != null) {
      final correctOptionText = _currentQuestion!.options[_currentQuestion!.correctIndex];
      if (option == correctOptionText) {
        buttonColor = Colors.green;
        icon = Icons.check_circle;
      } else if (option == _selectedOption) {
        buttonColor = Colors.red;
        icon = Icons.cancel;
      }
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: AbsorbPointer(
        absorbing: _selectedOption != null || !isMyTurnToAnswer,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: buttonColor,
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, 60),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          onPressed: () => _submitAnswer(option),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[Icon(icon), const SizedBox(width: 8)],
              Expanded(child: Text(option, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16))),
            ],
          ),
        ),
      ),
    );
  }
}