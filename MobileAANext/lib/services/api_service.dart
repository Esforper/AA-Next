// lib/services/api_service.dart
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../models/reel_model.dart';
import 'auth_service.dart';

class ApiService {
  // =========================
  // 💡 .env'den base URL al
  // =========================
  static String _resolveHostBase() {
    final envUrl = dotenv.env['API_URL'];
    if (envUrl != null && envUrl.isNotEmpty) {
      return envUrl;
    }
    if (kIsWeb) {
      // Web tarayıcısı bilgisayarda çalıştığı için 'localhost' kullanır.
      final backendPort = dotenv.env['BACKEND_PORT'] ?? '8000';
      return 'http://localhost:$backendPort';
    }

    if (!kIsWeb && _isAndroid) {
      return 'http://10.0.2.2:8000';
    }

    if (!kIsWeb && _isIOS) {
      return 'http://localhost:8000';
    }

    return 'http://localhost:8000';
  }

  static bool get _isAndroid {
    try {
      return !kIsWeb && Platform.isAndroid;
    } catch (_) {
      return false;
    }
  }

  static bool get _isIOS {
    try {
      return !kIsWeb && Platform.isIOS;
    } catch (_) {
      return false;
    }
  }

  // =========================
  // 🔐 Auth & Configuration
  // =========================
  final AuthService _authService = AuthService();
  final String _baseUrl = _resolveHostBase();
  


  
  // 🆕 Timeout ve retry ayarları
  static const Duration _timeoutDuration = Duration(seconds: 30);
  static const int _maxRetries = 3;

  Future<Map<String, String>> _getHeaders() async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'X-User-ID': 'demo_user_123',
    };

    final token = await _authService.getToken();
    if (token != null && !token.isExpired) {
      headers['Authorization'] = 'Bearer ${token.accessToken}';
    }

    return headers;
  }

  // =========================
  // 🆕 Helper: Retry Logic
  // =========================
  Future<T> _retryRequest<T>(
    Future<T> Function() request, {
    int maxRetries = _maxRetries,
  }) async {
    int attempt = 0;
    
    while (attempt < maxRetries) {
      try {
        return await request();
      } catch (e) {
        attempt++;
        
        if (attempt >= maxRetries) {
          debugPrint('❌ Max retries ($maxRetries) reached');
          rethrow;
        }
        
        // Exponential backoff: 1s, 2s, 4s
        final delay = Duration(seconds: 1 << (attempt - 1));
        debugPrint('⚠️ Retry $attempt/$maxRetries after ${delay.inSeconds}s');
        await Future.delayed(delay);
      }
    }
    
    throw Exception('Request failed after $maxRetries retries');
  }

  // =========================
  // 📡 API Endpoints
  // =========================

  /// 🆕 Fetch reels with pagination support
  Future<Map<String, dynamic>> fetchReels({
    int limit = 20,
    String? cursor,
  }) async {
    return _retryRequest(() async {
      try {
        final headers = await _getHeaders();
        final queryParams = <String, String>{
          'limit': limit.toString(),
        };
        
        if (cursor != null && cursor.isNotEmpty) {
          queryParams['cursor'] = cursor;
        }

        final uri = Uri.parse('$_baseUrl/api/reels/feed').replace(
          queryParameters: queryParams,
        );

        debugPrint('🔍 Fetching reels: $uri');
        
        final response = await http
            .get(uri, headers: headers)
            .timeout(_timeoutDuration);

        debugPrint('📡 Response status: ${response.statusCode}');

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body) as Map<String, dynamic>;
          
          // Response validation
          if (!data.containsKey('reels')) {
            throw Exception('Invalid response: missing "reels" field');
          }

          final reelsList = data['reels'] as List;
          final reels = reelsList.map((json) => Reel.fromJson(json)).toList();
          
          // Pagination bilgisini çıkar
          final pagination = data['pagination'] as Map<String, dynamic>?;
          
          debugPrint('✅ Loaded ${reels.length} reels');
          debugPrint('📄 Pagination: hasNext=${pagination?['has_next']}, cursor=${pagination?['next_cursor']}');

          return {
            'reels': reels,
            'pagination': pagination ?? {},
            'feed_metadata': data['feed_metadata'] ?? {},
          };
          
        } else if (response.statusCode == 500) {
          // 🆕 500 hatası - fallback döndür
          debugPrint('⚠️ Server error (500), returning empty feed');
          return _getEmptyFeedResponse();
          
        } else if (response.statusCode == 404) {
          debugPrint('⚠️ Endpoint not found (404)');
          return _getEmptyFeedResponse();
          
        } else {
          throw Exception('HTTP ${response.statusCode}: ${response.body}');
        }
        
      } on http.ClientException catch (e) {
        debugPrint('❌ Network error: $e');
        throw Exception('Network error: Check your connection');
        
      } on FormatException catch (e) {
        debugPrint('❌ JSON parse error: $e');
        throw Exception('Invalid server response');
        
      } catch (e) {
        debugPrint('❌ Unexpected error: $e');
        rethrow;
      }
    });
  }

  /// 🆕 Empty feed fallback response
  Map<String, dynamic> _getEmptyFeedResponse() {
    return {
      'reels': <Reel>[],
      'pagination': {
        'has_next': false,
        'next_cursor': null,
        'total_available': 0,
      },
      'feed_metadata': {
        'personalization_level': 'cold',
      },
    };
  }

  /// Track view (hata handling ile güçlendirilmiş)
  Future<void> trackView({
    required String reelId,
    required int durationMs,
    required bool completed,
    String? category,
    String? sessionId,
    String? emojiReaction,
    int pauseCount = 0,
    bool shared = false,
    bool saved = false,
  }) async {
    try {
      final headers = await _getHeaders();
      final uri = Uri.parse('$_baseUrl/api/reels/track-view');

      // TAM BODY - Tüm tracking bilgileri
      final body = jsonEncode({
        'reel_id': reelId,
        'duration_ms': durationMs,
        'completed': completed,
        if (category != null) 'category': category,
        if (sessionId != null) 'session_id': sessionId,
        if (emojiReaction != null) 'emoji_reaction': emojiReaction,
        'paused_count': pauseCount,
        'shared': shared,
        'saved': saved,
      });

      debugPrint('📊 Tracking view: $reelId');
      debugPrint('  ├─ Duration: ${durationMs}ms');
      debugPrint('  ├─ Completed: $completed');
      debugPrint('  ├─ Emoji: ${emojiReaction ?? "none"}');
      debugPrint('  ├─ Pause count: $pauseCount');
      debugPrint('  ├─ Shared: $shared');
      debugPrint('  └─ Saved: $saved');

      final response = await http
          .post(uri, headers: headers, body: body)
          .timeout(_timeoutDuration);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ View tracked successfully');
        debugPrint('  └─ Engagement score: ${data['engagement_score']}');
      } else {
        debugPrint('⚠️ Track view failed: ${response.statusCode}');
        debugPrint('  └─ Response: ${response.body}');
      }
      
    } catch (e) {
      // Track view hatalarını sessizce logla
      // (kritik olmayan işlem, kullanıcı deneyimini etkilemesin)
      debugPrint('⚠️ Track view error (non-critical): $e');
    }
  }

  /// ✅ YENİ: Track detail view - TAM İMPLEMENTASYON
  /// Detay okuma kaydını backend'e gönderir
  Future<void> trackDetailView({
    required String reelId,
    required int readDurationMs,
    required double scrollDepth,
    bool sharedFromDetail = false,
    bool savedFromDetail = false,
    String? sessionId,
  }) async {
    try {
      final headers = await _getHeaders();
      final uri = Uri.parse('$_baseUrl/api/reels/track-detail-view');

      final body = jsonEncode({
        'reel_id': reelId,
        'read_duration_ms': readDurationMs,
        'scroll_depth': scrollDepth,
        'shared_from_detail': sharedFromDetail,
        'saved_from_detail': savedFromDetail,
        if (sessionId != null) 'session_id': sessionId,
      });

      debugPrint('📖 Tracking detail view: $reelId');
      debugPrint('  ├─ Read duration: ${readDurationMs}ms');
      debugPrint('  ├─ Scroll depth: ${(scrollDepth * 100).toStringAsFixed(1)}%');
      debugPrint('  ├─ Shared: $sharedFromDetail');
      debugPrint('  └─ Saved: $savedFromDetail');

      final response = await http
          .post(uri, headers: headers, body: body)
          .timeout(_timeoutDuration);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        debugPrint('✅ Detail view tracked successfully');
        debugPrint('  └─ Meaningful read: ${data['meaningful_read']}');
      } else {
        debugPrint('⚠️ Track detail view failed: ${response.statusCode}');
      }
      
    } catch (e) {
      debugPrint('⚠️ Track detail view error (non-critical): $e');
    }
  }

  /// 🆕 Fetch user stats with error handling
  Future<Map<String, dynamic>?> fetchUserStats(String userId) async {
    return _retryRequest(() async {
      try {
        final headers = await _getHeaders();
        final uri = Uri.parse('$_baseUrl/api/reels/user/$userId/stats');

        final response = await http
            .get(uri, headers: headers)
            .timeout(_timeoutDuration);

        if (response.statusCode == 200) {
          return jsonDecode(response.body) as Map<String, dynamic>;
          
        } else if (response.statusCode == 500) {
          // 🆕 Yeni kullanıcı için boş stats döndür
          debugPrint('⚠️ User stats 500 error, returning empty stats');
          return _getEmptyUserStats(userId);
          
        } else {
          debugPrint('⚠️ Failed to fetch user stats: ${response.statusCode}');
          return null;
        }
        
      } catch (e) {
        debugPrint('❌ Fetch user stats error: $e');
        return _getEmptyUserStats(userId);
      }
    });
  }

  /// 🆕 Empty user stats fallback
  Map<String, dynamic> _getEmptyUserStats(String userId) {
    return {
      'success': true,
      'user_id': userId,
      'total_reels_watched': 0,
      'total_screen_time_ms': 0,
      'total_screen_time_hours': 0.0,
      'completion_rate': 0.0,
      'favorite_categories': <String>[],
      'last_activity': null,
      'current_streak_days': 0,
      'avg_daily_reels': 0.0,
    };
  }

  /// Track emoji reaction
  Future<void> trackEmoji({
    required String reelId,
    required String emoji,
  }) async {
    try {
      final headers = await _getHeaders();
      final uri = Uri.parse('$_baseUrl/api/reels/track-view');

      final body = jsonEncode({
        'reel_id': reelId,
        'duration_ms': 0,
        'completed': false,
        'emoji_reaction': emoji,
      });

      final response = await http
          .post(uri, headers: headers, body: body)
          .timeout(_timeoutDuration);

      if (response.statusCode == 200) {
        debugPrint('✅ Emoji tracked: $emoji for $reelId');
      } else {
        debugPrint('⚠️ Track emoji failed: ${response.statusCode}');
      }
      
    } catch (e) {
      debugPrint('⚠️ Track emoji error (non-critical): $e');
    }
  }

  /// 🆕 Fetch trending reels
  Future<List<Reel>> fetchTrendingReels({int limit = 10}) async {
    return _retryRequest(() async {
      try {
        final headers = await _getHeaders();
        final uri = Uri.parse('$_baseUrl/api/reels/trending').replace(
          queryParameters: {'limit': limit.toString()},
        );

        final response = await http
            .get(uri, headers: headers)
            .timeout(_timeoutDuration);

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final reelsList = data['trending_reels'] as List;
          return reelsList.map((json) => Reel.fromJson(json)).toList();
        } else {
          debugPrint('⚠️ Failed to fetch trending: ${response.statusCode}');
          return <Reel>[];
        }
        
      } catch (e) {
        debugPrint('❌ Fetch trending error: $e');
        return <Reel>[];
      }
    });
  }

  /// 🆕 Health check
  Future<bool> checkServerHealth() async {
    try {
      final uri = Uri.parse('$_baseUrl/api/reels/system/status');
      final response = await http
          .get(uri)
          .timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('❌ Health check failed: $e');
      return false;
    }
  }
}