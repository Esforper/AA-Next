// lib/providers/reels_provider.dart
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../models/reel_model.dart';

enum FeedStatus { initial, loading, loaded, error }

class ReelsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final AudioService _audioService = AudioService();
  
  final List<Reel> _reels = [];
  int _current = 0;
  FeedStatus _status = FeedStatus.initial;

  List<Reel> get reels => _reels;
  int get currentIndex => _current;
  Reel? get current => _reels.isEmpty ? null : _reels[_current];
  FeedStatus get status => _status;
  AudioService get audioService => _audioService;

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

      // ✅ İlk reel'in sesini başlat
      if (_reels.isNotEmpty && _reels[0].audioUrl.isNotEmpty) {
        await _audioService.play(_reels[0].audioUrl, _reels[0].id);
      }

      _status = FeedStatus.loaded;
    } catch (e, st) {
      debugPrint('ReelsProvider.loadReels() error: $e');
      debugPrintStack(stackTrace: st);
      _status = FeedStatus.error;
    } finally {
      notifyListeners();
    }
  }

  void setIndex(int i) async {
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

      // ✅ Yeni reel'in sesini çal
      if (reel.audioUrl.isNotEmpty) {
        await _audioService.play(reel.audioUrl, reel.id);
      } else {
        await _audioService.stop();
      }
    }

    notifyListeners();
  }

  @override
  void dispose() {
    _audioService.dispose();
    super.dispose();
  }
}