// gameApi.ts - Multiplayer Game API (Ported from Flutter game_service.dart)

import { API_CONFIG } from './config';
import {
  GameEligibility,
  MatchmakingResponse,
  MatchmakingStatusResponse,
  GameSession,
  GameQuestion,
  AnswerResponse,
  GameResult,
  GameHistoryItem,
  GameHistoryDetail
} from '../models/GameModels';

const BASE = API_CONFIG.BASE_URL;

/**
 * Get authentication token from localStorage/sessionStorage
 * Token is stored as a plain string, not JSON
 */
const getAuthToken = (): string | null => {
  try {
    // Check localStorage first (persistent)
    let token = localStorage.getItem('aa_auth_token');
    if (token) return token;
    
    // Check sessionStorage (temporary)
    token = sessionStorage.getItem('aa_auth_token');
    if (token) return token;
    
    return null;
  } catch {
    return null;
  }
};

/**
 * Create headers with authentication
 */
const headers = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
};

export class GameApi {
  
  // ============ MATCHMAKING ============
  
  /**
   * Check game eligibility
   * GET /api/game/check-eligibility
   */
  static async checkEligibility(params: {
    days?: number;
    min_reels?: number;
  } = {}): Promise<GameEligibility> {
    try {
      const { days = 6, min_reels = 8 } = params;
      const queryParams = new URLSearchParams({
        days: days.toString(),
        min_reels: min_reels.toString(),
      });
      
      const res = await fetch(`${BASE}/api/game/check-eligibility?${queryParams}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ checkEligibility failed:', error);
      return {
        success: false,
        eligible: false,
        current_count: 0,
        required: 8,
        needed: 8,
        message: error instanceof Error ? error.message : 'Failed to check eligibility',
      };
    }
  }
  
  /**
   * Join matchmaking queue
   * POST /api/game/matchmaking/join
   */
  static async joinMatchmaking(params: {
    days?: number;
    min_common_reels?: number;
  } = {}): Promise<MatchmakingResponse> {
    try {
      const { days = 6, min_common_reels = 8 } = params;
      
      const res = await fetch(`${BASE}/api/game/matchmaking/join`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({
          days,
          min_common_reels,
        }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.message || `HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ joinMatchmaking failed:', error);
      return {
        success: false,
        matched: false,
        common_reels_count: 0,
        message: error instanceof Error ? error.message : 'Failed to join matchmaking',
      };
    }
  }
  
  /**
   * Get matchmaking status (for polling)
   * GET /api/game/matchmaking/status
   */
  static async getMatchmakingStatus(): Promise<MatchmakingStatusResponse> {
    try {
      const res = await fetch(`${BASE}/api/game/matchmaking/status`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getMatchmakingStatus failed:', error);
      return {
        success: false,
        in_queue: false,
        matched: false,
        wait_time_seconds: 0,
        queue_position: 0,
        estimated_wait: 0,
        message: error instanceof Error ? error.message : 'Failed to get status',
      };
    }
  }
  
  /**
   * Cancel matchmaking
   * POST /api/game/matchmaking/cancel
   */
  static async cancelMatchmaking(): Promise<void> {
    try {
      await fetch(`${BASE}/api/game/matchmaking/cancel`, {
        method: 'POST',
        headers: headers(),
      });
      console.log('✅ Matchmaking cancelled');
    } catch (error) {
      console.error('❌ cancelMatchmaking failed:', error);
    }
  }
  
  // ============ GAME SESSION ============
  
  /**
   * Get game status
   * GET /api/game/session/{gameId}
   */
  static async getGameStatus(gameId: string): Promise<GameSession> {
    try {
      const res = await fetch(`${BASE}/api/game/session/${gameId}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getGameStatus failed:', error);
      throw error;
    }
  }
  
  /**
   * Get question for a round
   * GET /api/game/session/{gameId}/question/{roundNumber}
   */
  static async getQuestion(gameId: string, roundNumber: number): Promise<GameQuestion> {
    try {
      const res = await fetch(`${BASE}/api/game/session/${gameId}/question/${roundNumber}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getQuestion failed:', error);
      throw error;
    }
  }
  
  /**
   * Submit answer
   * POST /api/game/session/{gameId}/answer/{roundNumber}
   */
  static async answerQuestion(
    gameId: string,
    roundNumber: number,
    selectedIndex: number,
    isPass: boolean = false
  ): Promise<AnswerResponse> {
    try {
      const res = await fetch(`${BASE}/api/game/session/${gameId}/answer/${roundNumber}`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({
          selected_index: selectedIndex,
          is_pass: isPass,
        }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ answerQuestion failed:', error);
      throw error;
    }
  }
  
  /**
   * Get game result
   * GET /api/game/session/{gameId}/result
   */
  static async getGameResult(gameId: string): Promise<GameResult> {
    try {
      const res = await fetch(`${BASE}/api/game/session/${gameId}/result`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getGameResult failed:', error);
      throw error;
    }
  }
  
  /**
   * Leave game (forfeit)
   * POST /api/game/session/{gameId}/leave
   */
  static async leaveGame(gameId: string): Promise<void> {
    try {
      await fetch(`${BASE}/api/game/session/${gameId}/leave`, {
        method: 'POST',
        headers: headers(),
      });
      console.log('✅ Left game');
    } catch (error) {
      console.error('❌ leaveGame failed:', error);
    }
  }
  
  // ============ GAME HISTORY ============
  
  /**
   * Get game history
   * GET /api/game/history
   */
  static async getGameHistory(limit: number = 20): Promise<GameHistoryItem[]> {
    try {
      const res = await fetch(`${BASE}/api/game/history?limit=${limit}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      return data.history || [];
    } catch (error) {
      console.error('❌ getGameHistory failed:', error);
      return [];
    }
  }
  
  /**
   * Get game history detail
   * GET /api/game/history/{gameId}
   */
  static async getGameHistoryDetail(gameId: string): Promise<GameHistoryDetail> {
    try {
      const res = await fetch(`${BASE}/api/game/history/${gameId}`, {
        headers: headers(),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ getGameHistoryDetail failed:', error);
      throw error;
    }
  }
  
  // ============ TEST/DEBUG ============
  
  /**
   * Create bot match (test only)
   * POST /api/game/test/bot-match
   */
  static async createBotMatch(): Promise<{ game_id: string }> {
    try {
      const res = await fetch(`${BASE}/api/game/test/bot-match`, {
        method: 'POST',
        headers: headers(),
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || `HTTP ${res.status}`);
      }
      
      return await res.json();
    } catch (error) {
      console.error('❌ createBotMatch failed:', error);
      throw error;
    }
  }
}
