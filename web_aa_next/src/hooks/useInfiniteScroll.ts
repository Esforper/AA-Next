// src/hooks/useInfiniteScroll.ts

import { useState, useCallback, useRef } from 'react';
import { ReelData } from '../models';
import { API_CONFIG } from '../api/config';

interface FeedPagination {
  current_page: number;
  has_next: boolean;
  has_previous: boolean;
  next_cursor: string | null;
  total_available: number;
}

interface FeedMetadata {
  trending_count: number;
  personalized_count: number;
  fresh_count: number;
  algorithm_version: string;
}

interface BackendReelItem {
  id: string;
  news_data: {
    title: string;
    summary: string;
    full_content: string;
    url: string;
    category: string;
    author?: string;
    location?: string;
    main_image?: string;
    images: string[];
    tags: string[];
  };
  audio_url: string;
  duration_seconds: number;
  status: string;
  published_at: string;
  is_watched?: boolean;
  is_trending?: boolean;
  is_fresh?: boolean;
}

interface FeedResponse {
  success: boolean;
  reels: BackendReelItem[];
  pagination: FeedPagination;
  feed_metadata: FeedMetadata;
  generated_at: string;
  message?: string;
}

interface UseInfiniteScrollReturn {
  // Data
  reels: ReelData[];
  currentIndex: number;
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  
  // Pagination info
  totalAvailable: number;
  loadedCount: number;
  feedMetadata: FeedMetadata | null;
  
  // Actions
  loadMore: () => Promise<void>;
  refreshFeed: () => Promise<void>;
  goToNext: () => void;
  goToPrev: () => void;
  
  // Internal state
  isLoadingMore: boolean;
}

const API_BASE = API_CONFIG.BASE_URL;
const USER_ID = 'web_user_' + Math.random().toString(36).substr(2, 9); // Generate random user ID

export const useInfiniteScroll = (
  initialLimit: number = 20,
  preloadThreshold: number = 2 // Only prefetch up to 2 items ahead
): UseInfiniteScrollReturn => {
  
  // State
  const [reels, setReels] = useState<ReelData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [totalAvailable, setTotalAvailable] = useState(0);
  const [feedMetadata, setFeedMetadata] = useState<FeedMetadata | null>(null);
  
  // Prevent duplicate API calls
  const isLoadingRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const lastLoadAtRef = useRef<number>(0);
  const consecutiveEmptyRef = useRef<number>(0);
  const lastCursorRef = useRef<string | null>(null);

  // Simple SWR-like cache for the first page
  const cacheRef = useRef<{
    ts: number;
    data: FeedResponse | null;
  }>({ ts: 0, data: null });

  const STALE_MS = 60_000; // 60s stale-while-revalidate
  const LOAD_THROTTLE_MS = 800; // min interval between loadMore calls
  const MAX_CONSECUTIVE_EMPTY = 3; // stop after 3 empty/no-progress fetches
  
  const fetchReels = useCallback(async (isRefresh: boolean = false): Promise<void> => {
    // Prevent duplicate calls
    if (isLoadingRef.current) return;
    
    try {
      isLoadingRef.current = true;
      
      if (isRefresh) {
        setLoading(true);
        setError(null);
      } else {
        setIsLoadingMore(true);
      }
      
      // Abort previous in-flight request
      if (controllerRef.current) {
        try { controllerRef.current.abort(); } catch {}
      }
      controllerRef.current = new AbortController();

      // Serve from cache instantly if fresh and refresh requested
      const now = Date.now();
      if (isRefresh && cacheRef.current.data && now - cacheRef.current.ts < STALE_MS) {
        const cached = cacheRef.current.data;
        const convertedReels: ReelData[] = cached.reels.map(backendReel => ({
          id: backendReel.id,
          title: backendReel.news_data?.title || 'Untitled',
          content: backendReel.news_data?.full_content || '',
          summary: backendReel.news_data?.summary || '',
          category: backendReel.news_data?.category || 'general',
          images: backendReel.news_data?.images || [],
          main_image: backendReel.news_data?.main_image || '',
          audio_url: backendReel.audio_url,
          subtitles: [],
          estimated_duration: backendReel.duration_seconds,
          tags: backendReel.news_data?.tags || [],
          author: backendReel.news_data?.author || '',
          location: backendReel.news_data?.location || '',
          published_at: backendReel.published_at
        }));
        setReels(convertedReels);
        setCurrentIndex(0);
        setCursor(cached.pagination.next_cursor);
        setHasMore(cached.pagination.has_next);
        setTotalAvailable(cached.pagination.total_available);
        setFeedMetadata(cached.feed_metadata);
        setLoading(false);
        // Continue to revalidate in background (do not return)
      }

      // Build API URL
      const params = new URLSearchParams({
        limit: initialLimit.toString()
      });
      
      // Add cursor for pagination (not for refresh)
      if (!isRefresh && cursor) {
        params.append('cursor', cursor);
      }
      
      const url = `${API_BASE}/api/reels/feed?${params.toString()}`;
      
      console.log(`🔄 Fetching reels: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID // Backend requires this for user tracking
        },
        signal: controllerRef.current?.signal ?? AbortSignal.timeout(30000)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: FeedResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'API returned error');
      }
      
      console.log(`✅ Fetched ${data.reels.length} reels, has_next: ${data.pagination.has_next}`);
      
      // Convert backend ReelFeedItem to frontend ReelData format
      const convertedReels: ReelData[] = data.reels.map(backendReel => ({
        id: backendReel.id,
        title: backendReel.news_data?.title || 'Untitled',
        content: backendReel.news_data?.full_content || '',
        summary: backendReel.news_data?.summary || '',
        category: backendReel.news_data?.category || 'general',
        images: backendReel.news_data?.images || [],
        main_image: backendReel.news_data?.main_image || '',
        audio_url: backendReel.audio_url,
        subtitles: [], // Backend doesn't provide subtitles yet
        estimated_duration: backendReel.duration_seconds,
        tags: backendReel.news_data?.tags || [],
        author: backendReel.news_data?.author || '',
        location: backendReel.news_data?.location || '',
        
        // Additional backend data
        is_watched: backendReel.is_watched || false,
        is_trending: backendReel.is_trending || false,
        is_fresh: backendReel.is_fresh || false,
        published_at: backendReel.published_at
      }));
      
      if (isRefresh) {
        // Replace all reels
        setReels(convertedReels);
        setCurrentIndex(0);
        // Cache first page
        cacheRef.current = { ts: Date.now(), data };
        consecutiveEmptyRef.current = 0;
      } else {
        // Append new reels
        setReels(prev => [...prev, ...convertedReels]);
        if (convertedReels.length === 0) {
          consecutiveEmptyRef.current += 1;
        } else {
          consecutiveEmptyRef.current = 0;
        }
      }
      
      // Update pagination state
      setCursor(data.pagination.next_cursor);
      setHasMore(data.pagination.has_next);
      setTotalAvailable(data.pagination.total_available);
      setFeedMetadata(data.feed_metadata);

      // Stop further requests if no progress is possible
      const cursorUnchanged = lastCursorRef.current === (data.pagination.next_cursor || null);
      lastCursorRef.current = data.pagination.next_cursor || null;
      if (!isRefresh) {
        if (convertedReels.length === 0 && (!data.pagination.has_next || cursorUnchanged)) {
          setHasMore(false);
        }
        if (consecutiveEmptyRef.current >= MAX_CONSECUTIVE_EMPTY) {
          console.warn('🛑 Stopping further loads due to consecutive empty responses');
          setHasMore(false);
        }
      }
      
    } catch (err) {
      console.error('Failed to fetch reels:', err);

      // Fallback to public mock when backend is unreachable
      try {
        const mockRes = await fetch('/mocks/reels.json', {
          headers: { 'Content-Type': 'application/json' }
        });
        if (mockRes.ok) {
          const mockData: FeedResponse = await mockRes.json();
          const convertedReels: ReelData[] = mockData.reels.map(backendReel => ({
            id: backendReel.id,
            title: backendReel.news_data?.title || 'Untitled',
            content: backendReel.news_data?.full_content || '',
            summary: backendReel.news_data?.summary || '',
            category: backendReel.news_data?.category || 'general',
            images: backendReel.news_data?.images || [],
            main_image: backendReel.news_data?.main_image || '',
            audio_url: backendReel.audio_url,
            subtitles: [],
            estimated_duration: backendReel.duration_seconds,
            tags: backendReel.news_data?.tags || [],
            author: backendReel.news_data?.author || '',
            location: backendReel.news_data?.location || ''
          }));

          if (isRefresh) {
            setReels(convertedReels);
            setCurrentIndex(0);
          } else {
            setReels(prev => [...prev, ...convertedReels]);
          }

          setCursor(mockData.pagination.next_cursor);
          setHasMore(mockData.pagination.has_next);
          setTotalAvailable(mockData.pagination.total_available);
          setFeedMetadata(mockData.feed_metadata);

          setError(null);
          return;
        }
      } catch (mockErr) {
        console.error('Failed to load mock reels:', mockErr);
      }

      const errorMessage = err instanceof Error ? err.message : 'Failed to load reels';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
      isLoadingRef.current = false;
    }
  }, [cursor, initialLimit]);
  
  const loadMore = useCallback(async (): Promise<void> => {
    if (!hasMore || isLoadingRef.current) {
      console.log(`⏭️ Skip loadMore: hasMore=${hasMore}, isLoading=${isLoadingRef.current}`);
      return;
    }
    // Only prefetch when within preloadThreshold of the end
    const distanceToEnd = reels.length - currentIndex - 1;
    if (distanceToEnd > preloadThreshold) {
      return;
    }
    // Throttle rapid loadMore calls
    const now = Date.now();
    if (now - lastLoadAtRef.current < LOAD_THROTTLE_MS) {
      console.log('⏳ Throttled loadMore');
      return;
    }
    lastLoadAtRef.current = now;

    console.log('📥 Loading more reels...');
    await fetchReels(false);
  }, [hasMore, fetchReels, reels.length, currentIndex, preloadThreshold]);
  
  const refreshFeed = useCallback(async (): Promise<void> => {
    console.log('🔄 Refreshing feed...');
    setCursor(null); // Reset cursor for fresh start
    await fetchReels(true);
  }, [fetchReels]);
  
  const goToNext = useCallback((): void => {
    const nextIndex = Math.min(currentIndex + 1, reels.length - 1);
    setCurrentIndex(nextIndex);
    
    // Auto-load more when approaching end
    const reelsRemaining = reels.length - nextIndex - 1;
    if (reelsRemaining <= preloadThreshold && hasMore && !isLoadingRef.current) {
      console.log(`🔄 Auto-loading: ${reelsRemaining} reels remaining`);
      loadMore();
    }
  }, [currentIndex, reels.length, preloadThreshold, hasMore, loadMore]);
  
  const goToPrev = useCallback((): void => {
    const prevIndex = Math.max(currentIndex - 1, 0);
    setCurrentIndex(prevIndex);
  }, [currentIndex]);
  
  return {
    // Data
    reels,
    currentIndex,
    loading,
    error,
    hasMore,
    
    // Pagination info
    totalAvailable,
    loadedCount: reels.length,
    feedMetadata,
    
    // Actions
    loadMore,
    refreshFeed,
    goToNext,
    goToPrev,
    
    // Internal state
    isLoadingMore
  };
};