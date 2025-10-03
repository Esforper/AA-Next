import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/reel_model.dart';

class ApiService {
  /// Android emülatör: backend lokalde ise 10.0.2.2 kullan
  final String baseUrl;
  ApiService({this.baseUrl = 'http://10.0.2.2:8000'});

  Future<List<Reel>> fetchReels(
      {int count = 5, String voice = 'alloy', String? category}) async {
    final uri = Uri.parse('$baseUrl/api/reels/mockup/generate-reels').replace(
      queryParameters: <String, String>{
        'count': '$count',
        'voice': voice,
        if (category != null) 'category': category,
      },
    );

    final res = await http.get(uri);
    if (res.statusCode != 200) {
      throw Exception(
          'Mockup reels fetch failed: ${res.statusCode} ${res.body}');
    }

    final body = jsonDecode(res.body) as Map<String, dynamic>;
    final list = (body['reels'] as List?) ?? const [];
    return list.map((e) => Reel.fromJson(e as Map<String, dynamic>)).toList();
  }
}
