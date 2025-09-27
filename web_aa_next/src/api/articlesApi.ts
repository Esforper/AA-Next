import { ArticleResponse, ArticleDetailResponse, PaginationParams } from '../models';
import { API_CONFIG, createApiUrl } from './config';

export class ArticlesApi {
  static async fetchArticles(params: PaginationParams = {}): Promise<ArticleResponse> {
    try {
      const { limit = 20, offset = 0, ...otherParams } = params;
      const url = createApiUrl(API_CONFIG.ENDPOINTS.ARTICLES.LIST, { limit, offset, ...otherParams });
      
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
      console.error('Failed to fetch articles:', error);
      throw error;
    }
  }

  static async fetchArticleById(id: string): Promise<ArticleDetailResponse> {
    try {
      const url = createApiUrl(`${API_CONFIG.ENDPOINTS.ARTICLES.DETAIL}/${id}`);
      
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
      console.error(`Failed to fetch article with id ${id}:`, error);
      throw error;
    }
  }
}