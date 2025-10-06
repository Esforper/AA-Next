// lib/providers/reels_provider.dart
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/reel_model.dart';

class ReelsProvider with ChangeNotifier {
  final List<Reel> _reels = [];
  int _current = 0;

  bool _isDetailOpen = false;
  bool _isEmojiOpen = false;

  List<Reel> get reels => _reels;
  int get currentIndex => _current;
  Reel? get current => _reels.isEmpty ? null : _reels[_current];

  bool get isDetailOpen => _isDetailOpen;
  bool get isEmojiOpen => _isEmojiOpen;

  Future<void> loadReels() async {
    debugPrint('ReelsProvider.loadReels() → fetching...');
    final data = await ApiService.fetchReels();
    debugPrint('ReelsProvider.loadReels() → fetched ${data.length} items');
    _reels
      ..clear()
      ..addAll(data);
    _current = 0;
    notifyListeners();
  }

  void setIndex(int i) {
    if (i < 0 || i >= _reels.length) return;
    _current = i;
    notifyListeners();
  }

  void openDetail(bool v) {
    _isDetailOpen = v;
    if (v) _isEmojiOpen = false;
    notifyListeners();
  }

  void openEmoji(bool v) {
    _isEmojiOpen = v;
    if (v) _isDetailOpen = false;
    notifyListeners();
  }
}
