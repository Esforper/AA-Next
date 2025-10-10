// lib/providers/gamification_provider.dart

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/gamification_state.dart';
import '../services/auth_service.dart';
import '../services/gamification_api_service.dart';
/// Gamification Provider
/// XP, Level, Streak yönetimi + Local Storage
class GamificationProvider extends ChangeNotifier {
  GamificationState _state = const GamificationState();
  final AuthService _authService = AuthService();
  Future<String?> _getUserId() async {
    final user = await _authService.getUser();
    return user?.id;
  }
  // Reels tracking için
  final Map<String, bool> _emojiGivenPerReel = {};
  final Map<String, bool> _shareGivenPerReel = {};
  
  GamificationState get state => _state;
  
  // Quick getters
  int get currentXP => _state.currentXP;
  int get dailyXPGoal => _state.dailyXPGoal;
  int get currentLevel => _state.currentLevel;
  int get currentNode => _state.currentNode;
  int get currentStreak => _state.currentStreak;
  double get dailyProgress => _state.dailyProgress;
  double get nodeProgress => _state.nodeProgress;
  double get levelProgress => _state.levelProgress;
  bool get dailyGoalCompleted => _state.dailyGoalCompleted;
  
  // ============ INITIALIZATION ============
  
  /// Provider'ı başlat
  Future<void> init() async {
    await _loadFromStorage();
    _checkDailyReset();
    notifyListeners();
  }
  
  // ============ XP İŞLEMLERİ ============
  
  // XP eklerken backend'e de gönder
  Future<void> addXP(int amount, String source) async {
    // 1. Local state güncelle
    _state = _state.addXP(amount, source);
    
    // 2. Backend'e sync (opsiyonel)
    final userId = await _getUserId();
    if (userId != null) {
      await _syncToBackend(userId, amount, source);
    }
    
    notifyListeners();
  }

    Future<void> _syncToBackend(String userId, int xp, String source) async {
    try {
      // Backend API çağrısı
      await GamificationApiService().addXP(
        userId: userId,
        xpAmount: xp,
        source: source,
      );
    } catch (e) {
      debugPrint('⚠️ Backend sync failed: $e');
      // Hata olsa bile local state güncel
    }
  }
  
  /// Reels izlendi (3+ saniye)
  /// 10 XP
  void onReelWatched(String reelId) {
    addXP(10, 'reel_watched');
  }
  
  /// Emoji atıldı (sadece 1 kere)
  /// 5 XP
  bool onEmojiGiven(String reelId) {
    // Bu reel'e daha önce emoji atıldı mı?
    if (_emojiGivenPerReel[reelId] == true) {
      return false; // Zaten emoji atılmış
    }
    
    _emojiGivenPerReel[reelId] = true;
    addXP(5, 'emoji_given');
    return true;
  }
  
  /// Detail okundu (10+ saniye)
  /// 5 XP
  void onDetailRead(String reelId) {
    addXP(5, 'detail_read');
  }
  
  /// Paylaşım yapıldı (ilk paylaşım)
  /// 5 XP
  bool onShareGiven(String reelId) {
    // Bu reel daha önce paylaşıldı mı?
    if (_shareGivenPerReel[reelId] == true) {
      return false; // Zaten paylaşılmış
    }
    
    _shareGivenPerReel[reelId] = true;
    addXP(5, 'share_given');
    return true;
  }
  
  // ============ EMOJI/SHARE KONTROLÜ ============
  
  /// Reels'e emoji atılmış mı?
  bool hasEmojiGiven(String reelId) {
    return _emojiGivenPerReel[reelId] == true;
  }
  
  /// Reels paylaşılmış mı?
  bool hasShareGiven(String reelId) {
    return _shareGivenPerReel[reelId] == true;
  }
  
  // ============ GÜNLÜK RESET ============
  
  /// Günlük reset kontrolü
  void _checkDailyReset() {
    if (_state.lastActivityDate == null) return;
    
    final now = DateTime.now();
    final lastDate = _state.lastActivityDate!;
    
    final isNewDay = now.day != lastDate.day ||
                     now.month != lastDate.month ||
                     now.year != lastDate.year;
    
    if (isNewDay) {
      _performDailyReset();
    }
  }
  
  /// Günlük sıfırlama işlemi
  void _performDailyReset() {
    _state = _state.resetDaily();
    
    // Emoji ve paylaşım tracking'i temizle
    _emojiGivenPerReel.clear();
    _shareGivenPerReel.clear();
    
    _saveToStorage();
    debugPrint('📅 Günlük reset yapıldı. Streak: ${_state.currentStreak}');
  }
  
  /// Manuel günlük reset (test için)
  void forceResetDaily() {
    _performDailyReset();
    notifyListeners();
  }
  
  // ============ LOCAL STORAGE ============
  
  static const String _storageKey = 'gamification_state_v2';
  static const String _emojiTrackingKey = 'emoji_tracking';
  static const String _shareTrackingKey = 'share_tracking';
  
  /// Storage'a kaydet
  Future<void> _saveToStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // State'i kaydet
      final stateJson = jsonEncode(_state.toJson());
      await prefs.setString(_storageKey, stateJson);
      
      // Emoji tracking kaydet
      final emojiJson = jsonEncode(_emojiGivenPerReel);
      await prefs.setString(_emojiTrackingKey, emojiJson);
      
      // Share tracking kaydet
      final shareJson = jsonEncode(_shareGivenPerReel);
      await prefs.setString(_shareTrackingKey, shareJson);
      
    } catch (e) {
      debugPrint('❌ Storage kayıt hatası: $e');
    }
  }
  
  /// Storage'dan yükle
  Future<void> _loadFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // State'i yükle
      final stateStr = prefs.getString(_storageKey);
      if (stateStr != null) {
        final stateJson = jsonDecode(stateStr) as Map<String, dynamic>;
        _state = GamificationState.fromJson(stateJson);
      } else {
        // İlk açılış - mock data
        _state = GamificationState.mock();
      }
      
      // Emoji tracking yükle
      final emojiStr = prefs.getString(_emojiTrackingKey);
      if (emojiStr != null) {
        final emojiJson = jsonDecode(emojiStr) as Map<String, dynamic>;
        _emojiGivenPerReel.clear();
        emojiJson.forEach((key, value) {
          _emojiGivenPerReel[key] = value as bool;
        });
      }
      
      // Share tracking yükle
      final shareStr = prefs.getString(_shareTrackingKey);
      if (shareStr != null) {
        final shareJson = jsonDecode(shareStr) as Map<String, dynamic>;
        _shareGivenPerReel.clear();
        shareJson.forEach((key, value) {
          _shareGivenPerReel[key] = value as bool;
        });
      }
      
      debugPrint('✅ Storage yüklendi. Level: ${_state.currentLevel}, XP: ${_state.totalXP}');
      
    } catch (e) {
      debugPrint('❌ Storage yükleme hatası: $e');
      _state = GamificationState.mock();
    }
  }
  
  // ============ LEVEL UP CALLBACK ============
  
  /// Level atlandığında çağrılır
  void _onLevelUp() {
    debugPrint('🎉 LEVEL UP! Yeni level: ${_state.currentLevel}');
    // TODO: Celebration animasyonu göster
  }
  
  // ============ DEBUG & TEST ============
  
  /// Tüm verileri sıfırla (test için)
  Future<void> resetAll() async {
    _state = const GamificationState();
    _emojiGivenPerReel.clear();
    _shareGivenPerReel.clear();
    await _saveToStorage();
    notifyListeners();
    debugPrint('🔄 Tüm veriler sıfırlandı');
  }
  
  /// Debug bilgisi
  void printDebugInfo() {
    debugPrint('=== GAMIFICATION DEBUG ===');
    debugPrint('Level: ${_state.currentLevel}');
    debugPrint('Node: ${_state.currentNode}/${_state.nodesInLevel}');
    debugPrint('Current XP: ${_state.currentXP}/100');
    debugPrint('Total XP: ${_state.totalXP}');
    debugPrint('Daily XP: ${_state.xpEarnedToday}/${_state.dailyXPGoal}');
    debugPrint('Streak: ${_state.currentStreak} gün');
    debugPrint('Emoji given count: ${_emojiGivenPerReel.length}');
    debugPrint('Share given count: ${_shareGivenPerReel.length}');
    debugPrint('==========================');
  }
  
  /// Manuel XP ekle (test için)
  void addTestXP(int amount) {
    addXP(amount, 'test');
  }
}