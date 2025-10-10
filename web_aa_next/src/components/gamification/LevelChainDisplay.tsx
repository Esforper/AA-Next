// LevelChainDisplay.tsx - Flutter level_chain_display.dart'tan uyarlandı

import React from 'react';
import clsx from 'clsx';

export interface LevelChainDisplayProps {
  currentLevel: number;
  currentNode: number;
  totalNodes: number;
  currentXP: number;
  compact?: boolean;
}

export const LevelChainDisplay: React.FC<LevelChainDisplayProps> = ({
  currentLevel,
  currentNode,
  totalNodes,
  currentXP,
  compact = false,
}) => {
  const levelProgress = totalNodes > 0 ? currentNode / totalNodes : 0;
  const nodeProgress = currentXP / 100;
  
  if (compact) {
    return (
      <div className="px-2.5 py-1.5 bg-black/60 rounded-full inline-flex items-center space-x-1">
        <span className="text-sm">⚡</span>
        <span className="text-white text-xs font-bold">Lv {currentLevel}</span>
      </div>
    );
  }
  
  const remainingNodes = totalNodes - currentNode;
  const remainingXP = (remainingNodes * 100) - currentXP;
  
  return (
    <div className="p-5 bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border-2 border-amber-200 shadow-lg">
      {/* Header */}
      <div className="flex justify-between items-center mb-5">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl shadow-md">
            <span className="text-2xl">⚡</span>
          </div>
          <div>
            <h3 className="text-xl font-bold text-orange-900">Level {currentLevel}</h3>
            <p className="text-xs font-semibold text-gray-600">{currentNode + 1} / {totalNodes} düğüm</p>
          </div>
        </div>
        
        <div className="px-3.5 py-2 bg-white rounded-xl border-2 border-amber-300">
          <span className="text-base font-bold text-orange-700">{Math.round(levelProgress * 100)}%</span>
        </div>
      </div>
      
      {/* Chain visualization */}
      <div className="flex flex-wrap gap-2 mb-4">
        {Array.from({ length: totalNodes }).map((_, i) => {
          const isCompleted = i < currentNode;
          const isCurrent = i === currentNode;
          
          return (
            <React.Fragment key={i}>
              {/* Node */}
              <div
                className={clsx(
                  'w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300',
                  isCompleted || isCurrent
                    ? 'bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg'
                    : 'bg-gray-300',
                  isCurrent && 'ring-3 ring-orange-700'
                )}
              >
                {isCompleted && <span className="text-white text-base">✓</span>}
                {isCurrent && (
                  <svg className="w-6 h-6 animate-spin">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="white"
                      strokeWidth="3"
                      fill="none"
                    />
                    <circle
                      className="opacity-75"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="white"
                      strokeWidth="3"
                      fill="none"
                      strokeDasharray={`${nodeProgress * 62.8} 62.8`}
                    />
                  </svg>
                )}
                {!isCompleted && !isCurrent && <div className="w-3.5 h-3.5 rounded-full bg-gray-400" />}
              </div>
              
              {/* Connector */}
              {i < totalNodes - 1 && (
                <div className={clsx(
                  'w-4 h-1 rounded-sm my-4',
                  i < currentNode ? 'bg-gradient-to-r from-amber-400 to-orange-500' : 'bg-gray-300'
                )} />
              )}
            </React.Fragment>
          );
        })}
      </div>
      
      {/* Level progress bar */}
      <div className="mb-3">
        <p className="text-xs font-semibold text-gray-700 mb-2">Level İlerlemesi</p>
        <div className="h-2.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-300"
            style={{ width: `${levelProgress * 100}%` }}
          >
            <div className="h-full bg-gradient-to-b from-white/40 to-transparent" />
          </div>
        </div>
      </div>
      
      {/* Info text */}
      <div className="flex justify-between text-xs">
        <span className="font-medium text-gray-600">Sonraki level: {remainingNodes} düğüm</span>
        <span className="font-bold text-orange-700">{remainingXP} XP kaldı</span>
      </div>
    </div>
  );
};

export default LevelChainDisplay;

