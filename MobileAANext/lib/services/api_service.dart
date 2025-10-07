// lib/services/api_service.dart
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/reel_model.dart';

class ApiService {
  // =========================
  // 💡 Esnek host çözümleme
  // =========================
  //
  // Öncelik sırası (Android):
  // 1) --dart-define=BACKEND_BASE="http://X.X.X.X:8000" (varsa hep bunu kullan)
  // 2) ADB reverse aktifse: http://localhost:8000
  // 3) Emülatör kullanıyorsan: http://10.0.2.2:8000
  //
  // iOS sim/cihaz: http://localhost:8000
  // Web: mevcut origin (örn. http://localhost:5555)
  //
  // Not: Cleartext (http) için AndroidManifest + network_security_config ayarlı olmalı.

  static const int _port = 8000;

  // İstersen komple base’i tek define ile geç (en esnek yöntem):
  // flutter run --dart-define=BACKEND_BASE=http://192.168.1.8:8000
  static final String _baseFromDefine =
      const String.fromEnvironment('BACKEND_BASE', defaultValue: '');

  // Sadece IP geçmek istersen (base değil):
  // flutter run --dart-define=BACKEND_IP=192.168.1.8
  static final String _ipFromDefine =
      const String.fromEnvironment('BACKEND_IP', defaultValue: '');

  // Emülatör zorlaması için (gerekirse):
  // flutter run --dart-define=USE_EMULATOR=true
  static final bool _useEmulator =
      const String.fromEnvironment('USE_EMULATOR', defaultValue: 'false')
              .toLowerCase() ==
          'true';

  // Ana hostu üret
  static String _resolveHostBase() {
    // 0) Tam base define edilmişse onu kullan (en üst öncelik)
    if (_baseFromDefine.isNotEmpty) {
      return _baseFromDefine; // ör. http://10.42.0.55:8000
    }

    // 1) Web ise, bulunduğu origin'i kullan (CORS vs. için en doğrusu)
    if (kIsWeb) {
      return Uri.base.origin;
    }

    // 2) iOS sim/cihaz
    if (!kIsWeb && _isIOS) {
      return 'http://localhost:$_port';
    }

    // 3) Android (emülatör veya fiziksel cihaz)
    if (!kIsWeb && _isAndroid) {
      // 3.a) IP define verilmişse bunu kullan (Wi-Fi değişse de run komutunda geçersin)
      if (_ipFromDefine.isNotEmpty) {
        return 'http://$_ipFromDefine:$_port';
      }

      // 3.b) Emülatör zorlaması istenmişse
      if (_useEmulator) {
        return 'http://10.0.2.2:$_port';
      }

      // 3.c) Varsayılan strateji:
      // Önce ADB reverse varmış gibi localhost'u deneyeceğiz;
      // (biz burada sadece base üretiyoruz — çağrılar sırasında doğrudan kullanıyoruz.)
      // Eğer reverse yoksa ve fiziksel cihazdaysan yine çalışsın istiyorsan
      // run komutuna BACKEND_IP veya BACKEND_BASE geç.
      return 'http://localhost:$_port';
    }

    // 4) Masaüstü platformlar için fallback
    return 'http://localhost:$_port';
  }

  // Küçük yardımcılar
  static bool get _isAndroid {
    try {
      return Platform.isAndroid;
    } catch (_) {
      return false;
    }
  }

  static bool get _isIOS {
    try {
      return Platform.isIOS;
    } catch (_) {
      return false;
    }
  }

  // /api/reels kökü
  static String get _reelsBase => '${_resolveHostBase()}/api/reels';

  static Map<String, String> _headers(String userId) => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-User-ID': userId,
      };

  // =========================
  // FEED
  // =========================
  static Future<List<Reel>> fetchReels({
    int limit = 20,
    String userId = 'anonymous_user',
  }) async {
    try {
      final uri = Uri.parse('$_reelsBase/feed')
          .replace(queryParameters: {'limit': '$limit'});

      final res = await http.get(uri, headers: _headers(userId));

      if (res.statusCode == 200) {
        // Türkçe karakter bozulmasını engelle
        final body = utf8.decode(res.bodyBytes);
        final data = jsonDecode(body) as Map<String, dynamic>;
        final list = (data['reels'] ?? []) as List;
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

  // =========================
  // TRACK VIEW
  // =========================
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
      final uri = Uri.parse('$_reelsBase/track-view');
      final res = await http.post(
        uri,
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
