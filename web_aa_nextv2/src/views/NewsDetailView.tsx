import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useArticleDetailViewModel } from '../viewmodels';
import { LoadingSpinner, Button, Card } from '../components';

export const NewsDetailView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { article, loading, error, fetchArticle } = useArticleDetailViewModel(id);

  const handleBack = () => {
    navigate(-1);
  };

  const handleRetry = () => {
    if (id) {
      fetchArticle(id);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <Card padding="lg" className="text-center max-w-md">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Haber Yüklenemedi
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex flex-col sm:flex-row gap-2 justify-center">
            <Button onClick={handleRetry} variant="primary">
              Tekrar Dene
            </Button>
            <Button onClick={handleBack} variant="outline">
              Geri Dön
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <Card padding="lg" className="text-center max-w-md">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Haber Bulunamadı
          </h2>
          <p className="text-gray-600 mb-4">
            Aradığınız haber mevcut değil veya kaldırılmış olabilir.
          </p>
          <Button onClick={handleBack} variant="primary">
            Geri Dön
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Responsive */}
      <div className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors active:scale-95"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" />
              </svg>
              <span className="hidden sm:inline">Geri</span>
            </button>
            <h1 className="text-lg sm:text-xl font-semibold text-gray-900">
              Haber Detayı
            </h1>
            <div className="w-16" /> {/* Spacer */}
          </div>
        </div>
      </div>

      {/* Content - Responsive */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <Card padding="lg" shadow="lg">
          {/* Category Badge */}
          <div className="mb-4">
            <span className="px-3 py-1 text-sm font-medium bg-blue-600 text-white rounded-full">
              {article.category}
            </span>
          </div>

          {/* Title - Responsive */}
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 sm:mb-6 leading-tight">
            {article.title}
          </h1>

          {/* Meta Information - Responsive */}
          <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-4 text-sm text-gray-600 mb-6 pb-6 border-b border-gray-200">
            {article.author && (
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                </svg>
                <span className="truncate">{article.author}</span>
              </div>
            )}
            
            {article.location && (
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
                <span className="truncate">{article.location}</span>
              </div>
            )}
            
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" />
              </svg>
              <span>{formatDate(article.published_date)}</span>
            </div>
          </div>

          {/* Main Image - Responsive */}
          {article.main_image && (
            <div className="mb-6">
              <img
                src={article.main_image}
                alt={article.title}
                className="w-full h-64 sm:h-80 lg:h-96 object-cover rounded-lg shadow-lg"
              />
            </div>
          )}

          {/* Summary - Responsive */}
          {article.summary && (
            <div className="mb-6">
              <p className="text-base sm:text-lg text-gray-700 leading-relaxed font-medium">
                {article.summary}
              </p>
            </div>
          )}

          {/* Content - Responsive */}
          <div className="prose prose-sm sm:prose-base lg:prose-lg max-w-none mb-8">
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap text-sm sm:text-base">
              {article.content}
            </div>
          </div>

          {/* Additional Images - Responsive */}
          {article.images && article.images.length > 1 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                İlgili Görseller
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {article.images.slice(1).map((image, index) => (
                  <img
                    key={index}
                    src={image}
                    alt={`${article.title} - ${index + 2}`}
                    className="w-full h-32 sm:h-40 object-cover rounded-lg shadow-md hover:shadow-lg transition-shadow"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Etiketler
              </h3>
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex flex-col sm:flex-row justify-between items-center pt-6 border-t border-gray-200">
            {article.prevArticleId && (
              <Button
                onClick={() => navigate(`/news/${article.prevArticleId}`)}
                variant="outline"
                className="mb-2 sm:mb-0"
              >
                ← Önceki Haber
              </Button>
            )}
            
            <Button
              onClick={() => navigate('/')}
              variant="secondary"
              className="mb-2 sm:mb-0"
            >
              Ana Sayfaya Dön
            </Button>
            
            {article.nextArticleId && (
              <Button
                onClick={() => navigate(`/news/${article.nextArticleId}`)}
                variant="outline"
              >
                Sonraki Haber →
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};