// DailyProgressCard.tsx - Flutter daily_progress_card.dart'tan uyarlandı

import React from 'react';
import clsx from 'clsx';
import XPProgressBar from './XPProgressBar';

export interface DailyProgressCardProps {
  currentXP: number;
  goalXP: number;
  streakDays: number;
  percentile?: number;
  goalCompleted: boolean;
  onStartReels?: () => void;
}

const getMotivationalText = (progress: number, goalCompleted: boolean): string => {
  if (goalCompleted) return "Streak'in devam ediyor! 🎊";
  if (progress >= 0.8) return 'Neredeyse tamam! Son bir haber daha 💪';
  if (progress >= 0.5) return 'Yarı yoldasın, devam et! 🚀';
  if (progress >= 0.2) return 'İyi başladın, momentum kazanıyorsun! ⭐';
  return 'Bugün henüz başlamadın, hadi başlayalım! 🌟';
};

export const DailyProgressCard: React.FC<DailyProgressCardProps> = ({
  currentXP,
  goalXP,
  streakDays,
  percentile = 0,
  goalCompleted,
  onStartReels,
}) => {
  const progress = currentXP / goalXP;
  
  return (
    <div className={clsx(
      'm-4 rounded-2xl shadow-lg',
      goalCompleted
        ? 'bg-gradient-to-br from-green-50 to-teal-50'
        : 'bg-gradient-to-br from-blue-50 to-indigo-50'
    )}>
      {/* Header */}
      <div className="p-5 pb-3">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-2xl">{goalCompleted ? '🎉' : '📊'}</span>
              <h3 className={clsx(
                'text-lg font-bold',
                goalCompleted ? 'text-green-800' : 'text-indigo-800'
              )}>
                {goalCompleted ? 'Günlük Hedef Tamamlandı!' : 'Günlük İlerleme'}
              </h3>
            </div>
            <p className="text-xs font-medium text-gray-600">
              {getMotivationalText(progress, goalCompleted)}
            </p>
          </div>
        </div>
      </div>
      
      {/* XP Progress */}
      <div className="px-5 pb-4">
        <XPProgressBar currentXP={currentXP} goalXP={goalXP} />
      </div>
      
      {/* Divider */}
      <div className="px-5">
        <div className="border-t border-gray-300" />
      </div>
      
      {/* Stats */}
      <div className="px-5 py-3 flex">
        <div className="flex-1 text-center">
          <span className="text-2xl block">🔥</span>
          <p className="text-[11px] font-medium text-gray-600 mt-1">Streak</p>
          <p className="text-sm font-bold text-orange-600">{streakDays} gün</p>
        </div>
        
        <div className="w-px bg-gray-300" />
        
        <div className="flex-1 text-center">
          <span className="text-2xl block">🎯</span>
          <p className="text-[11px] font-medium text-gray-600 mt-1">Sıralama</p>
          <p className="text-sm font-bold text-purple-600">
            {percentile > 0 ? `Top %${percentile}` : '-'}
          </p>
        </div>
      </div>
      
      {/* Action button */}
      <div className="px-5 pb-5">
        {!goalCompleted ? (
          <button
            onClick={onStartReels}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition-colors"
          >
            <span>Haber İzlemeye Başla</span>
            <span className="text-lg">→</span>
          </button>
        ) : (
          <div className="w-full bg-green-100 border-2 border-green-300 py-3.5 rounded-xl flex items-center justify-center space-x-2">
            <span className="text-green-700 text-xl">✓</span>
            <span className="text-sm font-bold text-green-800">Harika! Yarın tekrar gel</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DailyProgressCard;

