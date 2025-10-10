import 'package:flutter/material.dart';
import 'dart:async';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'game_result_page.dart';
import '../../services/auth_service.dart';
import '../../services/game_websocket_service.dart'; // 🆕 YENİ

/// Haber Kapışması Oyunu - WhatsApp Tarzı Chat Ekranı
class GamePlayPage extends StatefulWidget {
  final String gameId;
  const GamePlayPage({super.key, required this.gameId});

  @override
  State<GamePlayPage> createState() => _GamePlayPageState();
}

class _GamePlayPageState extends State<GamePlayPage> {
  final GameService _gameService = GameService();
  final AuthService _authService = AuthService();
  final ScrollController _scrollController = ScrollController();
  final GameWebSocketService _wsService = GameWebSocketService();

  // State
  bool _isLoading = true;
  String? _errorMessage;
  GameSession? _session;
  String? _myUserId;
  
  // Oyun mesajları (chat history)
  List<ChatBubble> _chatBubbles = [];
  
  // Şu anki soru
  GameQuestion? _currentQuestion;
  int _currentRound = 0;
  bool _waitingForResponse = false;
  
  // Polling timer
  Timer? _pollingTimer;
  StreamSubscription<GameWebSocketMessage>? _wsSubscription; // 🆕 YENİ

  @override
  void initState() {
    super.initState();
    _initializeGame();
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    _wsSubscription?.cancel(); // 🆕 YENİ
    _wsService.dispose(); // 🆕 YENİ
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeGame() async {
  try {
    // Kullanıcı ID'sini al
    final user = await _authService.getUser();
    _myUserId = user?.id ?? 'anonymous';
    
    // Oyun durumunu getir
    final session = await _gameService.getGameStatus(widget.gameId);
    
    if (!mounted) return;
    
    setState(() {
      _session = session;
      _isLoading = false;
    });
    
    // 🆕 WebSocket'e bağlan
    await _connectWebSocket();
    
    // İlk soruyu yükle
    await _loadQuestion(0);
    
  } catch (e) {
    if (!mounted) return;
    setState(() {
      _isLoading = false;
      _errorMessage = "Oyun yüklenemedi: $e";
    });
  }
}
void _startPolling() {
  debugPrint('⚠️ Falling back to polling (WebSocket failed)');
  
  _pollingTimer = Timer.periodic(const Duration(seconds: 3), (timer) async {
    if (!mounted) {
      timer.cancel();
      return;
    }
    
    try {
      // Oyun durumunu güncelle
      final session = await _gameService.getGameStatus(widget.gameId);
      
      if (!mounted) return;
      
      setState(() {
        _session = session;
      });
      
      // Oyun bitti mi?
      if (session.isFinished) {
        timer.cancel();
        _navigateToResult();
      }
      
    } catch (e) {
      debugPrint('❌ Polling error: $e');
    }
  });
}

Future<void> _connectWebSocket() async {
  try {
    // WebSocket'e bağlan
    await _wsService.connect(
      gameId: widget.gameId,
      userId: _myUserId!,
    );
    
    // Mesajları dinle
    _wsSubscription = _wsService.messageStream.listen(_handleWebSocketMessage);
    
    debugPrint('✅ WebSocket connected and listening');
  } catch (e) {
    debugPrint('❌ WebSocket connection error: $e');
    // Hata durumunda polling'e geri dön
    _startPolling();
  }
}

void _handleWebSocketMessage(GameWebSocketMessage message) {
  if (!mounted) return;
  
  debugPrint('📨 Handling WS message: ${message.type}');
  
  switch (message.type) {
    case GameWebSocketEventType.connected:
      debugPrint('✅ Connected to game room');
      break;
      
    case GameWebSocketEventType.opponentAnswered:
      // Rakip cevap verdi
      final responseMessage = message.data['response_message'] as String?;
      final emojiComment = message.data['emoji_comment'] as String?;
      
      if (responseMessage != null) {
        _addChatBubble(
          isFromMe: false,
          text: responseMessage,
        );
        
        if (emojiComment != null && emojiComment.isNotEmpty) {
          Future.delayed(const Duration(milliseconds: 500), () {
            _addChatBubble(
              isFromMe: false,
              text: emojiComment,
              hasEmoji: true,
            );
          });
        }
      }
      break;
      
    case GameWebSocketEventType.scoreUpdate:
      // Skor güncellendi
      final p1Score = message.data['player1_score'] as int?;
      final p2Score = message.data['player2_score'] as int?;
      final currentRound = message.data['current_round'] as int?;
      
      if (p1Score != null && p2Score != null && _session != null) {
        setState(() {
          _session = GameSession(
            success: _session!.success,
            gameId: _session!.gameId,
            status: _session!.status,
            player1Id: _session!.player1Id,
            player2Id: _session!.player2Id,
            player1Score: p1Score,
            player2Score: p2Score,
            currentRound: currentRound ?? _session!.currentRound,
            totalRounds: _session!.totalRounds,
            createdAt: _session!.createdAt,
          );
        });
      }
      break;
      
    case GameWebSocketEventType.newQuestion:
      // Yeni soru geldi
      final roundNumber = message.data['round_number'] as int?;
      if (roundNumber != null && roundNumber >= _currentRound) {
        _loadQuestion(roundNumber);
      }
      break;
      
    case GameWebSocketEventType.gameFinished:
      // Oyun bitti
      _navigateToResult();
      break;
      
    default:
      debugPrint('⚠️ Unhandled message type: ${message.type}');
  }
}




  Future<void> _loadQuestion(int round) async {
    if (round >= (_session?.totalRounds ?? 8)) {
      _navigateToResult();
      return;
    }
    
    try {
      final question = await _gameService.getQuestion(widget.gameId, round);
      
      if (!mounted) return;
      
      setState(() {
        _currentQuestion = question;
        _currentRound = round;
        _waitingForResponse = false;
      });
      
      // Soru mesajını chat'e ekle
      _addChatBubble(
        isFromMe: question.askerId == _myUserId,
        text: '${question.questionText}\n\n"${question.newsTitle}"',
        isQuestion: true,
      );
      
      _scrollToBottom();
      
    } catch (e) {
      debugPrint('❌ Load question error: $e');
      if (!mounted) return;
      setState(() {
        _errorMessage = "Soru yüklenemedi: $e";
      });
    }
  }
Future<void> _submitAnswer({int? selectedIndex, bool isPass = false}) async {
  if (_waitingForResponse || _currentQuestion == null) return;
  
  setState(() {
    _waitingForResponse = true;
  });
  
  // Seçilen cevabı chat'e ekle
  if (!isPass && selectedIndex != null) {
    _addChatBubble(
      isFromMe: true,
      text: _currentQuestion!.options[selectedIndex],
      isAnswer: true,
    );
  } else if (isPass) {
    _addChatBubble(
      isFromMe: true,
      text: "Pas geçtim",
      isAnswer: true,
    );
  }
  
  _scrollToBottom();
  
  try {
    final response = await _gameService.answerQuestion(
      widget.gameId,
      _currentRound,
      selectedIndex: selectedIndex ?? 0,
      isPass: isPass,
    );
    
    if (!mounted) return;
    
    // 🔥 FIX: WebSocket varsa bekle, yoksa manuel yükle
    if (!_wsService.isConnected) {
      debugPrint('📡 Polling mode: manually loading next question');
      
      // Yanıt mesajını chat'e ekle (sadece polling modunda)
      _addChatBubble(
        isFromMe: false,
        text: response.responseMessage,
        isCorrect: response.isCorrect,
      );
      
      if (response.emojiComment != null && response.emojiComment!.isNotEmpty) {
        await Future.delayed(const Duration(milliseconds: 500));
        _addChatBubble(
          isFromMe: false,
          text: response.emojiComment!,
          hasEmoji: true,
        );
      }
      
      _scrollToBottom();
      
      // Skoru manuel güncelle
      setState(() {
        if (_myUserId == _session!.player1Id) {
          _session = GameSession(
            success: _session!.success,
            gameId: _session!.gameId,
            status: _session!.status,
            player1Id: _session!.player1Id,
            player2Id: _session!.player2Id,
            player1Score: response.currentScore,
            player2Score: _session!.player2Score,
            currentRound: _currentRound + 1,
            totalRounds: _session!.totalRounds,
            createdAt: _session!.createdAt,
          );
        } else {
          _session = GameSession(
            success: _session!.success,
            gameId: _session!.gameId,
            status: _session!.status,
            player1Id: _session!.player1Id,
            player2Id: _session!.player2Id,
            player1Score: _session!.player1Score,
            player2Score: response.currentScore,
            currentRound: _currentRound + 1,
            totalRounds: _session!.totalRounds,
            createdAt: _session!.createdAt,
          );
        }
        _waitingForResponse = false;  // ✅ Burada sıfırla
      });
      
      // Sonraki soruya geç
      await Future.delayed(const Duration(milliseconds: 1500));
      if (!mounted) return;
      
      final nextRound = _currentRound;  // ✅ currentRound zaten +1 oldu
      if (nextRound < _session!.totalRounds) {
        await _loadQuestion(nextRound);
      } else {
        _navigateToResult();
      }
      
    } else {
      // WebSocket modunda, backend otomatik broadcast yapacak
      debugPrint('🔌 WebSocket mode: waiting for backend broadcast');
      
      // Cevap sonucunu bekle (backend'den gelecek)
      // newQuestion eventi gelince otomatik yüklenecek
      setState(() {
        _waitingForResponse = false;
      });
    }
    
  } catch (e) {
    debugPrint('❌ Submit answer error: $e');
    if (!mounted) return;
    setState(() {
      _waitingForResponse = false;
      _errorMessage = "Cevap gönderilemedi: $e";
    });
  }
}

  void _addChatBubble({
    required bool isFromMe,
    required String text,
    bool isQuestion = false,
    bool isAnswer = false,
    bool? isCorrect,
    String? emojiComment,
    bool hasEmoji = false,
  }) {
    setState(() {
      _chatBubbles.add(ChatBubble(
        isFromMe: isFromMe,
        text: text,
        isQuestion: isQuestion,
        isAnswer: isAnswer,
        isCorrect: isCorrect,
        hasEmoji: hasEmoji,
        timestamp: DateTime.now(),
      ));
    });
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _navigateToResult() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => GameResultPage(gameId: widget.gameId),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Oyun Yükleniyor...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_errorMessage != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Hata')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.red),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Geri Dön'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFECE5DD), // WhatsApp arka plan rengi
      appBar: _buildAppBar(),
      body: Column(
        children: [
          // Chat mesajları
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _chatBubbles.length,
              itemBuilder: (context, index) {
                return _buildChatBubble(_chatBubbles[index]);
              },
            ),
          ),
          
          // Cevap seçenekleri (sadece sıra bendeyse)
          if (_shouldShowOptions()) _buildOptionsArea(),
          
          // Bekleme durumu
          if (_waitingForResponse) _buildWaitingIndicator(),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    final myScore = _myUserId == _session?.player1Id 
        ? _session?.player1Score ?? 0 
        : _session?.player2Score ?? 0;
    final opponentScore = _myUserId == _session?.player1Id 
        ? _session?.player2Score ?? 0 
        : _session?.player1Score ?? 0;

    return AppBar(
      backgroundColor: const Color(0xFF075E54), // WhatsApp yeşili
      foregroundColor: Colors.white,
      title: Column(
        children: [
          const Text('Haber Kapışması', style: TextStyle(fontSize: 18)),
          Text(
            'Round ${_currentRound + 1}/${_session?.totalRounds ?? 8}',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w300),
          ),
        ],
      ),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 16),
          child: Row(
            children: [
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Ben', style: TextStyle(fontSize: 10)),
                  Text('$myScore XP', 
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(width: 12),
              const Text('-', style: TextStyle(fontSize: 20)),
              const SizedBox(width: 12),
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Rakip', style: TextStyle(fontSize: 10)),
                  Text('$opponentScore XP', 
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildChatBubble(ChatBubble bubble) {
    return Align(
      alignment: bubble.isFromMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: bubble.isFromMe 
              ? const Color(0xFFDCF8C6) // Yeşil (benim mesajım)
              : Colors.white, // Beyaz (rakip mesajı)
          borderRadius: BorderRadius.circular(8),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Emoji indicator
            if (bubble.hasEmoji)
              const Padding(
                padding: EdgeInsets.only(bottom: 4),
                child: Text('💬', style: TextStyle(fontSize: 16)),
              ),
            
            // Mesaj metni
            Text(
              bubble.text,
              style: TextStyle(
                fontSize: 15,
                color: Colors.black87,
                fontWeight: bubble.isQuestion ? FontWeight.w500 : FontWeight.normal,
              ),
            ),
            
            // Doğru/Yanlış indicator
            if (bubble.isCorrect != null)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      bubble.isCorrect! ? Icons.check_circle : Icons.cancel,
                      size: 16,
                      color: bubble.isCorrect! ? Colors.green : Colors.red,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      bubble.isCorrect! ? 'Doğru! +20 XP' : 'Yanlış',
                      style: TextStyle(
                        fontSize: 12,
                        color: bubble.isCorrect! ? Colors.green : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            
            // Timestamp
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                '${bubble.timestamp.hour.toString().padLeft(2, '0')}:${bubble.timestamp.minute.toString().padLeft(2, '0')}',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.black.withOpacity(0.5),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  bool _shouldShowOptions() {
    if (_currentQuestion == null) {
    debugPrint('❌ No options: _currentQuestion is null');
    return false;
  }
  
  if (_waitingForResponse) {
    debugPrint('❌ No options: waiting for response');
    return false;
  }
  
  if (_session == null) {
    debugPrint('❌ No options: _session is null');
    return false;
  }
  
  if (_myUserId == null) {
    debugPrint('❌ No options: _myUserId is null');
    return false;
  }
  
  // Round bazlı sıra kontrolü
  final isPlayer1 = _myUserId == _session!.player1Id;
  
  // Çift round (0,2,4,6) -> Player1 sorar, Player2 cevaplar
  // Tek round (1,3,5,7) -> Player2 sorar, Player1 cevaplar
  final shouldAnswer = (_currentRound % 2 == 0) ? !isPlayer1 : isPlayer1;
  
  debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━');
  debugPrint('🎯 OPTIONS CHECK:');
  debugPrint('   Current Round: $_currentRound');
  debugPrint('   My User ID: $_myUserId');
  debugPrint('   Player1 ID: ${_session!.player1Id}');
  debugPrint('   Player2 ID: ${_session!.player2Id}');
  debugPrint('   Am I Player1?: $isPlayer1');
  debugPrint('   Should Answer?: $shouldAnswer');
  debugPrint('   Question exists: ${_currentQuestion != null}');
  debugPrint('   Waiting: $_waitingForResponse');
  debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━');
  
  return shouldAnswer;
}

  Widget _buildOptionsArea() {
  // 🔥 DEBUG: Seçenekleri kontrol et
  debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━');
  debugPrint('📋 OPTIONS AREA:');
  debugPrint('   Question: ${_currentQuestion?.questionText}');
  debugPrint('   Options count: ${_currentQuestion?.options.length}');
  debugPrint('   Options: ${_currentQuestion?.options}');
  debugPrint('━━━━━━━━━━━━━━━━━━━━━━━━');
  
  // Seçenekler boşsa hata göster
  if (_currentQuestion == null || _currentQuestion!.options.isEmpty) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.red[100],
      child: const Text(
        '❌ Seçenekler yüklenemedi!',
        style: TextStyle(color: Colors.red),
        textAlign: TextAlign.center,
      ),
    );
  }
  
  return Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.1),
          blurRadius: 8,
          offset: const Offset(0, -2),
        ),
      ],
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Cevabını seç:',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        
        // Seçenekler
        ..._currentQuestion!.options.asMap().entries.map((entry) {
          final index = entry.key;
          final option = entry.value;
          
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: ElevatedButton(
              onPressed: () => _submitAnswer(selectedIndex: index),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF075E54),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                option,
                style: const TextStyle(fontSize: 15),
                textAlign: TextAlign.left,
              ),
            ),
          );
        }).toList(),
        
        // Pas geç butonu
        TextButton.icon(
          onPressed: () => _submitAnswer(isPass: true),
          icon: const Icon(Icons.skip_next),
          label: const Text('Pas Geç'),
          style: TextButton.styleFrom(
            foregroundColor: Colors.grey[700],
          ),
        ),
      ],
    ),
  );
}


  Widget _buildWaitingIndicator() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.grey[200],
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          SizedBox(width: 12),
          Text(
            'Rakip düşünüyor...',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

// ============ CHAT BUBBLE MODEL ============

class ChatBubble {
  final bool isFromMe;
  final String text;
  final bool isQuestion;
  final bool isAnswer;
  final bool? isCorrect;
  final bool hasEmoji;
  final DateTime timestamp;

  ChatBubble({
    required this.isFromMe,
    required this.text,
    this.isQuestion = false,
    this.isAnswer = false,
    this.isCorrect,
    this.hasEmoji = false,
    required this.timestamp,
  });
}