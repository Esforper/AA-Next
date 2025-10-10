import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

/// WebSocket Mesaj Tipleri
enum GameWebSocketEventType {
  connected,
  playerJoined,
  playerLeft,
  turnUpdate,
  answerResult,
  opponentAnswered,
  newQuestion,
  scoreUpdate,
  gameFinished,
  error,
  unknown,
}

/// WebSocket Mesajı
class GameWebSocketMessage {
  final GameWebSocketEventType type;
  final Map<String, dynamic> data;
  final DateTime timestamp;

  GameWebSocketMessage({
    required this.type,
    required this.data,
    required this.timestamp,
  });

  factory GameWebSocketMessage.fromJson(Map<String, dynamic> json) {
    final typeString = json['type'] as String?;
    final type = _parseEventType(typeString);

    return GameWebSocketMessage(
      type: type,
      data: json,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }

  static GameWebSocketEventType _parseEventType(String? typeString) {
    switch (typeString) {
      case 'connected':
        return GameWebSocketEventType.connected;
      case 'player_joined':
        return GameWebSocketEventType.playerJoined;
      case 'player_left':
        return GameWebSocketEventType.playerLeft;
      case 'turn_update':
        return GameWebSocketEventType.turnUpdate;
      case 'answer_result':
        return GameWebSocketEventType.answerResult;
      case 'opponent_answered':
        return GameWebSocketEventType.opponentAnswered;
      case 'new_question':
        return GameWebSocketEventType.newQuestion;
      case 'score_update':
        return GameWebSocketEventType.scoreUpdate;
      case 'game_finished':
        return GameWebSocketEventType.gameFinished;
      case 'error':
        return GameWebSocketEventType.error;
      default:
        return GameWebSocketEventType.unknown;
    }
  }
}

/// Game WebSocket Service
class GameWebSocketService {
  WebSocketChannel? _channel;
  StreamController<GameWebSocketMessage>? _messageController;
  Timer? _pingTimer;
  bool _isConnected = false;

  String? _gameId;
  String? _userId;

  /// Mesaj stream'i (dinlemek için)
  Stream<GameWebSocketMessage> get messageStream {
    _messageController ??= StreamController<GameWebSocketMessage>.broadcast();
    return _messageController!.stream;
  }

  /// Bağlı mı?
  bool get isConnected => _isConnected;

  /// WebSocket'e bağlan
  Future<void> connect({
    required String gameId,
    required String userId,
  }) async {
    if (_isConnected) {
      debugPrint('⚠️ Already connected to WebSocket');
      return;
    }

    _gameId = gameId;
    _userId = userId;

    try {
      // Platform-aware WebSocket URL
      final wsUrl = _getWebSocketUrl(gameId, userId);

      debugPrint('🔌 Connecting to WebSocket: $wsUrl');

      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));

      // Bağlantıyı dinle
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDisconnect,
        cancelOnError: false,
      );

      _isConnected = true;
      debugPrint('✅ WebSocket connected');

      // Ping-pong başlat (keep-alive)
      _startPingTimer();
    } catch (e) {
      debugPrint('❌ WebSocket connection error: $e');
      _isConnected = false;
      rethrow;
    }
  }

  /// Mesaj geldiğinde
  void _onMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String) as Map<String, dynamic>;
      final wsMessage = GameWebSocketMessage.fromJson(data);

      debugPrint('📨 WebSocket message: ${wsMessage.type}');

      // Stream'e ekle
      _messageController?.add(wsMessage);
    } catch (e) {
      debugPrint('❌ WebSocket message parse error: $e');
    }
  }

  /// Hata olduğunda
  void _onError(dynamic error) {
    debugPrint('❌ WebSocket error: $error');
    _isConnected = false;
  }

  /// Bağlantı koptuğunda
  void _onDisconnect() {
    debugPrint('🔌 WebSocket disconnected');
    _isConnected = false;
    _stopPingTimer();
  }

  /// Ping-pong başlat (30 saniyede bir)
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_isConnected) {
        try {
          _channel?.sink.add('ping');
        } catch (e) {
          debugPrint('❌ Ping error: $e');
        }
      }
    });
  }

  /// Ping-pong durdur
  void _stopPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = null;
  }

  /// Bağlantıyı kapat
  Future<void> disconnect() async {
    debugPrint('🔌 Disconnecting WebSocket...');

    _stopPingTimer();
    _isConnected = false;

    try {
      await _channel?.sink.close(status.goingAway);
    } catch (e) {
      debugPrint('❌ Disconnect error: $e');
    }

    _channel = null;
    _gameId = null;
    _userId = null;
  }

  /// Dispose
  void dispose() {
    disconnect();
    _messageController?.close();
    _messageController = null;
  }

  /// WebSocket URL oluştur (platform-aware)
  String _getWebSocketUrl(String gameId, String userId) {
    String baseUrl;

    if (kIsWeb) {
      // Web için
      baseUrl = 'ws://localhost:8000';
    } else {
      // Mobile için
      try {
        if (defaultTargetPlatform == TargetPlatform.android) {
          baseUrl = 'ws://10.0.2.2:8000'; // Android Emulator
        } else if (defaultTargetPlatform == TargetPlatform.iOS) {
          baseUrl = 'ws://localhost:8000'; // iOS Simulator
        } else {
          baseUrl = 'ws://localhost:8000'; // Fallback
        }
      } catch (_) {
        baseUrl = 'ws://localhost:8000';
      }
    }

    return '$baseUrl/api/game/ws/$gameId?user_id=$userId';
  }
}