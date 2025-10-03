import { API_CONFIG, createApiUrl } from './config';
import { NewsListResponse, NewsQueryParams, NewsItem } from '../models/NewsModels';

export class NewsApi {
  static async fetchNews(params: NewsQueryParams = {}): Promise<NewsListResponse> {
    try {
      const endpoint = '/api/news';
      const url = new URL(endpoint, API_CONFIG.BASE_URL);
      const { category, limit = 20, offset = 0, q } = params;

      url.searchParams.set('limit', String(limit));
      url.searchParams.set('offset', String(offset));
      if (category) url.searchParams.set('category', category);
      if (q) url.searchParams.set('q', q);

      const res = await fetch(url.toString(), {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();

      // Normalize response to NewsListResponse
      const normalized: NewsListResponse = {
        success: Boolean(data.success ?? true),
        message: data.message,
        data: (data.data || data.items || data.news || []).map((item: any): NewsItem => ({
          id: String(item.id ?? item._id ?? crypto.randomUUID()),
          title: item.title ?? item.headline ?? 'Başlık',
          description: item.description ?? item.summary ?? '',
          content: item.content ?? item.full_content,
          imageUrl: item.imageUrl ?? item.image_url ?? item.main_image,
          url: item.url,
          category: item.category ?? 'General',
          publishedAt: item.publishedAt ?? item.published_at,
          author: item.author,
          source: item.source ?? 'AA'
        })),
        pagination: {
          limit: Number(data.pagination?.limit ?? limit),
          offset: Number(data.pagination?.offset ?? offset),
          total: Number(data.pagination?.total ?? data.total ?? undefined),
          hasMore: Boolean(data.pagination?.hasMore ?? (Array.isArray(data.items) ? data.items.length === limit : undefined))
        }
      };

      return normalized;
    } catch (error: any) {
      return {
        success: false,
        message: error?.message || 'Haberler alınamadı',
        data: [],
        pagination: { limit: params.limit, offset: params.offset, hasMore: false }
      };
    }
  }
}


