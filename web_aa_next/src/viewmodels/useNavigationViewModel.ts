import { useState, useCallback } from 'react';
import { TabItem } from '../models';

export interface NavigationViewModel {
  activeTab: string;
  tabs: TabItem[];
  
  // Actions
  setActiveTab: (tabId: string) => void;
}

export const useNavigationViewModel = (): NavigationViewModel => {
  const [activeTab, setActiveTabState] = useState('home');

  const tabs: TabItem[] = [
    {
      id: 'home',
      name: 'index',
      title: 'Haberler',
      icon: 'newspaper-outline',
      iconFocused: 'newspaper'
    },
    {
      id: 'reels',
      name: 'reels',
      title: 'Reels',
      icon: 'play-circle-outline',
      iconFocused: 'play-circle'
    },
    {
      id: 'games',
      name: 'games',
      title: 'Oyunlar',
      icon: 'game-controller-outline',
      iconFocused: 'game-controller'
    },
    {
      id: 'profile',
      name: 'profile',
      title: 'Profil',
      icon: 'person-outline',
      iconFocused: 'person'
    }
  ];

  const setActiveTab = useCallback((tabId: string) => {
    setActiveTabState(tabId);
  }, []);

  return {
    activeTab,
    tabs,
    setActiveTab
  };
};