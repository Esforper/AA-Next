// FloatingXP.tsx - Flutter floating_xp.dart'tan uyarlandı

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

export interface FloatingXPProps {
  xpAmount: number;
  source?: 'reel_watched' | 'emoji_given' | 'detail_read' | 'share_given';
  position?: { x: number; y: number };
  onComplete?: () => void;
}

const getColorForSource = (source?: string): string => {
  switch (source) {
    case 'reel_watched': return '#2563eb'; // blue-600
    case 'emoji_given': return '#ec4899'; // pink-500
    case 'detail_read': return '#9333ea'; // purple-600
    case 'share_given': return '#16a34a'; // green-600
    default: return '#2563eb';
  }
};

const getIconForSource = (source?: string): string => {
  switch (source) {
    case 'reel_watched': return '👀';
    case 'emoji_given': return '❤️';
    case 'detail_read': return '📖';
    case 'share_given': return '🔗';
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
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, 1500);
    
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
        animation: 'floatUpFade 1.5s ease-out forwards',
      }}
    >
      <div
        className="px-4 py-2 rounded-full shadow-lg flex items-center space-x-2"
        style={{
          background: `linear-gradient(135deg, ${color}, ${color}dd)`,
          animation: 'scaleBounce 1.5s ease-out forwards',
        }}
      >
        <span className="text-xl">{icon}</span>
        <span className="text-white font-bold text-lg">+{xpAmount} XP</span>
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

// ============ OVERLAY MANAGER ============

let currentOverlay: (() => void) | null = null;

export class FloatingXPOverlay {
  static show(params: FloatingXPProps) {
    this.remove();
    
    const container = document.createElement('div');
    document.body.appendChild(container);
    
    const { createRoot } = require('react-dom/client');
    const root = createRoot(container);
    
    root.render(
      <FloatingXP
        {...params}
        onComplete={() => {
          params.onComplete?.();
          this.remove();
        }}
      />
    );
    
    currentOverlay = () => {
      root.unmount();
      container.remove();
    };
  }
  
  static remove() {
    if (currentOverlay) {
      currentOverlay();
      currentOverlay = null;
    }
  }
}

