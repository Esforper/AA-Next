// lib/services/audio_service.dart
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

  bool get isPlaying => _isPlaying;
  Duration get position => _position;
  Duration get duration => _duration;
  String? get currentReelId => _currentReelId;

  AudioService() {
    // ✅ YENİ: PlayerMode ayarla
    _player.setReleaseMode(ReleaseMode.stop);
    _player.setPlayerMode(PlayerMode.mediaPlayer);
    
    _player.onPlayerStateChanged.listen((state) {
      _isPlaying = state == PlayerState.playing;
      debugPrint('🎵 Player state: $state');  // ✅ Debug log
      notifyListeners();
    });

    _player.onPositionChanged.listen((pos) {
      _position = pos;
      notifyListeners();
    });

    _player.onDurationChanged.listen((dur) {
      _duration = dur;
      debugPrint('🎵 Duration: $dur');  // ✅ Debug log
      notifyListeners();
    });
    
    // ✅ YENİ: Error listener
    _player.onPlayerComplete.listen((event) {
      debugPrint('🎵 Player completed');
    });
  }

  // ✅ YENİ: Base URL'i al (.env'den)
  String _getBaseUrl() {
    final envUrl = dotenv.env['API_URL'];
    if (envUrl != null && envUrl.isNotEmpty) {
      return envUrl;
    }

    // Fallback
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
      
      // ✅ URL'i düzelt
      String fullUrl = audioUrl;
      if (!audioUrl.startsWith('http://') && !audioUrl.startsWith('https://')) {
        final baseUrl = _getBaseUrl();
        final cleanAudioUrl = audioUrl.startsWith('/') ? audioUrl.substring(1) : audioUrl;
        fullUrl = '$baseUrl/$cleanAudioUrl';
      }
      
      debugPrint('🎵 Playing audio: $fullUrl');
      
      // ✅ DEĞİŞTİ: Basit yaklaşım - direkt play
      await _player.stop();  // Önce durdur
      await _player.play(UrlSource(fullUrl), volume: 1.0);  // Volume ekle
      
      _isPlaying = true;
      notifyListeners();
      
      debugPrint('✅ Audio play() called');
    } catch (e) {
      debugPrint('❌ Audio play error: $e');
      _isPlaying = false;
      notifyListeners();
    }
  }

  /// Sesi duraklat
  Future<void> pause() async {
    await _player.pause();
    _isPlaying = false;
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
    notifyListeners();
  }

  /// Belirli pozisyona git
  Future<void> seek(Duration position) async {
    await _player.seek(position);
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}