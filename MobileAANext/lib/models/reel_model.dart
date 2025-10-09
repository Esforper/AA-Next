// lib/models/reel_model.dart
class Reel {
  final String id;
  final NewsData newsData;
  final String audioUrl;
  final int durationSeconds;
  final DateTime publishedAt;
  final bool isWatched;
  final List<SubtitleSegment>? subtitles;  // ✅ YENİ: Alt yazı desteği

  Reel({
    required this.id,
    required this.newsData,
    this.audioUrl = '',
    this.durationSeconds = 0,
    DateTime? publishedAt,
    this.isWatched = false,
    this.subtitles,  // ✅ YENİ
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
    final m = (json['news_data'] ?? json['newsData'] ?? {}) as Map<String, dynamic>;
    final List imgsRaw = (m['images'] ?? []) as List? ?? [];
    final images = imgsRaw
        .map((e) => (e ?? '').toString())
        .where((s) => s.startsWith('http://') || s.startsWith('https://'))
        .toList();

    final dynamic fcRaw = m['full_content'] ?? m['fullContent'] ?? [];
    final List<String> fullContent;
    if (fcRaw is List) {
      fullContent = fcRaw
          .map((e) => (e ?? '').toString())
          .where((s) => s.isNotEmpty)
          .toList();
    } else if (fcRaw is String) {
      fullContent = fcRaw.split('\n\n').where((s) => s.isNotEmpty).toList();
    } else {
      fullContent = [];
    }

    // ✅ YENİ: Alt yazıları parse et
    List<SubtitleSegment>? subtitles;
    if (json['subtitles'] != null) {
      final subsRaw = json['subtitles'] as List;
      subtitles = subsRaw.map((s) => SubtitleSegment.fromJson(s)).toList();
    }

    return Reel(
      id: (json['id'] ?? '').toString(),
      newsData: NewsData(
        title: (m['title'] ?? '').toString(),
        summary: (m['summary'] ?? m['description'] ?? '').toString(),
        url: (m['url'] ?? '').toString(),
        images: images,
        category: (m['category'] ?? 'Genel').toString(),
        keywords: ((m['keywords'] as List?) ?? []).map((e) => e.toString()).toList(),
        fullContent: fullContent,
      ),
      audioUrl: (json['audio_url'] ?? json['audioUrl'] ?? '').toString(),
      durationSeconds: int.tryParse((json['duration_seconds'] ?? 0).toString()) ?? 0,
      publishedAt: DateTime.tryParse(
          (m['published_at'] ?? json['published_at'] ?? '').toString()) ?? DateTime.now(),
      isWatched: (json['is_watched'] ?? false) as bool,
      subtitles: subtitles,  // ✅ YENİ
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'news_data': newsData.toJson(),
      'audio_url': audioUrl,
      'duration_seconds': durationSeconds,
      'published_at': publishedAt.toIso8601String(),
      'is_watched': isWatched,
      'subtitles': subtitles?.map((s) => s.toJson()).toList(),  // ✅ YENİ
    };
  }
}

// ✅ YENİ: Alt yazı segment modeli
class SubtitleSegment {
  final double startTime;  // saniye cinsinden
  final double endTime;
  final String text;

  SubtitleSegment({
    required this.startTime,
    required this.endTime,
    required this.text,
  });

  factory SubtitleSegment.fromJson(Map<String, dynamic> json) {
    return SubtitleSegment(
      startTime: (json['start_time'] ?? 0).toDouble(),
      endTime: (json['end_time'] ?? 0).toDouble(),
      text: (json['text'] ?? '').toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start_time': startTime,
      'end_time': endTime,
      'text': text,
    };
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

  factory NewsData.fromJson(Map<String, dynamic> json) {
    final List imgsRaw = (json['images'] ?? []) as List? ?? [];
    final images = imgsRaw
        .map((e) => (e ?? '').toString())
        .where((s) => s.startsWith('http://') || s.startsWith('https://'))
        .toList();

    final dynamic fcRaw = json['full_content'] ?? json['fullContent'] ?? [];
    final List<String> fullContent;
    if (fcRaw is List) {
      fullContent = fcRaw
          .map((e) => (e ?? '').toString())
          .where((s) => s.isNotEmpty)
          .toList();
    } else if (fcRaw is String) {
      fullContent = fcRaw.split('\n\n').where((s) => s.isNotEmpty).toList();
    } else {
      fullContent = [];
    }

    return NewsData(
      title: (json['title'] ?? '').toString(),
      summary: (json['summary'] ?? json['description'] ?? '').toString(),
      url: (json['url'] ?? '').toString(),
      images: images,
      category: (json['category'] ?? 'Genel').toString(),
      keywords: ((json['keywords'] as List?) ?? []).map((e) => e.toString()).toList(),
      fullContent: fullContent,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'summary': summary,
      'url': url,
      'images': images,
      'category': category,
      'keywords': keywords,
      'full_content': fullContent,
    };
  }
}