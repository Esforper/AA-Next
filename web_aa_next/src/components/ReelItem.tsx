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
        'w-full max-w-sm mx-auto overflow-hidden select-none',
        {
          'ring-2 ring-blue-500': isActive
        },
        className
      )}
    >
      {/* Image Section - Full Screen Style */}
      <div 
        className="relative h-screen bg-gray-200 cursor-pointer"
        onClick={onImageClick}
        style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
      >
        <img
          src={reel.main_image}
          alt={reel.title}
          className="w-full h-full object-cover"
          loading="lazy"
          draggable={false}
          onContextMenu={(e) => e.preventDefault()}
        />
        
        {/* Audio Play Button Overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-10">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPlay?.();
            }}
            className={clsx(
              'w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200',
              'bg-white bg-opacity-90 hover:bg-opacity-100 hover:scale-110',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg'
            )}
          >
            <svg
              className="w-10 h-10 text-gray-800 ml-1"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M8 5v10l8-5-8-5z" />
            </svg>
          </button>
        </div>
        
        {/* Category Badge */}
        <div className="absolute top-4 left-4">
          <span className="px-3 py-1 text-sm font-medium bg-blue-600 text-white rounded-full">
            {reel.category}
          </span>
        </div>
        
        {/* Duration Badge */}
        <div className="absolute top-4 right-4">
          <span className="px-3 py-1 text-sm font-medium bg-black bg-opacity-70 text-white rounded-full">
            {Math.floor(reel.estimated_duration / 60)}:{(reel.estimated_duration % 60).toString().padStart(2, '0')}
          </span>
        </div>
      </div>
      
      {/* Content Section - Overlay Style */}
      <div 
        className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black via-black/70 to-transparent text-white select-none"
        style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
      >
        <h3 
          className="text-xl font-bold mb-2 line-clamp-2"
          style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
        >
          {reel.title}
        </h3>
        
        <p 
          className="text-sm text-gray-200 mb-3 line-clamp-2"
          style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
        >
          {reel.content}
        </p>
        
        {/* Tags */}
        {reel.tags && reel.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {reel.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 text-xs bg-white bg-opacity-20 text-white rounded-full backdrop-blur-sm"
                style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
        
        {/* Author & Location */}
        {(reel.author || reel.location) && (
          <div className="text-xs text-gray-300" style={{ userSelect: 'none', WebkitUserSelect: 'none' }}>
            {reel.author && <span>{reel.author}</span>}
            {reel.author && reel.location && <span> • </span>}
            {reel.location && <span>{reel.location}</span>}
          </div>
        )}
      </div>
    </Card>
  );
};