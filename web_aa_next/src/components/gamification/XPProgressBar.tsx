// XPProgressBar.tsx - Flutter xp_progress_bar.dart'tan uyarlandı

import React from 'react';
import clsx from 'clsx';

export interface XPProgressBarProps {
  currentXP: number;
  goalXP: number;
  compact?: boolean;
}

export const XPProgressBar: React.FC<XPProgressBarProps> = ({
  currentXP,
  goalXP,
  compact = false,
}) => {
  const progress = Math.min(currentXP / goalXP, 1);
  const isCompleted = currentXP >= goalXP;
  
  return (
    <div className="flex flex-col">
      {/* Progress bar */}
      <div
        className={clsx(
          'bg-gray-200 rounded-full overflow-hidden',
          compact ? 'h-1.5' : 'h-2'
        )}
      >
        <div className="relative h-full">
          {/* Progress fill */}
          <div
            className={clsx(
              'h-full transition-all duration-300',
              isCompleted ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-blue-400 to-blue-600'
            )}
            style={{ width: `${progress * 100}%` }}
          >
            {/* Shine effect */}
            {!compact && (
              <div className="absolute inset-0 bg-gradient-to-b from-white/30 to-transparent" />
            )}
          </div>
        </div>
      </div>
      
      {/* XP Text */}
      {!compact && (
        <div className="flex justify-between items-center mt-1.5">
          <span className={clsx(
            'text-xs font-semibold',
            isCompleted ? 'text-green-700' : 'text-gray-700'
          )}>
            {currentXP} / {goalXP} XP
          </span>
          
          {isCompleted ? (
            <div className="flex items-center space-x-1">
              <span className="text-green-600">✓</span>
              <span className="text-xs font-semibold text-green-700">Tamamlandı!</span>
            </div>
          ) : (
            <span className="text-xs font-medium text-gray-600">
              {Math.round(progress * 100)}%
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default XPProgressBar;

