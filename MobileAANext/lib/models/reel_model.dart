// Reel model: FastAPI mock API'sindeki news_data yapısını karşılar.
class Reel {
  final String id;
  final String title;
  final String summary;
  final String url;
  final String imageUrl;
  final String category;
  final DateTime publishedAt;
  final bool isWatched;

  Reel({
    required this.id,
    required this.title,
    required this.summary,
    required this.url,
    required this.imageUrl,
    required this.category,
    required this.publishedAt,
    this.isWatched = false,
  });

  factory Reel.fromJson(Map<String, dynamic> json) {
    // news_data içindeki alanlara erişiyoruz
    final Map<String, dynamic>? newsData =
        json['news_data'] as Map<String, dynamic>?;

    // Görsel için main_image veya images listesinin ilk öğesini kullan
    String imageUrl =
        'https://via.placeholder.com/400x600.png?text=Haber+Resmi';
    if (newsData != null) {
      if (newsData['main_image'] != null &&
          (newsData['main_image'] as String).isNotEmpty) {
        imageUrl = newsData['main_image'] as String;
      } else if (newsData['images'] is List &&
          (newsData['images'] as List).isNotEmpty) {
        imageUrl = (newsData['images'] as List).first as String;
      }
    }

    return Reel(
      id: json['id']?.toString() ?? '',
      title: newsData?['title'] as String? ?? 'Başlık Yok',
      summary: newsData?['summary'] as String? ?? 'Özet bulunamadı.',
      url: newsData?['url'] as String? ?? '',
      imageUrl: imageUrl,
      category: newsData?['category'] as String? ?? 'Genel',
      // FastAPI mock data'da tarih news_data.published_date alanında geliyor
      publishedAt: newsData?['published_date'] != null
          ? DateTime.parse(newsData!['published_date'] as String)
          : DateTime.now(),
      // API yanıtında is_watched alanı yoksa false
      isWatched: json['is_watched'] as bool? ?? false,
    );
  }
}
