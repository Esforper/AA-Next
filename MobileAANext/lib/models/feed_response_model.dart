// // lib/models/feed_response_model.dart

// // Bu dosyayı reel_model.dart veya benzeri bir dosyadan import etmeniz gerekebilir.
// // Reel, NewsData gibi sınıfların burada olduğunu varsayıyorum.
// // Eğer yoksa, onları da Python modellerine bakarak oluşturmalısınız.

// class Reel {
//   final String id;
//   final NewsData newsData;
//   final String audioUrl;
//   final int durationSeconds;
//   // Diğer alanları Python'daki ReelFeedItem modeline göre ekleyebilirsiniz.

//   Reel({
//     required this.id,
//     required this.newsData,
//     required this.audioUrl,
//     required this.durationSeconds,
//   });

//   factory Reel.fromJson(Map<String, dynamic> json) {
//     return Reel(
//       id: json['id'],
//       newsData: NewsData.fromJson(json['news_data']),
//       audioUrl: json['audio_url'],
//       durationSeconds: json['duration_seconds'],
//     );
//   }
// }

// class NewsData {
//   final String title;
//   final String summary;
//   final List<String> fullContent; // Backend'de liste, burada da liste olmalı.
//   final String category;

//   NewsData({
//     required this.title,
//     required this.summary,
//     required this.fullContent,
//     required this.category,
//   });

//   factory NewsData.fromJson(Map<String, dynamic> json) {
//     return NewsData(
//       title: json['title'],
//       summary: json['summary'],
//       // Gelen verinin bir liste olduğundan emin olmak için List.from kullanılır.
//       fullContent: List<String>.from(json['full_content']),
//       category: json['category'],
//     );
//   }
// }

// class FeedPagination {
//   final bool hasNext;
//   final String? nextCursor;

//   FeedPagination({required this.hasNext, this.nextCursor});

//   factory FeedPagination.fromJson(Map<String, dynamic> json) {
//     return FeedPagination(
//       hasNext: json['has_next'],
//       nextCursor: json['next_cursor'],
//     );
//   }
// }

// class FeedResponse {
//   final List<Reel> reels;
//   final FeedPagination pagination;

//   FeedResponse({required this.reels, required this.pagination});

//   factory FeedResponse.fromJson(Map<String, dynamic> json) {
//     return FeedResponse(
//       // Gelen 'reels' listesindeki her bir objeyi Reel.fromJson ile dönüştür
//       reels: (json['reels'] as List).map((reelJson) => Reel.fromJson(reelJson)).toList(),
//       pagination: FeedPagination.fromJson(json['pagination']),
//     );
//   }
// }