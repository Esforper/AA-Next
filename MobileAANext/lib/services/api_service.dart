// lib/services/api_service.dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/reel_model.dart';

class ApiService {
  /// Android emülatör için local FastAPI:
  /// iOS sim veya web kullanıyorsan: http://localhost:8000
  static const String _base = 'http://10.0.2.2:8000/api/reels';

  static Map<String, String> _headers(String userId) => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-User-ID': userId,
      };

  /// Ana feed (tek sayfa)
  static Future<List<Reel>> fetchReels({
    int limit = 20,
    String userId = 'anonymous_user',
  }) async {
    try {
      final uri = Uri.parse('$_base/feed')
          .replace(queryParameters: {'limit': '$limit'});

      final res = await http.get(uri, headers: _headers(userId));

      if (res.statusCode == 200) {
        // Türkçe karakter bozulmasını engelle
        final body = utf8.decode(res.bodyBytes);
        final data = jsonDecode(body) as Map<String, dynamic>;
        final List list = (data['reels'] ?? []) as List;
        return list
            .map((e) => Reel.fromJson(e as Map<String, dynamic>))
            .toList();
      } else {
        debugPrint('fetchReels status=${res.statusCode} body=${res.body}');
      }
    } catch (e) {
      debugPrint('fetchReels error: $e');
    }
    return const [];
  }

  /// İzleme/tepki kaydı (POST /api/reels/track-view)
  /// ReelsFeedPage'te çağırdığın metod bu.
  static Future<bool> trackView({
    required String reelId,
    int durationMs = 0,
    bool completed = false,
    String? category,
    String? sessionId,
    String? emojiReaction, // ör: '👍'
    int? pausedCount,
    bool? replayed,
    bool? shared,
    bool? saved,
    String userId = 'anonymous_user',
  }) async {
    final body = <String, dynamic>{
      'reel_id': reelId,
      'duration_ms': durationMs,
      'completed': completed,
      'category': category,
      'session_id': sessionId,
      // yeni sinyaller
      'emoji_reaction': emojiReaction,
      'paused_count': pausedCount,
      'replayed': replayed,
      'shared': shared,
      'saved': saved,
    }..removeWhere((k, v) => v == null);

    try {
      final res = await http.post(
        Uri.parse('$_base/track-view'),
        headers: _headers(userId),
        body: jsonEncode(body),
      );

      debugPrint('trackView status=${res.statusCode} body=${res.body}');
      return res.statusCode == 200;
    } catch (e) {
      debugPrint('trackView error: $e');
      return false;
    }
  }
}
