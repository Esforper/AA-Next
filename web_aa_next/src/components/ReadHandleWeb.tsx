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
    <div ref={containerRef} className="relative select-none">
      {/* Dış daire - scale ve blur animasyonu */}
      <div
        className={clsx(
          'absolute inset-0 flex items-center justify-center pointer-events-none',
          expanded ? 'opacity-100 scale-100' : 'opacity-0 scale-0'
        )}
        style={{
          transition: 'all 250ms cubic-bezier(0.34, 1.56, 0.64, 1)',
          transformOrigin: 'center'
        }}
        aria-hidden={!expanded}
      >
        <div
          className="rounded-full bg-black/70 backdrop-blur-md shadow-xl ring-1 ring-white/20 grid place-items-center relative"
          style={{ width: trackSize, height: trackSize }}
        >
          {/* Yön göstergeleri */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="absolute top-4 text-white/80 text-lg">
              <span className="material-icons">article</span>
            </div>
            <div className="absolute right-4 text-white/80 text-lg">
              <span className="material-icons">emoji_emotions</span>
            </div>
            <div className="absolute bottom-4 text-white/80 text-lg">
              <span className="material-icons">share</span>
            </div>
            <div className="absolute left-4 text-white/80 text-lg">
              <span className="material-icons">bookmark</span>
            </div>
          </div>
        </div>
      </div>

      {/* Çekirdek buton - transform ve scale animasyonu */}
      <button
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        className={clsx(
          'bg-white/20 hover:bg-white/30 backdrop-blur-lg border border-white/30 rounded-full',
          'flex items-center justify-center shadow-lg transition-all duration-200',
          pressed && 'scale-110 bg-white/40'
        )}
        style={{
          width: knobSize,
          height: knobSize,
          transform: `translate(${pos.x}px, ${pos.y}px)`,
          transition: pressed ? 'none' : 'all 250ms cubic-bezier(0.34, 1.56, 0.64, 1)'
        }}
        aria-label="Reels Aksiyon Butonu"
      >
        <span className="material-icons text-white">drag_indicator</span>
      </button>
    </div>
  );
};

export default ReadHandleWeb;
