import React from 'react';
import { ReelData } from '../models';
import { Card } from './Card';
import clsx from 'clsx';
import ReadHandleWeb from './ReadHandleWeb';

export interface ReelItemProps {
  reel: ReelData;
  isActive?: boolean;
  onPlay?: () => void;
  onImageClick?: () => void;
  onEmojiClick?: () => void;
  onSaveClick?: () => void;
  onShareClick?: () => void;
  className?: string;
  style?: React.CSSProperties;
}

export const ReelItem: React.FC<ReelItemProps> = ({
  reel,
  isActive = false,
  onPlay,
  onImageClick,
  onEmojiClick,
  onSaveClick,
  onShareClick,
  className,
  style
}) => {
  const formatRelativeTime = (iso?: string): string => {
    if (!iso) return '';
    const published = new Date(iso).getTime();
    if (Number.isNaN(published)) return '';
    const now = Date.now();
    const diffMs = Math.max(0, now - published);
    const oneMinute = 60 * 1000;
    const oneHour = 60 * oneMinute;
    const oneDay = 24 * oneHour;

    if (diffMs < oneHour) return 'Sıcak';
    if (diffMs < oneDay) {
      const hours = Math.floor(diffMs / oneHour);
      return `${hours} saat önce`;
    }
    const days = Math.floor(diffMs / oneDay);
    return `${days} gün önce`;
  };
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
  // Karakter limiti ve kısa overlay
  const fullTitle = (reel.title || '').trim();
  const maxChars = 40; // Maksimum 40 karakter
  const titleOverlayText = fullTitle.length > maxChars 
    ? fullTitle.substring(0, maxChars) + '...' 
    : fullTitle;
  const overlayWidth = Math.min(Math.max(titleOverlayText.length * 12 + 32, 180), 520); // Daha kısa max width
  const overlayHeight = 48; // Biraz daha küçük yükseklik

  // Aksiyon handlers
  const handleShare = () => {
    const url = window.location.origin + '/news/' + reel.id;
    if ((navigator as any).share) {
      (navigator as any).share({ title: reel.title, url }).catch(() => {});
    } else {
      void navigator.clipboard.writeText(url);
    }
  };

  const handleArticleOpen = () => {
    // ReadHandle'ın yukarı hareketi makale detayını açacak
    // Parent component'ten gelen callback varsa çağır
    onImageClick?.();
  };

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
        // Fill parent container, which is sized to viewport in ReelsView
        height: '100%',
        width: '100%',
        maxWidth: '100%',
        maxHeight: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Image Section - Responsive Height */}
      <div 
        className="relative w-full overflow-hidden flex-shrink-0"
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          height: '55vh', // Resim boyutunu daha da büyült
          minHeight: '50vh',
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

          {/* Transparent-text white panel under image edge - Kısa ve responsive */}
          {titleOverlayText && (
            <svg
              className="absolute left-4 z-50 max-w-[90%]" 
              style={{ bottom: '-8px' }}
              width={overlayWidth}
              height={overlayHeight}
              viewBox={`0 0 ${overlayWidth} ${overlayHeight}`}
              preserveAspectRatio="xMinYMid meet"
              aria-hidden="true"
            >
              <defs>
                <mask id={`title-overlay-mask-${reel.id}`}>
                  <rect x="0" y="0" width={overlayWidth} height={overlayHeight} fill="white" rx="12" ry="12" />
                  <text x="12" y={overlayHeight - 12} fontSize="20" fontWeight="800" fill="black">{titleOverlayText}</text>
                </mask>
              </defs>
              <rect x="0" y="0" width={overlayWidth} height={overlayHeight} rx="12" ry="12" fill="rgba(255,255,255,0.95)" mask={`url(#title-overlay-mask-${reel.id})`} />
            </svg>
          )}
        </div>
        
        {/* Category Badge - Top Left */}
        <div className="absolute top-4 left-4 z-10">
          <span className="px-3 py-1.5 text-sm font-bold bg-white/20 text-white rounded-full shadow-xl backdrop-blur-lg border border-white/30">
            {reel.category}
          </span>
        </div>
        {/* Relative Time - Top Right */}
        {!!(reel as any).published_at && (
          <div className="absolute top-4 right-4 z-10">
            <span className="px-3 py-1.5 text-sm font-bold bg-black/40 text-white rounded-full shadow-xl backdrop-blur-lg border border-white/20">
              {formatRelativeTime((reel as any).published_at)}
            </span>
          </div>
        )}
      </div>
      
      {/* Content Section - Responsive Fill */}
      <div 
        className="flex-1 flex flex-col justify-between px-4 sm:px-6 py-4 bg-black text-white md:min-h-[25vh] md:max-h-[35vh]"
        style={{ 
          userSelect: 'none', 
          WebkitUserSelect: 'none',
          minHeight: '8vh', // Mobil için küçük
          maxHeight: '15vh' // Mobil için küçük
        }}
      >
        {/* Title, Meta and First Sentence */}
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
          {!!(reel as any).published_at && (
            <div className="text-xs text-gray-300 mb-2">
              {formatRelativeTime((reel as any).published_at)}
            </div>
          )}
          
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
        
        {/* Floating Action Button - Bottom Center with ReadHandle */}
        <div className="relative flex justify-center">
          <ReadHandleWeb
            onArticle={handleArticleOpen}
            onEmoji={onEmojiClick}
            onShare={onShareClick || handleShare}
            onSave={onSaveClick}
            longPressMs={500}
          />
        </div>
      </div>
    </div>
  );
};