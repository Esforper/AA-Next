// lib/providers/saved_reels_provider.dart

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/saved_reel.dart';

class SavedReelsProvider extends ChangeNotifier {
  final List<SavedReel> _savedReels = [];

  List<SavedReel> get savedReels => _savedReels;

  bool isSaved(String reelId) {
    return _savedReels.any((r) => r.reelId == reelId);
  }

  Future<void> init() async {
    await _loadFromStorage();
    notifyListeners();
  }

  // Reel kaydet
  void saveReel({
    required String reelId,
    required String title,
    required String imageUrl,
  }) {
    if (isSaved(reelId)) {
      debugPrint('Reel already saved: $reelId');
      return;
    }

    final saved = SavedReel(
      reelId: reelId,
      title: title,
      imageUrl: imageUrl,
      savedAt: DateTime.now(),
    );

    _savedReels.insert(0, saved); // En başa ekle
    _saveToStorage();
    notifyListeners();

    debugPrint('✅ Reel saved: $title');
  }

  // Kaydı kaldır
  void unsaveReel(String reelId) {
    _savedReels.removeWhere((r) => r.reelId == reelId);
    _saveToStorage();
    notifyListeners();

    debugPrint('❌ Reel unsaved: $reelId');
  }

  // Toggle
  void toggleSave({
    required String reelId,
    required String title,
    required String imageUrl,
  }) {
    if (isSaved(reelId)) {
      unsaveReel(reelId);
    } else {
      saveReel(reelId: reelId, title: title, imageUrl: imageUrl);
    }
  }

  // Storage'a kaydet
  Future<void> _saveToStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final data = _savedReels.map((r) => r.toJson()).toList();
      await prefs.setString('saved_reels', jsonEncode(data));
    } catch (e) {
      debugPrint('Save error: $e');
    }
  }

  // Storage'dan yükle
  Future<void> _loadFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final dataStr = prefs.getString('saved_reels');

      if (dataStr == null) return;

      final List<dynamic> data = jsonDecode(dataStr);
      _savedReels.clear();
      _savedReels.addAll(data.map((json) => SavedReel.fromJson(json)));

      debugPrint('✅ Loaded ${_savedReels.length} saved reels');
    } catch (e) {
      debugPrint('Load error: $e');
    }
  }

  // Clear all
  void clearAll() {
    _savedReels.clear();
    _saveToStorage();
    notifyListeners();
  }
}