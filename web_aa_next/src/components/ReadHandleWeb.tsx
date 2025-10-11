import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import clsx from 'clsx';

export type HandleAction = 'up' | 'right' | 'down' | 'left' | 'none';

export interface ReadHandleWebProps {
  onArticle?: () => void;      // up
  onEmoji?: () => void;        // right
  onShare?: () => void;        // down
  onSave?: () => void;         // left
  longPressMs?: number;        // genişleme eşiği
  trackSize?: number;          // dış daire çapı
  knobSize?: number;           // merkez topuz çapı
  threshold?: number;          // yön algı eşik px
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

export const ReadHandleWeb: React.FC<ReadHandleWebProps> = ({
  onArticle,
  onEmoji,
  onShare,
  onSave,
  longPressMs = 500,
  trackSize = 160,
  knobSize = 56,
  threshold = 35,
}) => {
  const [pressed, setPressed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const timerRef = useRef<number | null>(null);
  const longPressedRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startRef = useRef<{ x: number; y: number } | null>(null);
  const animatingRef = useRef(false);

  const maxX = useMemo(() => (trackSize / 2) - (knobSize / 2) - 8, [trackSize, knobSize]);
  const maxY = maxX;

  const clearTimer = useCallback(() => {
    if (timerRef.current != null) {
      window.clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (animatingRef.current) return;

    longPressedRef.current = false;
    setPressed(true);
    startRef.current = { x: e.clientX, y: e.clientY };
    clearTimer();

    timerRef.current = window.setTimeout(() => {
      longPressedRef.current = true;
      setExpanded(true);
    }, longPressMs);
  }, [longPressMs, clearTimer]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!pressed || !startRef.current || animatingRef.current) return;

    const rawDx = e.clientX - startRef.current.x;
    const rawDy = e.clientY - startRef.current.y;
    const dx = clamp(rawDx, -maxX, maxX);
    const dy = clamp(rawDy, -maxY, maxY);
    setPos({ x: dx, y: dy });
  }, [pressed, maxX, maxY]);

  const detectDirection = useCallback((): HandleAction => {
    const dx = Math.abs(pos.x);
    const dy = Math.abs(pos.y);
    if (dx > dy && dx > threshold) {
      return pos.x > 0 ? 'right' : 'left';
    } else if (dy > dx && dy > threshold) {
      return pos.y > 0 ? 'down' : 'up';
    }
    return 'none';
  }, [pos.x, pos.y, threshold]);

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (animatingRef.current) return;

    clearTimer();
    const wasLong = longPressedRef.current;
    setPressed(false);

    if (wasLong && expanded) {
      const dir = detectDirection();
      animatingRef.current = true;

      // Önce animasyon, sonra aksiyon
      requestAnimationFrame(() => {
        setExpanded(false);
        setPos({ x: 0, y: 0 });

        setTimeout(() => {
          switch (dir) {
            case 'up':
              onArticle?.();
              break;
            case 'right':
              onEmoji?.();
              break;
            case 'down':
              onShare?.();
              break;
            case 'left':
              onSave?.();
              break;
          }
          animatingRef.current = false;
        }, 250); // Animasyon süresi
      });
    } else {
      setExpanded(false);
      setPos({ x: 0, y: 0 });
    }

    startRef.current = null;
  }, [clearTimer, expanded, detectDirection, onArticle, onEmoji, onShare, onSave]);

  useEffect(() => () => clearTimer(), [clearTimer]);

  return (
    <div 
      ref={containerRef} 
      className="relative select-none flex items-center justify-center"
      style={{ width: trackSize, height: trackSize }}
    >
      {/* Dış daire - AA Mavi arka plan - TAM YUVARLAK */}
      <div
        className={clsx(
          'absolute pointer-events-none',
          expanded ? 'opacity-100 scale-100' : 'opacity-0 scale-0'
        )}
        style={{
          transition: 'all 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
          transformOrigin: 'center',
          top: 0,
          left: 0
        }}
        aria-hidden={!expanded}
      >
        <div
          className="rounded-full bg-[#003D82] shadow-2xl grid place-items-center relative"
          style={{ 
            width: trackSize, 
            height: trackSize,
            backgroundColor: 'rgba(0, 61, 130, 0.85)',
            boxShadow: '0 4px 12px rgba(0, 61, 130, 0.4)'
          }}
        >
          {/* Yön göstergeleri - SVG Icons (Beyaz) */}
          <div className="absolute inset-0 flex items-center justify-center">
            {/* Article icon - Up */}
            <div className="absolute top-4 text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            {/* Emoji icon - Right */}
            <div className="absolute right-4 text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            {/* Share icon - Down */}
            <div className="absolute bottom-4 text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </div>
            {/* Bookmark icon - Left */}
            <div className="absolute left-4 text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Çekirdek buton - AA Logosu */}
      <button
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        className={clsx(
          'bg-[#003D82] hover:bg-[#00468f] rounded-xl',
          'flex items-center justify-center shadow-lg transition-all duration-200',
          pressed && 'scale-110 brightness-110'
        )}
        style={{
          width: knobSize,
          height: knobSize,
          transform: `translate(${pos.x}px, ${pos.y}px)`,
          transition: pressed ? 'none' : 'all 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
          boxShadow: pressed 
            ? '0 12px 20px rgba(0, 0, 0, 0.3)' 
            : '0 6px 12px rgba(0, 0, 0, 0.3)'
        }}
        aria-label="Reels Aksiyon Butonu"
      >
        {/* AA Logosu - Beyaz */}
        <span className="text-white text-xl font-bold tracking-wider">
          AA
        </span>
      </button>
    </div>
  );
};

export default ReadHandleWeb;
