import { API_CONFIG } from './config';
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

      let data: any;
      if (!res.ok) {
        // Try reels feed as fallback source (BackendAPIDemo Reels.py)
        const reelsParams = new URLSearchParams({ limit: String(limit) });
        const reelsUrl = `${API_CONFIG.BASE_URL}/api/reels/feed?${reelsParams.toString()}`;
        const reelsRes = await fetch(reelsUrl, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-User-ID': 'web_user_' + Math.random().toString(36).substr(2, 9)
          },
          signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
        });

        if (reelsRes.ok) {
          const reelsData = await reelsRes.json();
          // Map reels to NewsItem list
          const mapped: NewsListResponse = {
            success: Boolean(reelsData.success ?? true),
            message: reelsData.message,
            data: (reelsData.reels || []).map((r: any): NewsItem => ({
              id: String(r.id),
              title: r.news_data?.title || 'Başlık',
              description: r.news_data?.summary || '',
              content: r.news_data?.full_content,
              imageUrl: r.news_data?.main_image || (Array.isArray(r.news_data?.images) ? r.news_data.images[0] : undefined),
              url: r.news_data?.url,
              category: r.news_data?.category || 'General',
              publishedAt: r.published_at,
              author: r.news_data?.author,
              source: 'AA'
            })),
            pagination: {
              limit,
              offset,
              total: reelsData.pagination?.total_available,
              hasMore: reelsData.pagination?.has_next
            }
          };
          return mapped;
        }

        // Fallback to mock when both /api/news and reels feed are unavailable
        const mockUrl = `${window.location.origin}/mocks/news.json`;
        const mockRes = await fetch(mockUrl);
        if (!mockRes.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        data = await mockRes.json();
      } else {
        data = await res.json();
      }

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


