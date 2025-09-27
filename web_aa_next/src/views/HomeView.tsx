import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticlesViewModel } from '../viewmodels';
import { ArticleCard, LoadingSpinner, Button } from '../components';

export const HomeView: React.FC = () => {
  const navigate = useNavigate();
  const { articles, loading, error, hasMore, loadMore } = useArticlesViewModel();

  const handleArticleClick = (articleId: string) => {
    navigate(`/news/${articleId}`);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  if (loading && articles.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error && articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96 px-4">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Haberler Yüklenemedi
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={handleRefresh}>
            Tekrar Dene
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Haberler
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
              onClick={() => handleArticleClick(article.id)}
              className="hover:scale-105 transition-transform duration-200"
            />
          ))}
        </div>

        {/* Load More Button */}
        {hasMore && (
          <div className="flex justify-center mt-8">
            <Button
              onClick={loadMore}
              disabled={loading}
              className="px-6 py-3"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span>Yükleniyor...</span>
                </div>
              ) : (
                'Daha Fazla Yükle'
              )}
            </Button>
          </div>
        )}

        {/* No More Articles */}
        {!hasMore && articles.length > 0 && (
          <div className="text-center mt-8 text-gray-500">
            <p>Tüm haberler yüklendi</p>
          </div>
        )}
      </div>
    </div>
  );
};