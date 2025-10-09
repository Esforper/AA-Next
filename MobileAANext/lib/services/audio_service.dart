// lib/services/audio_service.dart
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

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
    _player.onPlayerStateChanged.listen((state) {
      _isPlaying = state == PlayerState.playing;
      notifyListeners();
    });

    _player.onPositionChanged.listen((pos) {
      _position = pos;
      notifyListeners();
    });

    _player.onDurationChanged.listen((dur) {
      _duration = dur;
      notifyListeners();
    });
  }

  /// Ses çal (reels değiştiğinde çağrılır)
  Future<void> play(String audioUrl, String reelId) async {
    if (_currentReelId == reelId && _isPlaying) return;

    try {
      _currentReelId = reelId;
      await _player.stop();
      await _player.play(UrlSource(audioUrl));
      _isPlaying = true;
      notifyListeners();
    } catch (e) {
      debugPrint('Audio play error: $e');
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