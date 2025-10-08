// lib/services/gamification_api_service.dart
// Gerçek Backend API Servisi

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

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
  
  // Headers
  Map<String, String> _getHeaders({String? userId}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (userId != null) {
      headers['X-User-ID'] = userId;
    }
    
    return headers;
  }

  // Initialize
  void init() {
    _baseUrl = dotenv.env['API_URL'] ?? 'http://localhost:8000';
    debugPrint('🎮 [API] Initialized with base URL: $_baseUrl');
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
        'user_id': userId,
        'xp_amount': xpAmount,
        'source': source,
        if (metadata != null) 'metadata': metadata,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: _getHeaders(userId: userId),
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
        headers: _getHeaders(userId: userId),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
  }

  // ============ STATS ENDPOINTS ============

  /// Kullanıcı istatistiklerini al
  /// GET /api/gamification/stats/{userId}
  Future<Map<String, dynamic>> getUserStats({
    required String userId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/stats/$userId');
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: _getHeaders(userId: userId),
      );

      return _handleResponse(response);
    } catch (e) {
      return _handleError(e);
    }
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
        headers: _getHeaders(userId: userId),
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
        headers: _getHeaders(userId: userId),
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
    int limit = 50,
    String period = 'all_time',
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/gamification/leaderboard').replace(
        queryParameters: {
          'limit': limit.toString(),
          'period': period,
        },
      );
      
      debugPrint('🎮 [API] GET $uri');

      final response = await http.get(
        uri,
        headers: _getHeaders(),
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
        headers: _getHeaders(userId: userId),
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
        headers: _getHeaders(userId: userId),
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
        'user_id': userId,
        'achievement_id': achievementId,
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Body: $body');

      final response = await http.post(
        uri,
        headers: _getHeaders(userId: userId),
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
      
      final body = {
        'user_id': userId,
        'local_state': localState,
        'timestamp': DateTime.now().toIso8601String(),
      };

      debugPrint('🎮 [API] POST $uri');
      debugPrint('📦 Syncing state for user: $userId');

      final response = await http.post(
        uri,
        headers: _getHeaders(userId: userId),
        body: jsonEncode(body),
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
        headers: _getHeaders(userId: userId),
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
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      debugPrint('✅ Success: ${data['message'] ?? 'OK'}');
      return data;
    } else {
      debugPrint('❌ Error: ${response.statusCode} - ${response.body}');
      return {
        'success': false,
        'message': 'API error: ${response.statusCode}',
        'error': response.body,
      };
    }
  }

  /// Error handler
  Map<String, dynamic> _handleError(dynamic error) {
    debugPrint('❌ [API] Error: $error');
    return {
      'success': false,
      'message': 'Request failed: $error',
      'error': error.toString(),
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