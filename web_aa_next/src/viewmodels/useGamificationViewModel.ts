import { useCallback, useEffect, useRef, useState } from 'react';
import { GamificationApi } from '../api/gamificationApi';
import { GamificationState, AddXpRequest } from '../models/GamificationModels';
import { FloatingXPOverlay } from '../components/gamification/FloatingXPOverlay';

const getStorageKey = (userId: string) => `gamification_state_${userId}_v2`;
const getEmojiTrackingKey = (userId: string) => `emoji_tracking_${userId}`;
const getShareTrackingKey = (userId: string) => `share_tracking_${userId}`;

const defaultState: GamificationState = {
  currentXP: 0,
  dailyXPGoal: 300,
  totalXP: 0,
  currentLevel: 1,
  xpToNextLevel: 100, // İlk seviye için 100 XP gerekli
  currentNode: 0,
  nodesInLevel: 2,
  currentStreak: 0,
  lastActivityDate: null,
  streakPercentile: 0,
  reelsWatchedToday: 0,
  emojisGivenToday: 0,
  detailsReadToday: 0,
  sharesGivenToday: 0,
  xpEarnedToday: 0,
  dailyGoalCompleted: false,
};

// Level formülü: Flutter'daki _getNodesForLevel
const getNodesForLevel = (level: number): number => {
  if (level <= 5) return 2;
  if (level <= 10) return 4;
  if (level <= 15) return 6;
  return 8; // 16+
};

// XP hesaplama: Her seviye için gereken toplam XP
const getRequiredXPForLevel = (level: number): number => {
  return level * 100; // Basit formül: her seviye 100 XP
};

const calculatePercentile = (streak: number): number => {
  if (streak >= 30) return 95;
  if (streak >= 14) return 85;
  if (streak >= 7) return 70;
  if (streak >= 3) return 50;
  return 30;
};

export function useGamificationViewModel(userId: string = 'web_user') {
  const [state, setState] = useState<GamificationState>(defaultState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const emojiGivenRef = useRef<Set<string>>(new Set());
  const shareGivenRef = useRef<Set<string>>(new Set());
  const lastActionTimestampRef = useRef<Record<string, number>>({});

  // Computed properties
  const dailyProgress = state.xpEarnedToday / state.dailyXPGoal;
  const nodeProgress = state.currentXP / 100;
  const levelProgress = state.nodesInLevel > 0 ? state.currentNode / state.nodesInLevel : 0;
  const xpToNextLevel = getRequiredXPForLevel(state.currentLevel + 1) - state.totalXP;

  // ============ STORAGE FUNCTIONS ============
  
  const BACKUP_INTERVAL = 5000; // 5 saniyede bir yedekle
  const SYNC_INTERVAL = 30000; // 30 saniyede bir senkronize et

  const saveToStorage = useCallback((nextState: GamificationState) => {
    try {
      localStorage.setItem(getStorageKey(userId), JSON.stringify(nextState));
      localStorage.setItem(getEmojiTrackingKey(userId), JSON.stringify(Array.from(emojiGivenRef.current)));
      localStorage.setItem(getShareTrackingKey(userId), JSON.stringify(Array.from(shareGivenRef.current)));
      localStorage.setItem(`reel_interactions_${userId}`, JSON.stringify(reelInteractionsRef.current));
    } catch (e) {
      console.error('❌ Storage kayıt hatası:', e);
    }
  }, [userId]);

  const loadFromStorage = useCallback(async () => {
    try {
      // Önce localStorage'dan yükle
      const stateStr = localStorage.getItem(getStorageKey(userId));
      const emojiStr = localStorage.getItem(getEmojiTrackingKey(userId));
      const shareStr = localStorage.getItem(getShareTrackingKey(userId));

      // Anonim kullanıcıdan giriş yapılmış kullanıcıya geçiş kontrolü
      const oldAnonymousId = localStorage.getItem('anonymous_id');
      if (userId !== 'web_user' && oldAnonymousId) {
        const oldStateStr = localStorage.getItem(getStorageKey(oldAnonymousId));
        if (oldStateStr) {
          const oldState = JSON.parse(oldStateStr);
          // Eski anonim state'i yeni kullanıcıya aktar
          const mergedState = {
            ...oldState,
            userId: userId,
          };
          setState(mergedState);
          saveToStorage(mergedState);
          // Eski anonim veriyi temizle
          localStorage.removeItem(getStorageKey(oldAnonymousId));
          localStorage.removeItem(getEmojiTrackingKey(oldAnonymousId));
          localStorage.removeItem(getShareTrackingKey(oldAnonymousId));
          localStorage.removeItem('anonymous_id');
          return;
        }
      }

      // Normal yükleme
      if (stateStr) {
        setState(JSON.parse(stateStr));
      } else {
        // Backend'den son state'i al
        try {
          const res = await GamificationApi.getCurrentLevel(userId);
          if (res?.success && res.data) {
            setState(res.data);
          } else {
            setState(defaultState);
          }
        } catch {
          setState(defaultState);
        }
      }
      
      // Emoji ve share tracking yükle
      if (emojiStr) {
        const data = JSON.parse(emojiStr) as string[];
        emojiGivenRef.current = new Set(data);
      }
      if (shareStr) {
        const data = JSON.parse(shareStr) as string[];
        shareGivenRef.current = new Set(data);
      }
      
      // Reel interactions yükle
      const interactionsStr = localStorage.getItem(`reel_interactions_${userId}`);
      if (interactionsStr) {
        reelInteractionsRef.current = JSON.parse(interactionsStr);
      }
      
      console.log(`✅ Gamification storage yüklendi (${userId})`);
    } catch (e) {
      console.error('❌ Storage yükleme hatası:', e);
      setState(defaultState);
    }
  }, [userId, saveToStorage]);

  const checkDailyReset = useCallback(() => {
    if (!state.lastActivityDate) return;
    
    const now = new Date();
    const last = new Date(state.lastActivityDate);
    
    const isNewDay = now.getDate() !== last.getDate() ||
                     now.getMonth() !== last.getMonth() ||
                     now.getFullYear() !== last.getFullYear();
    
    if (isNewDay) {
      performDailyReset();
    }
  }, [state.lastActivityDate]);

  const performDailyReset = useCallback(() => {
    const newStreak = state.dailyGoalCompleted ? state.currentStreak + 1 : 0;
    const percentile = calculatePercentile(newStreak);
    
    const nextState: GamificationState = {
      ...state,
      xpEarnedToday: 0,
      reelsWatchedToday: 0,
      emojisGivenToday: 0,
      detailsReadToday: 0,
      sharesGivenToday: 0,
      dailyGoalCompleted: false,
      currentStreak: newStreak,
      lastActivityDate: new Date().toISOString(),
      streakPercentile: percentile,
    };
    
    // Flutter'daki gibi tüm tracking'leri temizle
    emojiGivenRef.current.clear();
    shareGivenRef.current.clear();
    reelInteractionsRef.current = {}; // Günlük reset: Tüm reel interactions temizle
    
    setState(nextState);
    saveToStorage(nextState);
    console.log('📅 Günlük reset yapıldı. Streak:', newStreak);
  }, [state, saveToStorage]);

  // ============ INITIALIZATION ============
  
  useEffect(() => {
    // userId değiştiğinde state'i yeniden yükle
    loadFromStorage();
    checkDailyReset();
  }, [userId, loadFromStorage, checkDailyReset]);

  // Otomatik yedekleme
  useEffect(() => {
    const backupTimer = setInterval(() => {
      const currentState = state;
      try {
        localStorage.setItem(getStorageKey(userId), JSON.stringify(currentState));
      } catch (e) {
        console.error('Yedekleme hatası:', e);
      }
    }, BACKUP_INTERVAL);

    return () => clearInterval(backupTimer);
  }, [userId, state]);

  // Backend senkronizasyonu
  useEffect(() => {
    const syncTimer = setInterval(async () => {
      try {
        const res = await GamificationApi.getCurrentLevel(userId);
        if (res?.success && res.data) {
          // Local ve remote state'i karşılaştır
          const remoteState = res.data;
          const localState = state;
          
          // Hangisi daha yüksek XP'ye sahipse onu kullan
          if (remoteState.totalXP > localState.totalXP) {
            setState(remoteState);
            saveToStorage(remoteState);
          } else if (localState.totalXP > remoteState.totalXP) {
            // Local state daha güncel, backend'e gönder
            await GamificationApi.syncState(userId, localState as Record<string, unknown>);
          }
        }
      } catch (e) {
        console.error('Senkronizasyon hatası:', e);
      }
    }, SYNC_INTERVAL);

    return () => clearInterval(syncTimer);
  }, [userId, state, saveToStorage]);

  // ============ XP İŞLEMLERİ ============
  
  const MAX_LEVEL = 100;
  const MIN_XP_PER_NODE = 100;

  const checkLevelUp = (current: GamificationState): GamificationState => {
    // Negatif XP kontrolü
    let newCurrentXP = Math.max(0, current.currentXP);
    let newNode = current.currentNode;
    let newLevel = Math.min(MAX_LEVEL, current.currentLevel);
    let newNodesInLevel = current.nodesInLevel;
    let levelUpOccurred = false;
    
    // Düğüm tamamlandı mı? (100 XP = 1 düğüm)
    while (newCurrentXP >= MIN_XP_PER_NODE && newLevel < MAX_LEVEL) {
      newCurrentXP -= MIN_XP_PER_NODE;
      newNode++;
      
      // Level tamamlandı mı?
      if (newNode >= newNodesInLevel) {
        newLevel++;
        newNode = 0;
        newNodesInLevel = getNodesForLevel(newLevel);
        levelUpOccurred = true;
        console.log('🎉 LEVEL UP! Yeni level:', newLevel);
        
        // Maximum level kontrolü
        if (newLevel >= MAX_LEVEL) {
          newCurrentXP = MIN_XP_PER_NODE - 1; // Son seviyede tutmak için
          break;
        }
      }
    }
    
    // Level atlamada XP animasyonu
    if (levelUpOccurred) {
      FloatingXPOverlay.show({
        xpAmount: 0,
        source: 'level_up',
        position: { x: window.innerWidth / 2 - 60, y: window.innerHeight / 2 - 100 },
      });
    }
    
    return {
      ...current,
      currentXP: newCurrentXP,
      currentNode: newNode,
      currentLevel: newLevel,
      nodesInLevel: newNodesInLevel,
    };
  };
  
  const addXP = useCallback((amount: number, source: AddXpRequest['source'], metadata?: Record<string, unknown>) => {
    let nextState: GamificationState = {
      ...state,
      currentXP: state.currentXP + amount,
      totalXP: state.totalXP + amount,
      xpEarnedToday: state.xpEarnedToday + amount,
    };
    
    // Activity counts güncelle
    if (source === 'reel_watched') nextState.reelsWatchedToday++;
    if (source === 'emoji_given') nextState.emojisGivenToday++;
    if (source === 'detail_read') nextState.detailsReadToday++;
    if (source === 'share_given') nextState.sharesGivenToday++;
    
    // Günlük hedef kontrolü
    if (nextState.xpEarnedToday >= nextState.dailyXPGoal) {
      nextState.dailyGoalCompleted = true;
    }
    
    // Level up kontrolü
    nextState = checkLevelUp(nextState);
    
    setState(nextState);
    saveToStorage(nextState);
    
    // Backend'e gönder
    void GamificationApi.addXP({
      user_id: userId,
      xp_amount: amount,
      source,
      metadata,
    });
  }, [state, userId, saveToStorage]);

  // ============ REEL INTERACTION TRACKING ============
  // Flutter'daki yapı: Her reel için watch/emoji/detail/share ayrı ayrı takip edilir
  
  const reelInteractionsRef = useRef<Record<string, {
    watched: boolean;
    emojiGiven: boolean;
    detailRead: boolean;
    shareGiven: boolean;
  }>>({});
  
  const getReelInteraction = (reelId: string) => {
    if (!reelInteractionsRef.current[reelId]) {
      reelInteractionsRef.current[reelId] = {
        watched: false,
        emojiGiven: false,
        detailRead: false,
        shareGiven: false,
      };
    }
    return reelInteractionsRef.current[reelId];
  };
  
  // ============ XP KAYNAKLARI ============
  
  /// Reels izlendi (3+ saniye) - 10 XP
  const onReelWatched = useCallback((reelId: string): boolean => {
    const interaction = getReelInteraction(reelId);
    
    // Bu reel daha önce izlendiyse XP verme
    if (interaction.watched) {
      return false;
    }
    
    interaction.watched = true;
    addXP(10, 'reel_watched', { reelId });
    return true;
  }, [addXP]);

  /// Emoji atıldı (sadece 1 kere) - 5 XP
  const onEmojiGiven = useCallback((reelId: string): boolean => {
    const interaction = getReelInteraction(reelId);
    const now = Date.now();
    const lastActionTime = lastActionTimestampRef.current[`emoji_${reelId}`] || 0;
    
    // Bu reel'e daha önce emoji atıldıysa veya son işlemden 2 saniye geçmediyse XP verme
    if (interaction.emojiGiven || (now - lastActionTime) < 2000) {
      return false;
    }
    
    lastActionTimestampRef.current[`emoji_${reelId}`] = now;
    interaction.emojiGiven = true;
    emojiGivenRef.current.add(reelId); // Eski sistem için backward compatibility
    addXP(5, 'emoji_given', { reelId });
    return true;
  }, [addXP]);

  /// Detail okundu (10+ saniye) - 5 XP
  const onDetailRead = useCallback((reelId: string): boolean => {
    const interaction = getReelInteraction(reelId);
    
    // Bu reel'in detayı daha önce okunduysa XP verme
    if (interaction.detailRead) {
      return false;
    }
    
    interaction.detailRead = true;
    addXP(5, 'detail_read', { reelId });
    return true;
  }, [addXP]);

  /// Paylaşım yapıldı (ilk paylaşım) - 5 XP
  const onShareGiven = useCallback((reelId: string): boolean => {
    const interaction = getReelInteraction(reelId);
    const now = Date.now();
    const lastActionTime = lastActionTimestampRef.current[`share_${reelId}`] || 0;
    
    // Bu reel daha önce paylaşıldıysa veya son işlemden 2 saniye geçmediyse XP verme
    if (interaction.shareGiven || (now - lastActionTime) < 2000) {
      return false;
    }
    
    lastActionTimestampRef.current[`share_${reelId}`] = now;
    interaction.shareGiven = true;
    shareGivenRef.current.add(reelId); // Eski sistem için backward compatibility
    addXP(5, 'share_given', { reelId });
    return true;
  }, [addXP]);

  // ============ API SYNC ============
  
  const refreshLevel = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await GamificationApi.getCurrentLevel(userId);
      if (res?.success && res.data) {
        setState(res.data);
        saveToStorage(res.data);
      }
    } catch (e: any) {
      setError(e?.message || 'Level yüklenemedi');
    } finally {
      setLoading(false);
    }
  }, [userId, saveToStorage]);

  // ============ HELPER METHODS ============
  
  const hasEmojiGiven = useCallback((reelId: string): boolean => {
    const interaction = reelInteractionsRef.current[reelId];
    return interaction?.emojiGiven || false;
  }, []);

  const hasShareGiven = useCallback((reelId: string): boolean => {
    const interaction = reelInteractionsRef.current[reelId];
    return interaction?.shareGiven || false;
  }, []);
  
  const hasWatched = useCallback((reelId: string): boolean => {
    const interaction = reelInteractionsRef.current[reelId];
    return interaction?.watched || false;
  }, []);
  
  const hasDetailRead = useCallback((reelId: string): boolean => {
    const interaction = reelInteractionsRef.current[reelId];
    return interaction?.detailRead || false;
  }, []);

  const forceResetDaily = useCallback(() => {
    performDailyReset();
  }, [performDailyReset]);

  const addTestXP = useCallback((amount: number) => {
    addXP(amount, 'test');
  }, [addXP]);

  return {
    // State
    state: {
      ...state,
      xpToNextLevel,
      dailyProgress,
      nodeProgress,
      levelProgress,
    },
    loading,
    error,
    
    // Actions
    refreshLevel,
    onReelWatched,
    onEmojiGiven,
    onDetailRead,
    onShareGiven,
    
    // Helpers
    hasEmojiGiven,
    hasShareGiven,
    hasWatched,
    hasDetailRead,
    forceResetDaily,
    addTestXP,
  };
}