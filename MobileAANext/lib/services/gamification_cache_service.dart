// lib/services/gamification_cache_service.dart
// 💾 Gamification Cache Service - Offline XP data storage
// SharedPreferences ile local cache yönetimi

import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart';

/// Gamification verilerini local'de cache'leyen servis
/// Offline erişim ve hızlı yükleme için
class GamificationCacheService {
  static const String _keyPrefix = 'gamification_';
  static const String _keyState = '${_keyPrefix}state';
  static const String _keyLastSync = '${_keyPrefix}last_sync';
  static const String _keyUserId = '${_keyPrefix}user_id';
  
  // Cache süreleri
  static const Duration cacheValidDuration = Duration(hours: 1);
  static const Duration maxCacheDuration = Duration(days: 7);

  /// Singleton instance
  static GamificationCacheService? _instance;
  static GamificationCacheService get instance {
    _instance ??= GamificationCacheService._();
    return _instance!;
  }

  GamificationCacheService._();

  SharedPreferences? _prefs;

  /// Initialize SharedPreferences
  Future<void> init() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      debugPrint('✅ [Cache] Initialized');
      
      // Eski cache'leri temizle
      await _cleanOldCache();
    } catch (e) {
      debugPrint('❌ [Cache] Init error: $e');
    }
  }

  /// SharedPreferences instance'ını al (lazy load)
  Future<SharedPreferences> get _prefsInstance async {
    if (_prefs == null) {
      await init();
    }
    return _prefs!;
  }

  // ============ GAMIFICATION STATE CACHE ============

  /// Gamification state'i cache'le
  Future<bool> cacheState({
    required String userId,
    required Map<String, dynamic> stateData,
  }) async {
    try {
      final prefs = await _prefsInstance;
      
      // State'i JSON'a çevir
      final jsonString = jsonEncode(stateData);
      
      // Kaydet
      await prefs.setString(_keyState, jsonString);
      await prefs.setString(_keyUserId, userId);
      await prefs.setString(_keyLastSync, DateTime.now().toIso8601String());
      
      debugPrint('💾 [Cache] State saved for user: $userId');
      debugPrint('   Total XP: ${stateData['totalXP']}');
      debugPrint('   Level: ${stateData['currentLevel']}');
      debugPrint('   Node: ${stateData['currentNode']}');
      
      return true;
    } catch (e) {
      debugPrint('❌ [Cache] Save error: $e');
      return false;
    }
  }

  /// Cache'lenmiş state'i oku
  Future<Map<String, dynamic>?> getCachedState(String userId) async {
    try {
      final prefs = await _prefsInstance;
      
      // User ID kontrolü
      final cachedUserId = prefs.getString(_keyUserId);
      if (cachedUserId != userId) {
        debugPrint('⚠️ [Cache] User ID mismatch, clearing cache');
        await clearCache();
        return null;
      }
      
      // Cache geçerli mi kontrol et
      if (!await isCacheValid()) {
        debugPrint('⚠️ [Cache] Expired, clearing');
        await clearCache();
        return null;
      }
      
      // State'i oku
      final jsonString = prefs.getString(_keyState);
      if (jsonString == null) {
        debugPrint('⚠️ [Cache] No cached state found');
        return null;
      }
      
      final stateData = jsonDecode(jsonString) as Map<String, dynamic>;
      debugPrint('✅ [Cache] State loaded from cache');
      debugPrint('   Total XP: ${stateData['totalXP']}');
      debugPrint('   Level: ${stateData['currentLevel']}');
      
      return stateData;
    } catch (e) {
      debugPrint('❌ [Cache] Read error: $e');
      return null;
    }
  }

  /// Cache geçerli mi?
  Future<bool> isCacheValid() async {
    try {
      final prefs = await _prefsInstance;
      final lastSyncStr = prefs.getString(_keyLastSync);
      
      if (lastSyncStr == null) return false;
      
      final lastSync = DateTime.parse(lastSyncStr);
      final now = DateTime.now();
      final difference = now.difference(lastSync);
      
      // Max cache süresi kontrolü
      if (difference > maxCacheDuration) {
        debugPrint('⚠️ [Cache] Max duration exceeded (${difference.inDays} days)');
        return false;
      }
      
      // Normal cache süresi kontrolü
      final isValid = difference < cacheValidDuration;
      debugPrint('🔍 [Cache] Valid: $isValid (age: ${difference.inMinutes} min)');
      
      return isValid;
    } catch (e) {
      debugPrint('❌ [Cache] Validation error: $e');
      return false;
    }
  }

  /// Cache'i temizle
  Future<void> clearCache() async {
    try {
      final prefs = await _prefsInstance;
      await prefs.remove(_keyState);
      await prefs.remove(_keyLastSync);
      await prefs.remove(_keyUserId);
      debugPrint('🗑️ [Cache] Cleared');
    } catch (e) {
      debugPrint('❌ [Cache] Clear error: $e');
    }
  }

  // ============ OFFLINE XP TRACKING ============

  /// Offline XP değişikliklerini sakla
  /// (Backend'e gönderilemeyen işlemler için)
  Future<bool> addPendingXP({
    required int xpAmount,
    required String source,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final prefs = await _prefsInstance;
      
      // Mevcut pending XP'leri al
      final pendingListJson = prefs.getString('${_keyPrefix}pending_xp') ?? '[]';
      final pendingList = jsonDecode(pendingListJson) as List;
      
      // Yeni XP ekle
      pendingList.add({
        'xpAmount': xpAmount,
        'source': source,
        'metadata': metadata,
        'timestamp': DateTime.now().toIso8601String(),
      });
      
      // Kaydet
      await prefs.setString('${_keyPrefix}pending_xp', jsonEncode(pendingList));
      
      debugPrint('📝 [Cache] Pending XP added: +$xpAmount from $source');
      debugPrint('   Total pending: ${pendingList.length}');
      
      return true;
    } catch (e) {
      debugPrint('❌ [Cache] Add pending XP error: $e');
      return false;
    }
  }

  /// Bekleyen XP işlemlerini al
  Future<List<Map<String, dynamic>>> getPendingXP() async {
    try {
      final prefs = await _prefsInstance;
      final pendingListJson = prefs.getString('${_keyPrefix}pending_xp') ?? '[]';
      final pendingList = jsonDecode(pendingListJson) as List;
      
      return pendingList.cast<Map<String, dynamic>>();
    } catch (e) {
      debugPrint('❌ [Cache] Get pending XP error: $e');
      return [];
    }
  }

  /// Bekleyen XP işlemlerini temizle
  Future<void> clearPendingXP() async {
    try {
      final prefs = await _prefsInstance;
      await prefs.remove('${_keyPrefix}pending_xp');
      debugPrint('🗑️ [Cache] Pending XP cleared');
    } catch (e) {
      debugPrint('❌ [Cache] Clear pending XP error: $e');
    }
  }

  // ============ DAILY STATS CACHE ============

  /// Günlük istatistikleri cache'le
  Future<bool> cacheDailyStats({
    required Map<String, dynamic> stats,
  }) async {
    try {
      final prefs = await _prefsInstance;
      final today = DateTime.now().toIso8601String().split('T')[0];
      
      await prefs.setString(
        '${_keyPrefix}daily_stats_$today',
        jsonEncode(stats),
      );
      
      debugPrint('💾 [Cache] Daily stats saved for $today');
      return true;
    } catch (e) {
      debugPrint('❌ [Cache] Daily stats save error: $e');
      return false;
    }
  }

  /// Günlük istatistikleri oku
  Future<Map<String, dynamic>?> getCachedDailyStats() async {
    try {
      final prefs = await _prefsInstance;
      final today = DateTime.now().toIso8601String().split('T')[0];
      
      final statsJson = prefs.getString('${_keyPrefix}daily_stats_$today');
      if (statsJson == null) return null;
      
      return jsonDecode(statsJson) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('❌ [Cache] Daily stats read error: $e');
      return null;
    }
  }

  // ============ MAINTENANCE ============

  /// Eski cache'leri temizle (7 günden eski)
  Future<void> _cleanOldCache() async {
    try {
      final prefs = await _prefsInstance;
      final keys = prefs.getKeys();
      final now = DateTime.now();
      
      int cleaned = 0;
      for (final key in keys) {
        if (!key.startsWith(_keyPrefix)) continue;
        
        // Daily stats temizliği
        if (key.contains('daily_stats_')) {
          final dateStr = key.split('_').last;
          try {
            final date = DateTime.parse(dateStr);
            if (now.difference(date).inDays > 7) {
              await prefs.remove(key);
              cleaned++;
            }
          } catch (_) {
            // Invalid date format, remove it
            await prefs.remove(key);
            cleaned++;
          }
        }
      }
      
      if (cleaned > 0) {
        debugPrint('🧹 [Cache] Cleaned $cleaned old entries');
      }
    } catch (e) {
      debugPrint('❌ [Cache] Clean error: $e');
    }
  }

  /// Tüm cache'i temizle (logout için)
  Future<void> clearAllCache() async {
    try {
      final prefs = await _prefsInstance;
      final keys = prefs.getKeys().where((k) => k.startsWith(_keyPrefix)).toList();
      
      for (final key in keys) {
        await prefs.remove(key);
      }
      
      debugPrint('🗑️ [Cache] All gamification cache cleared');
    } catch (e) {
      debugPrint('❌ [Cache] Clear all error: $e');
    }
  }

  // ============ DEBUG & STATS ============

  /// Cache istatistiklerini göster
  Future<Map<String, dynamic>> getCacheStats() async {
    try {
      final prefs = await _prefsInstance;
      final keys = prefs.getKeys().where((k) => k.startsWith(_keyPrefix)).toList();
      
      final lastSyncStr = prefs.getString(_keyLastSync);
      final userId = prefs.getString(_keyUserId);
      final pendingXP = await getPendingXP();
      
      return {
        'totalKeys': keys.length,
        'lastSync': lastSyncStr,
        'userId': userId,
        'pendingXPCount': pendingXP.length,
        'isCacheValid': await isCacheValid(),
        'keys': keys,
      };
    } catch (e) {
      debugPrint('❌ [Cache] Stats error: $e');
      return {};
    }
  }

  /// Debug: Cache içeriğini yazdır
  Future<void> printCacheDebug() async {
    try {
      final stats = await getCacheStats();
      debugPrint('📊 [Cache] Debug Info:');
      debugPrint('   Total Keys: ${stats['totalKeys']}');
      debugPrint('   Last Sync: ${stats['lastSync']}');
      debugPrint('   User ID: ${stats['userId']}');
      debugPrint('   Pending XP: ${stats['pendingXPCount']}');
      debugPrint('   Valid: ${stats['isCacheValid']}');
      debugPrint('   Keys: ${stats['keys']}');
    } catch (e) {
      debugPrint('❌ [Cache] Debug error: $e');
    }
  }
}