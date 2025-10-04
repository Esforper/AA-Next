import 'package:flutter/material.dart';
// import 'package:flutter_tts/flutter_tts.dart'; // flutter_tts import'u kaldırıldı.
import '../models/reel_model.dart';
import '../services/api_service.dart';

class ReelsProvider with ChangeNotifier {
  final ApiService api;
  // final FlutterTts _tts = FlutterTts(); // TTS nesnesi kaldırıldı.

  List<Reel> reels = [];
  int currentIndex = 0;
  bool overlayOpen = false;

  // TTS ile ilgili durumlar kaldırıldı.
  // String? speakingReelId;
  // bool get isSpeaking => speakingReelId != null;

  // YERİNE BUNLARI KULLANABİLİRSİNİZ (Ses oynatıcı paketine göre değişir)
  String? playingReelId; // Şu an sesi çalan reel'in ID'si
  bool get isPlayingAudio =>
      playingReelId != null; // Sesin çalınıp çalınmadığını kontrol eder

  // ReelsProvider(this.api) {
  //   _initTts(); // TTS başlatma fonksiyonu kaldırıldı.
  // }
  ReelsProvider(this.api); // Kurucu metod sadeleştirildi.

  // _initTts metodu tamamen kaldırıldı.

  Future<void> loadMock() async {
    reels = await api.getMockupReels(count: 15);
    notifyListeners();
  }

  void onPageChanged(int i) {
    currentIndex = i;
    overlayOpen = false;
    // Sayfa değiştiğinde önceki ses durdurulmalı.
    if (isPlayingAudio) stopAudio();
    notifyListeners();
    _delayedTrack();
  }

  void setOverlay(bool v) {
    overlayOpen = v;
    // Overlay açıldığında ses durdurulmalı.
    if (v && isPlayingAudio) stopAudio();
    notifyListeners();
  }

  // Bu fonksiyon artık API'den gelen ses URL'sini oynatacak.
  Future<void> playAudio(Reel reel) async {
    // Eğer aynı reel'in sesi zaten çalıyorsa, durdur.
    if (playingReelId == reel.id) {
      await stopAudio();
      return;
    }
    // Eğer başka bir ses çalıyorsa, önce onu durdur.
    if (playingReelId != null) {
      await stopAudio();
    }

    playingReelId = reel.id;
    notifyListeners();

    // --- BURAYA SES OYNATICI KODU GELECEK ---
    // Örnek: await audioPlayer.play(UrlSource(reel.audioUrl));
    // Oynatma bittiğinde veya durdurulduğunda playingReelId'yi null yapmayı unutmayın.
    // audioPlayer.onPlayerCompletion.listen((event) {
    //   playingReelId = null;
    //   notifyListeners();
    // });
    print("Playing audio for reel: ${reel.id}");
  }

  // Bu fonksiyon ses oynatmayı durduracak.
  Future<void> stopAudio() async {
    // --- BURAYA SESİ DURDURMA KODU GELECEK ---
    // Örnek: await audioPlayer.stop();

    playingReelId = null;
    notifyListeners();
    print("Audio stopped.");
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
    // _tts.stop(); // TTS durdurma kaldırıldı.
    // Eğer ses oynatıcı kullanıyorsanız, burada temizlenmesi gerekir.
    // Örnek: audioPlayer.dispose();
    super.dispose();
  }
}
