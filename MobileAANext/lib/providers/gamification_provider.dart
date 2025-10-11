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
  
  // 2. Storage'a kaydet
  await _saveToStorage();
  
  // 3. Backend'e sync (opsiyonel - hata olsa bile devam eder)
  final userId = await _getUserId();
  if (userId != null) {
    _syncToBackend(userId, amount, source); // await yok - fire and forget
  }
  
  notifyListeners();
}

    void _syncToBackend(String userId, int xp, String source) {
    GamificationApiService().addXP(
      userId: userId,  // ✅ Hala var (backend user_id bekliyor)
      xpAmount: xp,
      source: source,
    ).then((response) {
      if (response['success'] == true) {
        debugPrint('✅ Backend sync success');
      } else {
        debugPrint('⚠️ Backend sync failed: ${response['message']}');
      }
    }).catchError((error) {
      debugPrint('❌ Backend sync error: $error');
    });
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
  Future<bool> spendNodes(int amount, {String reason = 'game_entry'}) async {
    // 1. Local kontrolü
    if (_state.currentNode < amount) {
      debugPrint('❌ [Spend Node] Insufficient nodes: ${_state.currentNode} < $amount');
      return false;
    }
    
    debugPrint('💸 [Spend Node] Spending $amount node(s) for $reason');
    debugPrint('   Before: Level ${_state.currentLevel}, Node ${_state.currentNode}');
    
    // 2. Backend'e sync
    final userId = await _getUserId();
    if (userId != null) {
      try {
        final response = await GamificationApiService().spendNodes(
          userId: userId,
          amount: amount,
          reason: reason,
        );
        
        if (response['success'] != true) {
          debugPrint('⚠️ [Spend Node] Backend failed: ${response['message']}');
          return false;
        }
        
        debugPrint('✅ [Spend Node] Backend confirmed');
      } catch (e) {
        debugPrint('❌ [Spend Node] Backend error: $e');
        // Backend hatası olsa bile devam et (local güncelleyeceğiz)
      }
    }
    
    // 3. Local state güncelle (1 node = 100 XP düş)
    final xpToRemove = amount * 100;
    final newTotalXP = _state.totalXP - xpToRemove;
    
    if (newTotalXP < 0) {
      debugPrint('❌ [Spend Node] Would result in negative XP');
      return false;
    }
    
    // 4. Yeni level/node hesapla
    final newState = _recalculateFromTotalXP(newTotalXP);
    
    _state = newState.copyWith(
      totalXP: newTotalXP,
    );
    
    debugPrint('   After: Level ${_state.currentLevel}, Node ${_state.currentNode}');
    
    // 5. Storage'a kaydet
    await _saveToStorage();
    notifyListeners();
    
    return true;
  }
  
  /// Node ekle (oyun ödülü)
  Future<void> addNodes(int amount, {String source = 'game_reward'}) async {
    debugPrint('🎁 [Add Node] Adding $amount node(s) from $source');
    debugPrint('   Before: Level ${_state.currentLevel}, Node ${_state.currentNode}');
    
    // 1 node = 100 XP
    final xpAmount = amount * 100;
    
    // XP ekle (mevcut addXP metodunu kullan)
    await addXP(xpAmount, source);
    
    debugPrint('   After: Level ${_state.currentLevel}, Node ${_state.currentNode}');
  }
  
  /// Total XP'den state hesapla (helper metod)
  /// Total XP'den state hesapla (helper metod)
GamificationState _recalculateFromTotalXP(int totalXP) {
  int remainingXP = totalXP;
  int level = 0;  // ✅ DEĞİŞTİ: 1 → 0
  int node = 0;
  int currentXP = 0;
  
  debugPrint('🔄 [Recalculate] Starting from totalXP: $totalXP');
  
  while (remainingXP > 0) {
    // Bu level'de kaç node var?
    final nodesInLevel = _getNodesForLevel(level);
    final xpForLevel = nodesInLevel * 100;
    
    debugPrint('   Level $level: $nodesInLevel nodes = $xpForLevel XP needed');
    
    if (remainingXP < xpForLevel) {
      // Bu level'deyiz
      node = remainingXP ~/ 100;
      currentXP = remainingXP % 100;
      
      debugPrint('   → Final: Level $level, Node $node, CurrentXP $currentXP');
      
      return _state.copyWith(
        totalXP: totalXP,
        currentLevel: level,
        currentNode: node,
        currentXP: currentXP,
        nodesInLevel: nodesInLevel,
      );
    }
    
    // Bu level'i tamamladık, sonrakine geç
    remainingXP -= xpForLevel;
    level++;
    
    debugPrint('   ✓ Level completed, remaining XP: $remainingXP');
    
    // Safety check
    if (level > 100) {
      debugPrint('⚠️ Max level reached!');
      return _state.copyWith(
        totalXP: totalXP,
        currentLevel: 100,
        currentNode: 0,
        currentXP: 0,
        nodesInLevel: 10,
      );
    }
  }
  
  // XP = 0 ise
  debugPrint('   → Zero XP: Level 0, Node 0');
  return _state.copyWith(
    totalXP: 0,
    currentLevel: 0,
    currentNode: 0,
    currentXP: 0,
    nodesInLevel: 2,
  );
}
  
  /// Level'e göre node sayısı
  int _getNodesForLevel(int level) {
    if (level <= 5) return 2;
    if (level <= 10) return 4;
    if (level <= 15) return 6;
    return 8;
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
        _state = const GamificationState();
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
      _state = const GamificationState();
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