class Reel {
  final String id;
  final NewsData newsData;
  final String audioUrl;
  final int durationSeconds;
  final DateTime publishedAt;
  final bool isWatched;

  Reel({
    required this.id,
    required this.newsData,
    this.audioUrl = '',
    this.durationSeconds = 0,
    DateTime? publishedAt,
    this.isWatched = false,
  }) : publishedAt = publishedAt ?? DateTime.now();

  // UI kolaylığı için kısayollar
  String get title => newsData.title;
  String get summary => newsData.summary;
  String get url => newsData.url;
  String get category => newsData.category;
  List<String> get imageUrls => newsData.images;
  List<String> get fullContent => newsData.fullContent;
  String get fullText =>
      fullContent.isEmpty ? summary : fullContent.join('\n\n');

  factory Reel.fromJson(Map<String, dynamic> json) {
    final m =
        (json['news_data'] ?? json['newsData'] ?? {}) as Map<String, dynamic>;
    final List imgsRaw = (m['images'] ?? []) as List? ?? [];
    final images = imgsRaw
        .map((e) => (e ?? '').toString())
        .where((s) => s.startsWith('http://') || s.startsWith('https://'))
        .toList();

    final List fcRaw =
        (m['full_content'] ?? m['fullContent'] ?? []) as List? ?? [];
    final fullContent = fcRaw
        .map((e) => (e ?? '').toString())
        .where((s) => s.isNotEmpty)
        .toList();

    return Reel(
      id: (json['id'] ?? '').toString(),
      newsData: NewsData(
        title: (m['title'] ?? '').toString(),
        summary: (m['summary'] ?? m['description'] ?? '').toString(),
        url: (m['url'] ?? '').toString(),
        images: images,
        category: (m['category'] ?? 'Genel').toString(),
        keywords:
            ((m['keywords'] as List?) ?? []).map((e) => e.toString()).toList(),
        fullContent: fullContent,
      ),
      audioUrl: (json['audio_url'] ?? json['audioUrl'] ?? '').toString(),
      durationSeconds:
          int.tryParse((json['duration_seconds'] ?? 0).toString()) ?? 0,
      publishedAt: DateTime.tryParse(
          (m['published_at'] ?? json['published_at'] ?? '').toString()),
      isWatched: (json['is_watched'] == true) || (json['isWatched'] == true),
    );
  }
}

class NewsData {
  final String title;
  final String summary;
  final String url;
  final List<String> images;
  final String category;
  final List<String> keywords;
  final List<String> fullContent;

  NewsData({
    required this.title,
    required this.summary,
    required this.url,
    required this.images,
    required this.category,
    required this.keywords,
    required this.fullContent,
  });
}
