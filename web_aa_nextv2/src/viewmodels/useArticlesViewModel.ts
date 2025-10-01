import { useState, useEffect, useCallback } from 'react';
import { ArticleData } from '../models';
import { ArticlesApi } from '../api';

export interface ArticlesViewModel {
  articles: ArticleData[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  
  // Actions
  fetchArticles: (refresh?: boolean) => Promise<void>;
  loadMore: () => Promise<void>;
}

export const useArticlesViewModel = (): ArticlesViewModel => {
  const [articles, setArticles] = useState<ArticleData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);

  const fetchArticles = useCallback(async (refresh = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const currentOffset = refresh ? 0 : offset;
      const response = await ArticlesApi.fetchArticles({
        limit: 20,
        offset: currentOffset
      });
      
      if (response.success) {
        if (refresh) {
          setArticles(response.articles);
          setOffset(response.articles.length);
        } else {
          setArticles(prev => [...prev, ...response.articles]);
          setOffset(prev => prev + response.articles.length);
        }
        
        // Check if we have more articles
        setHasMore(response.articles.length === 20);
      } else {
        setError(response.message || 'Failed to fetch articles');
      }
    } catch (err) {
      console.error('Failed to fetch articles:', err);
      setError('Failed to load articles. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [offset]);

  const loadMore = useCallback(async () => {
    if (!loading && hasMore) {
      await fetchArticles(false);
    }
  }, [loading, hasMore, fetchArticles]);

  // Auto-fetch articles on mount
  useEffect(() => {
    fetchArticles(true);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    articles,
    loading,
    error,
    hasMore,
    fetchArticles,
    loadMore
  };
};