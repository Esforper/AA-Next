import React from 'react';
import { TabItem } from '../models';
import clsx from 'clsx';

export interface TabBarProps {
  tabs: TabItem[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}

export const TabBar: React.FC<TabBarProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className
}) => {
  const getIconComponent = (iconName: string) => {
    // Enhanced icon mapping with better visual distinction
    const iconMap: Record<string, string> = {
      'newspaper': '📰',
      'newspaper-outline': '📰',
      'play-circle': '🎬',
      'play-circle-outline': '▶️',
      'game-controller': '🎮',
      'game-controller-outline': '🎮',
      'person': '👤',
      'person-outline': '👤'
    };
    
    return iconMap[iconName] || '•';
  };

  return (
    <div 
      className={clsx(
        'fixed bottom-0 left-0 right-0 z-50 shadow-lg',
        'safe-area-pb', // iOS safe area support
        className
      )}
      style={{ backgroundColor: '#005799' }}
    >
      <div className="flex items-center justify-around py-3 px-2 sm:px-4">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const icon = getIconComponent(isActive ? tab.iconFocused : tab.icon);
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={clsx(
                'flex flex-col items-center justify-center py-2 px-3 min-w-0 flex-1 rounded-lg',
                'transition-all duration-200 ease-in-out',
                'focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-inset',
                'active:scale-95', // Touch feedback
                {
                  'bg-white/20 text-white scale-105 shadow-md': isActive,
                  'text-white/70 hover:text-white hover:bg-white/10 hover:scale-105': !isActive
                }
              )}
            >
              <span className={clsx(
                'text-lg sm:text-xl mb-1 transition-all duration-300',
                isActive ? 'animate-bounce' : 'hover:scale-110'
              )}>
                {icon}
              </span>
              <span className={clsx(
                'text-xs font-medium truncate transition-colors duration-200',
                'sm:text-sm', // Larger text on desktop
                {
                  'text-white font-semibold': isActive,
                  'text-white/70': !isActive
                }
              )}>
                {tab.title}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};