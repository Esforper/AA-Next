// lib/providers/reels_provider.dart - MANTIK HATASI DÜZELTİLMİŞ HALİ

import 'package:flutter/foundation.dart';
import 'package:audioplayers/audioplayers.dart';
import '../services/api_service.dart';
import '../models/reel_model.dart';

class ReelsProvider with ChangeNotifier {
  final ApiService _apiService;
  final AudioPlayer _audioPlayer = AudioPlayer();

  ReelsProvider(this._apiService) {
    print("✅ [PROVIDER] ReelsProvider oluşturuldu.");

    _audioPlayer.onPlayerComplete.listen((_) {
      _playingReelId = null;
      notifyListeners();
    });
  }

  List<Reel> _reels = [];
  List<Reel> get reels => _reels;

  String? _nextCursor;
  bool _hasNextPage = true;
  bool _isLoading = false;
  int _currentPageIndex = 0;
  
  String? _playingReelId;
  String? get playingReelId => _playingReelId;

  bool _overlayOpen = false;
  bool get overlayOpen => _overlayOpen;

  Future<void> fetchInitialFeed() async {
    print("🚀 [PROVIDER] fetchInitialFeed() çağrıldı.");
    
    if (_isLoading) {
      print("⚠️ [PROVIDER] Zaten bir yükleme devam ediyor, fetchInitialFeed iptal edildi.");
      return;
    }
    
    _isLoading = true;
    _reels = [];
    _nextCursor = null;
    _hasNextPage = true;
    notifyListeners();

    await _fetchMoreReels();
  }
  
  Future<void> _fetchMoreReels() async {
    // ‼️ SORUNLU KISIM BURADAYDI. BU KONTROL KALDIRILDI. ‼️
    // `isLoading` kontrolü zaten bu fonksiyonu çağıran yerlerde yapılıyor.
    // if (_isLoading || !_hasNextPage) { ... } // <-- BU BLOK SİLİNDİ.

    // Sadece `hasNextPage` kontrolü kalabilir, bu mantıklı.
    if (!_hasNextPage) {
       print("⚠️ [PROVIDER] Yüklenecek başka sayfa yok, _fetchMoreReels iptal edildi.");
       _isLoading = false; // Yüklemeyi bitir.
       notifyListeners();
       return;
    }
    
    // Bu satır da gereksizdi, çünkü çağıran fonksiyon zaten _isLoading'ı yönetiyor.
    // _isLoading = true; 

    print("🔄 [PROVIDER] _fetchMoreReels() çalışıyor, API'den veri çekilecek...");

    try {
      final response = await _apiService.getFeed(cursor: _nextCursor);
      
      print("✅ [PROVIDER] API'den yanıt alındı. ${response.reels.length} adet yeni reel geldi. hasNext: ${response.pagination.hasNext}");

      _reels.addAll(response.reels);
      _hasNextPage = response.pagination.hasNext;
      _nextCursor = response.pagination.nextCursor;

    } catch (e, stacktrace) {
      print("❌❌❌ [PROVIDER] KRİTİK HATA: API'den veri çekilemedi! ❌❌❌");
      print("Hata Mesajı: $e");
      print("Hata Detayı (Stacktrace): $stacktrace");
      _hasNextPage = false; 
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

   void onPageChanged(int index) {
    _currentPageIndex = index;
    
    if (_reels.isNotEmpty && index < _reels.length) {
      playAudio(_reels[index]);
    }
    
    // Buradaki `!_isLoading` kontrolü sayesinde `_fetchMoreReels` tekrar tekrar çağrılmaz.
    if (index >= _reels.length - 2 && _hasNextPage && !_isLoading) {
      print(" приближаемся к концу списка, загружаем еще...");
      _fetchMoreReels();
    }
  }

  Future<void> playAudio(Reel reel) async {
    if (_playingReelId == reel.id) {
      await _audioPlayer.stop();
      _playingReelId = null;
    } else {
      if (_audioPlayer.state == PlayerState.playing) {
        await _audioPlayer.stop();
      }
      await _audioPlayer.play(UrlSource(reel.audioUrl));
      _playingReelId = reel.id;
    }
    notifyListeners();
  }

  void setOverlay(bool isOpen) {
    if (_overlayOpen == isOpen) return;
    _overlayOpen = isOpen;

    if (_overlayOpen) {
      if (_audioPlayer.state == PlayerState.playing) {
        _audioPlayer.pause();
      }
    } else {
       if (_audioPlayer.state == PlayerState.paused) {
        _audioPlayer.resume();
      }
    }
    notifyListeners();
  }
  
  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }
}