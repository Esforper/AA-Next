import React from 'react';
import { ReelData } from '../models';
import { Card } from './Card';
import clsx from 'clsx';

export interface ReelItemProps {
  reel: ReelData;
  isActive?: boolean;
  onPlay?: () => void;
  onImageClick?: () => void;
  className?: string;
}

export const ReelItem: React.FC<ReelItemProps> = ({
  reel,
  isActive = false,
  onPlay,
  onImageClick,
  className
}) => {
  return (
    <Card
      padding="none"
      shadow="lg"
      rounded="lg"
      className={clsx(
        'w-full max-w-sm mx-auto overflow-hidden',
        {
          'ring-2 ring-blue-500': isActive
        },
        className
      )}
    >
      {/* Image Section */}
      <div 
        className="relative h-96 bg-gray-200 cursor-pointer"
        onClick={onImageClick}
      >
        <img
          src={reel.main_image}
          alt={reel.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        
        {/* Play Button Overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPlay?.();
            }}
            className={clsx(
              'w-16 h-16 rounded-full flex items-center justify-center transition-all duration-200',
              'bg-white bg-opacity-90 hover:bg-opacity-100 hover:scale-110',
              'focus:outline-none focus:ring-2 focus:ring-blue-500'
            )}
          >
            <svg
              className="w-8 h-8 text-gray-800 ml-1"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M8 5v10l8-5-8-5z" />
            </svg>
          </button>
        </div>
        
        {/* Category Badge */}
        <div className="absolute top-3 left-3">
          <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
            {reel.category}
          </span>
        </div>
        
        {/* Duration Badge */}
        <div className="absolute top-3 right-3">
          <span className="px-2 py-1 text-xs font-medium bg-black bg-opacity-70 text-white rounded-full">
            {Math.floor(reel.estimated_duration / 60)}:{(reel.estimated_duration % 60).toString().padStart(2, '0')}
          </span>
        </div>
      </div>
      
      {/* Content Section */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {reel.title}
        </h3>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
          {reel.content}
        </p>
        
        {/* Tags */}
        {reel.tags && reel.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {reel.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
        
        {/* Author & Location */}
        {(reel.author || reel.location) && (
          <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
            {reel.author && <span>{reel.author}</span>}
            {reel.author && reel.location && <span> • </span>}
            {reel.location && <span>{reel.location}</span>}
          </div>
        )}
      </div>
    </Card>
  );
};