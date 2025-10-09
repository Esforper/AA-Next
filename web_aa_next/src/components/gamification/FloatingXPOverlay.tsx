import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { createRoot } from 'react-dom/client';

interface FloatingXPProps {
  xpAmount: number;
  source?: 'reel_watched' | 'emoji_given' | 'detail_read' | 'share_given' | 'level_up';
  position?: { x: number; y: number };
  onComplete?: () => void;
}

interface FloatingXPOverlayStatic {
  show: (props: Omit<FloatingXPProps, 'onComplete'>) => void;
}

const getColorForSource = (source?: string) => {
  // Flutter ile aynı renkler
  switch (source) {
    case 'reel_watched': return '#2563EB'; // blue-600
    case 'emoji_given': return '#EC4899';  // pink-500
    case 'detail_read': return '#9333EA'; // purple-600
    case 'share_given': return '#16A34A'; // green-600
    case 'level_up': return '#F59E0B';    // amber-500
    default: return '#2563EB';            // blue-600
  }
};

const getIconForSource = (source?: string) => {
  switch (source) {
    case 'reel_watched': return '👀';
    case 'emoji_given': return '❤️';
    case 'detail_read': return '📖';
    case 'share_given': return '🔗';
    case 'level_up': return '🎉';
    default: return '⚡';
  }
};

export const FloatingXP: React.FC<FloatingXPProps> = ({
  xpAmount,
  source,
  position,
  onComplete,
}) => {
  const [visible, setVisible] = useState(true);
  const DURATION_MS = 500; // extend animation duration to 5s
  const durationSec = DURATION_MS / 600;
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, DURATION_MS);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  if (!visible) return null;
  
  const color = getColorForSource(source);
  const icon = getIconForSource(source);
  const defaultPos = { x: window.innerWidth / 2 - 60, y: window.innerHeight / 2 - 100 };
  const pos = position || defaultPos;
  
  return createPortal(
    <div
      className="fixed pointer-events-none z-[9999]"
      style={{
        left: pos.x,
        top: pos.y,
        animation: `floatUpFade ${durationSec}s ease-out forwards`,
      }}
    >
      <div
        className="px-4 py-2 rounded-full shadow-lg flex items-center space-x-2"
        style={{
          background: `linear-gradient(135deg, ${color}, ${color}dd)`,
          animation: `scaleBounce ${durationSec}s ease-out forwards`,
        }}
      >
        <span className="text-xl">{icon}</span>
        {xpAmount > 0 ? (
          <span className="text-white font-bold text-lg">+{xpAmount} XP</span>
        ) : (
          <span className="text-white font-bold text-lg">Level Up!</span>
        )}
      </div>
      
      <style>{`
        @keyframes floatUpFade {
          0% { transform: translateY(0); opacity: 1; }
          50% { transform: translateY(-80px); opacity: 1; }
          100% { transform: translateY(-100px); opacity: 0; }
        }
        @keyframes scaleBounce {
          0% { transform: scale(0); }
          25% { transform: scale(1.3); }
          40% { transform: scale(1); }
          100% { transform: scale(1); }
        }
      `}</style>
    </div>,
    document.body
  );
};

// Static show method implementation
let currentOverlay: (() => void) | null = null;

export const FloatingXPOverlay = Object.assign(FloatingXP, {
  show: (props: Omit<FloatingXPProps, 'onComplete'>) => {
    if (currentOverlay) {
      currentOverlay();
    }

    const container = document.createElement('div');
    document.body.appendChild(container);

    const cleanup = () => {
      if (document.body.contains(container)) {
        document.body.removeChild(container);
      }
      if (currentOverlay === cleanup) {
        currentOverlay = null;
      }
    };

    currentOverlay = cleanup;

    const root = createRoot(container);
    root.render(<FloatingXP {...props} onComplete={cleanup} />);
  }
}) as React.FC<FloatingXPProps> & FloatingXPOverlayStatic;
