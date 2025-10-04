import { API_CONFIG } from './config';

export interface NewsDetailData {
  id: string;
  title: string;
  imageUrl?: string;
  content: string;
  summary?: string;
  category?: string;
  publishedAt?: string;
  author?: string;
  source?: string;
}

export interface NewsDetailResponse {
  success: boolean;
  message?: string;
  data?: NewsDetailData;
}

export class NewsDetailApi {
  static async fetchDetailById(id: string): Promise<NewsDetailResponse> {
    try {
      // Primary: if there is a dedicated news detail endpoint use it
      const url = new URL(`/api/news/${id}`, API_CONFIG.BASE_URL);
      const res = await fetch(url.toString(), {
        headers: { 'Accept': 'application/json' },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });
      if (res.ok) {
        const data = await res.json();
        const item = data.data || data.news_item || data;
        return {
          success: true,
          data: {
            id: String(item.id ?? id),
            title: item.title ?? item.headline ?? 'Başlık',
            imageUrl: item.imageUrl ?? item.image_url ?? item.main_image,
            content: item.content ?? item.full_content ?? item.description ?? '',
            summary: item.summary ?? item.description,
            category: item.category,
            publishedAt: item.publishedAt ?? item.published_at,
            author: item.author,
            source: item.source ?? 'AA'
          }
        };
      }

      // Fallback: Reels detail by mapping feed item (BackendAPIDemo Reels.py)
      const reelsRes = await fetch(`${API_CONFIG.BASE_URL}/api/reels/${id}`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });
      if (reelsRes.ok) {
        const reelsData = await reelsRes.json();
        const r = reelsData.reel || reelsData.data || reelsData;
        return {
          success: true,
          data: {
            id: String(r.id ?? id),
            title: r.news_data?.title || 'Başlık',
            imageUrl: r.news_data?.main_image || (Array.isArray(r.news_data?.images) ? r.news_data.images[0] : undefined),
            content: r.news_data?.full_content || r.news_data?.summary || '',
            summary: r.news_data?.summary,
            category: r.news_data?.category,
            publishedAt: r.published_at,
            author: r.news_data?.author,
            source: 'AA'
          }
        };
      }

      // Final fallback: public mock
      const mockRes = await fetch(`${window.location.origin}/mocks/news.json`);
      if (mockRes.ok) {
        const mock = await mockRes.json();
        const item = (mock.data || []).find((x: any) => String(x.id) === String(id)) || (mock.data || [])[0];
        if (item) {
          return {
            success: true,
            data: {
              id: String(item.id ?? id),
              title: item.title,
              imageUrl: item.imageUrl,
              content: item.content || item.description || '',
              summary: item.description,
              category: item.category,
              publishedAt: item.publishedAt,
              author: item.author,
              source: item.source
            }
          };
        }
      }

      return { success: false, message: 'Detay bulunamadı' };
    } catch (e: any) {
      return { success: false, message: e?.message || 'Detay alınamadı' };
    }
  }
}



