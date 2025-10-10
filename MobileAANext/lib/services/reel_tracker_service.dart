// lib/services/reel_tracker_service.dart

import 'package:flutter/foundation.dart';
import 'api_service.dart';

/// Tek bir reel'in izlenme tracking'ini yöneten servis
/// Her reel için bir instance oluşturulur
class ReelTrackerService {
  final String reelId;
  final String? category;
  final ApiService _apiService;
  
  late DateTime _startTime;
  int _pauseCount = 0;
  String? _emojiReaction;
  bool _shared = false;
  bool _saved = false;
  bool _isStopped = false;

  ReelTrackerService({
    required this.reelId,
    this.category,
    ApiService? apiService,
  }) : _apiService = apiService ?? ApiService();

  /// Tracking'i başlat
  void start() {
    _startTime = DateTime.now();
    _pauseCount = 0;
    _emojiReaction = null;
    _shared = false;
    _saved = false;
    _isStopped = false;
    
    debugPrint('🎬 Tracker started: $reelId');
  }

  /// Pause sayısını artır
  void onPause() {
    if (_isStopped) return;
    _pauseCount++;
    debugPrint('⏸️ Pause count: $_pauseCount for $reelId');
  }

  /// Emoji tepkisi kaydet
  void onEmoji(String emoji) {
    if (_isStopped) return;
    _emojiReaction = emoji;
    debugPrint('❤️ Emoji set: $emoji for $reelId');
  }

  /// Paylaşım yapıldı
  void onShare() {
    if (_isStopped) return;
    _shared = true;
    debugPrint('📤 Shared: $reelId');
  }

  /// Kaydetme yapıldı
  void onSave() {
    if (_isStopped) return;
    _saved = true;
    debugPrint('💾 Saved: $reelId');
  }

  /// Tracking'i durdur ve backend'e gönder
  Future<void> stop({
    required bool completed,
    int? overrideDurationMs,
  }) async {
    if (_isStopped) {
      debugPrint('⚠️ Tracker already stopped for $reelId');
      return;
    }

    _isStopped = true;

    // İzlenme süresini hesapla
    final durationMs = overrideDurationMs ?? 
                       DateTime.now().difference(_startTime).inMilliseconds;

    debugPrint('🛑 Tracker stopping: $reelId');
    debugPrint('  ├─ Duration: ${durationMs}ms');
    debugPrint('  ├─ Completed: $completed');
    debugPrint('  ├─ Pause count: $_pauseCount');
    debugPrint('  ├─ Emoji: ${_emojiReaction ?? "none"}');
    debugPrint('  ├─ Shared: $_shared');
    debugPrint('  └─ Saved: $_saved');

    // Backend'e gönder
    try {
      await _apiService.trackView(
        reelId: reelId,
        durationMs: durationMs,
        completed: completed,
        category: category,
        emojiReaction: _emojiReaction,
        pauseCount: _pauseCount,
        shared: _shared,
        saved: _saved,
      );
      
      debugPrint('✅ Tracking sent successfully for $reelId');
    } catch (e) {
      debugPrint('❌ Tracking failed for $reelId: $e');
      // Hata olsa bile devam et (kullanıcı deneyimini etkilemesin)
    }
  }

  /// Tracking durumunu kontrol et
  bool get isStopped => _isStopped;

  /// Mevcut izlenme süresi (ms)
  int get currentDurationMs {
    if (_isStopped) return 0;
    return DateTime.now().difference(_startTime).inMilliseconds;
  }

  /// Tracker bilgilerini debug için
  Map<String, dynamic> getDebugInfo() {
    return {
      'reel_id': reelId,
      'duration_ms': currentDurationMs,
      'pause_count': _pauseCount,
      'emoji': _emojiReaction,
      'shared': _shared,
      'saved': _saved,
      'is_stopped': _isStopped,
    };
  }
}