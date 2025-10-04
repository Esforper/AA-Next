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
        'w-full max-w-sm mx-auto overflow-hidden select-none bg-black',
        {
          'ring-2 ring-blue-500': isActive
        },
        className
      )}
      style={style}
    >
      {/* Image Section - Responsive Full Screen Style */}
      <div 
        className="relative h-full cursor-pointer overflow-hidden"
        onClick={onImageClick}
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          height: '100%'
        }}
      >
        {/* Main Image - Centered and Full Format with Enhanced Blur */}
        <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
          <img
            src={reel.main_image}
            alt={reel.title}
            className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
            style={{
              minWidth: '100%',
              minHeight: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
              width: '100%',
              height: '100%'
            }}
            loading="lazy"
            draggable={false}
            onContextMenu={(e) => e.preventDefault()}
          />
          
          {/* Subtle Edge Blur Effects - No Center Blur */}
          <div className="absolute inset-0 pointer-events-none">
            {/* Left Edge Blur - Subtle */}
            <div 
              className="absolute left-0 top-0 w-16 h-full"
              style={{
                background: 'linear-gradient(90deg, rgba(0,0,0,0.2) 0%, transparent 100%)',
                filter: 'blur(2px)'
              }}
            />
            
            {/* Right Edge Blur - Subtle */}
            <div 
              className="absolute right-0 top-0 w-16 h-full"
              style={{
                background: 'linear-gradient(270deg, rgba(0,0,0,0.2) 0%, transparent 100%)',
                filter: 'blur(2px)'
              }}
            />
          </div>
        </div>
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        
        {/* Category Badge - Instagram Stories Style */}
        <div className="absolute top-4 left-4">
          <span className="px-3 py-1.5 text-sm font-bold bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-xl backdrop-blur-lg border border-white/30 hover:scale-105 transition-all duration-300">
            {reel.category}
          </span>
        </div>
        
      </div>
      
      {/* Content Section - YouTube Shorts & Instagram Stories Style */}
      <div 
        className="absolute bottom-0 left-0 right-0 px-4 sm:px-6 bg-gradient-to-t from-black/95 via-black/70 to-transparent text-white select-none"
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          paddingTop: 16,
          paddingBottom: 'calc(env(safe-area-inset-bottom, 0px) + 56px)'
        }}
      >
        {/* Title - YouTube Shorts Style */}
        <h3 
          className="font-extrabold mb-2 line-clamp-2 leading-tight text-white drop-shadow-2xl"
          style={{ 
            userSelect: 'none', 
            WebkitUserSelect: 'none',
            fontSize: 'clamp(18px, 2.6vw, 28px)'
          }}
        >
          {reel.title}
        </h3>
        
        {/* Description - Instagram Stories Style */}
        <p 
          className="text-gray-100/95 mb-3 line-clamp-3 leading-relaxed drop-shadow-lg"
          style={{ 
            userSelect: 'none', 
            WebkitUserSelect: 'none',
            fontSize: 'clamp(13px, 1.8vw, 18px)'
          }}
        >
          {reel.content}
        </p>
        
        {/* Tags - Modern Instagram Style */}
        {reel.tags && reel.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {reel.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1.5 text-xs font-semibold bg-white/20 text-white rounded-full backdrop-blur-lg border border-white/30 hover:bg-white/30 hover:scale-105 transition-all duration-300 shadow-lg"
                style={{ userSelect: 'none', WebkitUserSelect: 'none' }}
              >
                #{tag}
              </span>
            ))}
            {reel.tags.length > 3 && (
              <span className="px-3 py-1.5 text-xs font-semibold bg-white/10 text-white/70 rounded-full backdrop-blur-lg border border-white/20">
                +{reel.tags.length - 3}
              </span>
            )}
          </div>
        )}
        
        {/* Author & Location - YouTube Shorts Style */}
        {(reel.author || reel.location) && (
          <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 text-sm text-gray-200" style={{ userSelect: 'none', WebkitUserSelect: 'none' }}>
            {reel.author && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full shadow-lg"></div>
                <span className="font-semibold text-white">{reel.author}</span>
              </div>
            )}
            {reel.author && reel.location && <span className="text-white/50 hidden sm:inline">•</span>}
            {reel.location && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-blue-400 rounded-full shadow-lg"></div>
                <span className="font-semibold text-white">{reel.location}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};