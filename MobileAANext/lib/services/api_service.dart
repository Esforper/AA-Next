// lib/services/api_service.dart
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/reel_model.dart';
import 'auth_service.dart';

class ApiService {
  // =========================
  // 💡 Esnek host çözümleme
  // =========================
  static const int _port = 8000;

  static final String _baseFromDefine =
      const String.fromEnvironment('BACKEND_BASE', defaultValue: '');

  static final String _ipFromDefine =
      const String.fromEnvironment('BACKEND_IP', defaultValue: '');

  static final bool _useEmulator =
      const String.fromEnvironment('USE_EMULATOR', defaultValue: 'false')
              .toLowerCase() ==
          'true';

  static String _resolveHostBase() {
    if (_baseFromDefine.isNotEmpty) {
      return _baseFromDefine;
    }

    if (kIsWeb) {
      return Uri.base.origin;
    }

    if (!kIsWeb && _isIOS) {
      return 'http://localhost:$_port';
    }

    if (!kIsWeb && _isAndroid) {
      if (_ipFromDefine.isNotEmpty) {
        return 'http://$_ipFromDefine:$_port';
      }

      if (_useEmulator) {
        return 'http://10.0.2.2:$_port';
      }

      return 'http://localhost:$_port';
    }

    return 'http://localhost:$_port';
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

  /// Authorization header'ını al (token varsa)
  Future<Map<String, String>> _getHeaders() async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    // Token varsa ekle
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

  /// Reels feed'ini çek
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

      final response = await http.get(uri, headers: headers);

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

  /// Reel izleme tracking'i gönder (kısa versiyon)
  Future<void> trackView({
    required String reelId,
    String? category,
  }) async {
    await trackReelView(
      reelId: reelId,
      durationMs: 0,
      completed: false,
      category: category,
    );
  }

  /// Reel izleme tracking'i gönder (detaylı)
  Future<void> trackReelView({
    required String reelId,
    required int durationMs,
    required bool completed,
    String? category,
    String? sessionId,
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
        }),
      );

      if (response.statusCode != 200) {
        print('Track view error: ${response.statusCode}');
      }
    } catch (e) {
      print('Track view exception: $e');
    }
  }

  /// Detail view tracking'i gönder
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

  /// Günlük progress'i al
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

  /// User istatistiklerini al
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
}
