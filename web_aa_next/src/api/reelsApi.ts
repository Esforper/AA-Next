import { 
  ReelResponse, 
  PaginationParams,
  ScrapedNewsResponse,
  GenerateReelsResponse,
  NewsDetailResponse,
  CategoriesResponse,
  StatsResponse,
  MockupReelOutput,
  ScrapedNewsItem,
  ReelData
} from '../models';
import { API_CONFIG, createApiUrl } from './config';

export class ReelsApi {
  // Get scraped news from backend
  static async fetchScrapedNews(count: number = 3, category?: string): Promise<ScrapedNewsResponse> {
    try {
      const params: Record<string, string | number> = { count };
      if (category) params.category = category;
      
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.SCRAPED_NEWS, params);
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
      console.error('Failed to fetch scraped news:', error);
      throw error;
    }
  }

  // Generate reels from scraped news
  static async generateReels(count: number = 3, voice: string = 'alloy', category?: string): Promise<GenerateReelsResponse> {
    try {
      const params: Record<string, string | number> = { count, voice };
      if (category) params.category = category;
      
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.GENERATE, params);
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
      console.error('Failed to generate reels:', error);
      throw error;
    }
  }

  // Get news detail
  static async fetchNewsDetail(newsId: string): Promise<NewsDetailResponse> {
    try {
      const url = createApiUrl(`${API_CONFIG.ENDPOINTS.REELS.NEWS_DETAIL}/${newsId}`);
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
      console.error('Failed to fetch news detail:', error);
      throw error;
    }
  }

  // Get categories
  static async fetchCategories(): Promise<CategoriesResponse> {
    try {
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.CATEGORIES);
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
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  }

  // Get stats
  static async fetchStats(): Promise<StatsResponse> {
    try {
      const url = createApiUrl(API_CONFIG.ENDPOINTS.REELS.STATS);
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
      console.error('Failed to fetch stats:', error);
      throw error;
    }
  }

  // Legacy methods for compatibility
  static async fetchReelsMix(count: number = 10): Promise<ReelResponse> {
    try {
      // Convert backend reels to legacy format
      const generateResponse = await this.generateReels(count);
      
      const legacyReels: ReelData[] = generateResponse.reels.map((reel: MockupReelOutput) => ({
        id: reel.id,
        title: reel.news_data.title,
        content: reel.news_data.full_content,
        category: reel.news_data.category,
        images: reel.news_data.images,
        main_image: reel.news_data.main_image || '',
        audio_url: reel.audio_url,
        subtitles: [], // Backend doesn't provide subtitles yet
        estimated_duration: reel.duration_seconds,
        tags: reel.news_data.tags,
        author: reel.news_data.author,
        location: reel.news_data.location,
        summary: reel.news_data.summary
      }));

      return {
        success: generateResponse.success,
        reels: legacyReels,
        message: generateResponse.message
      };
    } catch (error) {
      console.error('Failed to fetch reels mix:', error);
      throw error;
    }
  }

  static async fetchReelsReady(params: PaginationParams = {}): Promise<ReelResponse> {
    try {
      // Check if backend is available and get reels
      const { limit = 15 } = params;
      return await this.fetchReelsMix(limit);
    } catch (error) {
      console.error('Failed to fetch ready reels:', error);
      throw error;
    }
  }
}