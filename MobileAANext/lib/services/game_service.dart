// lib/services/game_service.dart
// Haber Kapışması Oyunu - Backend API İletişimi

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart';
import '../models/game_models.dart';
import 'dart:io' show Platform;
import 'auth_service.dart';
import 'package:flutter/foundation.dart';
/// Game Service - Oyun API'leri ile iletişim
class GameService {
  static final GameService _instance = GameService._internal();
  factory GameService() => _instance;
  GameService._internal();
  final AuthService _authService = AuthService();
  // Base URL
  // ✅ FIX: Web için doğru URL
// ✅ SONRA:
String get _baseUrl {
  final envUrl = dotenv.env['API_URL'];
  if (envUrl != null && envUrl.isNotEmpty) {
    return envUrl;
  }

  if (kIsWeb) {
    // WEB: localhost kullan
    final backendPort = dotenv.env['BACKEND_PORT'] ?? '8000';
    return 'http://localhost:$backendPort';
  }

  // Mobile platforms
  try {
    if (!kIsWeb && Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    if (!kIsWeb && Platform.isIOS) {
      return 'http://localhost:8000';
    }
  } catch (_) {}

  return 'http://localhost:8000';
}
  // Timeout
  final _timeoutDuration = const Duration(seconds: 60);

  // User ID (ApiService'den alınacak - şimdilik hardcoded)
  Future<String> _getUserId() async {
    final user = await _authService.getUser();
    if (user != null) {
      debugPrint('🎮 Game Service - Using real user ID: ${user.id}');
      return user.id;
    }
    debugPrint('⚠️ Game Service - No user logged in, using: anonymous_user');
    return 'anonymous_user';
  }

  // ============ MATCHMAKING ============
/// Oyun uygunluğunu kontrol et
Future<GameEligibility> checkEligibility({
  int days = 6,
  int minReels = 8,
}) async {
  try {
    final token = await _authService.getToken(); // 🔥 Token al
    
    final uri = Uri.parse('$_baseUrl/api/game/check-eligibility')
        .replace(queryParameters: {
      'days': days.toString(),
      'min_reels': minReels.toString(),
    });

    debugPrint('🔗 GET $uri');

    final response = await http.get(
      uri,
headers: await _getHeaders(),
    ).timeout(_timeoutDuration);

    debugPrint('📡 Eligibility Response: ${response.statusCode}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return GameEligibility.fromJson(data);
    } else {
      throw Exception('Failed to check eligibility');
    }
  } catch (e) {
    debugPrint('❌ Check eligibility error: $e');
    rethrow;
  }
}

  /// Matchmaking başlat - Rakip ara
  Future<MatchmakingResponse> startMatchmaking({
    int days = 6,
    int minCommonReels = 8,
  }) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/matchmaking/start');

      debugPrint('🔗 POST $uri');
      debugPrint('📤 Body: days=$days, min_common_reels=$minCommonReels');

      final response = await http.post(
        uri,
headers: await _getHeaders(),
        body: jsonEncode({
          'days': days,
          'min_common_reels': minCommonReels,
        }),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Matchmaking Response: ${response.statusCode}');
      debugPrint('📥 Body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MatchmakingResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['message'] ?? 'Matchmaking failed');
      }
    } catch (e) {
      debugPrint('❌ Matchmaking error: $e');
      rethrow;
    }
  }


// game_service.dart içine eklenecek (startMatchmaking fonksiyonundan SONRA)

/// 🆕 Matchmaking queue'ya katıl
Future<MatchmakingResponse> joinMatchmaking({
  int days = 6,
  int minCommonReels = 8,
}) async {
  try {
    final uri = Uri.parse('$_baseUrl/api/game/matchmaking/join');

    debugPrint('🔗 POST $uri');
    debugPrint('📤 Body: days=$days, min_common_reels=$minCommonReels');

    final response = await http.post(
      uri,
      headers: await _getHeaders(),
      body: jsonEncode({
        'days': days,
        'min_common_reels': minCommonReels,
      }),
    ).timeout(_timeoutDuration);

    debugPrint('📡 Join Matchmaking Response: ${response.statusCode}');
    debugPrint('📥 Body: ${response.body}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return MatchmakingResponse.fromJson(data);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['message'] ?? 'Join matchmaking failed');
    }
  } catch (e) {
    debugPrint('❌ Join matchmaking error: $e');
    rethrow;
  }
}


/// 🆕 Matchmaking durumunu kontrol et (polling için)
Future<MatchmakingStatusResponse> getMatchmakingStatus() async {
  try {
    final uri = Uri.parse('$_baseUrl/api/game/matchmaking/status');

    debugPrint('🔗 GET $uri');

    final response = await http.get(
      uri,
      headers: await _getHeaders(),
    ).timeout(_timeoutDuration);

    debugPrint('📡 Matchmaking Status: ${response.statusCode}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return MatchmakingStatusResponse.fromJson(data);
    } else {
      throw Exception('Failed to get matchmaking status');
    }
  } catch (e) {
    debugPrint('❌ Get matchmaking status error: $e');
    rethrow;
  }
}






   /// Matchmaking iptal et (GÜNCELLEME - zaten vardı ama endpoint değişti)
  @override
  Future<void> cancelMatchmaking() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/game/matchmaking/cancel');

      debugPrint('🔗 POST $uri');

      await http.post(
        uri,
        headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('✅ Matchmaking cancelled');
    } catch (e) {
      debugPrint('❌ Cancel matchmaking error: $e');
    }
  }

  // ============ GAME SESSION ============

  /// Oyun durumunu getir
  Future<GameSession> getGameStatus(String gameId) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/session/$gameId');

      debugPrint('🔗 GET $uri');

      final response = await http.get(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Game Status Response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return GameSession.fromJson(data);
      } else if (response.statusCode == 404) {
        throw Exception('Game not found');
      } else {
        throw Exception('Failed to get game status');
      }
    } catch (e) {
      debugPrint('❌ Get game status error: $e');
      rethrow;
    }
  }

  /// Oyunu başlat (her iki oyuncu hazır olunca)
  Future<void> startGame(String gameId) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/session/$gameId/start');

      debugPrint('🔗 POST $uri');

      final response = await http.post(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Start Game Response: ${response.statusCode}');

      if (response.statusCode != 200) {
        throw Exception('Failed to start game');
      }

      debugPrint('✅ Game started!');
    } catch (e) {
      debugPrint('❌ Start game error: $e');
      rethrow;
    }
  }



  /// Belirli bir round'un sorusunu getir
  Future<GameQuestion> getQuestion(String gameId, int roundNumber) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri =
          Uri.parse('$_baseUrl/api/game/session/$gameId/question/$roundNumber');

      debugPrint('🔗 GET $uri');

      final response = await http.get(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Question Response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return GameQuestion.fromJson(data);
      } else if (response.statusCode == 404) {
        throw Exception('Question not found');
      } else {
        throw Exception('Failed to get question');
      }
    } catch (e) {
      debugPrint('❌ Get question error: $e');
      rethrow;
    }
  }

  /// Soruya cevap ver
  Future<AnswerResponse> answerQuestion(
    String gameId,
    int roundNumber, {
    required int selectedIndex,
    bool isPass = false,
  }) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri =
          Uri.parse('$_baseUrl/api/game/session/$gameId/answer/$roundNumber');

      debugPrint('🔗 POST $uri');
      debugPrint('📤 Answer: index=$selectedIndex, pass=$isPass');

      final response = await http.post(
        uri,
headers: await _getHeaders(),
        body: jsonEncode({
          'selected_index': selectedIndex,
          'is_pass': isPass,
        }),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Answer Response: ${response.statusCode}');
      debugPrint('📥 Body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AnswerResponse.fromJson(data);
      } else {
        throw Exception('Failed to submit answer');
      }
    } catch (e) {
      debugPrint('❌ Answer question error: $e');
      rethrow;
    }
  }

  /// Oyun sonucunu getir
  Future<GameResult> getGameResult(String gameId) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/session/$gameId/result');

      debugPrint('🔗 GET $uri');

      final response = await http.get(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Game Result Response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return GameResult.fromJson(data);
      } else if (response.statusCode == 400) {
        throw Exception('Game not finished yet');
      } else {
        throw Exception('Failed to get game result');
      }
    } catch (e) {
      debugPrint('❌ Get game result error: $e');
      rethrow;
    }
  }

  /// Oyundan ayrıl (forfeit)
  Future<void> leaveGame(String gameId) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/session/$gameId/leave');

      await http.post(
        uri,
        headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('✅ Left game');
    } catch (e) {
      debugPrint('❌ Leave game error: $e');
    }
  }

  // ============ DEBUG ============

  /// Debug: Eşleşebilir kullanıcılar
  Future<Map<String, dynamic>> getMatchableUsers({
    int days = 6,
    int minCommon = 8,
  }) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/debug/matchable-users')
          .replace(queryParameters: {
        'days': days.toString(),
        'min_common': minCommon.toString(),
      });

      final response = await http.get(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get matchable users');
      }
    } catch (e) {
      debugPrint('❌ Get matchable users error: $e');
      return {'success': false, 'matchable_users': [], 'count': 0};
    }
  }

  /// Debug: Kendi izlediğim haberler
  Future<Map<String, dynamic>> getMyViews({int days = 6}) async {
    try {
      final userId = await _getUserId(); // 🔥 UPDATED
      final uri = Uri.parse('$_baseUrl/api/game/debug/my-views')
          .replace(queryParameters: {
        'days': days.toString(),
      });

      final response = await http.get(
        uri,
headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get my views');
      }
    } catch (e) {
      debugPrint('❌ Get my views error: $e');
      return {'success': false, 'total_views': 0, 'views': []};
    }
  }



  /// Header'ları oluştur (Authorization + Content-Type)
Future<Map<String, String>> _getHeaders() async {
  final headers = <String, String>{
    'Content-Type': 'application/json',
  };

  // Token'ı al ve Authorization header'ına ekle
  final token = await _authService.getToken();
  if (token != null && !token.isExpired) {
    headers['Authorization'] = 'Bearer ${token.accessToken}';
  }

  return headers;
}

  Future<MatchmakingResponse> joinMatchmakingQueue({
    int days = 6,
    int minCommonReels = 8,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/game/matchmaking/join');

      debugPrint('🔗 POST $uri');
      debugPrint('📤 Body: days=$days, min_common_reels=$minCommonReels');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode({
          'days': days,
          'min_common_reels': minCommonReels,
        }),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Join Queue Response: ${response.statusCode}');
      debugPrint('📥 Body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return MatchmakingResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['message'] ?? 'Queue join failed');
      }
    } catch (e) {
      debugPrint('❌ Join queue error: $e');
      rethrow;
    }
  }

  /// Matchmaking durumunu kontrol et (polling için)
  Future<Map<String, dynamic>> checkMatchmakingStatus() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/game/matchmaking/status');

      debugPrint('🔗 GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      ).timeout(_timeoutDuration);

      debugPrint('📡 Status Response: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data;
      } else {
        throw Exception('Failed to check status');
      }
    } catch (e) {
      debugPrint('❌ Check status error: $e');
      rethrow;
    }
  }


// ============ GAME HISTORY ============

/// Oyun geçmişini getir
Future<List<GameHistoryItem>> getGameHistory({int limit = 20}) async {
  try {
    final uri = Uri.parse('$_baseUrl/api/game/history?limit=$limit');

    debugPrint('🔗 GET $uri');

    final response = await http.get(
      uri,
      headers: await _getHeaders(),
    ).timeout(_timeoutDuration);

    debugPrint('📡 Game History Response: ${response.statusCode}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      
      if (data['success'] == true) {
        final List<dynamic> historyList = data['history'] ?? [];
        return historyList
            .map((item) => GameHistoryItem.fromJson(item))
            .toList();
      } else {
        throw Exception('Failed to load game history');
      }
    } else {
      throw Exception('Failed to get game history');
    }
  } catch (e) {
    debugPrint('❌ Get game history error: $e');
    rethrow;
  }
}

/// Oyun detayını getir (geçmişten)
Future<GameHistoryDetail> getGameHistoryDetail(String gameId) async {
  try {
    final uri = Uri.parse('$_baseUrl/api/game/history/$gameId');

    debugPrint('🔗 GET $uri');

    final response = await http.get(
      uri,
      headers: await _getHeaders(),
    ).timeout(_timeoutDuration);

    debugPrint('📡 Game History Detail Response: ${response.statusCode}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return GameHistoryDetail.fromJson(data);
    } else if (response.statusCode == 404) {
      throw Exception('Game not found');
    } else if (response.statusCode == 403) {
      throw Exception('Not your game');
    } else {
      throw Exception('Failed to get game detail');
    }
  } catch (e) {
    debugPrint('❌ Get game detail error: $e');
    rethrow;
  }
}



}


