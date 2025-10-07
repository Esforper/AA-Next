// lib/providers/gamification_provider.dart

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/gamification_state.dart';

/// Gamification Provider
/// State management ve persistence
class GamificationProvider extends ChangeNotifier {
  GamificationState _state = GamificationState.mock();
  
  GamificationState get state => _state;
  
  // Getters
  int get currentXP => _state.currentXP;
  int get dailyXPGoal => _state.dailyXPGoal;
  int get currentLevel => _state.currentLevel;
  int get currentStreak => _state.currentStreak;
  double get dailyProgress => _state.dailyProgress;
  bool get dailyGoalCompleted => _state.dailyGoalCompleted;
  
  /// Initialize
  Future<void> init() async {
    await _loadFromStorage();
    _checkDailyReset();
    notifyListeners();
  }
  
  /// XP Ekle
  void addXP(int amount, String source) {
    _state = _state.addXP(amount, source);
    _state = _state.checkLevelUp();
    
    _saveToStorage();
    notifyListeners();
    
    // Level up check
    if (_state.currentChain == 0 && _state.currentLevel > 1) {
      _showLevelUpCelebration();
    }
  }
  
  /// Reel izlendi
  void onReelWatched() {
    addXP(10, 'reel_watched');
  }
  
  /// Emoji atıldı
  void onEmojiGiven() {
    addXP(5, 'emoji_given');
  }
  
  /// Detail okundu (15+ saniye)
  void onDetailRead() {
    addXP(10, 'detail_read');
  }
  
  /// Günlük reset kontrolü
  void _checkDailyReset() {
    if (_state.lastActivityDate == null) return;
    
    final now = DateTime.now();
    final lastDate = _state.lastActivityDate!;
    
    final isNewDay = now.day != lastDate.day ||
                     now.month != lastDate.month ||
                     now.year != lastDate.year;
    
    if (isNewDay) {
      _state = _state.resetDaily();
      _saveToStorage();
    }
  }
  
  /// Storage'a kaydet
  Future<void> _saveToStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final data = {
        'currentXP': _state.currentXP,
        'totalXP': _state.totalXP,
        'currentLevel': _state.currentLevel,
        'currentChain': _state.currentChain,
        'chainsInLevel': _state.chainsInLevel,
        'currentStreak': _state.currentStreak,
        'lastActivityDate': _state.lastActivityDate?.toIso8601String(),
        'streakPercentile': _state.streakPercentile,
        'reelsWatchedToday': _state.reelsWatchedToday,
        'emojisGivenToday': _state.emojisGivenToday,
        'detailsReadToday': _state.detailsReadToday,
        'xpEarnedToday': _state.xpEarnedToday,
        'dailyGoalCompleted': _state.dailyGoalCompleted,
      };
      await prefs.setString('gamification_state', jsonEncode(data));
    } catch (e) {
      debugPrint('Save error: $e');
    }
  }
  
  /// Storage'dan yükle
  Future<void> _loadFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final dataStr = prefs.getString('gamification_state');
      
      if (dataStr == null) {
        // İlk açılış, mock data kullan
        _state = GamificationState.mock();
        return;
      }
      
      final data = jsonDecode(dataStr) as Map<String, dynamic>;
      
      _state = GamificationState(
        currentXP: data['currentXP'] ?? 0,
        totalXP: data['totalXP'] ?? 0,
        currentLevel: data['currentLevel'] ?? 1,
        currentChain: data['currentChain'] ?? 0,
        chainsInLevel: data['chainsInLevel'] ?? 3,
        currentStreak: data['currentStreak'] ?? 0,
        lastActivityDate: data['lastActivityDate'] != null
            ? DateTime.parse(data['lastActivityDate'])
            : null,
        streakPercentile: data['streakPercentile'] ?? 0,
        reelsWatchedToday: data['reelsWatchedToday'] ?? 0,
        emojisGivenToday: data['emojisGivenToday'] ?? 0,
        detailsReadToday: data['detailsReadToday'] ?? 0,
        xpEarnedToday: data['xpEarnedToday'] ?? 0,
        dailyGoalCompleted: data['dailyGoalCompleted'] ?? false,
      );
    } catch (e) {
      debugPrint('Load error: $e');
      _state = GamificationState.mock();
    }
  }
  
  /// Level up celebration (placeholder)
  void _showLevelUpCelebration() {
    debugPrint('🎉 LEVEL UP! New level: ${_state.currentLevel}');
    // TODO: Show celebration animation
  }
  
  /// Reset for testing
  void resetAll() {
    _state = GamificationState();
    _saveToStorage();
    notifyListeners();
  }
}