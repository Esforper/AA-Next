// lib/providers/reels_provider.dart
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../models/reel_model.dart';

enum FeedStatus { initial, loading, loaded, error }

class ReelsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  // ❌ KALDIRILDI: final AudioService _audioService = AudioService();
  // ✅ YENİ: AudioService artık main.dart'tan inject edilecek
  
  final List<Reel> _reels = [];
  int _current = 0;
  FeedStatus _status = FeedStatus.initial;

  List<Reel> get reels => _reels;
  int get currentIndex => _current;
  Reel? get current => _reels.isEmpty ? null : _reels[_current];
  FeedStatus get status => _status;
  
  // ✅ YENİ: AudioService getter - context.read<AudioService>() ile alınacak
  // Bu getter artık kullanılmayacak, doğrudan Provider.of<AudioService> kullanılacak

  Future<void> loadReels() async {
    if (_status == FeedStatus.loading) return;
    
    _status = FeedStatus.loading;
    notifyListeners();

    try {
      final List<Reel> data = await _apiService.fetchReels();
      _reels
        ..clear()
        ..addAll(data);
      _current = 0;

      // ❌ KALDIRILDI: İlk reel'in sesini başlatma kodu
      // Audio artık reels_feed_page.dart'ta kontrol edilecek

      _status = FeedStatus.loaded;
    } catch (e, st) {
      debugPrint('ReelsProvider.loadReels() error: $e');
      debugPrintStack(stackTrace: st);
      _status = FeedStatus.error;
    } finally {
      notifyListeners();
    }
  }

  void setIndex(int i) {
    if (i < 0 || i >= _reels.length || i == _current) return;
    _current = i;

    final reel = current;
    if (reel != null) {
      debugPrint('[Reels] visible -> ${reel.id}');
      
      // ✅ View tracking
      _apiService.trackView(
        reelId: reel.id,
        category: reel.category,
      );

      // ❌ KALDIRILDI: Audio play kodu
      // Audio artık reels_feed_page.dart'ta kontrol edilecek
    }

    notifyListeners();
  }

  @override
  void dispose() {
    // ❌ KALDIRILDI: _audioService.dispose()
    // AudioService artık ayrı bir provider, kendi dispose'unu kendisi yapacak
    super.dispose();
  }
}