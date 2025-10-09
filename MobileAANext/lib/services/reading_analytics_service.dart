import 'dart:async';
import 'package:flutter/foundation.dart';

/// Okuma analitiklerini yöneten servis.
/// Bu servis, bir makalenin ne kadar süreyle ve ne kadarının okunduğunu takip eder.
class ReadingAnalyticsService {
  final String articleId;
  Timer? _timer;
  final Stopwatch _stopwatch = Stopwatch();
  double _maxScrollDepth = 0.0; // 0.0 ile 1.0 arasında

  // Servis, belirli bir makale ID'si ile başlatılır.
  ReadingAnalyticsService({required this.articleId});

  /// Takip oturumunu başlatır.
  /// Okumaya başlama zamanını kaydeder.
  void startTracking() {
    debugPrint('[Analytics] Tracking started for article: $articleId');
    _stopwatch.start();
  }

  /// Mevcut scroll ilerlemesini günceller.
  /// Kullanıcının makalede ulaştığı en derin noktayı kaydeder.
  void updateScrollProgress(double currentProgress) {
    if (currentProgress > _maxScrollDepth) {
      _maxScrollDepth = currentProgress;
    }
  }

  /// Takip oturumunu sonlandırır.
  /// Zamanlayıcıyı durdurur ve son analitik verilerini backend'e gönderir.
  void stopTracking() {
    _stopwatch.stop();
    debugPrint('[Analytics] Tracking stopped for article: $articleId');
    debugPrint('[Analytics] Total time spent: ${_stopwatch.elapsedMilliseconds}ms');
    debugPrint('[Analytics] Max scroll depth: ${(_maxScrollDepth * 100).toStringAsFixed(1)}%');

    _sendAnalyticsData();
  }

  /// Toplanan verileri backend'e gönderen özel fonksiyon.
  /// Gerçek bir uygulamada burada bir API çağrısı yapılır.
  Future<void> _sendAnalyticsData() async {
    // Sadece anlamlı bir okuma süresi ve ilerlemesi varsa veri gönder.
    // Örn: en az 5 saniye okuduysa ve %10'dan fazlasını gördüyse.
    if (_stopwatch.elapsedMilliseconds > 5000 && _maxScrollDepth > 0.1) {
      debugPrint('[Analytics] Sending data to backend...');
      debugPrint('  - Article ID: $articleId');
      debugPrint('  - Duration (ms): ${_stopwatch.elapsedMilliseconds}');
      debugPrint('  - Max Scroll Depth: $_maxScrollDepth');
      
      // NOT: Gerçek ApiService çağrısını buraya ekleyebilirsiniz.
      // await ApiService().trackDetailView(
      //   reelId: articleId,
      //   durationMs: _stopwatch.elapsedMilliseconds,
      //   scrollDepth: _maxScrollDepth,
      // );
    } else {
       debugPrint('[Analytics] Not enough data to send. User interaction was too short.');
    }
  }
}
