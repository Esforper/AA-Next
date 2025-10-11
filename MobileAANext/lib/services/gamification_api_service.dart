// lib/services/gamification_api_service.dart
// Gerçek Backend API Servisi

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'auth_service.dart';

/// Gamification API Service
/// Backend API ile gerçek iletişim kuran servis
/// Backend hazır olunca mock yerine bu kullanılacak
class GamificationApiService {
  // Singleton pattern
  static final GamificationApiService _instance = GamificationApiService._internal();
  factory GamificationApiService() => _instance;
  GamificationApiService._internal();

  // Base URL
  late final String _baseUrl;
  
  // Auth service
  final AuthService _authService = AuthService();
  // ============ HEADERS (UPDATED) ============
  
  /// Headers oluştur - JWT Token ile
  Future<Map<String, String>> _getHeaders() async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    // Token'ı al ve Authorization header'ına ekle
    final token = await _authService.getToken();
    if (token != null && !token.isExpired) {
      headers['Authorization'] = 'Bearer ${token.accessToken}';
      debugPrint('✅ [Gamification API] Token added to header');
    } else {
      debugPrint('⚠️ [Gamification API] No valid token found');
    }
    
    return headers;
  }

  // Initialize
// Initialize
void init() {
  // ✅ FIX: Android emulator için 10.0.2.2 kullan
  final envUrl = dotenv.env['API_URL'] ?? '';
  
  if (envUrl.isEmpty) {
    // Fallback: Platform'a göre otomatik belirle
    _baseUrl = 'http://10.0.2.2:8000'; // Android emulator
    debugPrint('⚠️ [Gamification API] API_URL not found in .env, using Android emulator default');
  } else {
    // localhost -> 10.0.2.2 değiştir (Android için)
    _baseUrl = envUrl.replaceAll('localhost', '10.0.2.2');
    debugPrint('✅ [Gamification API] Using URL from .env (converted): $_baseUrl');
  }
  
  debugPrint('🎮 [Gamification API] Initialized with base URL: $_baseUrl');
}

  // ============ XP ENDPOINTS ============

  /// XP Ekle
  /// POST /api/gamification/add-xp
  Future<Map<String, dynamic>> addXP({
    required String userId,
    required int xpAmount,
    required String source,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/add-xp');
      
      final body = {
        'xp_amount': xpAmount,
        'source': source,
        if (metadata != null) 'metadata': metadata,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }


  // ============ LEVEL ENDPOINTS ============

  /// Mevcut level verilerini al
  /// GET /api/gamification/level/{userId}
  Future<Map<String, dynamic>> getCurrentLevel({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/level/$userId');
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }
  // ============ STATS ENDPOINTS ============

  /// Kullanıcı istatistiklerini al
  /// GET /api/gamification/stats/{userId}
/// Kullanıcı istatistiklerini getir (FULL STATE)
/// GET /api/gamification/stats/{user_id}
Future<Map<String, dynamic>> getUserStats({required String userId}) async {
  try {
    final uri = Uri.parse('$_baseUrl/api/gamification/stats/$userId');
    
    debugPrint('🎮 [API] GET $uri');

    final response = await http.get(
      uri,
      headers: await _getHeaders(),
    );

    final result = _handleResponse(response);
    
    // nodes_in_level ekle (backend'den gelmiyorsa hesapla)
    if (result['success'] == true && result['nodes_in_level'] == null) {
      final level = result['current_level'] ?? 0;
      result['nodes_in_level'] = _calculateNodesInLevel(level);
    }
    
    return result;
  } catch (e) {
    return _handleError(e);
  }
}

// Helper: Level'e göre node sayısı
int _calculateNodesInLevel(int level) {
  if (level < 5) return 2;
  if (level < 10) return 4;
  if (level < 15) return 6;
  if (level < 20) return 8;
  return 10;
}

  /// Günlük progress al
  /// GET /api/gamification/daily-progress/{userId}
  Future<Map<String, dynamic>> getDailyProgress({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/daily-progress/$userId');
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ DAILY RESET ============

  /// Günlük progress'i sıfırla
  /// POST /api/gamification/reset-daily/{userId}
  Future<Map<String, dynamic>> resetDaily({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/reset-daily/$userId');
      
      debugPrint('🎮 [API] POST $uri');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ LEADERBOARD ============

  /// Leaderboard al
  /// GET /api/gamification/leaderboard
  Future<Map<String, dynamic>> getLeaderboard({
    String timeframe = 'all_time',
    int limit = 100,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/leaderboard').replace(
        queryParameters: {
          'timeframe': timeframe,
          'limit': limit.toString(),
        },
      );
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Kullanıcının rank'ini al
  /// GET /api/gamification/rank/{userId}
  Future<Map<String, dynamic>> getUserRank({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/rank/$userId');
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ ACHIEVEMENTS ============

  /// Kullanıcının başarımlarını al
  /// GET /api/gamification/achievements/{userId}
  Future<Map<String, dynamic>> getAchievements({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/achievements/$userId');
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Başarım unlock'la
  /// POST /api/gamification/unlock-achievement
  Future<Map<String, dynamic>> unlockAchievement({
    required String userId,
    required String achievementId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/unlock-achievement');
      
      final body = {
        'achievement_id': achievementId,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }


// ============ NODE MANAGEMENT ============

  /// Node kontrolü - Yeterli node var mı?
  /// GET /api/gamification/check-node-eligibility/{user_id}
  Future<Map<String, dynamic>> checkNodeEligibility({
    required String userId,
    int requiredNodes = 1,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/check-node-eligibility/$userId')
          .replace(queryParameters: {
        'required_nodes': requiredNodes.toString(),
      });

      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: await _getHeaders(),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Node harca (oyuna giriş için)
  /// POST /api/gamification/spend-nodes
  Future<Map<String, dynamic>> spendNodes({
    required String userId,
    required int amount,
    String reason = 'game_entry',
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/spend-nodes');

      final body = {
        'amount': amount,
        'reason': reason,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  /// Node ekle (oyun ödülü)
  /// POST /api/gamification/add-nodes
  Future<Map<String, dynamic>> addNodesReward({
    required String userId,
    required int amount,
    String source = 'game_reward',
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/add-nodes');

      final body = {
        'amount': amount,
        'source': source,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }




  // ============ SYNC ============

  /// Local state'i backend ile senkronize et
  /// POST /api/gamification/sync
  Future<Map<String, dynamic>> syncState({
    required String userId,
    required Map<String, dynamic> localState,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/sync');
      
      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Local state: $localState');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(localState),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ TRACKING ============

  /// Aktivite tracking
  /// POST /api/gamification/track-activity
  Future<Map<String, dynamic>> trackActivity({
    required String userId,
    required String activityType,
    required Map<String, dynamic> activityData,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/track-activity');
      
      final body = {
        'user_id': userId,
        'activity_type': activityType,
        'activity_data': activityData,
        'timestamp': DateTime.now().toIso8601String(),
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: await _getHeaders(),
        body: jsonEncode(body),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ HELPER METHODS ============

  /// Response handler
  Map<String, dynamic> _handleResponse(http.Response response) {
    debugPrint('📡 Response status: ${response.statusCode}');
    debugPrint('📥 Response body: ${response.body}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else if (response.statusCode == 401) {
      return {
        'success': false,
        'message': 'Authentication failed - Invalid token',
      };
    } else if (response.statusCode == 404) {
      return {
        'success': false,
        'message': 'Endpoint not found',
      };
    } else {
      return {
        'success': false,
        'message': 'API error: ${response.statusCode}',
      };
    }
  }

  Map<String, dynamic> _handleError(dynamic error) {
    debugPrint('❌ [Gamification API] Error: $error');
    return {
      'success': false,
      'message': 'Request failed: $error',
    };
  }


  /// Health check
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/health');
      
      debugPrint('🎮 [API] Health check: $uri');

      final response = await http.get(uri).timeout(
        const Duration(seconds: 5),
      );

      if (response.statusCode == 200) {
        debugPrint('✅ [API] Health check: OK');
        return true;
      } else {
        debugPrint('❌ [API] Health check failed: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('❌ [API] Health check error: $e');
      return false;
    }
  }

  /// API bilgisi
  Map<String, dynamic> getInfo() {
    return {
      'service': 'Gamification API Service',
      'version': '1.0.0',
      'base_url': _baseUrl,
      'status': 'ready',
      'note': 'Real API service. Requires backend to be running.',
    };
  }
}