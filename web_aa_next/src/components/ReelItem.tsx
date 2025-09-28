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
  style?: React.CSSProperties;
}

export const ReelItem: React.FC<ReelItemProps> = ({
  reel,
  isActive = false,
  onPlay,
  onImageClick,
  className,
  style
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
      style={style}
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
        
        
        {/* Category Badge */}
        <div className="absolute top-4 left-4">
          <span className="px-3 py-1 text-sm font-medium bg-blue-600 text-white rounded-full">
            {reel.category}
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