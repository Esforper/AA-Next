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
    // Simple icon mapping - in a real app you'd use react-icons or similar
    const iconMap: Record<string, string> = {
      'newspaper': '📰',
      'newspaper-outline': '📰',
      'play-circle': '▶️',
      'play-circle-outline': '▶️',
      'game-controller': '🎮',
      'game-controller-outline': '🎮',
      'person': '👤',
      'person-outline': '👤'
    };
    
    return iconMap[iconName] || '•';
  };

  return (
    <div className={clsx(
      'fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50',
      className
    )}>
      <div className="flex items-center justify-around py-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const icon = getIconComponent(isActive ? tab.iconFocused : tab.icon);
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={clsx(
                'flex flex-col items-center justify-center py-2 px-3 min-w-0 flex-1',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset',
                {
                  'text-blue-600': isActive,
                  'text-gray-500 hover:text-gray-700': !isActive
                }
              )}
            >
              <span className="text-xl mb-1">{icon}</span>
              <span className={clsx(
                'text-xs font-medium truncate',
                {
                  'text-blue-600': isActive,
                  'text-gray-500': !isActive
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