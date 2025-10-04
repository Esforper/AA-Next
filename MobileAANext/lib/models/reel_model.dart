// lib/models/reel_model.dart - BACKEND'E UYGUN, SON HALİ

import 'dart:convert';

// ===============================================
// ANA REEL MODELİ (ReelFeedItem karşılığı)
// ===============================================

class Reel {
  final String id;
  final NewsData newsData;
  final String audioUrl;
  final int durationSeconds;
  final String voiceUsed;
  final DateTime publishedAt;
  final bool isWatched;
  final bool isTrending;
  final bool isRecommended;
  final String feedReason;
  
  // Backend'deki ReelFeedItem modelindeki diğer tüm alanları
  // ihtiyacınıza göre buraya ekleyebilirsiniz.

  Reel({
    required this.id,
    required this.newsData,
    required this.audioUrl,
    required this.durationSeconds,
    required this.voiceUsed,
    required this.publishedAt,
    this.isWatched = false,
    this.isTrending = false,
    this.isRecommended = false,
    required this.feedReason,
  });

  // Backend'den gelen JSON'ı Reel nesnesine çevirir.
  factory Reel.fromJson(Map<String, dynamic> json) {
    return Reel(
      id: json['id'] ?? '',
      newsData: NewsData.fromJson(json['news_data'] ?? {}),
      audioUrl: json['audio_url'] ?? '',
      durationSeconds: json['duration_seconds'] ?? 0,
      voiceUsed: json['voice_used'] ?? 'unknown',
      publishedAt: DateTime.tryParse(json['published_at'] ?? '') ?? DateTime.now(),
      isWatched: json['is_watched'] ?? false,
      isTrending: json['is_trending'] ?? false,
      isRecommended: json['is_recommended'] ?? false,
      feedReason: json['feed_reason'] ?? 'unknown',
    );
  }
}

// ===============================================
// HABER DETAY MODELİ (NewsData karşılığı)
// ===============================================

class NewsData {
  final String title;
  final String summary;
  // ÖNEMLİ: Bu alan artık bir String değil, bir String LİSTESİ.
  final List<String> fullContent; 
  final String url;
  final String category;
  final String? mainImage;
  final List<String> images;
  final List<String> keywords;

  NewsData({
    required this.title,
    required this.summary,
    required this.fullContent,
    required this.url,
    required this.category,
    this.mainImage,
    required this.images,
    required this.keywords,
  });

  factory NewsData.fromJson(Map<String, dynamic> json) {
    return NewsData(
      title: json['title'] ?? 'Başlık Yok',
      summary: json['summary'] ?? '',
      // Gelen verinin bir liste olduğundan emin olmak için List.from kullanılır.
      fullContent: List<String>.from(json['full_content'] ?? []),
      url: json['url'] ?? '',
      category: json['category'] ?? 'Kategori Yok',
      mainImage: json['main_image'],
      images: List<String>.from(json['images'] ?? []),
      keywords: List<String>.from(json['keywords'] ?? []),
    );
  }
}

// ===============================================
// SAYFALAMA VE FEED RESPONSE MODELLERİ
// ===============================================

class FeedPagination {
  final bool hasNext;
  final String? nextCursor;

  FeedPagination({required this.hasNext, this.nextCursor});

  factory FeedPagination.fromJson(Map<String, dynamic> json) {
    return FeedPagination(
      hasNext: json['has_next'] ?? false,
      nextCursor: json['next_cursor'],
    );
  }
}

class FeedResponse {
  final List<Reel> reels;
  final FeedPagination pagination;

  FeedResponse({required this.reels, required this.pagination});

  factory FeedResponse.fromJson(Map<String, dynamic> json) {
    final reelsList = (json['reels'] as List? ?? [])
        .map((reelJson) => Reel.fromJson(reelJson))
        .toList();
        
    return FeedResponse(
      reels: reelsList,
      pagination: FeedPagination.fromJson(json['pagination'] ?? {}),
    );
  }
}