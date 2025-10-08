// lib/models/gamification_state.dart

import 'package:flutter/foundation.dart';

/// Gamification State Model
/// Tüm oyunlaştırma verilerini tutar
class GamificationState {
  // XP & Level
  final int currentXP;           // Bugünkü XP
  final int dailyXPGoal;         // Hedef (100 XP)
  final int totalXP;             // Tüm zamanlar
  final int currentLevel;        // Seviye (1-100)
  final int currentChain;        // Zincir pozisyonu
  final int chainsInLevel;       // Bu seviyedeki toplam zincir
  
  // Streak
  final int currentStreak;       // Güncel streak (gün)
  final DateTime? lastActivityDate;
  final int streakPercentile;    // Kullanıcıların %X'i
  
  // Daily Progress
  final int reelsWatchedToday;
  final int emojisGivenToday;
  final int detailsReadToday;
  final int xpEarnedToday;
  final bool dailyGoalCompleted;
  
  const GamificationState({
    this.currentXP = 0,
    this.dailyXPGoal = 100,
    this.totalXP = 0,
    this.currentLevel = 1,
    this.currentChain = 0,
    this.chainsInLevel = 3,
    this.currentStreak = 0,
    this.lastActivityDate,
    this.streakPercentile = 0,
    this.reelsWatchedToday = 0,
    this.emojisGivenToday = 0,
    this.detailsReadToday = 0,
    this.xpEarnedToday = 0,
    this.dailyGoalCompleted = false,
  });
  
  /// Progress yüzdesi (0.0 - 1.0)
  double get dailyProgress => 
    (xpEarnedToday / dailyXPGoal).clamp(0.0, 1.0);
  
  /// Zincir progress yüzdesi
  double get chainProgress => 
    chainsInLevel > 0 ? currentChain / chainsInLevel : 0.0;
  
  /// XP Ekle
  GamificationState addXP(int amount, String source) {
    int newXP = xpEarnedToday + amount;
    int newCurrentXP = currentXP + amount;
    int newTotalXP = totalXP + amount;
    
    bool goalCompleted = newXP >= dailyXPGoal;
    
    // Update activity counts
    int reels = reelsWatchedToday;
    int emojis = emojisGivenToday;
    int details = detailsReadToday;
    
    if (source == 'reel_watched') reels++;
    if (source == 'emoji_given') emojis++;
    if (source == 'detail_read') details++;
    
    return copyWith(
      currentXP: newCurrentXP,
      xpEarnedToday: newXP,
      totalXP: newTotalXP,
      dailyGoalCompleted: goalCompleted,
      reelsWatchedToday: reels,
      emojisGivenToday: emojis,
      detailsReadToday: details,
    );
  }
  
  /// Level atlama kontrolü
  GamificationState checkLevelUp() {
    int xpPerChain = _getXPPerChain();
    
    if (currentXP < xpPerChain) return this;
    
    int newCurrentXP = currentXP - xpPerChain;
    int newChain = currentChain + 1;
    int newLevel = currentLevel;
    int newChainsInLevel = chainsInLevel;
    
    // Zincir tamamlandı mı?
    if (newChain >= chainsInLevel) {
      newLevel++;
      newChain = 0;
      newChainsInLevel = _getChainsForLevel(newLevel);
    }
    
    return copyWith(
      currentXP: newCurrentXP,
      currentLevel: newLevel,
      currentChain: newChain,
      chainsInLevel: newChainsInLevel,
    );
  }
  
  /// Günlük reset
  GamificationState resetDaily() {
    // Streak kontrolü
    int newStreak = currentStreak;
    if (dailyGoalCompleted) {
      newStreak++;
    } else if (currentStreak > 0) {
      newStreak = 0; // Streak kırıldı
    }
    
    return copyWith(
      currentXP: 0,
      xpEarnedToday: 0,
      reelsWatchedToday: 0,
      emojisGivenToday: 0,
      detailsReadToday: 0,
      dailyGoalCompleted: false,
      currentStreak: newStreak,
      lastActivityDate: DateTime.now(),
      streakPercentile: _calculatePercentile(newStreak),
    );
  }
  
  // Helper methods
  int _getXPPerChain() {
    return (dailyXPGoal / chainsInLevel).floor();
  }
  
  int _getChainsForLevel(int level) {
    if (level <= 10) return 3;
    if (level <= 20) return 7;
    if (level <= 30) return 10;
    return 15; // 30+
  }
  
  int _calculatePercentile(int streak) {
    if (streak >= 30) return 95;
    if (streak >= 14) return 85;
    if (streak >= 7) return 70;
    if (streak >= 3) return 50;
    return 30;
  }
  
  // CopyWith
  GamificationState copyWith({
    int? currentXP,
    int? dailyXPGoal,
    int? totalXP,
    int? currentLevel,
    int? currentChain,
    int? chainsInLevel,
    int? currentStreak,
    DateTime? lastActivityDate,
    int? streakPercentile,
    int? reelsWatchedToday,
    int? emojisGivenToday,
    int? detailsReadToday,
    int? xpEarnedToday,
    bool? dailyGoalCompleted,
  }) {
    return GamificationState(
      currentXP: currentXP ?? this.currentXP,
      dailyXPGoal: dailyXPGoal ?? this.dailyXPGoal,
      totalXP: totalXP ?? this.totalXP,
      currentLevel: currentLevel ?? this.currentLevel,
      currentChain: currentChain ?? this.currentChain,
      chainsInLevel: chainsInLevel ?? this.chainsInLevel,
      currentStreak: currentStreak ?? this.currentStreak,
      lastActivityDate: lastActivityDate ?? this.lastActivityDate,
      streakPercentile: streakPercentile ?? this.streakPercentile,
      reelsWatchedToday: reelsWatchedToday ?? this.reelsWatchedToday,
      emojisGivenToday: emojisGivenToday ?? this.emojisGivenToday,
      detailsReadToday: detailsReadToday ?? this.detailsReadToday,
      xpEarnedToday: xpEarnedToday ?? this.xpEarnedToday,
      dailyGoalCompleted: dailyGoalCompleted ?? this.dailyGoalCompleted,
    );
  }
  
  // Mock data için factory
  factory GamificationState.mock() {
    return GamificationState(
      currentXP: 45,
      dailyXPGoal: 100,
      totalXP: 1250,
      currentLevel: 5,
      currentChain: 2,
      chainsInLevel: 3,
      currentStreak: 7,
      lastActivityDate: DateTime.now(),
      streakPercentile: 78,
      reelsWatchedToday: 3,
      emojisGivenToday: 2,
      detailsReadToday: 1,
      xpEarnedToday: 45,
      dailyGoalCompleted: false,
    );
  }
}