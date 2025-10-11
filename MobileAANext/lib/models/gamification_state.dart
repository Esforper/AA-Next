// lib/models/gamification_state.dart
// Gamification State - Immutable state yönetimi
// ✅ NODE ARTIŞ SORUNU DÜZELTİLDİ
// ✅ TÜM EKSİK GETTER'LAR EKLENDİ

import 'package:flutter/foundation.dart';

@immutable
class GamificationState {
  // ============ CORE LEVEL/NODE DATA ============
  final int totalXP;        // Toplam kazanılan XP
  final int currentLevel;   // Mevcut level (0'dan başlar)
  final int currentNode;    // Level içindeki node (0'dan başlar)
  final int currentXP;      // Düğüm içindeki XP (0-99)
  final int nodesInLevel;   // Bu level'deki toplam node sayısı
  
  // ============ DAILY PROGRESS ============
  final int xpEarnedToday;
  final int dailyXPGoal;
  final bool dailyGoalCompleted;
  
  // ============ STREAK ============
  final int currentStreak;
  final int longestStreak;
  final DateTime? lastActivityDate;
  
  // ============ DAILY ACTIVITY COUNTS ============
  final int reelsWatchedToday;
  final int emojisGivenToday;
  final int detailsReadToday;
  final int sharesGivenToday;

  const GamificationState({
    this.totalXP = 0,
    this.currentLevel = 0,
    this.currentNode = 0,
    this.currentXP = 0,
    this.nodesInLevel = 2,
    this.xpEarnedToday = 0,
    this.dailyXPGoal = 300,
    this.dailyGoalCompleted = false,
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.lastActivityDate,
    this.reelsWatchedToday = 0,
    this.emojisGivenToday = 0,
    this.detailsReadToday = 0,
    this.sharesGivenToday = 0,
  });

  // ============ COMPUTED PROPERTIES ============
  
  /// Level ilerleme yüzdesi (0.0 - 1.0)
  double get levelProgress => nodesInLevel > 0 
      ? (currentNode / nodesInLevel).clamp(0.0, 1.0) : 0.0;
  
  /// Günlük hedef ilerleme yüzdesi (0.0 - 1.0)
  double get dailyProgress => dailyXPGoal > 0
      ? (xpEarnedToday / dailyXPGoal).clamp(0.0, 1.0) : 0.0;
  
  /// Node içindeki ilerleme yüzdesi (0.0 - 1.0)
  double get nodeProgress => currentXP / 100.0;
  
  /// Streak percentile (mock değer - gerçek değer backend'den gelecek)
  int get streakPercentile => currentStreak >= 30 ? 95
      : currentStreak >= 20 ? 85
      : currentStreak >= 10 ? 70
      : currentStreak >= 5 ? 50
      : 20;
  
  /// Level tamamlanması için gereken toplam XP
  int get xpNeededForLevel => nodesInLevel * 100;
  
  /// Level içinde kazanılan toplam XP
  int get xpEarnedInLevel => (currentNode * 100) + currentXP;
  
  /// Bir sonraki node için gereken XP
  int get xpNeededForNextNode => 100 - currentXP;
  
  // ============ XP EKLEME (DÜZELTİLDİ) ============
  
  /// XP Ekle - Total XP'den otomatik hesaplama yapar
  GamificationState addXP(int amount, String source) {
    final newTotalXP = totalXP + amount;
    final newXPToday = xpEarnedToday + amount;
    final goalCompleted = newXPToday >= dailyXPGoal;
    
    // Activity counts güncelle
    int reels = reelsWatchedToday;
    int emojis = emojisGivenToday;
    int details = detailsReadToday;
    int shares = sharesGivenToday;
    
    if (source == 'reel_watched') reels++;
    if (source == 'emoji_given') emojis++;
    if (source == 'detail_read') details++;
    if (source == 'share_given') shares++;
    
    // ✅ YENİ: Total XP'den level/node/currentXP hesapla
    final calculatedState = _calculateFromTotalXP(newTotalXP);
    
    return calculatedState.copyWith(
      totalXP: newTotalXP,
      xpEarnedToday: newXPToday,
      dailyGoalCompleted: goalCompleted,
      reelsWatchedToday: reels,
      emojisGivenToday: emojis,
      detailsReadToday: details,
      sharesGivenToday: shares,
    );
  }
  
  // ============ TOTAL XP'DEN HESAPLAMA (YENİ) ============
  
  /// Total XP'den level, node, currentXP hesapla
  /// Backend'deki _calculate_level_and_node ile aynı mantık
  GamificationState _calculateFromTotalXP(int totalXP) {
    int remainingXP = totalXP;
    int level = 0;
    int node = 0;
    int currentXP = 0;
    
    debugPrint('🔄 [Calculate] Total XP: $totalXP');
    
    while (remainingXP > 0) {
      final nodesInLevel = _getNodesForLevel(level);
      final xpForLevel = nodesInLevel * 100;
      
      if (remainingXP < xpForLevel) {
        // Bu level'deyiz
        node = remainingXP ~/ 100;
        currentXP = remainingXP % 100;
        
        debugPrint('   → Level $level, Node $node, Current XP $currentXP');
        
        return copyWith(
          currentLevel: level,
          currentNode: node,
          currentXP: currentXP,
          nodesInLevel: nodesInLevel,
        );
      }
      
      // Bu level'i tamamladık, sonrakine geç
      remainingXP -= xpForLevel;
      level++;
      
      // Safety check
      if (level > 100) {
        debugPrint('⚠️ Max level reached!');
        return copyWith(
          currentLevel: 100,
          currentNode: 0,
          currentXP: 0,
          nodesInLevel: 10,
        );
      }
    }
    
    // Tam 0 XP
    return copyWith(
      currentLevel: 0,
      currentNode: 0,
      currentXP: 0,
      nodesInLevel: 2,
    );
  }
  
  // ============ HELPER: LEVEL'E GÖRE NODE SAYISI ============
  
  /// Level'e göre node sayısını hesapla
  /// Backend ile aynı: Her 5 levelda 2 node artar
  int _getNodesForLevel(int level) {
    if (level < 5) return 2;
    if (level < 10) return 4;
    if (level < 15) return 6;
    if (level < 20) return 8;
    return 10; // Max
  }

  // ============ DAILY RESET ============
  
  /// Günlük verileri sıfırla
  GamificationState resetDaily() {
    return copyWith(
      xpEarnedToday: 0,
      dailyGoalCompleted: false,
      reelsWatchedToday: 0,
      emojisGivenToday: 0,
      detailsReadToday: 0,
      sharesGivenToday: 0,
    );
  }

  // ============ STREAK ============
  
  /// Streak güncelle
  GamificationState updateStreak(DateTime now) {
    if (lastActivityDate == null) {
      // İlk aktivite
      return copyWith(
        currentStreak: 1,
        longestStreak: 1,
        lastActivityDate: now,
      );
    }
    
    final lastDate = lastActivityDate!;
    final daysDiff = now.difference(DateTime(lastDate.year, lastDate.month, lastDate.day)).inDays;
    
    if (daysDiff == 0) {
      // Bugün zaten aktivite var
      return this;
    } else if (daysDiff == 1) {
      // Dün aktivite vardı, streak devam
      final newStreak = currentStreak + 1;
      return copyWith(
        currentStreak: newStreak,
        longestStreak: newStreak > longestStreak ? newStreak : longestStreak,
        lastActivityDate: now,
      );
    } else {
      // Streak kırıldı
      return copyWith(
        currentStreak: 1,
        lastActivityDate: now,
      );
    }
  }

  // ============ COPY WITH ============
  
  GamificationState copyWith({
    int? totalXP,
    int? currentLevel,
    int? currentNode,
    int? currentXP,
    int? nodesInLevel,
    int? xpEarnedToday,
    int? dailyXPGoal,
    bool? dailyGoalCompleted,
    int? currentStreak,
    int? longestStreak,
    DateTime? lastActivityDate,
    int? reelsWatchedToday,
    int? emojisGivenToday,
    int? detailsReadToday,
    int? sharesGivenToday,
  }) {
    return GamificationState(
      totalXP: totalXP ?? this.totalXP,
      currentLevel: currentLevel ?? this.currentLevel,
      currentNode: currentNode ?? this.currentNode,
      currentXP: currentXP ?? this.currentXP,
      nodesInLevel: nodesInLevel ?? this.nodesInLevel,
      xpEarnedToday: xpEarnedToday ?? this.xpEarnedToday,
      dailyXPGoal: dailyXPGoal ?? this.dailyXPGoal,
      dailyGoalCompleted: dailyGoalCompleted ?? this.dailyGoalCompleted,
      currentStreak: currentStreak ?? this.currentStreak,
      longestStreak: longestStreak ?? this.longestStreak,
      lastActivityDate: lastActivityDate ?? this.lastActivityDate,
      reelsWatchedToday: reelsWatchedToday ?? this.reelsWatchedToday,
      emojisGivenToday: emojisGivenToday ?? this.emojisGivenToday,
      detailsReadToday: detailsReadToday ?? this.detailsReadToday,
      sharesGivenToday: sharesGivenToday ?? this.sharesGivenToday,
    );
  }

  // ============ JSON ============
  
  Map<String, dynamic> toJson() {
    return {
      'totalXP': totalXP,
      'currentLevel': currentLevel,
      'currentNode': currentNode,
      'currentXP': currentXP,
      'nodesInLevel': nodesInLevel,
      'xpEarnedToday': xpEarnedToday,
      'dailyXPGoal': dailyXPGoal,
      'dailyGoalCompleted': dailyGoalCompleted,
      'currentStreak': currentStreak,
      'longestStreak': longestStreak,
      'lastActivityDate': lastActivityDate?.toIso8601String(),
      'reelsWatchedToday': reelsWatchedToday,
      'emojisGivenToday': emojisGivenToday,
      'detailsReadToday': detailsReadToday,
      'sharesGivenToday': sharesGivenToday,
    };
  }

  factory GamificationState.fromJson(Map<String, dynamic> json) {
    return GamificationState(
      totalXP: json['totalXP'] ?? 0,
      currentLevel: json['currentLevel'] ?? 0,
      currentNode: json['currentNode'] ?? 0,
      currentXP: json['currentXP'] ?? 0,
      nodesInLevel: json['nodesInLevel'] ?? 2,
      xpEarnedToday: json['xpEarnedToday'] ?? 0,
      dailyXPGoal: json['dailyXPGoal'] ?? 300,
      dailyGoalCompleted: json['dailyGoalCompleted'] ?? false,
      currentStreak: json['currentStreak'] ?? 0,
      longestStreak: json['longestStreak'] ?? 0,
      lastActivityDate: json['lastActivityDate'] != null
          ? DateTime.parse(json['lastActivityDate'])
          : null,
      reelsWatchedToday: json['reelsWatchedToday'] ?? 0,
      emojisGivenToday: json['emojisGivenToday'] ?? 0,
      detailsReadToday: json['detailsReadToday'] ?? 0,
      sharesGivenToday: json['sharesGivenToday'] ?? 0,
    );
  }

  @override
  String toString() {
    return 'GamificationState(level: $currentLevel, node: $currentNode/$nodesInLevel, '
           'xp: $currentXP/100, total: $totalXP, streak: $currentStreak)';
  }
}