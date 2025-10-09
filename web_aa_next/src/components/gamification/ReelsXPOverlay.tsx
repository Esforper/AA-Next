// ReelsXPOverlay.tsx - Flutter reels_xp_overlay.dart'tan uyarlandı

import React, { useEffect, useRef, useState } from 'react';
import clsx from 'clsx';
import { GamificationState } from '../../models/GamificationModels';

export interface ReelsXPOverlayProps {
  state: GamificationState;
}

export const ReelsXPOverlay: React.FC<ReelsXPOverlayProps> = ({ state }) => {
  const [showProgress, setShowProgress] = useState(false);
  const lastTotalXPRef = useRef(state.totalXP);
  
  // XP artışı varsa progress bar'ı göster
  useEffect(() => {
    if (state.totalXP > lastTotalXPRef.current) {
      setShowProgress(true);
      
      const timer = setTimeout(() => {
        setShowProgress(false);
      }, 3000);
      
      lastTotalXPRef.current = state.totalXP;
      return () => clearTimeout(timer);
    }
  }, [state.totalXP]);
  
  const nodeProgress = state.currentXP / 100;
  
  return (
    <div className="px-4 py-2.5 bg-gradient-to-b from-black/70 via-black/30 to-transparent pointer-events-none">
      {/* Tek satır: Level + Düğümler + Sayı + XP */}
      <div className="inline-flex items-center space-x-3 px-3 py-2 bg-black/60 rounded-full border border-white/20 pointer-events-none">
        {/* Level sayısı */}
        <div className="px-2 py-1 bg-gradient-to-r from-amber-400 to-orange-500 rounded-xl flex items-center space-x-1">
          <span className="text-sm">⚡</span>
          <span className="text-white text-sm font-bold">{state.currentLevel}</span>
        </div>
        
        {/* Düğüm görseli */}
        <div className="flex items-center space-x-0.5">
          {Array.from({ length: state.nodesInLevel }).map((_, i) => {
            const isCompleted = i < state.currentNode;
            const isCurrent = i === state.currentNode;
            
            return (
              <div
                key={i}
                className={clsx(
                  'rounded-full transition-all duration-200',
                  isCurrent ? 'w-2.5 h-2.5 ring-2 ring-amber-300' : 'w-2 h-2',
                  isCompleted
                    ? 'bg-amber-400'
                    : isCurrent
                      ? 'bg-amber-200'
                      : 'bg-white/30'
                )}
              />
            );
          })}
        </div>
        
        {/* Düğüm sayısı */}
        <span className="text-white text-xs font-semibold">
          {state.currentNode + 1}/{state.nodesInLevel}
        </span>
        
        {/* XP */}
        <span className="text-amber-300 text-xs font-bold">
          {state.currentXP} XP
        </span>
      </div>
      
      {/* Progress bar (animasyonlu açılır/kapanır) */}
      <div
        className={clsx(
          'overflow-hidden transition-all duration-300',
          showProgress ? 'max-h-16 opacity-100 mt-2' : 'max-h-0 opacity-0'
        )}
      >
        <div className="flex flex-col">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-white/90 text-[11px] font-semibold">Düğüm İlerlemesi</span>
            <span className="text-amber-300 text-[11px] font-bold">{Math.round(nodeProgress * 100)}%</span>
          </div>
          
          <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
            <div className="relative h-full">
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-300"
                style={{ width: `${nodeProgress * 100}%` }}
              >
                <div className="absolute inset-0 bg-gradient-to-b from-white/40 to-transparent" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReelsXPOverlay;

