import { useCallback, useState } from 'react';
import { NewsDetailApi, NewsDetailData } from '../api/newsDetailApi';

export interface NewsDetailViewModel {
  isOpen: boolean;
  loading: boolean;
  error: string | null;
  data: NewsDetailData | null;
  open: (id: string) => Promise<void>;
  close: () => void;
}

export const useNewsDetailViewModel = (): NewsDetailViewModel => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<NewsDetailData | null>(null);

  const open = useCallback(async (id: string) => {
    try {
      setIsOpen(true);
      setLoading(true);
      setError(null);
      setData(null);
      const res = await NewsDetailApi.fetchDetailById(id);
      if (!res.success || !res.data) throw new Error(res.message || 'Detay alınamadı');
      setData(res.data);
    } catch (e: any) {
      setError(e?.message || 'Detay alınamadı');
    } finally {
      setLoading(false);
    }
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setData(null);
    setError(null);
  }, []);

  return { isOpen, loading, error, data, open, close };
};



