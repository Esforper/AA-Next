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
      className={clsx('overflow-hidden', className)}
    >
      {/* Image Section */}
      {article.main_image && (
        <div className="relative h-48 bg-gray-200">
          <img
            src={article.main_image}
            alt={article.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          
          {/* Category Badge */}
          <div className="absolute top-3 left-3">
            <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
              {article.category}
            </span>
          </div>
        </div>
      )}
      
      {/* Content Section */}
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {article.title}
        </h2>
        
        {article.summary && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-3">
            {article.summary}
          </p>
        )}
        
        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {article.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
        
        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
          <div className="flex items-center space-x-2">
            {article.author && <span>{article.author}</span>}
            {article.author && article.location && <span>•</span>}
            {article.location && <span>{article.location}</span>}
          </div>
          <span>{formatDate(article.published_date)}</span>
        </div>
      </div>
    </Card>
  );
};