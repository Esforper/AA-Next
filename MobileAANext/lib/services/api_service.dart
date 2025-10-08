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
    // .env'den oku
    final envUrl = dotenv.env['API_URL'];
    if (envUrl != null && envUrl.isNotEmpty) {
      return envUrl;
    }

    // Fallback: Platform'a göre
    if (kIsWeb) {
      return Uri.base.origin;
    }

    if (!kIsWeb && _isAndroid) {
      return 'http://10.0.2.2:8000'; // Android emulator
    }

    if (!kIsWeb && _isIOS) {
      return 'http://localhost:8000'; // iOS simulator
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
  // 🔐 Auth Token Yönetimi
  // =========================
  final AuthService _authService = AuthService();
Future<Map<String, String>> _getHeaders() async {
  final headers = <String, String>{
    'Content-Type': 'application/json',
    'X-User-ID': 'demo_user_123', // 👈 Geçici user ID
  };

  final token = await _authService.getToken();
  if (token != null && !token.isExpired) {
    headers['Authorization'] = 'Bearer ${token.accessToken}';
  }

  return headers;
}
  // =========================
  // 📡 API Endpoints
  // =========================
  final String _baseUrl = _resolveHostBase();
Future<List<Reel>> fetchReels({
  int limit = 20,
  String? cursor,
}) async {
  try {
    final headers = await _getHeaders();
    final uri = Uri.parse('$_baseUrl/api/reels/feed').replace(
      queryParameters: {
        'limit': limit.toString(),
        if (cursor != null) 'cursor': cursor,
      },
    );

    print('🔍 Fetching reels from: $uri'); // Debug
    final response = await http.get(uri, headers: headers);
    print('📡 Response status: ${response.statusCode}'); // Debug
    print('📦 Response body: ${response.body}'); // Debug

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final reelsList = data['reels'] as List;
      return reelsList.map((json) => Reel.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load reels: ${response.statusCode}');
    }
  } catch (e) {
    throw Exception('Fetch reels error: $e');
  }
}

  Future<void> trackView({
    required String reelId,
    String? category,
    String? emojiReaction,
  }) async {
    await trackReelView(
      reelId: reelId,
      durationMs: 0,
      completed: false,
      category: category,
      emojiReaction: emojiReaction,
    );
  }

  Future<void> trackReelView({
    required String reelId,
    required int durationMs,
    required bool completed,
    String? category,
    String? sessionId,
    String? emojiReaction,
    int? pausedCount,
    bool? replayed,
    bool? shared,
    bool? saved,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$_baseUrl/api/reels/track-view'),
        headers: headers,
        body: jsonEncode({
          'reel_id': reelId,
          'duration_ms': durationMs,
          'completed': completed,
          if (category != null) 'category': category,
          if (sessionId != null) 'session_id': sessionId,
          if (emojiReaction != null) 'emoji_reaction': emojiReaction,
          if (pausedCount != null) 'paused_count': pausedCount,
          if (replayed != null) 'replayed': replayed,
          if (shared != null) 'shared': shared,
          if (saved != null) 'saved': saved,
        }),
      );

      if (response.statusCode != 200) {
        print('Track view error: ${response.statusCode}');
      }
    } catch (e) {
      print('Track view exception: $e');
    }
  }

  Future<void> trackDetailView({
    required String reelId,
    required int durationMs,
    bool? clickedSource,
  }) async {
    try {
      final headers = await _getHeaders();
      final response = await http.post(
        Uri.parse('$_baseUrl/api/reels/track-detail-view'),
        headers: headers,
        body: jsonEncode({
          'reel_id': reelId,
          'duration_ms': durationMs,
          if (clickedSource != null) 'clicked_source': clickedSource,
        }),
      );

      if (response.statusCode != 200) {
        print('Track detail view error: ${response.statusCode}');
      }
    } catch (e) {
      print('Track detail view exception: $e');
    }
  }

  Future<Map<String, dynamic>?> fetchDailyProgress(String userId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$_baseUrl/api/reels/user/$userId/daily-progress'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Fetch daily progress error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> fetchUserStats(String userId) async {
    try {
      final headers = await _getHeaders();
      final response = await http.get(
        Uri.parse('$_baseUrl/api/reels/user/$userId/stats'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Fetch user stats error: $e');
      return null;
    }
  }

  Future<void> trackEmoji({
    required String reelId,
    required String emoji,
    String? category,
  }) async {
    await trackView(
      reelId: reelId,
      category: category,
      emojiReaction: emoji,
    );
  }
}