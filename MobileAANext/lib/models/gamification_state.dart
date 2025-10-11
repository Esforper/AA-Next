// lib/models/gamification_state.dart

import 'package:flutter/foundation.dart';

/// Gamification State Model
/// XP & Level sistemi - Her düğüm 100 XP
class GamificationState {
  // XP & Level
  final int currentXP;           // Mevcut düğümdeki XP (0-100)
  final int dailyXPGoal;         // Günlük hedef (300 XP)
  final int totalXP;             // Tüm zamanlar toplam XP
  final int currentLevel;        // Seviye (1-100)
  final int currentNode;         // Mevcut düğüm pozisyonu (0-based)
  final int nodesInLevel;        // Bu seviyedeki toplam düğüm sayısı
  
  // Streak
  final int currentStreak;       // Güncel streak (gün)
  final DateTime? lastActivityDate;
  final int streakPercentile;    // Kullanıcıların %X'inden iyi
  
  // Daily Progress
  final int reelsWatchedToday;
  final int emojisGivenToday;
  final int detailsReadToday;
  final int sharesGivenToday;
  final int xpEarnedToday;
  final bool dailyGoalCompleted;
  
  const GamificationState({
    this.currentXP = 0,
    this.dailyXPGoal = 300,
    this.totalXP = 0,
    this.currentLevel = 0,
    this.currentNode = 0,
    this.nodesInLevel = 2,
    this.currentStreak = 0,
    this.lastActivityDate,
    this.streakPercentile = 0,
    this.reelsWatchedToday = 0,
    this.emojisGivenToday = 0,
    this.detailsReadToday = 0,
    this.sharesGivenToday = 0,
    this.xpEarnedToday = 0,
    this.dailyGoalCompleted = false,
  });
  
  // ============ COMPUTED PROPERTIES ============
  
  /// Günlük progress yüzdesi (0.0 - 1.0)
  double get dailyProgress => 
    (xpEarnedToday / dailyXPGoal).clamp(0.0, 1.0);
  
  /// Düğüm progress yüzdesi (0.0 - 1.0)
  double get nodeProgress => 
    (currentXP / 100).clamp(0.0, 1.0);
  
  /// Level progress yüzdesi (0.0 - 1.0)
  double get levelProgress => 
    nodesInLevel > 0 ? (currentNode / nodesInLevel).clamp(0.0, 1.0) : 0.0;
  
  /// Level tamamlanması için gereken toplam XP
  int get xpNeededForLevel => nodesInLevel * 100;
  
  /// Level içinde kazanılan toplam XP
  int get xpEarnedInLevel => (currentNode * 100) + currentXP;
  
  // ============ XP EKLEME ============
  
  /// XP Ekle
  GamificationState addXP(int amount, String source) {
    int newXP = xpEarnedToday + amount;
    int newCurrentXP = currentXP + amount;
    int newTotalXP = totalXP + amount;
    
    bool goalCompleted = newXP >= dailyXPGoal;
    
    // Activity counts güncelle
    int reels = reelsWatchedToday;
    int emojis = emojisGivenToday;
    int details = detailsReadToday;
    int shares = sharesGivenToday;
    
    if (source == 'reel_watched') reels++;
    if (source == 'emoji_given') emojis++;
    if (source == 'detail_read') details++;
    if (source == 'share_given') shares++;
    
    return copyWith(
      currentXP: newCurrentXP,
      xpEarnedToday: newXP,
      totalXP: newTotalXP,
      dailyGoalCompleted: goalCompleted,
      reelsWatchedToday: reels,
      emojisGivenToday: emojis,
      detailsReadToday: details,
      sharesGivenToday: shares,
    );
  }
  
  // ============ LEVEL UP KONTROLÜ ============
  
  /// Düğüm ve level atlamayı kontrol et
  /// Düğüm ve level atlamayı kontrol et
GamificationState checkLevelUp() {
  int newCurrentXP = currentXP;
  int newNode = currentNode;
  int newLevel = currentLevel;
  int newNodesInLevel = nodesInLevel;
  
  // Düğüm tamamlandı mı? (100 XP = 1 düğüm)
  while (newCurrentXP >= 100) {
    newCurrentXP -= 100;
    newNode++;
    
    // Level tamamlandı mı?
    if (newNode >= newNodesInLevel) {
      newLevel++;
      newNode = 0;
      newNodesInLevel = _getNodesForLevel(newLevel);
      
      debugPrint('🎉 LEVEL UP! Level $newLevel reached, ${newNodesInLevel} nodes in this level');
    }
  }
  
  return copyWith(
    currentXP: newCurrentXP,
    currentNode: newNode,
    currentLevel: newLevel,
    nodesInLevel: newNodesInLevel,
  );
}
  
  // ============ LEVEL FORMÜLÜ ============
  
  /// Seviyeye göre düğüm sayısını hesapla
  /// Level 1-5: 2 düğüm
  /// Level 6-10: 4 düğüm
  /// Level 11-15: 6 düğüm
  /// Level 16+: 8 düğüm
  int _getNodesForLevel(int level) {
  if (level < 5) return 2;
  if (level < 10) return 4;
  if (level < 15) return 6;
  if (level < 20) return 8;
  return 10; // Level 20+
}
  
  // ============ GÜNLÜK RESET ============
  
  /// Günlük sıfırlama (her gün)
  GamificationState resetDaily() {
    // Streak kontrolü
    int newStreak = currentStreak;
    if (dailyGoalCompleted) {
      newStreak++; // Hedef tamamlandıysa streak devam
    } else if (currentStreak > 0) {
      newStreak = 0; // Hedef tamamlanmadıysa streak kırıldı
    }
    
    return copyWith(
      xpEarnedToday: 0,
      reelsWatchedToday: 0,
      emojisGivenToday: 0,
      detailsReadToday: 0,
      sharesGivenToday: 0,
      dailyGoalCompleted: false,
      currentStreak: newStreak,
      lastActivityDate: DateTime.now(),
      streakPercentile: _calculatePercentile(newStreak),
    );
  }
  
  // ============ HELPER METHODS ============
  
  /// Streak'e göre percentile hesapla
  int _calculatePercentile(int streak) {
    if (streak >= 30) return 95;
    if (streak >= 14) return 85;
    if (streak >= 7) return 70;
    if (streak >= 3) return 50;
    return 30;
  }
  
  // ============ COPYWITH ============
  
  GamificationState copyWith({
    int? currentXP,
    int? dailyXPGoal,
    int? totalXP,
    int? currentLevel,
    int? currentNode,
    int? nodesInLevel,
    int? currentStreak,
    DateTime? lastActivityDate,
    int? streakPercentile,
    int? reelsWatchedToday,
    int? emojisGivenToday,
    int? detailsReadToday,
    int? sharesGivenToday,
    int? xpEarnedToday,
    bool? dailyGoalCompleted,
  }) {
    return GamificationState(
      currentXP: currentXP ?? this.currentXP,
      dailyXPGoal: dailyXPGoal ?? this.dailyXPGoal,
      totalXP: totalXP ?? this.totalXP,
      currentLevel: currentLevel ?? this.currentLevel,
      currentNode: currentNode ?? this.currentNode,
      nodesInLevel: nodesInLevel ?? this.nodesInLevel,
      currentStreak: currentStreak ?? this.currentStreak,
      lastActivityDate: lastActivityDate ?? this.lastActivityDate,
      streakPercentile: streakPercentile ?? this.streakPercentile,
      reelsWatchedToday: reelsWatchedToday ?? this.reelsWatchedToday,
      emojisGivenToday: emojisGivenToday ?? this.emojisGivenToday,
      detailsReadToday: detailsReadToday ?? this.detailsReadToday,
      sharesGivenToday: sharesGivenToday ?? this.sharesGivenToday,
      xpEarnedToday: xpEarnedToday ?? this.xpEarnedToday,
      dailyGoalCompleted: dailyGoalCompleted ?? this.dailyGoalCompleted,
    );
  }
  
  // ============ MOCK DATA ============
  
  /// Test için mock data
  factory GamificationState.mock() {
  return GamificationState(
      currentXP: 0,           // 45 → 0
      totalXP: 0,            // 850 → 0  
      currentLevel: 1,        // 3 → 1 (değişmedi ama tutarlılık için)
      currentNode: 0,         // 1 → 0
      nodesInLevel: 2,
      currentStreak: 0,
      lastActivityDate: DateTime.now(),
      streakPercentile: 65,
      reelsWatchedToday: 0,
      emojisGivenToday: 0,
      detailsReadToday: 0,
      sharesGivenToday: 0,
      xpEarnedToday: 0,
      dailyGoalCompleted: false,
    );
  }
  
  // ============ JSON SERİALİZATION ============
  
  /// JSON'a çevir (Local storage için)
  Map<String, dynamic> toJson() {
    return {
      'currentXP': currentXP,
      'dailyXPGoal': dailyXPGoal,
      'totalXP': totalXP,
      'currentLevel': currentLevel,
      'currentNode': currentNode,
      'nodesInLevel': nodesInLevel,
      'currentStreak': currentStreak,
      'lastActivityDate': lastActivityDate?.toIso8601String(),
      'streakPercentile': streakPercentile,
      'reelsWatchedToday': reelsWatchedToday,
      'emojisGivenToday': emojisGivenToday,
      'detailsReadToday': detailsReadToday,
      'sharesGivenToday': sharesGivenToday,
      'xpEarnedToday': xpEarnedToday,
      'dailyGoalCompleted': dailyGoalCompleted,
    };
  }
  
  /// JSON'dan oluştur
  factory GamificationState.fromJson(Map<String, dynamic> json) {
    return GamificationState(
      currentXP: json['currentXP'] ?? 0,
      dailyXPGoal: json['dailyXPGoal'] ?? 300,
      totalXP: json['totalXP'] ?? 0,
      currentLevel: json['currentLevel'] ?? 1,
      currentNode: json['currentNode'] ?? 0,
      nodesInLevel: json['nodesInLevel'] ?? 2,
      currentStreak: json['currentStreak'] ?? 0,
      lastActivityDate: json['lastActivityDate'] != null
          ? DateTime.parse(json['lastActivityDate'])
          : null,
      streakPercentile: json['streakPercentile'] ?? 0,
      reelsWatchedToday: json['reelsWatchedToday'] ?? 0,
      emojisGivenToday: json['emojisGivenToday'] ?? 0,
      detailsReadToday: json['detailsReadToday'] ?? 0,
      sharesGivenToday: json['sharesGivenToday'] ?? 0,
      xpEarnedToday: json['xpEarnedToday'] ?? 0,
      dailyGoalCompleted: json['dailyGoalCompleted'] ?? false,
    );
  }
}