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
  // Get first sentence from content (guards against non-string inputs)
  const getFirstSentence = (content: unknown) => {
    if (content == null) return '';
    let text: string;
    if (typeof content === 'string') {
      text = content;
    } else if (Array.isArray(content)) {
      // Join array items with space
      text = content.map((item) => (typeof item === 'string' ? item : String(item))).join(' ');
    } else if (typeof content === 'object') {
      // Try common fields, fallback to stringified object
      const anyContent: any = content as any;
      text =
        (typeof anyContent.text === 'string' && anyContent.text) ||
        (typeof anyContent.content === 'string' && anyContent.content) ||
        String(anyContent);
    } else {
      text = String(content);
    }

    const sentences = text.split(/[.!?]+/);
    const first = sentences[0]?.trim();
    return first && first.length > 0 ? first : (text.substring(0, 100) + '...');
  };

  // Title overlay sizing for transparent-text white panel under image
  const titleOverlayText = (reel.title || '').trim();
  const overlayWidth = Math.min(Math.max(titleOverlayText.length * 13 + 32, 200), 820);
  const overlayHeight = 52;

  return (
    <div
      className={clsx(
        'relative w-full h-full flex flex-col bg-black overflow-hidden select-none',
        {
          'ring-2 ring-blue-500': isActive
        },
        className
      )}
      style={{
        ...style,
        // Responsive dimensions - no fixed heights
        height: '100%',
        width: '100%',
        maxWidth: '100%',
        maxHeight: '100%',
        minHeight: '100vh', // Full viewport height
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Image Section - Responsive Height */}
      <div 
        className="relative w-full cursor-pointer overflow-hidden flex-shrink-0"
        onClick={onImageClick}
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          height: '50vh', // Daha az yükseklik - dikdörtgen
          minHeight: '40vh',
          maxHeight: '60vh'
        }}
      >
        {/* Main Image - Cinematic Bleed Effect */}
        <div className="relative w-full h-full flex items-center justify-center">
          <img
            src={reel.main_image}
            alt={reel.title}
            className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
            style={{
              minWidth: '130%', // Daha geniş bleed effect
              minHeight: '130%',
              objectFit: 'cover',
              objectPosition: 'center',
              transform: 'scale(1.15)' // Daha geniş cinematic overflow
            }}
            loading="lazy"
            draggable={false}
            onContextMenu={(e) => e.preventDefault()}
          />
          
          {/* Cinematic Vignette for Bleed Effect */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-black/20" />

          {/* Transparent-text white panel under image edge */}
          {titleOverlayText && (
            <svg
              className="absolute left-4 z-50"
              style={{ bottom: '-10px' }}
              width={overlayWidth}
              height={overlayHeight}
              viewBox={`0 0 ${overlayWidth} ${overlayHeight}`}
              aria-hidden="true"
            >
              <defs>
                <mask id={`title-overlay-mask-${reel.id}`}>
                  <rect x="0" y="0" width={overlayWidth} height={overlayHeight} fill="white" rx="14" ry="14" />
                  <text x="12" y={overlayHeight - 14} fontSize="22" fontWeight="800" fill="black">{titleOverlayText}</text>
                </mask>
              </defs>
              <rect x="0" y="0" width={overlayWidth} height={overlayHeight} rx="14" ry="14" fill="rgba(255,255,255,0.95)" mask={`url(#title-overlay-mask-${reel.id})`} />
            </svg>
          )}
        </div>
        
        {/* Category Badge - Top Left */}
        <div className="absolute top-4 left-4 z-10">
          <span className="px-3 py-1.5 text-sm font-bold bg-white/20 text-white rounded-full shadow-xl backdrop-blur-lg border border-white/30">
            {reel.category}
          </span>
        </div>
      </div>
      
      {/* Content Section - Responsive Fill */}
      <div 
        className="flex-1 flex flex-col justify-between px-4 sm:px-6 py-4 bg-black text-white"
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          minHeight: '30vh', // Daha fazla alan yazılar için
          maxHeight: '40vh' // Daha fazla alan yazılar için
        }}
      >
        {/* Title and First Sentence */}
        <div className="flex-1 flex flex-col justify-center">
          <h3 
            className="font-bold mb-2 line-clamp-2 leading-tight text-white"
            style={{ 
              userSelect: 'none', 
              WebkitUserSelect: 'none',
              fontSize: 'clamp(16px, 2.5vw, 24px)'
            }}
          >
            {reel.title}
          </h3>
          
          <p 
            className="text-gray-200 line-clamp-2 leading-relaxed mb-3"
            style={{ 
              userSelect: 'none', 
              WebkitUserSelect: 'none',
              fontSize: 'clamp(14px, 1.8vw, 18px)'
            }}
          >
            {getFirstSentence(reel.content)}
          </p>
        </div>
        
        {/* Floating Action Button - Bottom Center */}
        <div className="flex justify-center">
          <button
            onClick={onPlay}
            className="bg-white/20 hover:bg-white/30 backdrop-blur-lg border border-white/30 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110 shadow-lg"
            style={{ 
              userSelect: 'none', 
              WebkitUserSelect: 'none',
              width: 'clamp(48px, 8vw, 64px)',
              height: 'clamp(48px, 8vw, 64px)'
            }}
          >
            <svg 
              className="text-white" 
              fill="currentColor" 
              viewBox="0 0 24 24"
              style={{
                width: 'clamp(20px, 4vw, 28px)',
                height: 'clamp(20px, 4vw, 28px)',
                marginLeft: '2px'
              }}
            >
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};