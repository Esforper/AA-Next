import { useState, useEffect, useCallback } from 'react';
import { ArticleData } from '../models';
import { ArticlesApi } from '../api';

export interface ArticleDetailViewModel {
  article: ArticleData | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchArticle: (id: string) => Promise<void>;
}

export const useArticleDetailViewModel = (articleId?: string): ArticleDetailViewModel => {
  const [article, setArticle] = useState<ArticleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticle = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ArticlesApi.fetchArticleById(id);
      
      if (response.success) {
        setArticle(response.article);
      } else {
        setError(response.message || 'Failed to fetch article');
      }
    } catch (err) {
      console.error('Failed to fetch article:', err);
      setError('Failed to load article. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-fetch article when articleId changes
  useEffect(() => {
    if (articleId) {
      fetchArticle(articleId);
    }
  }, [articleId, fetchArticle]);

  return {
    article,
    loading,
    error,
    fetchArticle
  };
};