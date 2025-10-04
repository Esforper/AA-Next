// lib/services/api_service.dart
import 'dart:async'; // <-- TimeoutException burada
import 'dart:convert';
import 'dart:io'
    show Platform, SocketException, HttpException; // <-- bu ikileri ekledik
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

import '../models/reel_model.dart';

/// API ile konuşmak için tek kapı.
/// - Android emülatör: http://10.0.2.2:<port>
/// - iOS simülatör:    http://127.0.0.1:<port>
/// - Web:              http://localhost:<port>
class ApiService {
  final String baseUrl;
  final http.Client _c;

  /// Otomatik baseUrl çözen kurucu.
  /// Örn: `final api = ApiService.auto(port: 8000);`
  factory ApiService.auto(
      {int port = 8000, http.Client? client, String? override}) {
    final resolved = _resolveBaseUrl(port: port, override: override);
    return ApiService(resolved, client);
  }

  ApiService(this.baseUrl, [http.Client? c]) : _c = c ?? http.Client();

  // ---------- Public Methods ----------

  /// Mockup Reels getirir (backend: /api/reels/mockup/generate-reels)
  Future<List<Reel>> getMockupReels({int count = 10}) async {
    final uri = Uri.parse('$baseUrl/api/reels/mockup/generate-reels')
        .replace(queryParameters: {'count': '$count'});

    final r = await _safeGet(uri);
    // r.body zaten String; modelin beklediği String ise bunu direkt kullanmak daha hızlı:
    return Reel.listFromMockup(r.body);
    // Eğer model JSON Map bekleseydi: final body = _decodeJson(r.body);
  }

  /// Bir reel izlenmesini backend’e bildirir (fire-and-forget).
  Future<void> trackView({
    required String reelId,
    required int durationMs,
    required bool completed,
    String? category,
  }) async {
    final uri = Uri.parse('$baseUrl/api/reels/track-view');
    final payload = {
      'reel_id': reelId,
      'duration_ms': durationMs,
      'completed': completed,
      'category': category,
    };

    await _safePost(uri, payload, allowNon200: false);
  }

  /// Çoklu reel’i “görüldü” işaretler.
  Future<void> markSeen(List<String> reelIds) async {
    final uri = Uri.parse('$baseUrl/api/reels/mark-seen');
    final payload = {'reel_ids': reelIds};
    await _safePost(uri, payload, allowNon200: false);
  }

  /// Haber makalesinin tam içeriğini çeker.
  Future<String> fetchFullArticle(String url) async {
    final uri = Uri.parse('$baseUrl/api/news/article').replace(
        queryParameters: {'url': Uri.encodeComponent(url)}); // encodeComponent

    final r = await _safeGet(uri, allowNon200: true);
    if (r.statusCode != 200) return '';

    final j = _decodeJson(r.body);
    final article = j['article'];
    if (article is Map && article['content'] is String) {
      return article['content'] as String;
    }
    return '';
  }

  /// HTTP client’ı kapatmak istersen (örn. dispose’da).
  void dispose() {
    _c.close();
  }

  // ---------- Internal: Base URL Resolver ----------

  static String _resolveBaseUrl({required int port, String? override}) {
    if (override != null && override.isNotEmpty) {
      return override.endsWith('/')
          ? override.substring(0, override.length - 1)
          : override;
    }

    if (kIsWeb) {
      return 'http://localhost:$port';
    }

    // Mobil/platform
    try {
      if (Platform.isAndroid) return 'http://localhost:$port';
      if (Platform.isIOS) return 'http://127.0.0.1:$port';
    } catch (_) {
      // Bazı ortamlarda Platform erişimi kısıtlı olabilir → localhost’a düş
    }
    return 'http://localhost:$port';
  }

  // ---------- Internal: Safe HTTP helpers ----------

  static const Duration _timeout = Duration(seconds: 15);

  Future<http.Response> _safeGet(
    Uri uri, {
    bool allowNon200 = false,
  }) async {
    http.Response r;
    try {
      r = await _c.get(uri, headers: _jsonHeaders).timeout(_timeout);
    } on SocketException {
      throw Exception('Sunucuya ulaşılamadı: ${uri.host}');
    } on HttpException {
      throw Exception('HTTP hatası (GET): $uri');
    } on FormatException {
      throw Exception('Geçersiz yanıt formatı (GET): $uri');
    } on TimeoutException {
      throw Exception('İstek zaman aşımına uğradı (GET): $uri');
    }

    if (!allowNon200 && r.statusCode != 200) {
      throw Exception('GET ${uri.path} başarısız: ${r.statusCode} - ${r.body}');
    }
    return r;
  }

  Future<http.Response> _safePost(
    Uri uri,
    Map<String, dynamic> payload, {
    bool allowNon200 = false,
  }) async {
    http.Response r;
    try {
      r = await _c
          .post(uri, headers: _jsonHeaders, body: jsonEncode(payload))
          .timeout(_timeout);
    } on SocketException {
      throw Exception('Sunucuya ulaşılamadı: ${uri.host}');
    } on HttpException {
      throw Exception('HTTP hatası (POST): $uri');
    } on FormatException {
      throw Exception('Geçersiz yanıt formatı (POST): $uri');
    } on TimeoutException {
      throw Exception('İstek zaman aşımına uğradı (POST): $uri');
    }

    if (!allowNon200 && r.statusCode != 200) {
      throw Exception(
          'POST ${uri.path} başarısız: ${r.statusCode} - ${r.body}');
    }
    return r;
  }

  Map<String, String> get _jsonHeaders => const {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  dynamic _decodeJson(String body) {
    try {
      return jsonDecode(body);
    } catch (_) {
      throw Exception('Sunucudan geçersiz JSON döndü.');
    }
  }
}
