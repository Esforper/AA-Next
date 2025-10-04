import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useArticlesViewModel } from '../viewmodels';
import { ArticleCard, LoadingSpinner, Button } from '../components';
import { NewsSection } from './NewsSection';

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
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Header - Responsive */}
      <div className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">
            Haberler
          </h1>
        </div>
      </div>

      {/* Content - Responsive Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        {/* Articles Grid - Enhanced Responsive */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          {articles.map((article) => (
            <ArticleCard
              key={article.id}
              article={article}
              onClick={() => handleArticleClick(article.id)}
              className="hover:scale-105 hover:shadow-lg transition-all duration-300 ease-in-out"
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

        {/* Latest News Section - Modular integration without breaking layout */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold" style={{ color: '#0C2340' }}>Latest News</h2>
          </div>
          <div className="rounded-xl overflow-hidden ring-1 ring-gray-200">
            <NewsSection hideHeader />
          </div>
        </div>
      </div>
    </div>
  );
};