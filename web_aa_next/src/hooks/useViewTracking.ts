// src/hooks/useViewTracking.ts




/*
Burada izlenme verisinde, kullanıcı kayıt sistemi yaptıktan sonra USER ID kısmı değiştirilecek
*/






import { useState, useEffect, useRef, useCallback } from 'react';
import { ReelData, AudioState } from '../models';

interface TrackViewRequest {
  reel_id: string;
  duration_ms: number;
  completed: boolean;
  category?: string;
  session_id?: string;
}

interface TrackViewResponse {
  success: boolean;
  message: string;
  view_id?: string;
  meaningful_view: boolean;
  daily_progress_updated?: boolean;
  new_achievement?: string;
}

interface ViewTrackingState {
  currentReelId: string | null;
  startTime: number | null;
  totalDuration: number;
  isActive: boolean;
  lastSentDuration: number;
}

interface UseViewTrackingReturn {
  // Current viewing state
  viewingState: ViewTrackingState;
  
  // Actions
  startTracking: (reel: ReelData) => void;
  stopTracking: () => Promise<void>;
  pauseTracking: () => void;
  resumeTracking: () => void;
  forceSync: () => Promise<void>;
  
  // Audio integration
  updateAudioState: (audioState: AudioState) => void;
  
  // Stats
  getTotalViewTime: () => number;
  isReelCompleted: (reel: ReelData) => boolean;
}

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
const USER_ID = 'web_user_' + Math.random().toString(36).substr(2, 9);
const SESSION_ID = 'session_' + Date.now();

// Tracking thresholds
const MEANINGFUL_VIEW_THRESHOLD = 3000; // 3 seconds
const SYNC_INTERVAL = 5000; // Sync to backend every 5 seconds
const COMPLETION_THRESHOLD = 0.8; // 80% of audio = completed

export const useViewTracking = (): UseViewTrackingReturn => {
  
  const [viewingState, setViewingState] = useState<ViewTrackingState>({
    currentReelId: null,
    startTime: null,
    totalDuration: 0,
    isActive: false,
    lastSentDuration: 0
  });
  
  // Refs for accurate timing
  const startTimeRef = useRef<number | null>(null);
  const accumulatedTimeRef = useRef<number>(0);
  const syncIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const pendingSyncRef = useRef<Promise<void> | null>(null);
  const audioStateRef = useRef<AudioState | null>(null);
  
  // Track view to backend
  const trackView = useCallback(async (
    reelId: string, 
    durationMs: number, 
    completed: boolean = false,
    category?: string
  ): Promise<TrackViewResponse | null> => {
    try {
      console.log(`📊 Tracking view: ${reelId}, duration: ${durationMs}ms, completed: ${completed}`);
      
      const requestBody: TrackViewRequest = {
        reel_id: reelId,
        duration_ms: Math.round(durationMs),
        completed,
        category,
        session_id: SESSION_ID
      };
      
      // Get auth token from localStorage
      const token = localStorage.getItem('aa_auth_token') || sessionStorage.getItem('aa_auth_token');
      
      // Build headers with auth if available
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else {
        headers['X-User-ID'] = USER_ID; // Fallback to X-User-ID if no token
      }
      
      const response = await fetch(`${API_BASE}/api/reels/track-view`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(10000)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: TrackViewResponse = await response.json();
      
      if (data.success) {
        console.log(`✅ View tracked: ${data.meaningful_view ? 'meaningful' : 'partial'} view`);
        if (data.new_achievement) {
          console.log(`🏆 New achievement: ${data.new_achievement}`);
        }
      } else {
        console.error(`❌ Track view failed: ${data.message}`);
      }
      
      return data;
      
    } catch (error) {
      console.error('Failed to track view:', error);
      return null;
    }
  }, []);
  
  // Calculate current accumulated time
  const getCurrentDuration = useCallback((): number => {
    const accumulated = accumulatedTimeRef.current;
    const current = startTimeRef.current ? Date.now() - startTimeRef.current : 0;
    return accumulated + current;
  }, []);
  
  // Start tracking a new reel
  const startTracking = useCallback((reel: ReelData): void => {
    console.log(`▶️ Start tracking: ${reel.id} - ${reel.title}`);
    
    // Stop previous tracking
    if (viewingState.currentReelId && viewingState.currentReelId !== reel.id) {
      stopTracking();
    }
    
    // Reset state
    startTimeRef.current = Date.now();
    accumulatedTimeRef.current = 0;
    
    setViewingState({
      currentReelId: reel.id,
      startTime: Date.now(),
      totalDuration: 0,
      isActive: true,
      lastSentDuration: 0
    });
    
    // Start periodic sync
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
    }
    
    syncIntervalRef.current = setInterval(async () => {
      const currentDuration = getCurrentDuration();
      const reelCategory = reel.category;
      
      // Only sync if meaningful progress made (1+ second since last sync)
      if (currentDuration - accumulatedTimeRef.current > 1000) {
        // Update accumulated time
        accumulatedTimeRef.current = currentDuration;
        startTimeRef.current = Date.now(); // Reset timer
        
        // Check if completed based on audio progress
        const isCompleted = isReelCompleted(reel);
        
        await trackView(reel.id, currentDuration, isCompleted, reelCategory);
        
        // Update local state
        setViewingState(prev => ({
          ...prev,
          totalDuration: currentDuration,
          lastSentDuration: currentDuration
        }));
      }
    }, SYNC_INTERVAL);
    
  }, [viewingState.currentReelId, getCurrentDuration, trackView]);
  
  // Stop tracking current reel
  const stopTracking = useCallback(async (): Promise<void> => {
    if (!viewingState.currentReelId) return;
    
    console.log(`⏹️ Stop tracking: ${viewingState.currentReelId}`);
    
    // Clear interval
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
      syncIntervalRef.current = null;
    }
    
    // Calculate final duration
    const finalDuration = getCurrentDuration();
    
    // Send final tracking data
    if (finalDuration > 0) {
      const isCompleted = finalDuration >= MEANINGFUL_VIEW_THRESHOLD;
      await trackView(viewingState.currentReelId, finalDuration, isCompleted);
    }
    
    // Reset state
    startTimeRef.current = null;
    accumulatedTimeRef.current = 0;
    
    setViewingState({
      currentReelId: null,
      startTime: null,
      totalDuration: 0,
      isActive: false,
      lastSentDuration: 0
    });
    
  }, [viewingState.currentReelId, getCurrentDuration, trackView]);
  
  // Pause tracking (user paused video/audio)
  const pauseTracking = useCallback((): void => {
    if (!viewingState.isActive) return;
    
    console.log('⏸️ Pause tracking');
    
    // Accumulate current time
    if (startTimeRef.current) {
      accumulatedTimeRef.current += Date.now() - startTimeRef.current;
      startTimeRef.current = null;
    }
    
    setViewingState(prev => ({
      ...prev,
      isActive: false,
      totalDuration: accumulatedTimeRef.current
    }));
  }, [viewingState.isActive]);
  
  // Resume tracking (user resumed video/audio)
  const resumeTracking = useCallback((): void => {
    if (viewingState.isActive || !viewingState.currentReelId) return;
    
    console.log('▶️ Resume tracking');
    
    startTimeRef.current = Date.now();
    
    setViewingState(prev => ({
      ...prev,
      isActive: true
    }));
  }, [viewingState.isActive, viewingState.currentReelId]);
  
  // Force sync current state to backend
  const forceSync = useCallback(async (): Promise<void> => {
    if (!viewingState.currentReelId) return;
    
    const currentDuration = getCurrentDuration();
    
    if (currentDuration > viewingState.lastSentDuration) {
      console.log('🔄 Force sync to backend');
      const isCompleted = currentDuration >= MEANINGFUL_VIEW_THRESHOLD;
      await trackView(viewingState.currentReelId, currentDuration, isCompleted);
      
      setViewingState(prev => ({
        ...prev,
        lastSentDuration: currentDuration
      }));
    }
  }, [viewingState.currentReelId, viewingState.lastSentDuration, getCurrentDuration, trackView]);
  
  // Update audio state for completion calculation
  const updateAudioState = useCallback((audioState: AudioState): void => {
    audioStateRef.current = audioState;
    
    // Auto pause/resume tracking based on audio state
    if (viewingState.currentReelId) {
      if (audioState.isPlaying && !viewingState.isActive) {
        resumeTracking();
      } else if (!audioState.isPlaying && viewingState.isActive) {
        pauseTracking();
      }
    }
  }, [viewingState.currentReelId, viewingState.isActive, pauseTracking, resumeTracking]);
  
  // Get total view time for current reel
  const getTotalViewTime = useCallback((): number => {
    return getCurrentDuration();
  }, [getCurrentDuration]);
  
  // Check if reel is completed based on audio progress
  const isReelCompleted = useCallback((reel: ReelData): boolean => {
    if (!audioStateRef.current || !audioStateRef.current.duration) {
      // Fallback: use time-based completion
      const totalTime = getCurrentDuration();
      return totalTime >= MEANINGFUL_VIEW_THRESHOLD;
    }
    
    // Use audio progress for accurate completion
    const audioProgress = audioStateRef.current.position / audioStateRef.current.duration;
    return audioProgress >= COMPLETION_THRESHOLD;
  }, [getCurrentDuration]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
      // Force sync on cleanup
      if (viewingState.currentReelId) {
        stopTracking();
      }
    };
  }, [viewingState.currentReelId, stopTracking]);
  
  return {
    // Current viewing state
    viewingState,
    
    // Actions
    startTracking,
    stopTracking,
    pauseTracking,
    resumeTracking,
    forceSync,
    
    // Audio integration
    updateAudioState,
    
    // Stats
    getTotalViewTime,
    isReelCompleted
  };
};