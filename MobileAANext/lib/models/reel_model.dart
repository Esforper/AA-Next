import 'dart:convert';

class Reel {
  final String id;
  final String title;
  final String summary;
  final String url;
  final List<String> images;
  final String? mainImage;
  final String fullContent;
  final String category;
  final DateTime publishedAt;
  final bool isWatched;

  Reel({
    required this.id,
    required this.title,
    required this.summary,
    required this.url,
    required this.images,
    this.mainImage,
    required this.fullContent,
    required this.category,
    required this.publishedAt,
    this.isWatched = false,
  });

  factory Reel.fromMockupJson(Map<String, dynamic> json) {
    final nd = json['news_data'] ?? {};
    return Reel(
      id: (json['id'] ?? '').toString(),
      title: nd['title'] ?? '',
      summary: nd['summary'] ?? '',
      url: nd['url'] ?? '',
      images: List<String>.from(nd['images'] ?? const []),
      mainImage: nd['main_image'],
      fullContent: nd['full_content'] ?? '',
      category: nd['category'] ?? '',
      publishedAt:
          DateTime.tryParse(nd['published_date'] ?? '') ?? DateTime.now(),
    );
  }

  static List<Reel> listFromMockup(String body) {
    final data = jsonDecode(body);
    final List items = data['reels'] ?? [];
    return items.map((e) => Reel.fromMockupJson(e)).toList();
  }
}
