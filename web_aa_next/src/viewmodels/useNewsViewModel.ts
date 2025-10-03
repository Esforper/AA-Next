import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { NewsApi } from '../api/newsApi';
import { NewsItem, NewsCategory } from '../models/NewsModels';

export interface NewsViewModel {
  news: NewsItem[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  category: string;
  setCategory: (c: string) => void;
  refresh: () => Promise<void>;
  loadMore: () => Promise<void>;
}

const DEFAULT_LIMIT = 12;

export const useNewsViewModel = (): NewsViewModel => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const [category, setCategoryState] = useState<string>('');
  const cacheRef = useRef<Record<string, { items: NewsItem[]; offset: number; hasMore: boolean }>>({});

  const key = useMemo(() => `${category || 'all'}`, [category]);

  const fetchNews = useCallback(async (refresh: boolean) => {
    try {
      setLoading(true);
      setError(null);

      const currentOffset = refresh ? 0 : offset;
      const res = await NewsApi.fetchNews({ category: category || undefined, limit: DEFAULT_LIMIT, offset: currentOffset });

      if (!res.success) throw new Error(res.message || 'Haberler alınamadı');

      const items = res.data;
      const nextOffset = refresh ? items.length : currentOffset + items.length;
      const nextHasMore = items.length === DEFAULT_LIMIT;

      setNews(prev => (refresh ? items : [...prev, ...items]));
      setOffset(nextOffset);
      setHasMore(Boolean(nextHasMore));

      cacheRef.current[key] = { items: refresh ? items : [...(cacheRef.current[key]?.items || []), ...items], offset: nextOffset, hasMore: nextHasMore };
    } catch (e: any) {
      setError(e?.message || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  }, [category, offset, key]);

  const refresh = useCallback(async () => {
    await fetchNews(true);
  }, [fetchNews]);

  const loadMore = useCallback(async () => {
    if (!loading && hasMore) {
      await fetchNews(false);
    }
  }, [loading, hasMore, fetchNews]);

  const setCategory = useCallback((c: string) => {
    setCategoryState(c);
    const cache = cacheRef.current[c || 'all'];
    if (cache) {
      setNews(cache.items);
      setOffset(cache.offset);
      setHasMore(cache.hasMore);
    } else {
      setNews([]);
      setOffset(0);
      setHasMore(true);
      // trigger fresh fetch
      void fetchNews(true);
    }
  }, [fetchNews]);

  useEffect(() => {
    // initial fetch
    void fetchNews(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { news, loading, error, hasMore, category, setCategory, refresh, loadMore };
};


