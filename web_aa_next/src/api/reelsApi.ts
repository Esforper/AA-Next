// src/api/reelsApi.ts - Updated with Real Backend Integration

import { 
  ReelResponse, 
  PaginationParams,
  ReelData
} from '../models';

// Backend API Response Types
interface BackendReelItem {
  id: string;
  news_data: {
    title: string;
    summary: string;
    full_content: string;
    url: string;
    category: string;
    author?: string;
    location?: string;
    main_image?: string;
    images: string[];
    tags: string[];
  };
  audio_url: string;
  duration_seconds: number;
  status: string;
  published_at: string;
  is_watched?: boolean;
  is_trending?: boolean;
  is_fresh?: boolean;
}

interface FeedPagination {
  current_page: number;
  has_next: boolean;
  has_previous: boolean;
  next_cursor: string | null;
  total_available: number;
}

interface FeedMetadata {
  trending_count: number;
  personalized_count: number;
  fresh_count: number;
  algorithm_version: string;
}

interface FeedResponse {
  success: boolean;
  reels: BackendReelItem[];
  pagination: FeedPagination;
  feed_metadata: FeedMetadata;
  generated_at: string;
  message?: string;
}

interface TrackViewRequest {
  reel_id: string;
  duration_ms: number;
  completed: boolean;
  category?: string;
  session_id?: string;
}

interface TrackViewResponse {
  success: boolean;
  message: string;
  view_id?: string;
  meaningful_view: boolean;
  daily_progress_updated?: boolean;
  new_achievement?: string;
}

// API Configuration
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE || 'http://localhost:8000',
  TIMEOUT: 30000,
  DEFAULT_LIMIT: 20
};

// Generate consistent user ID for session
const USER_ID = 'web_user_' + Math.random().toString(36).substr(2, 9);

export class ReelsApi {
  
  /**
   * 🔥 NEW: Get infinite scroll feed from real backend
   */
  static async fetchInfiniteFeed(params: {
    limit?: number;
    cursor?: string;
    include_watched?: boolean;
  } = {}): Promise<{
    success: boolean;
    reels: ReelData[];
    pagination: FeedPagination;
    metadata: FeedMetadata;
    message?: string;
  }> {
    try {
      const { limit = API_CONFIG.DEFAULT_LIMIT, cursor, include_watched = true } = params;
      
      // Build query params
      const queryParams = new URLSearchParams({
        limit: limit.toString(),
        include_watched: include_watched.toString()
      });
      
      if (cursor) {
        queryParams.append('cursor', cursor);
      }
      
      const url = `${API_CONFIG.BASE_URL}/api/reels/feed?${queryParams.toString()}`;
      
      console.log(`🔄 Fetching infinite feed: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: FeedResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Feed API returned error');
      }
      
      // Convert backend format to frontend format
      const convertedReels = this.convertBackendReels(data.reels);
      
      console.log(`✅ Fetched ${convertedReels.length} reels, has_next: ${data.pagination.has_next}`);
      
      return {
        success: true,
        reels: convertedReels,
        pagination: data.pagination,
        metadata: data.feed_metadata,
        message: data.message
      };
      
    } catch (error) {
      console.error('Failed to fetch infinite feed:', error);
      
      return {
        success: false,
        reels: [],
        pagination: {
          current_page: 1,
          has_next: false,
          has_previous: false,
          next_cursor: null,
          total_available: 0
        },
        metadata: {
          trending_count: 0,
          personalized_count: 0,
          fresh_count: 0,
          algorithm_version: 'v1.0'
        },
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * 🔥 NEW: Track reel viewing
   */
  static async trackReelView(request: TrackViewRequest): Promise<TrackViewResponse | null> {
    try {
      console.log(`📊 Tracking view: ${request.reel_id}, duration: ${request.duration_ms}ms`);
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/reels/track-view`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID,
          'Accept': 'application/json'
        },
        body: JSON.stringify(request),
        signal: AbortSignal.timeout(10000)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: TrackViewResponse = await response.json();
      
      if (data.success) {
        console.log(`✅ View tracked: ${data.meaningful_view ? 'meaningful' : 'partial'} view`);
        if (data.new_achievement) {
          console.log(`🏆 Achievement: ${data.new_achievement}`);
        }
      }
      
      return data;
      
    } catch (error) {
      console.error('Failed to track view:', error);
      return null;
    }
  }
  
  /**
   * 🔥 NEW: Get trending reels
   */
  static async fetchTrendingReels(params: {
    period?: 'hourly' | 'daily' | 'weekly';
    limit?: number;
  } = {}): Promise<{
    success: boolean;
    reels: ReelData[];
    period: string;
    calculated_at: string;
  }> {
    try {
      const { period = 'daily', limit = 20 } = params;
      
      const queryParams = new URLSearchParams({
        period,
        limit: limit.toString()
      });
      
      const url = `${API_CONFIG.BASE_URL}/api/reels/trending?${queryParams.toString()}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        const convertedReels = this.convertBackendReels(data.trending_reels || []);
        return {
          success: true,
          reels: convertedReels,
          period: data.period,
          calculated_at: data.calculated_at
        };
      }
      
      throw new Error(data.message || 'Trending API error');
      
    } catch (error) {
      console.error('Failed to fetch trending reels:', error);
      return {
        success: false,
        reels: [],
        period: 'daily',
        calculated_at: new Date().toISOString()
      };
    }
  }
  
  /**
   * 🔥 NEW: Get user daily progress
   */
  static async fetchUserProgress(userId?: string): Promise<{
    success: boolean;
    progress_percentage: number;
    total_published_today: number;
    watched_today: number;
    category_breakdown: Record<string, any>;
  }> {
    try {
      const targetUserId = userId || USER_ID;
      const url = `${API_CONFIG.BASE_URL}/api/reels/user/${targetUserId}/daily-progress`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
      
    } catch (error) {
      console.error('Failed to fetch user progress:', error);
      return {
        success: false,
        progress_percentage: 0,
        total_published_today: 0,
        watched_today: 0,
        category_breakdown: {}
      };
    }
  }
  
  /**
   * 🔥 NEW: Get single reel by ID
   */
  static async fetchReelById(reelId: string): Promise<{
    success: boolean;
    reel?: ReelData;
    message?: string;
  }> {
    try {
      const url = `${API_CONFIG.BASE_URL}/api/reels/${reelId}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.TIMEOUT)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success && data.reel) {
        const convertedReel = this.convertBackendReels([data.reel])[0];
        return {
          success: true,
          reel: convertedReel
        };
      }
      
      return {
        success: false,
        message: data.message || 'Reel not found'
      };
      
    } catch (error) {
      console.error('Failed to fetch reel by ID:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * Convert backend reel format to frontend format
   */
  private static convertBackendReels(backendReels: BackendReelItem[]): ReelData[] {
    return backendReels.map(backendReel => ({
      id: backendReel.id,
      title: backendReel.news_data?.title || 'Untitled',
      content: backendReel.news_data?.full_content || '',
      summary: backendReel.news_data?.summary || '',
      category: backendReel.news_data?.category || 'general',
      images: backendReel.news_data?.images || [],
      main_image: backendReel.news_data?.main_image || '',
      audio_url: backendReel.audio_url,
      subtitles: [], // Backend doesn't provide subtitles yet
      estimated_duration: backendReel.duration_seconds,
      tags: backendReel.news_data?.tags || [],
      author: backendReel.news_data?.author || '',
      location: backendReel.news_data?.location || '',
      
      // Additional backend fields
      is_watched: backendReel.is_watched || false,
      is_trending: backendReel.is_trending || false,
      is_fresh: backendReel.is_fresh || false,
      published_at: backendReel.published_at,
      
      // Computed fields
      url: backendReel.news_data?.url || '',
      source: 'aa'
    }));
  }
  
  /**
   * Get current user ID
   */
  static getUserId(): string {
    return USER_ID;
  }
  
  // ============ LEGACY METHODS (for backward compatibility) ============
  
  /**
   * Legacy fetchReelsMix - now uses infinite feed
   */
  static async fetchReelsMix(count: number = 10): Promise<ReelResponse> {
    try {
      const result = await this.fetchInfiniteFeed({ limit: count });
      
      return {
        success: result.success,
        reels: result.reels,
        message: result.message
      };
      
    } catch (error) {
      console.error('Failed to fetch reels mix:', error);
      return {
        success: false,
        reels: [],
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
  
  /**
   * Legacy fetchReelsReady - now uses infinite feed
   */
  static async fetchReelsReady(params: PaginationParams = {}): Promise<ReelResponse> {
    try {
      const { limit = 15 } = params;
      const result = await this.fetchInfiniteFeed({ limit });
      
      return {
        success: result.success,
        reels: result.reels,
        message: result.message
      };
      
    } catch (error) {
      console.error('Failed to fetch ready reels:', error);
      return {
        success: false,
        reels: [],
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}

// Export types for external use
export type {
  TrackViewRequest,
  TrackViewResponse,
  FeedPagination,
  FeedMetadata
};