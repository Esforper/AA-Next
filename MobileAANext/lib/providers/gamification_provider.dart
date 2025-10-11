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
    debugPrint('🎮 [Gamification] Initializing...');
    
    // Backend'den state çek
    final userId = await _getUserId();
    if (userId != null) {
      await _fetchStateFromBackend(userId);
    } else {
      debugPrint('⚠️ [Gamification] No user ID, using default state');
      _state = const GamificationState();
    }
    
    notifyListeners();
  }
  

/// Backend'den tüm state'i çek
Future<void> _fetchStateFromBackend(String userId) async {
  try {
    debugPrint('📥 [Fetch State] Fetching from backend for user: ${userId.substring(0, 8)}');
    
    final response = await GamificationApiService().getUserStats(userId: userId);
    
    if (response['success'] == true) {
      // Backend'den gelen veriyi state'e dönüştür
      _state = GamificationState(
        totalXP: response['total_xp'] ?? 0,
        currentLevel: response['current_level'] ?? 0,
        currentNode: response['current_node'] ?? 0,
        currentXP: response['current_xp'] ?? 0,
        nodesInLevel: response['nodes_in_level'] ?? 2,
        currentStreak: response['current_streak'] ?? 0,
        xpEarnedToday: response['today_stats']['xp_earned'] ?? 0,
        reelsWatchedToday: response['today_stats']['reels_watched'] ?? 0,
        emojisGivenToday: response['today_stats']['emojis_given'] ?? 0,
        detailsReadToday: response['today_stats']['details_read'] ?? 0,
        sharesGivenToday: response['today_stats']['shares_given'] ?? 0,
      );
      
      debugPrint('✅ [Fetch State] Success! Total XP: ${_state.totalXP}, Level: ${_state.currentLevel}');
    } else {
      debugPrint('❌ [Fetch State] Failed: ${response['message']}');
    }
  } catch (e) {
    debugPrint('❌ [Fetch State] Error: $e');
  }
}




  // ============ XP İŞLEMLERİ ============
  
  // XP eklerken backend'e de gönder
/// XP ekle - Backend'e gönder ve response'u kullan
Future<void> addXP(int amount, String source) async {
  debugPrint('💎 [Add XP] Adding $amount XP from $source');
  debugPrint('   Before: Total XP: ${_state.totalXP}, Level: ${_state.currentLevel}, Node: ${_state.currentNode}');
  
  // 1. Backend'e gönder
  final userId = await _getUserId();
  if (userId == null) {
    debugPrint('❌ [Add XP] No user ID');
    return;
  }
  
  try {
    final response = await GamificationApiService().addXP(
      userId: userId,
      xpAmount: amount,
      source: source,
    );
    
    if (response['success'] == true) {
      // 2. Backend'den gelen güncel state'i kullan
      _state = _state.copyWith(
        totalXP: response['total_xp'],
        currentLevel: response['current_level'],
        currentNode: response['current_node'],
        currentXP: response['current_xp'],
        nodesInLevel: response['nodes_in_level'],
      );
      
      // 3. Activity counts güncelle (local)
      if (source == 'reel_watched') {
        _state = _state.copyWith(reelsWatchedToday: _state.reelsWatchedToday + 1);
      } else if (source == 'emoji_given') {
        _state = _state.copyWith(emojisGivenToday: _state.emojisGivenToday + 1);
      } else if (source == 'detail_read') {
        _state = _state.copyWith(detailsReadToday: _state.detailsReadToday + 1);
      } else if (source == 'share_given') {
        _state = _state.copyWith(sharesGivenToday: _state.sharesGivenToday + 1);
      }
      
      debugPrint('✅ [Add XP] Success!');
      debugPrint('   After: Total XP: ${_state.totalXP}, Level: ${_state.currentLevel}, Node: ${_state.currentNode}');
      
      // Level up kontrolü
      if (response['level_up'] == true) {
        debugPrint('🎉 LEVEL UP! New level: ${_state.currentLevel}');
        _onLevelUp();
      }
      
      notifyListeners();
    } else {
      debugPrint('❌ [Add XP] Backend failed: ${response['message']}');
    }
  } catch (e) {
    debugPrint('❌ [Add XP] Error: $e');
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
  
// ============ NODE MANAGEMENT ============
  
  /// Node kontrolü - Oyun için yeterli node var mı?
  bool hasAvailableNodes({int requiredNodes = 1}) {
    final hasNodes = _state.currentNode >= requiredNodes;
    
    debugPrint('🎮 [Node Check] Current: ${_state.currentNode}, Required: $requiredNodes → $hasNodes');
    
    return hasNodes;
  }
  
  /// Node harca (oyuna giriş için)
/// Node harca - Backend'e gönder ve response'u kullan
Future<bool> spendNodes(int amount, {String reason = 'game_entry'}) async {
  debugPrint('💸 [Spend Node] Spending $amount node(s) for $reason');
  debugPrint('   Before: Level ${_state.currentLevel}, Node ${_state.currentNode}');
  
  // 1. Local kontrol
  if (_state.currentNode < amount) {
    debugPrint('❌ [Spend Node] Insufficient nodes: ${_state.currentNode} < $amount');
    return false;
  }
  
  // 2. Backend'e gönder
  final userId = await _getUserId();
  if (userId == null) {
    debugPrint('❌ [Spend Node] No user ID');
    return false;
  }
  
  try {
    final response = await GamificationApiService().spendNodes(
      userId: userId,
      amount: amount,
      reason: reason,
    );
    
    if (response['success'] == true) {
      // 3. Backend'den gelen güncel state'i kullan
      _state = _state.copyWith(
        totalXP: response['total_xp'],
        currentLevel: response['current_level'],
        currentNode: response['current_node'],
        currentXP: response['current_xp'],
        nodesInLevel: response['nodes_in_level'],
      );
      
      debugPrint('✅ [Spend Node] Success!');
      debugPrint('   After: Level ${_state.currentLevel}, Node ${_state.currentNode}');
      
      notifyListeners();
      return true;
    } else {
      debugPrint('❌ [Spend Node] Backend failed: ${response['message']}');
      return false;
    }
  } catch (e) {
    debugPrint('❌ [Spend Node] Error: $e');
    return false;
  }
}
  
  /// Node ekle (oyun ödülü)
/// Node ekle (oyun ödülü) - Backend'e gönder
Future<void> addNodes(int amount, {String source = 'game_reward'}) async {
  debugPrint('🎁 [Add Node] Adding $amount node(s) from $source');
  debugPrint('   Before: Level ${_state.currentLevel}, Node ${_state.currentNode}');
  
  final userId = await _getUserId();
  if (userId == null) {
    debugPrint('❌ [Add Node] No user ID');
    return;
  }
  
  try {
    final response = await GamificationApiService().addNodesReward(
      userId: userId,
      amount: amount,
      source: source,
    );
    
    if (response['success'] == true) {
      // Backend'den gelen güncel state'i kullan
      _state = _state.copyWith(
        totalXP: response['total_xp'],
        currentLevel: response['current_level'],
        currentNode: response['current_node'],
        currentXP: response['current_xp'],
        nodesInLevel: response['nodes_in_level'],
      );
      
      debugPrint('✅ [Add Node] Success!');
      debugPrint('   After: Level ${_state.currentLevel}, Node ${_state.currentNode}');
      
      // Level up kontrolü
      if (response['level_up'] == true) {
        debugPrint('🎉 LEVEL UP! New level: ${_state.currentLevel}');
        _onLevelUp();
      }
      
      notifyListeners();
    } else {
      debugPrint('❌ [Add Node] Backend failed: ${response['message']}');
    }
  } catch (e) {
    debugPrint('❌ [Add Node] Error: $e');
  }
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

  
  /// Manuel günlük reset (test için)
/// Manuel günlük reset (test için) - Backend'e gönder
Future<void> forceResetDaily() async {
  debugPrint('🔄 [Force Reset] Forcing daily reset...');
  
  final userId = await _getUserId();
  if (userId == null) {
    debugPrint('❌ [Force Reset] No user ID');
    return;
  }
  
  try {
    final response = await GamificationApiService().resetDaily(userId: userId);
    
    if (response['success'] == true) {
      // Backend'den güncel state'i çek
      await _fetchStateFromBackend(userId);
      
      // Emoji ve paylaşım tracking'i temizle
      _emojiGivenPerReel.clear();
      _shareGivenPerReel.clear();
      
      debugPrint('✅ [Force Reset] Daily reset completed. Streak: ${_state.currentStreak}');
      notifyListeners();
    } else {
      debugPrint('❌ [Force Reset] Failed: ${response['message']}');
    }
  } catch (e) {
    debugPrint('❌ [Force Reset] Error: $e');
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
/// Tüm verileri sıfırla (test için) - Backend'e gönder
Future<void> resetAll() async {
  debugPrint('🔄 [Reset All] Resetting all data...');
  
  final userId = await _getUserId();
  if (userId == null) {
    debugPrint('❌ [Reset All] No user ID');
    return;
  }
  
  try {
    // Backend'de reset endpoint'i yoksa, manuel sıfırlama yapabiliriz
    // Şimdilik local temizlik + backend'den state çek
    
    _state = const GamificationState();
    _emojiGivenPerReel.clear();
    _shareGivenPerReel.clear();
    
    // Backend'den fresh state çek (muhtemelen 0 olacak)
    await _fetchStateFromBackend(userId);
    
    notifyListeners();
    debugPrint('✅ [Reset All] All data reset completed');
  } catch (e) {
    debugPrint('❌ [Reset All] Error: $e');
  }
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