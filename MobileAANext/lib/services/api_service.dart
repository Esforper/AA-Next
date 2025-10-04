// lib/services/api_service.dart - HATA DÜZELTİLMİŞ, SON HALİ

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform, SocketException, HttpException;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import '../models/reel_model.dart';

class ApiService {
  final String baseUrl;
  final http.Client _c;

  factory ApiService.auto({int port = 8000, http.Client? client, String? override}) {
    final resolved = _resolveBaseUrl(port: port, override: override);
    return ApiService(resolved, client);
  }

  ApiService(this.baseUrl, [http.Client? c]) : _c = c ?? http.Client();

  Future<FeedResponse> getFeed({
    String? cursor,
    int limit = 20,
    String userId = "anonymous_user",
  }) async {
    final uri = Uri.parse('$baseUrl/api/reels/feed').replace(queryParameters: {
      'limit': '$limit',
      if (cursor != null) 'cursor': cursor,
    });

    // =======================================================================
    // DÜZELTME BURADA:
    // Değiştirilemez `_jsonHeaders`'ı doğrudan değiştirmek yerine,
    // onun bir kopyasını oluşturup yeni başlığı o kopyaya ekliyoruz.
    final headers = {
      ..._jsonHeaders, // Spread operatörü ile eski başlıkları kopyala
      'X-User-ID': userId, // Yeni başlığı ekle
    };
    // =======================================================================

    final response = await _safeGet(uri, headers: headers);
    final decodedBody = _decodeJson(response.body);
    return FeedResponse.fromJson(decodedBody);
  }

  void dispose() {
    _c.close();
  }

  static String _resolveBaseUrl({required int port, String? override}) {
     if (override != null && override.isNotEmpty) return override;
     if (kIsWeb) return 'http://localhost:$port';
     if (Platform.isAndroid) return 'http://10.0.2.2:$port';
     return 'http://127.0.0.1:$port';
  }
  
  static const Duration _timeout = Duration(seconds: 15);

  Future<http.Response> _safeGet(
    Uri uri, {
    Map<String, String>? headers,
    bool allowNon200 = false,
  }) async {
    http.Response r;
    try {
      r = await _c.get(uri, headers: headers ?? _jsonHeaders).timeout(_timeout);
    } on SocketException {
      throw Exception('Sunucuya ulaşılamadı: ${uri.host}');
    } on TimeoutException {
      throw Exception('İstek zaman aşımına uğradı (GET): $uri');
    } catch (e) {
      throw Exception('Bilinmeyen bir ağ hatası oluştu: $e');
    }

    if (!allowNon200 && r.statusCode != 200) {
      throw Exception('GET ${uri.path} başarısız: ${r.statusCode} - ${r.body}');
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