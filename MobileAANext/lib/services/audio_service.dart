// lib/services/audio_service.dart
// ⚠️ MEVCUT DOSYAYA EKLENECEK/GÜNCELLENECEKTİR
// AudioService class'ına aşağıdaki değişiklikleri yapın

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:io' show Platform;

class AudioService extends ChangeNotifier {
  final AudioPlayer _player = AudioPlayer();
  
  String? _currentReelId;
  bool _isPlaying = false;
  Duration _position = Duration.zero;
  Duration _duration = Duration.zero;

  // ✅ YENİ: Pause count tracking
  int _pauseCountForCurrentReel = 0;

  bool get isPlaying => _isPlaying;
  Duration get position => _position;
  Duration get duration => _duration;
  String? get currentReelId => _currentReelId;
  
  // ✅ YENİ: Pause count getter
  int get pauseCountForCurrentReel => _pauseCountForCurrentReel;

  AudioService() {
    _player.setReleaseMode(ReleaseMode.stop);
    _player.setPlayerMode(PlayerMode.mediaPlayer);
    
    _player.onPlayerStateChanged.listen((state) {
      _isPlaying = state == PlayerState.playing;
      debugPrint('🎵 Player state: $state');
      notifyListeners();
    });

    _player.onPositionChanged.listen((pos) {
      _position = pos;
      notifyListeners();
    });

    _player.onDurationChanged.listen((dur) {
      _duration = dur;
      debugPrint('🎵 Duration: $dur');
      notifyListeners();
    });
    
    _player.onPlayerComplete.listen((event) {
      debugPrint('🎵 Player completed');
    });
  }

  String _getBaseUrl() {
    final envUrl = dotenv.env['API_URL'];
    if (envUrl != null && envUrl.isNotEmpty) {
      return envUrl;
    }

    if (kIsWeb) {
      return Uri.base.origin;
    }

    try {
      if (!kIsWeb && Platform.isAndroid) {
        return 'http://10.0.2.2:8000';
      }
      if (!kIsWeb && Platform.isIOS) {
        return 'http://localhost:8000';
      }
    } catch (_) {}

    return 'http://localhost:8000';
  }

  /// Ses çal (reels değiştiğinde çağrılır)
  Future<void> play(String audioUrl, String reelId) async {
    if (_currentReelId == reelId && _isPlaying) return;

    try {
      _currentReelId = reelId;
      
      // ✅ YENİ: Yeni reel başladığında pause count'u sıfırla
      _pauseCountForCurrentReel = 0;
      
      String fullUrl = audioUrl;
      if (!audioUrl.startsWith('http://') && !audioUrl.startsWith('https://')) {
        final baseUrl = _getBaseUrl();
        final cleanAudioUrl = audioUrl.startsWith('/') ?
            audioUrl.substring(1) : audioUrl;
        fullUrl = '$baseUrl/$cleanAudioUrl';
      }
      
      debugPrint('🎵 Playing audio: $fullUrl');
      
      await _player.stop();
      await _player.play(UrlSource(fullUrl), volume: 1.0);
      
      _isPlaying = true;
      notifyListeners();
      
      debugPrint('✅ Audio play() called');
    } catch (e) {
      debugPrint('❌ Audio play error: $e');
      _isPlaying = false;
      notifyListeners();
    }
  }

  /// ✅ GÜNCELLEME: Sesi duraklat + pause count artır
  Future<void> pause() async {
    await _player.pause();
    _isPlaying = false;
    
    // ✅ YENİ: Pause count artır
    _pauseCountForCurrentReel++;
    debugPrint('⏸️ Paused (count: $_pauseCountForCurrentReel)');
    
    notifyListeners();
  }

  /// Devam ettir
  Future<void> resume() async {
    await _player.resume();
    _isPlaying = true;
    notifyListeners();
  }

  /// Durdur
  Future<void> stop() async {
    await _player.stop();
    _isPlaying = false;
    _position = Duration.zero;
    _currentReelId = null;
    
    // ✅ YENİ: Stop edildiğinde pause count'u sıfırla
    _pauseCountForCurrentReel = 0;
    
    notifyListeners();
  }

  /// Belirli pozisyona git
  Future<void> seek(Duration position) async {
    await _player.seek(position);
  }

  /// ✅ YENİ: Completed kontrolü (reel'in %80'i izlendi mi?)
  bool isCompleted() {
    if (_duration == Duration.zero) return false;
    
    // %80+ izlendiyse completed
    final completionThreshold = _duration.inMilliseconds * 0.8;
    final isCompleted = _position.inMilliseconds >= completionThreshold;
    
    debugPrint('🎯 Completion check: ${_position.inMilliseconds}ms / ${_duration.inMilliseconds}ms = ${isCompleted ? "COMPLETED" : "PARTIAL"}');
    
    return isCompleted;
  }

  /// ✅ YENİ: Pause count'u sıfırla (yeni reel başladığında dışarıdan çağrılabilir)
  void resetPauseCount() {
    _pauseCountForCurrentReel = 0;
    debugPrint('🔄 Pause count reset');
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}