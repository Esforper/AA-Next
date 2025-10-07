// lib/providers/reels_provider.dart
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/reel_model.dart';

enum FeedStatus { initial, loading, loaded, error }

class ReelsProvider with ChangeNotifier {
  final List<Reel> _reels = [];
  int _current = 0;
  FeedStatus _status = FeedStatus.initial;

  List<Reel> get reels => _reels;
  int get currentIndex => _current;
  Reel? get current => _reels.isEmpty ? null : _reels[_current];
  FeedStatus get status => _status;

  /// Reels'i yükle (re-entrancy koruması ile)
  Future<void> loadReels() async {
    if (_status == FeedStatus.loading)
      return; // aynı anda birden fazla çağrıyı engelle
    _status = FeedStatus.loading;
    notifyListeners();

    try {
      final List<Reel> data = await ApiService.fetchReels();
      _reels
        ..clear()
        ..addAll(data);
      _current = 0;

      // Boş listeyse UI'da "Gösterilecek içerik yok" göstermek için loaded bırakıyoruz.
      _status = FeedStatus.loaded;
    } catch (e, st) {
      debugPrint('ReelsProvider.loadReels() error: $e');
      debugPrintStack(stackTrace: st);
      _status = FeedStatus.error;
    } finally {
      notifyListeners();
    }
  }

  /// Dikey PageView sayfası değiştiğinde çağrılır
  void setIndex(int i) {
    if (i < 0 || i >= _reels.length || i == _current) return;
    _current = i;

    final reel = current;
    if (reel != null) {
      debugPrint('[Reels] visible -> ${reel.id}');
      // Buraya istersen "mark seen / kısa izleme" tracking'ini koyabilirsin.
      // ApiService.trackView(reelId: reel.id, category: reel.category);
    }

    notifyListeners();
  }
}
