import { useState, useEffect, useCallback, useRef } from 'react';
import { ReelData, AudioState } from '../models';
import { ReelsApi } from '../api';

export interface ReelsViewModel {
  reels: ReelData[];
  currentReelIndex: number;
  loading: boolean;
  error: string | null;
  audioState: AudioState;
  
  // Actions
  fetchReels: () => Promise<void>;
  setCurrentReel: (index: number) => void;
  nextReel: () => void;
  prevReel: () => void;
  togglePlayPause: () => void;
  seekAudio: (position: number) => void;
}

export const useReelsViewModel = (): ReelsViewModel => {
  const [reels, setReels] = useState<ReelData[]>([]);
  const [currentReelIndex, setCurrentReelIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioState, setAudioState] = useState<AudioState>({
    isPlaying: false,
    position: 0,
    duration: 0,
    isLoaded: false
  });

  const audioRef = useRef<HTMLAudioElement | null>(null);

  const fetchReels = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to fetch from API first, then fallback to ready endpoint
      let response;
      try {
        response = await ReelsApi.fetchReelsMix(10);
      } catch (apiError) {
        console.warn('Mix API failed, trying ready endpoint:', apiError);
        response = await ReelsApi.fetchReelsReady({ limit: 15 });
      }
      
      if (response.success) {
        setReels(response.reels);
        if (response.reels.length > 0) {
          loadAudio(response.reels[0]);
        }
      } else {
        setError(response.message || 'Failed to fetch reels');
      }
    } catch (err) {
      console.error('Failed to fetch reels:', err);
      setError('Failed to load reels. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAudio = useCallback((reel: ReelData) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    // For web, we'll use HTML5 Audio API
    if (reel.audio_url) {
      const audio = new Audio(reel.audio_url);
      audioRef.current = audio;

      audio.addEventListener('loadedmetadata', () => {
        setAudioState(prev => ({
          ...prev,
          duration: audio.duration,
          isLoaded: true
        }));
      });

      audio.addEventListener('timeupdate', () => {
        setAudioState(prev => ({
          ...prev,
          position: audio.currentTime
        }));
      });

      audio.addEventListener('ended', () => {
        setAudioState(prev => ({
          ...prev,
          isPlaying: false
        }));
        // Auto-advance to next reel
        const nextIndex = (currentReelIndex + 1) % reels.length;
        setCurrentReelIndex(nextIndex);
        if (reels[nextIndex]) {
          loadAudio(reels[nextIndex]);
        }
      });

      audio.addEventListener('error', (e) => {
        console.warn('Audio load error:', e);
        setAudioState(prev => ({
          ...prev,
          isLoaded: false
        }));
      });
    }
  }, [currentReelIndex, reels]);

  const setCurrentReel = useCallback((index: number) => {
    if (index >= 0 && index < reels.length) {
      setCurrentReelIndex(index);
      loadAudio(reels[index]);
    }
  }, [reels, loadAudio]);

  const nextReel = useCallback(() => {
    const nextIndex = (currentReelIndex + 1) % reels.length;
    setCurrentReelIndex(nextIndex);
    if (reels[nextIndex]) {
      loadAudio(reels[nextIndex]);
    }
  }, [currentReelIndex, reels, loadAudio]);

  const prevReel = useCallback(() => {
    const prevIndex = currentReelIndex === 0 ? reels.length - 1 : currentReelIndex - 1;
    setCurrentReel(prevIndex);
  }, [currentReelIndex, reels.length, setCurrentReel]);

  const togglePlayPause = useCallback(() => {
    if (audioRef.current) {
      if (audioState.isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(console.error);
      }
      setAudioState(prev => ({
        ...prev,
        isPlaying: !prev.isPlaying
      }));
    }
  }, [audioState.isPlaying]);

  const seekAudio = useCallback((position: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = position;
      setAudioState(prev => ({
        ...prev,
        position
      }));
    }
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Auto-fetch reels on mount
  useEffect(() => {
    fetchReels();
  }, [fetchReels]);

  return {
    reels,
    currentReelIndex,
    loading,
    error,
    audioState,
    fetchReels,
    setCurrentReel,
    nextReel,
    prevReel,
    togglePlayPause,
    seekAudio
  };
};