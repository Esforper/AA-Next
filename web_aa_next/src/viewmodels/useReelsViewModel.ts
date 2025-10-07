// src/viewmodels/useReelsViewModel.ts - Updated with Infinite Scroll & Real API

import { useState, useEffect, useCallback, useRef } from 'react';
import { ReelData, AudioState } from '../models';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';
import { useViewTracking } from '../hooks/useViewTracking';

export interface ReelsViewModel {
  // Data
  reels: ReelData[];
  currentReelIndex: number;
  loading: boolean;
  error: string | null;
  audioState: AudioState;
  
  // Infinite scroll
  hasMore: boolean;
  isLoadingMore: boolean;
  totalAvailable: number;
  loadedCount: number;
  
  // Actions
  fetchReels: () => Promise<void>;
  refreshFeed: () => Promise<void>;
  loadMore: () => Promise<void>;
  setCurrentReel: (index: number) => void;
  nextReel: () => void;
  prevReel: () => void;
  togglePlayPause: () => void;
  seekAudio: (position: number) => void;
  
  // Stats
  getTotalViewTime: () => number;
  getCurrentReel: () => ReelData | null;
}

export const useReelsViewModel = (): ReelsViewModel => {
  
  // Infinite scroll hook
  const {
    reels,
    currentIndex,
    loading,
    error,
    hasMore,
    totalAvailable,
    loadedCount,
    isLoadingMore,
    loadMore: loadMoreReels,
    refreshFeed: refreshInfiniteFeed,
    goToNext: goToNextReel,
    goToPrev: goToPrevReel,
    goToIndex
  } = useInfiniteScroll(20, 3); // Load 20, preload when 3 left

  // Expose goToIndex to window for embed/openId jumps (scoped to this instance)
  useEffect(() => {
    (window as any).__goToIndex = (idx: number) => {
      try {
        // Clamp and update
        const clamped = Math.max(0, Math.min(idx, reels.length - 1));
        if (clamped !== currentIndex) {
          // move index via internal helpers
          if (clamped > currentIndex) {
            // step forward
            for (let i = currentIndex; i < clamped; i++) {
              goToNextReel();
            }
          } else {
            for (let i = currentIndex; i > clamped; i--) {
              goToPrevReel();
            }
          }
        }
      } catch {}
    };
    return () => {
      if ((window as any).__goToIndex) {
        try { delete (window as any).__goToIndex; } catch {}
      }
    };
  }, [currentIndex, reels.length, goToNextReel, goToPrevReel]);
  
  // View tracking hook
  const {
    startTracking,
    stopTracking,
    pauseTracking,
    resumeTracking,
    updateAudioState: updateViewTracking,
    getTotalViewTime
  } = useViewTracking();
  
  // Audio state
  const [audioState, setAudioState] = useState<AudioState>({
    isPlaying: false,
    position: 0,
    duration: 0,
    isLoaded: false
  });
  
  // Audio reference
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentReelRef = useRef<ReelData | null>(null);
  
  // Current reel helper
  const getCurrentReel = useCallback((): ReelData | null => {
    return reels[currentIndex] || null;
  }, [reels, currentIndex]);
  
  // Update current reel ref
  useEffect(() => {
    currentReelRef.current = getCurrentReel();
  }, [getCurrentReel]);
  
  // Load audio for current reel
  const loadAudio = useCallback((reel: ReelData) => {
    // Clean up previous audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.removeEventListener('loadedmetadata', () => {});
      audioRef.current.removeEventListener('timeupdate', () => {});
      audioRef.current.removeEventListener('ended', () => {});
      audioRef.current.removeEventListener('error', () => {});
      audioRef.current = null;
    }
    
    // Reset audio state
    setAudioState({
      isPlaying: false,
      position: 0,
      duration: 0,
      isLoaded: false
    });
    
    if (!reel.audio_url) {
      console.warn(`No audio URL for reel: ${reel.id}`);
      return;
    }
    
    console.log(`🎵 Loading audio for reel: ${reel.id}`);
    
    // Create new audio element
    const audio = new Audio(reel.audio_url);
    audioRef.current = audio;
    
    // Audio event listeners
    audio.addEventListener('loadedmetadata', () => {
      console.log(`✅ Audio loaded: ${reel.title} (${audio.duration}s)`);
      const newState = {
        ...audioState,
        duration: audio.duration,
        isLoaded: true
      };
      setAudioState(newState);
      updateViewTracking(newState);
    });
    
    audio.addEventListener('timeupdate', () => {
      const newState = {
        ...audioState,
        position: audio.currentTime,
        isLoaded: true,
        duration: audio.duration
      };
      setAudioState(newState);
      updateViewTracking(newState);
    });
    
    audio.addEventListener('ended', () => {
      console.log(`🏁 Audio ended: ${reel.title}`);
      const newState = {
        ...audioState,
        isPlaying: false,
        position: audio.duration,
        isLoaded: true
      };
      setAudioState(newState);
      updateViewTracking(newState);
      
      // Auto-advance to next reel after a short delay
      setTimeout(() => {
        nextReel();
      }, 500);
    });
    
    audio.addEventListener('play', () => {
      const newState = { ...audioState, isPlaying: true, isLoaded: true };
      setAudioState(newState);
      updateViewTracking(newState);
    });
    
    audio.addEventListener('pause', () => {
      const newState = { ...audioState, isPlaying: false, isLoaded: true };
      setAudioState(newState);
      updateViewTracking(newState);
    });
    
    audio.addEventListener('error', (e) => {
      console.error('Audio load error:', e);
      setAudioState(prev => ({
        ...prev,
        isLoaded: false,
        isPlaying: false
      }));
    });
    
    // Preload audio
    audio.preload = 'metadata';
    
  }, [audioState, updateViewTracking]);
  
  // Set current reel and start tracking
  const setCurrentReel = useCallback((index: number) => {
    if (index < 0 || index >= reels.length) {
      console.warn(`Invalid reel index: ${index} (total: ${reels.length})`);
      return;
    }
    
    const newReel = reels[index];
    
    console.log(`🎯 Setting current reel: ${index} - ${newReel.title}`);
    
    // Stop tracking previous reel
    stopTracking();
    
    // Load new reel audio
    loadAudio(newReel);
    
    // Start tracking new reel
    startTracking(newReel);
    
    // Navigation handled by infinite scroll hook
    // currentIndex is managed there
    
  }, [reels, loadAudio, startTracking, stopTracking]);
  
  // Navigate to next reel
  const nextReel = useCallback(() => {
    if (currentIndex >= reels.length - 1) {
      console.log('🔚 Reached end of reels');
      return;
    }
    
    console.log(`➡️ Next reel: ${currentIndex} → ${currentIndex + 1}`);
    
    // Use infinite scroll navigation
    goToNextReel();
    
    // setCurrentReel will be called by useEffect when currentIndex changes
  }, [currentIndex, reels.length, goToNextReel]);
  
  // Navigate to previous reel
  const prevReel = useCallback(() => {
    if (currentIndex <= 0) {
      console.log('🔚 At first reel');
      return;
    }
    
    console.log(`⬅️ Previous reel: ${currentIndex} → ${currentIndex - 1}`);
    
    // Use infinite scroll navigation
    goToPrevReel();
    
    // setCurrentReel will be called by useEffect when currentIndex changes
  }, [currentIndex, goToPrevReel]);
  
  // Toggle play/pause
  const togglePlayPause = useCallback(() => {
    if (!audioRef.current) {
      console.warn('No audio available for play/pause');
      return;
    }
    
    try {
      if (audioState.isPlaying) {
        console.log('⏸️ Pausing audio');
        audioRef.current.pause();
      } else {
        console.log('▶️ Playing audio');
        audioRef.current.play().catch(error => {
          console.error('Failed to play audio:', error);
        });
      }
    } catch (error) {
      console.error('Toggle play/pause error:', error);
    }
  }, [audioState.isPlaying]);
  
  // Seek audio to specific position
  const seekAudio = useCallback((position: number) => {
    if (!audioRef.current) {
      console.warn('No audio available for seeking');
      return;
    }
    
    try {
      console.log(`⏩ Seeking to: ${position}s`);
      audioRef.current.currentTime = Math.max(0, Math.min(position, audioRef.current.duration));
    } catch (error) {
      console.error('Seek audio error:', error);
    }
  }, []);
  
  // Fetch reels (refresh)
  const fetchReels = useCallback(async () => {
    console.log('🔄 Fetching reels...');
    await refreshInfiniteFeed();
  }, [refreshInfiniteFeed]);
  
  // Load more reels
  const loadMore = useCallback(async () => {
    console.log('📥 Loading more reels...');
    await loadMoreReels();
  }, [loadMoreReels]);
  
  // Handle current reel changes
  useEffect(() => {
    const currentReel = getCurrentReel();
    
    if (currentReel && currentReel !== currentReelRef.current) {
      console.log(`🎬 Current reel changed: ${currentReel.title}`);
      setCurrentReel(currentIndex);
    }
  }, [currentIndex, getCurrentReel, setCurrentReel]);
  
  // Auto-fetch reels on mount
  useEffect(() => {
    if (reels.length === 0 && !loading) {
      console.log('🚀 Auto-fetching reels on mount');
      fetchReels();
    }
  }, [reels.length, loading, fetchReels]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('🧹 Cleaning up reels view model');
      
      // Stop tracking
      stopTracking();
      
      // Clean up audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [stopTracking]);
  
  // Auto-play first reel when reels are loaded
  useEffect(() => {
    if (reels.length > 0 && currentIndex === 0 && !audioRef.current) {
      console.log('🎬 Auto-loading first reel');
      const firstReel = reels[0];
      setCurrentReel(0);
    }
  }, [reels.length, currentIndex, setCurrentReel]);
  
  return {
    // Data
    reels,
    currentReelIndex: currentIndex,
    loading,
    error,
    audioState,
    
    // Infinite scroll
    hasMore,
    isLoadingMore,
    totalAvailable,
    loadedCount,
    
    // Actions
    fetchReels,
    refreshFeed: fetchReels, // Alias for consistency
    loadMore,
    setCurrentReel,
    nextReel,
    prevReel,
    togglePlayPause,
    seekAudio,
    
    // Stats
    getTotalViewTime,
    getCurrentReel
  };
};