// gamificationApi.ts - Flutter gamification_api_service.dart'tan uyarlandı

import { API_CONFIG } from './config';
import {
  AddXpRequest,
  AddXpResponse,
  LevelResponse,
  UserStatsResponse,
  DailyProgressResponse,
  LeaderboardResponse,
  AchievementsResponse
} from '../models/GamificationModels';

const BASE = API_CONFIG.BASE_URL;

const headers = (userId?: string) => ({
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  ...(userId ? { 'X-User-ID': userId } : {}),
});

export class GamificationApi {
  
  // ============ XP ENDPOINTS ============
  
  /**
   * XP Ekle
   * POST /api/gamification/add-xp
   */
  static async addXP(body: AddXpRequest): Promise<AddXpResponse> {
    try {
      const res = await fetch(`${BASE}/api/gamification/add-xp`, {
        method: 'POST',
        headers: headers(body.user_id),
        body: JSON.stringify(body),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ addXP failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ LEVEL ENDPOINTS ============
  
  /**
   * Mevcut level verilerini al
   * GET /api/gamification/level/{userId}
   */
  static async getCurrentLevel(userId: string): Promise<LevelResponse> {
    try {
      const res = await fetch(`${BASE}/api/gamification/level/${userId}`, {
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getCurrentLevel failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ STATS ENDPOINTS ============
  
  /**
   * Kullanıcı istatistiklerini al
   * GET /api/gamification/stats/{userId}
   */
  static async getUserStats(userId: string): Promise<UserStatsResponse> {
    try {
      const res = await fetch(`${BASE}/api/gamification/stats/${userId}`, {
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getUserStats failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  /**
   * Günlük progress al
   * GET /api/gamification/daily-progress/{userId}
   */
  static async getDailyProgress(userId: string): Promise<DailyProgressResponse> {
    try {
      const res = await fetch(`${BASE}/api/gamification/daily-progress/${userId}`, {
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getDailyProgress failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ DAILY RESET ============
  
  /**
   * Günlük progress'i sıfırla
   * POST /api/gamification/reset-daily/{userId}
   */
  static async resetDaily(userId: string): Promise<{ success: boolean; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/reset-daily/${userId}`, {
        method: 'POST',
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ resetDaily failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ LEADERBOARD ============
  
  /**
   * Leaderboard al
   * GET /api/gamification/leaderboard
   */
  static async getLeaderboard(params: {
    limit?: number;
    period?: 'all_time' | 'weekly' | 'daily';
  } = {}): Promise<LeaderboardResponse> {
    try {
      const { limit = 50, period = 'all_time' } = params;
      const queryParams = new URLSearchParams({
        limit: limit.toString(),
        period,
      });
      
      const res = await fetch(`${BASE}/api/gamification/leaderboard?${queryParams}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getLeaderboard failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  /**
   * Kullanıcının rank'ini al
   * GET /api/gamification/rank/{userId}
   */
  static async getUserRank(userId: string): Promise<{ success: boolean; rank?: number; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/rank/${userId}`, {
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getUserRank failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ ACHIEVEMENTS ============
  
  /**
   * Kullanıcının başarımlarını al
   * GET /api/gamification/achievements/{userId}
   */
  static async getAchievements(userId: string): Promise<AchievementsResponse> {
    try {
      const res = await fetch(`${BASE}/api/gamification/achievements/${userId}`, {
        headers: headers(userId),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getAchievements failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  /**
   * Başarım unlock'la
   * POST /api/gamification/unlock-achievement
   */
  static async unlockAchievement(userId: string, achievementId: string): Promise<{ success: boolean; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/unlock-achievement`, {
        method: 'POST',
        headers: headers(userId),
        body: JSON.stringify({ user_id: userId, achievement_id: achievementId }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ unlockAchievement failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ SYNC ============
  
  /**
   * Local state'i backend ile senkronize et
   * POST /api/gamification/sync
   */
  static async syncState(userId: string, localState: Record<string, unknown>): Promise<{ success: boolean; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/sync`, {
        method: 'POST',
        headers: headers(userId),
        body: JSON.stringify({
          user_id: userId,
          local_state: localState,
          timestamp: new Date().toISOString(),
        }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ syncState failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ TRACKING ============

  /**
   * Reel etkileşimlerini senkronize et
   * POST /api/gamification/sync-reel-interactions
   */
  static async syncReelInteractions(
    userId: string,
    reelInteractions: Record<string, { watched: boolean; detailViewed: boolean; shared: boolean; lastInteractionDate: string }>
  ): Promise<{ success: boolean; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/sync-reel-interactions`, {
        method: 'POST',
        headers: headers(userId),
        body: JSON.stringify({
          user_id: userId,
          reel_interactions: reelInteractions,
          timestamp: new Date().toISOString(),
        }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ syncReelInteractions failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }

  /**
   * Aktivite tracking
   * POST /api/gamification/track-activity
   */
  static async trackActivity(
    userId: string,
    activityType: string,
    activityData: Record<string, unknown>
  ): Promise<{ success: boolean; message?: string }> {
    try {
      const res = await fetch(`${BASE}/api/gamification/track-activity`, {
        method: 'POST',
        headers: headers(userId),
        body: JSON.stringify({
          user_id: userId,
          activity_type: activityType,
          activity_data: activityData,
          timestamp: new Date().toISOString(),
        }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ trackActivity failed:', error);
      return { success: false, message: error instanceof Error ? error.message : 'Failed' };
    }
  }
  
  // ============ HEALTH CHECK ============
  
  /**
   * Health check
   * GET /api/health
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const res = await fetch(`${BASE}/api/health`, {
        signal: AbortSignal.timeout(5000),
      });
      return res.ok;
    } catch {
      return false;
    }
  }
}
