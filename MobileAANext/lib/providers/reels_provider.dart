import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/reel_model.dart';
import '../services/api_service.dart';

class ReelsProvider with ChangeNotifier {
  final ApiService api;
  final FlutterTts _tts = FlutterTts();

  List<Reel> reels = [];
  int currentIndex = 0;
  bool overlayOpen = false;

  String? speakingReelId;
  bool get isSpeaking => speakingReelId != null;

  ReelsProvider(this.api) {
    _initTts();
  }

  Future<void> _initTts() async {
    await _tts.setLanguage("tr-TR");
    await _tts.setSpeechRate(0.46);
    await _tts.setPitch(1.0);
    await _tts.awaitSpeakCompletion(true);
    _tts.setCompletionHandler(() {
      speakingReelId = null;
      notifyListeners();
    });
    _tts.setCancelHandler(() {
      speakingReelId = null;
      notifyListeners();
    });
  }

  Future<void> loadMock() async {
    reels = await api.getMockupReels(count: 15);
    notifyListeners();
  }

  void onPageChanged(int i) {
    currentIndex = i;
    overlayOpen = false;
    if (isSpeaking) stopSpeaking();
    notifyListeners();
    _delayedTrack();
  }

  void setOverlay(bool v) {
    overlayOpen = v;
    if (v && isSpeaking) stopSpeaking();
    notifyListeners();
  }

  Future<void> speakSummary(Reel reel) async {
    if (speakingReelId == reel.id) {
      await stopSpeaking();
      return;
    }
    if (speakingReelId != null) {
      await _tts.stop();
    }
    speakingReelId = reel.id;
    notifyListeners();
    final text = reel.summary.isNotEmpty ? reel.summary : reel.title;
    await _tts.speak(text);
  }

  Future<void> stopSpeaking() async {
    await _tts.stop();
    speakingReelId = null;
    notifyListeners();
  }

  Future<void> _delayedTrack() async {
    final captured = currentIndex;
    await Future.delayed(const Duration(seconds: 3));
    if (captured == currentIndex && reels.isNotEmpty) {
      final reel = reels[currentIndex];
      api.trackView(
        reelId: reel.id,
        durationMs: 3000,
        completed: false,
        category: reel.category,
      );
    }
  }

  @override
  void dispose() {
    _tts.stop();
    super.dispose();
  }
}
