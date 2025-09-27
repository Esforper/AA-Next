import { ReelResponse, PaginationParams } from '../models';
import { API_CONFIG, createApiUrl } from './config';

export class ReelsApi {
  static async fetchReelsMix(count: number = 10): Promise<ReelResponse> {
    try {
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.MIX, { count });
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to fetch reels mix:', error);
      throw error;
    }
  }

  static async fetchReelsReady(params: PaginationParams = {}): Promise<ReelResponse> {
    try {
      const { limit = 15, ...otherParams } = params;
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.READY, { limit, ...otherParams });
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to fetch ready reels:', error);
      throw error;
    }
  }
}