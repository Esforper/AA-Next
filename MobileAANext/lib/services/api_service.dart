import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/reel_model.dart';

class ApiService {
  final String baseUrl;
  final http.Client _c;
  ApiService(this.baseUrl, [http.Client? c]) : _c = c ?? http.Client();

  Future<List<Reel>> getMockupReels({int count = 10}) async {
    final r = await _c.get(
      Uri.parse('$baseUrl/api/reels/mockup/generate-reels?count=$count'),
    );
    if (r.statusCode != 200) {
      throw Exception('Mockup reels alınamadı: ${r.statusCode}');
    }
    return Reel.listFromMockup(r.body);
  }

  Future<void> trackView({
    required String reelId,
    required int durationMs,
    required bool completed,
    String? category,
  }) async {
    await _c.post(
      Uri.parse('$baseUrl/api/reels/track-view'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "reel_id": reelId,
        "duration_ms": durationMs,
        "completed": completed,
        "category": category
      }),
    );
  }

  Future<void> markSeen(List<String> reelIds) async {
    await _c.post(
      Uri.parse('$baseUrl/api/reels/mark-seen'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({"reel_ids": reelIds}),
    );
  }

  Future<String> fetchFullArticle(String url) async {
    final r = await _c.get(
      Uri.parse('$baseUrl/api/news/article?url=${Uri.encodeComponent(url)}'),
    );
    if (r.statusCode != 200) return '';
    final j = jsonDecode(r.body);
    return (j['article']?['content'] ?? '') as String;
  }
}
