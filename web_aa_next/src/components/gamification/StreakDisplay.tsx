// StreakDisplay.tsx - Flutter streak_display.dart'tan uyarlandı

import React from 'react';
import clsx from 'clsx';

export interface StreakDisplayProps {
  streakDays: number;
  percentile?: number;
  compact?: boolean;
}

const getStreakColor = (streakDays: number): string => {
  if (streakDays >= 30) return 'purple-600';
  if (streakDays >= 14) return 'orange-700';
  if (streakDays >= 7) return 'orange-600';
  if (streakDays >= 3) return 'orange-500';
  return 'orange-400';
};

export const StreakDisplay: React.FC<StreakDisplayProps> = ({
  streakDays,
  percentile = 0,
  compact = false,
}) => {
  const colorClass = getStreakColor(streakDays);
  
  if (compact) {
    return (
      <div className="px-2.5 py-1.5 bg-black/60 rounded-full inline-flex items-center space-x-1">
        <span className="text-base">🔥</span>
        <span className="text-white text-xs font-bold">{streakDays} gün</span>
      </div>
    );
  }
  
  const milestones = [7, 14, 30, 100];
  const nextMilestone = milestones.find(m => m > streakDays) || 100;
  const previousMilestone = [...milestones].reverse().find(m => m <= streakDays) || 0;
  
  const milestoneProgress = previousMilestone > 0
    ? (streakDays - previousMilestone) / (nextMilestone - previousMilestone)
    : streakDays / nextMilestone;
  
  return (
    <div className={clsx(
      'p-4 rounded-2xl border-2',
      `bg-gradient-to-br from-${colorClass}/10 to-${colorClass}/5 border-${colorClass}/30`
    )}>
      {/* Header */}
      <div className="flex items-center space-x-2.5 mb-3">
        <span className="text-3xl">🔥</span>
        <div>
          <h3 className={`text-lg font-bold text-${colorClass}`}>
            {streakDays} Günlük Seri
          </h3>
          {percentile > 0 && (
            <p className="text-xs font-medium text-gray-600">
              Kullanıcıların %{percentile}'inden iyisin! 🎯
            </p>
          )}
        </div>
      </div>
      
      {/* Milestone progress */}
      <div>
        <p className="text-xs font-semibold text-gray-600 mb-1.5">
          Sonraki hedef: {nextMilestone} gün
        </p>
        <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full bg-${colorClass} transition-all duration-300`}
            style={{ width: `${Math.min(milestoneProgress, 1) * 100}%` }}
          />
        </div>
        <p className="text-[10px] font-medium text-gray-500 mt-1">
          {nextMilestone - streakDays} gün kaldı
        </p>
      </div>
    </div>
  );
};

export default StreakDisplay;

