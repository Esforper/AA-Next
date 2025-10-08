// lib/services/mock_gamification_service.dart
// Mock API - Backend hazır olana kadar geçici servis

import 'dart:async';
import 'package:flutter/foundation.dart';

/// Mock Gamification Service
/// Backend API hazır olana kadar kullanılacak geçici servis
/// Gerçek API'ye geçişi kolaylaştırmak için aynı interface'i kullanır
class MockGamificationService {
  // Singleton pattern
  static final MockGamificationService _instance = MockGamificationService._internal();
  factory MockGamificationService() => _instance;
  MockGamificationService._internal();

  // ============ RESPONSE MODELS ============

  /// XP Response
  Map<String, dynamic> _createXPResponse({
    required bool success,
    required String message,
    required int xpGained,
    required int totalXP,
    required int currentLevel,
    required int currentNode,
    required bool levelUp,
  }) {
    return {
      'success': success,
      'message': message,
      'xp_gained': xpGained,
      'total_xp': totalXP,
      'current_level': currentLevel,
      'current_node': currentNode,
      'level_up': levelUp,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  /// Level Data Response
  Map<String, dynamic> _createLevelDataResponse({
    required int currentLevel,
    required int currentNode,
    required int nodesInLevel,
    required int currentXP,
    required int xpNeededForNextNode,
    required int totalXP,
  }) {
    return {
      'success': true,
      'current_level': currentLevel,
      'current_node': currentNode,
      'nodes_in_level': nodesInLevel,
      'current_xp': currentXP,
      'xp_needed_for_next_node': xpNeededForNextNode,
      'total_xp': totalXP,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  /// User Stats Response
  Map<String, dynamic> _createUserStatsResponse({
    required int totalXP,
    required int currentLevel,
    required int currentStreak,
    required int reelsWatchedToday,
    required int emojisGivenToday,
    required int detailsReadToday,
    required int sharesGivenToday,
  }) {
    return {
      'success': true,
      'total_xp': totalXP,
      'current_level': currentLevel,
      'current_streak': currentStreak,
      'today_stats': {
        'reels_watched': reelsWatchedToday,
        'emojis_given': emojisGivenToday,
        'details_read': detailsReadToday,
        'shares_given': sharesGivenToday,
      },
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  // ============ API METHODS ============

  /// XP Ekle
  /// Backend: POST /api/gamification/add-xp
  Future<Map<String, dynamic>> addXP({
    required String userId,
    required int xpAmount,
    required String source,
  }) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 300));

    try {
      debugPrint('🎮 [Mock API] Adding XP: $xpAmount from $source for user: $userId');

      // Mock response
      return _createXPResponse(
        success: true,
        message: 'XP added successfully',
        xpGained: xpAmount,
        totalXP: 0, // Provider'dan gelecek
        currentLevel: 0, // Provider'dan gelecek
        currentNode: 0, // Provider'dan gelecek
        levelUp: false, // Provider kontrol edecek
      );
    } catch (e) {
      debugPrint('❌ [Mock API] Error adding XP: $e');
      return {
        'success': false,
        'message': 'Failed to add XP: $e',
      };
    }
  }

  /// Mevcut level verilerini al
  /// Backend: GET /api/gamification/level/{userId}
  Future<Map<String, dynamic>> getCurrentLevel({
    required String userId,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));

    try {
      debugPrint('🎮 [Mock API] Getting level data for user: $userId');

      // Mock response - gerçek veriler provider'dan gelecek
      return _createLevelDataResponse(
        currentLevel: 1,
        currentNode: 0,
        nodesInLevel: 2,
        currentXP: 0,
        xpNeededForNextNode: 100,
        totalXP: 0,
      );
    } catch (e) {
      debugPrint('❌ [Mock API] Error getting level: $e');
      return {
        'success': false,
        'message': 'Failed to get level data: $e',
      };
    }
  }

  /// Kullanıcı istatistiklerini al
  /// Backend: GET /api/gamification/stats/{userId}
  Future<Map<String, dynamic>> getUserStats({
    required String userId,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));

    try {
      debugPrint('🎮 [Mock API] Getting user stats for: $userId');

      // Mock response
      return _createUserStatsResponse(
        totalXP: 0,
        currentLevel: 1,
        currentStreak: 0,
        reelsWatchedToday: 0,
        emojisGivenToday: 0,
        detailsReadToday: 0,
        sharesGivenToday: 0,
      );
    } catch (e) {
      debugPrint('❌ [Mock API] Error getting stats: $e');
      return {
        'success': false,
        'message': 'Failed to get user stats: $e',
      };
    }
  }

  /// Günlük progress'i sıfırla
  /// Backend: POST /api/gamification/reset-daily/{userId}
  Future<Map<String, dynamic>> resetDaily({
    required String userId,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));

    try {
      debugPrint('🎮 [Mock API] Resetting daily progress for: $userId');

      return {
        'success': true,
        'message': 'Daily progress reset successfully',
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('❌ [Mock API] Error resetting daily: $e');
      return {
        'success': false,
        'message': 'Failed to reset daily progress: $e',
      };
    }
  }

  /// Leaderboard al
  /// Backend: GET /api/gamification/leaderboard
  Future<Map<String, dynamic>> getLeaderboard({
    int limit = 50,
    String period = 'all_time', // 'daily', 'weekly', 'monthly', 'all_time'
  }) async {
    await Future.delayed(const Duration(milliseconds: 400));

    try {
      debugPrint('🎮 [Mock API] Getting leaderboard (period: $period, limit: $limit)');

      // Mock leaderboard data
      final mockLeaderboard = List.generate(
        limit,
        (index) => {
          'rank': index + 1,
          'user_id': 'user_${index + 1}',
          'username': 'User${index + 1}',
          'total_xp': 10000 - (index * 100),
          'level': 10 - (index ~/ 10),
          'avatar': null,
        },
      );

      return {
        'success': true,
        'leaderboard': mockLeaderboard,
        'period': period,
        'total_users': mockLeaderboard.length,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('❌ [Mock API] Error getting leaderboard: $e');
      return {
        'success': false,
        'message': 'Failed to get leaderboard: $e',
      };
    }
  }

  /// Kullanıcının rank'ini al
  /// Backend: GET /api/gamification/rank/{userId}
  Future<Map<String, dynamic>> getUserRank({
    required String userId,
  }) async {
    await Future.delayed(const Duration(milliseconds: 200));

    try {
      debugPrint('🎮 [Mock API] Getting rank for user: $userId');

      return {
        'success': true,
        'user_id': userId,
        'rank': 42,
        'total_users': 1000,
        'percentile': 95.8,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('❌ [Mock API] Error getting rank: $e');
      return {
        'success': false,
        'message': 'Failed to get user rank: $e',
      };
    }
  }

  /// Achievements al
  /// Backend: GET /api/gamification/achievements/{userId}
  Future<Map<String, dynamic>> getAchievements({
    required String userId,
  }) async {
    await Future.delayed(const Duration(milliseconds: 300));

    try {
      debugPrint('🎮 [Mock API] Getting achievements for: $userId');

      final mockAchievements = [
        {
          'id': 'first_reel',
          'name': 'İlk Haber',
          'description': 'İlk haberini izle',
          'icon': '👀',
          'unlocked': true,
          'unlocked_at': DateTime.now().subtract(const Duration(days: 5)).toIso8601String(),
        },
        {
          'id': 'emoji_master',
          'name': 'Emoji Ustası',
          'description': '50 emoji at',
          'icon': '❤️',
          'unlocked': false,
          'progress': 23,
          'total': 50,
        },
        {
          'id': 'reader',
          'name': 'Okuyucu',
          'description': '10 haberi detaylı oku',
          'icon': '📖',
          'unlocked': false,
          'progress': 4,
          'total': 10,
        },
      ];

      return {
        'success': true,
        'achievements': mockAchievements,
        'total_unlocked': 1,
        'total_achievements': mockAchievements.length,
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('❌ [Mock API] Error getting achievements: $e');
      return {
        'success': false,
        'message': 'Failed to get achievements: $e',
      };
    }
  }

  // ============ SYNC METHODS ============

  /// Local state'i backend ile senkronize et
  /// Backend: POST /api/gamification/sync
  Future<Map<String, dynamic>> syncState({
    required String userId,
    required Map<String, dynamic> localState,
  }) async {
    await Future.delayed(const Duration(milliseconds: 500));

    try {
      debugPrint('🎮 [Mock API] Syncing state for user: $userId');
      debugPrint('📦 Local state: $localState');

      // Mock: Backend'den güncel state döner
      return {
        'success': true,
        'message': 'State synced successfully',
        'synced_state': localState, // Mock olarak aynı state'i döndür
        'conflicts': [], // Çakışma yoksa boş array
        'timestamp': DateTime.now().toIso8601String(),
      };
    } catch (e) {
      debugPrint('❌ [Mock API] Error syncing state: $e');
      return {
        'success': false,
        'message': 'Failed to sync state: $e',
      };
    }
  }

  // ============ HELPER METHODS ============

  /// API sağlık kontrolü
  Future<bool> healthCheck() async {
    await Future.delayed(const Duration(milliseconds: 100));
    debugPrint('✅ [Mock API] Health check: OK');
    return true;
  }

  /// Mock API bilgisi
  Map<String, dynamic> getInfo() {
    return {
      'service': 'Mock Gamification Service',
      'version': '1.0.0',
      'status': 'active',
      'note': 'This is a mock service. Replace with real API when backend is ready.',
      'endpoints': {
        'add_xp': 'POST /api/gamification/add-xp',
        'get_level': 'GET /api/gamification/level/{userId}',
        'get_stats': 'GET /api/gamification/stats/{userId}',
        'reset_daily': 'POST /api/gamification/reset-daily/{userId}',
        'leaderboard': 'GET /api/gamification/leaderboard',
        'rank': 'GET /api/gamification/rank/{userId}',
        'achievements': 'GET /api/gamification/achievements/{userId}',
        'sync': 'POST /api/gamification/sync',
      },
    };
  }
}