import React from 'react';
import { ArticleData } from '../models';
import { Card } from './Card';
import clsx from 'clsx';

export interface ArticleCardProps {
  article: ArticleData;
  onClick?: () => void;
  className?: string;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onClick,
  className
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <Card
      padding="none"
      shadow="md"
      rounded="lg"
      onClick={onClick}
      className={clsx(
        'overflow-hidden cursor-pointer',
        'hover:shadow-xl transition-all duration-300 ease-in-out',
        'active:scale-95', // Touch feedback
        className
      )}
    >
      {/* Image Section - Responsive */}
      {article.main_image && (
        <div className="relative h-40 sm:h-48 lg:h-52 bg-gray-200">
          <img
            src={article.main_image}
            alt={article.title}
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
            loading="lazy"
          />
          
          {/* Category Badge - Enhanced */}
          <div className="absolute top-2 left-2 sm:top-3 sm:left-3">
            <span className="px-2 py-1 text-xs font-semibold bg-blue-600/90 backdrop-blur-sm text-white rounded-full shadow-lg">
              {article.category}
            </span>
          </div>
        </div>
      )}
      
      {/* Content Section - Responsive */}
      <div className="p-3 sm:p-4">
        <h2 className="text-base sm:text-lg font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
          {article.title}
        </h2>
        
        {article.summary && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2 sm:line-clamp-3 leading-relaxed">
            {article.summary}
          </p>
        )}
        
        {/* Tags - Responsive */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {article.tags.slice(0, 2).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
              >
                #{tag}
              </span>
            ))}
            {article.tags.length > 2 && (
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded-full">
                +{article.tags.length - 2}
              </span>
            )}
          </div>
        )}
        
        {/* Footer - Responsive */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-gray-500 pt-3 border-t border-gray-100 space-y-1 sm:space-y-0">
          <div className="flex items-center space-x-2 truncate">
            {article.author && <span className="truncate">{article.author}</span>}
            {article.author && article.location && <span>•</span>}
            {article.location && <span className="truncate">{article.location}</span>}
          </div>
          <span className="text-xs text-gray-400">{formatDate(article.published_date)}</span>
        </div>
      </div>
    </Card>
  );
};