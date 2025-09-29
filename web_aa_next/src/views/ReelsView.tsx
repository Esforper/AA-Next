// src/views/ReelsView.tsx - Updated with Infinite Scroll & View Tracking

import React, { useState, useEffect, useRef } from 'react';
import { useReelsViewModel } from '../viewmodels';
import { LoadingSpinner, Button } from '../components';
import { ReelData } from '../models';

export const ReelsView: React.FC = () => {
  const {
    reels,
    currentReelIndex,
    loading,
    error,
    audioState,
    hasMore,
    isLoadingMore,
    totalAvailable,
    loadedCount,
    nextReel,
    prevReel,
    togglePlayPause,
    fetchReels,
    loadMore,
    getTotalViewTime,
    getCurrentReel
  } = useReelsViewModel();

  // UI State
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [touchStartY, setTouchStartY] = useState(0);
  const [touchStartX, setTouchStartX] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  const [mouseStartY, setMouseStartY] = useState(0);
  const [mouseStartX, setMouseStartX] = useState(0);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<'up' | 'down' | 'left' | 'right' | null>(null);
  const [slideOffset, setSlideOffset] = useState({ x: 0, y: 0 });
  const [imageAnimation, setImageAnimation] = useState<'slide-left-in' | 'slide-right-in' | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const currentReel = getCurrentReel();
  
  // Progress tracking
  const [viewStartTime, setViewStartTime] = useState<number | null>(null);

  // Calculate next and previous reels for preview
  const getNextReel = () => {
    if (currentReelIndex < reels.length - 1) {
      return reels[currentReelIndex + 1];
    }
    return null;
  };

  const getPrevReel = () => {
    if (currentReelIndex > 0) {
      return reels[currentReelIndex - 1];
    }
    return null;
  };

  // Get current image to display
  const getCurrentImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0) {
      return currentReel?.main_image || '';
    }
    return currentReel.images[currentImageIndex] || currentReel.main_image || '';
  };

  // Get current image for a specific reel
  const getReelImage = (reel: ReelData, imageIndex: number = 0) => {
    if (!reel?.images || reel.images.length === 0) {
      return reel?.main_image || '';
    }
    return reel.images[imageIndex] || reel.main_image || '';
  };

  // Handle image navigation
  const nextImage = () => {
    if (!currentReel?.images || currentReel.images.length <= 1) return;
    
    if (isTransitioning) return;
    setIsTransitioning(true);
    setImageAnimation('slide-left-in');
    setSlideOffset({ x: 100, y: 0 });
    
    setTimeout(() => {
      setCurrentImageIndex(prev => 
        prev === currentReel.images.length - 1 ? 0 : prev + 1
      );
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
      setImageAnimation(null);
    }, 300);
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length <= 1) return;
    
    if (isTransitioning) return;
    setIsTransitioning(true);
    setImageAnimation('slide-right-in');
    setSlideOffset({ x: -100, y: 0 });
    
    setTimeout(() => {
      setCurrentImageIndex(prev => 
        prev === 0 ? currentReel.images.length - 1 : prev - 1
      );
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
      setImageAnimation(null);
    }, 300);
  };

  // YouTube Shorts style navigation with infinite scroll
  const animatedNextReel = async () => {
    if (isTransitioning) return;
    
    // Check if we need to load more reels
    if (currentReelIndex >= reels.length - 3 && hasMore && !isLoadingMore) {
      console.log('🔄 Auto-loading more reels before navigation');
      await loadMore();
    }
    
    if (currentReelIndex >= reels.length - 1) {
      console.log('🔚 No more reels to show');
      return;
    }
    
    setIsTransitioning(true);
    setSwipeDirection('up');
    setSlideOffset({ x: 0, y: -100 });
    
    setTimeout(() => {
      nextReel();
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
    }, 300);
  };

  const animatedPrevReel = () => {
    if (isTransitioning) return;
    if (currentReelIndex <= 0) return;
    
    setIsTransitioning(true);
    setSwipeDirection('down');
    setSlideOffset({ x: 0, y: 100 });
    
    setTimeout(() => {
      prevReel();
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
    }, 300);
  };

  // Reset image index when reel changes
  useEffect(() => {
    setCurrentImageIndex(0);
    setViewStartTime(Date.now());
  }, [currentReelIndex]);

  // Touch event handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.touches[0];
    setTouchStartY(touch.clientY);
    setTouchStartX(touch.clientX);
    setIsScrolling(false);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.touches[0];
    const deltaY = touch.clientY - touchStartY;
    const deltaX = touch.clientX - touchStartX;
    
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    if (absDeltaY > 10 || absDeltaX > 10) {
      if (absDeltaY > absDeltaX) {
        setIsScrolling(true); // Vertical scroll
      } else {
        setIsScrolling(false); // Horizontal scroll
      }
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    
    const touch = e.changedTouches[0];
    const deltaY = touch.clientY - touchStartY;
    const deltaX = touch.clientX - touchStartX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    const minSwipeDistance = 50;
    
    if (absDeltaY < minSwipeDistance && absDeltaX < minSwipeDistance) {
      return;
    }
    
    if (absDeltaY > absDeltaX) {
      // Vertical swipe - Reels navigation
      if (deltaY > 0) {
        animatedPrevReel();
      } else {
        animatedNextReel();
      }
    } else {
      // Horizontal swipe - Image navigation
      if (deltaX > 0) {
        prevImage();
      } else {
        nextImage();
      }
    }
  };

  // Mouse event handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setMouseStartY(e.clientY);
    setMouseStartX(e.clientX);
    setIsMouseDown(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isMouseDown) return;
    e.preventDefault();
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (!isMouseDown) return;
    e.preventDefault();
    
    const deltaY = e.clientY - mouseStartY;
    const deltaX = e.clientX - mouseStartX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    const minSwipeDistance = 50;
    
    if (absDeltaY < minSwipeDistance && absDeltaX < minSwipeDistance) {
      setIsMouseDown(false);
      return;
    }
    
    if (absDeltaY > absDeltaX) {
      if (deltaY > 0) {
        animatedPrevReel();
      } else {
        animatedNextReel();
      }
    } else {
      if (deltaX > 0) {
        prevImage();
      } else {
        nextImage();
      }
    }
    
    setIsMouseDown(false);
  };

  // Wheel event handler
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    const deltaY = e.deltaY;
    const deltaX = e.deltaX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    if (absDeltaY > absDeltaX) {
      if (deltaY > 0) {
        animatedNextReel();
      } else {
        animatedPrevReel();
      }
    } else {
      if (deltaX > 0) {
        nextImage();
      } else {
        prevImage();
      }
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          animatedPrevReel();
          break;
        case 'ArrowDown':
          e.preventDefault();
          animatedNextReel();
          break;
        case ' ':
          e.preventDefault();
          togglePlayPause();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          prevImage();
          break;
        case 'ArrowRight':
          e.preventDefault();
          nextImage();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Loading state
  if (loading && reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
        <LoadingSpinner size="lg" className="text-white mb-4" />
        <p className="text-lg animate-pulse">Loading reels from RSS feeds...</p>
        <p className="text-sm text-gray-400 mt-2">Getting latest news...</p>
      </div>
    );
  }

  // Error state
  if (error && reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white px-4">
        <div className="text-center animate-fade-in">
          <h2 className="text-xl font-semibold mb-2 animate-bounce">
            Cannot Load Reels
          </h2>
          <p className="text-gray-300 mb-4 animate-pulse">{error}</p>
          <Button 
            onClick={fetchReels} 
            variant="primary"
            className="animate-pulse hover:animate-none"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  // No reels state
  if (reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
        <p className="text-lg">No reels available</p>
        <p className="text-sm text-gray-400 mt-2">Check back later for new content</p>
        <Button 
          onClick={fetchReels} 
          variant="primary"
          className="mt-4"
        >
          Refresh
        </Button>
      </div>
    );
  }

  const nextReelData = getNextReel();
  const prevReelData = getPrevReel();

  return (
    <div 
      ref={containerRef}
      className="relative h-screen bg-black overflow-hidden select-none reels-container"
      style={{
        userSelect: 'none', 
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none',
        minHeight: '100dvh'
      } as React.CSSProperties}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      onContextMenu={(e) => e.preventDefault()}
    >
      {/* YouTube Shorts Style Container */}
      <div className="relative h-full w-full">
        
        {/* Previous Reel (Behind) */}
        {prevReelData && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateY(${100 + slideOffset.y}%)`,
              transition: isTransitioning ? 'transform 0.3s ease-out' : 'none',
              zIndex: 1
            }}
          >
            <div className="relative h-full w-full">
              <img
                src={getReelImage(prevReelData)}
                alt={prevReelData.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />
            </div>
          </div>
        )}

        {/* Current Reel (Active) */}
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            transform: `translateY(${slideOffset.y}%)`,
            transition: isTransitioning ? 'transform 0.3s ease-out' : 'none',
            zIndex: 2
          }}
        >
          <div className="relative h-full w-full">
            {/* Background Image with Animation */}
            <div className="relative h-full w-full overflow-hidden">
              <img
                key={`${currentReel?.id}-${currentImageIndex}`}
                src={getCurrentImage()}
                alt={currentReel?.title || 'Reel image'}
                className={`w-full h-full object-cover transition-transform duration-500 ${
                  imageAnimation === 'slide-left-in' ? 'animate-slide-left-in' : ''
                } ${
                  imageAnimation === 'slide-right-in' ? 'animate-slide-right-in' : ''
                }`}
                style={{
                  transform: `translateX(${slideOffset.x}%)`
                }}
              />
            </div>

            {/* Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40" />
            
            {/* Content Overlay */}
            <div className="absolute inset-0 flex flex-col justify-end p-4 md:p-6 text-white">
              
              {/* Main Content */}
              <div className="space-y-3 max-w-2xl">
                <h1 className="text-lg md:text-2xl font-bold leading-tight">
                  {currentReel?.title}
                </h1>
                
                {currentReel?.summary && (
                  <p className="text-sm md:text-base text-gray-200 leading-relaxed line-clamp-3">
                    {currentReel.summary}
                  </p>
                )}
                
                {/* Metadata */}
                <div className="flex items-center space-x-4 text-xs text-gray-300">
                  {currentReel?.category && (
                    <span className="px-2 py-1 bg-white/20 rounded-full">
                      #{currentReel.category}
                    </span>
                  )}
                  {currentReel?.author && (
                    <span>📝 {currentReel.author}</span>
                  )}
                  {currentReel?.location && (
                    <span>📍 {currentReel.location}</span>
                  )}
                </div>
                
                {/* Audio Controls */}
                <div className="flex items-center space-x-4">
                  <button
                    onClick={togglePlayPause}
                    className="bg-white/20 backdrop-blur-lg rounded-full p-3 hover:bg-white/30 transition-colors"
                  >
                    {audioState.isPlaying ? (
                      <span className="text-2xl">⏸️</span>
                    ) : (
                      <span className="text-2xl">▶️</span>
                    )}
                  </button>
                  
                  {audioState.isLoaded && (
                    <div className="flex-1 text-xs text-gray-300">
                      <div className="flex justify-between mb-1">
                        <span>{Math.floor(audioState.position)}s</span>
                        <span>{Math.floor(audioState.duration)}s</span>
                      </div>
                      <div className="w-full bg-gray-600 rounded-full h-1">
                        <div
                          className="bg-white h-1 rounded-full transition-all duration-100"
                          style={{
                            width: `${(audioState.position / audioState.duration) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Image Navigation Dots */}
            {currentReel?.images && currentReel.images.length > 1 && (
              <div className="absolute top-4 left-1/2 transform -translate-x-1/2 flex space-x-2 z-10">
                {currentReel.images.map((_, index) => (
                  <div
                    key={index}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentImageIndex 
                        ? 'bg-white' 
                        : index < currentImageIndex 
                          ? 'bg-white/60' 
                          : 'bg-white/20'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Next Reel (Front) */}
        {nextReelData && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateY(${-100 + slideOffset.y}%)`,
              transition: isTransitioning ? 'transform 0.3s ease-out' : 'none',
              zIndex: 1
            }}
          >
            <div className="relative h-full w-full">
              <img
                src={getReelImage(nextReelData)}
                alt={nextReelData.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />
            </div>
          </div>
        )}

        {/* Infinite Scroll Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 pointer-events-auto">
          <div className="h-1 bg-black/20">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-700 ease-out"
              style={{ 
                width: totalAvailable > 0 
                  ? `${(loadedCount / totalAvailable) * 100}%` 
                  : `${((currentReelIndex + 1) / Math.max(reels.length, 1)) * 100}%`
              }}
            />
          </div>
        </div>

        {/* Stats Overlay (Debug) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="absolute top-4 right-4 text-xs text-white/60 bg-black/50 p-2 rounded">
            <div>Reel: {currentReelIndex + 1}/{reels.length}</div>
            <div>Loaded: {loadedCount}/{totalAvailable}</div>
            <div>Has More: {hasMore ? 'Yes' : 'No'}</div>
            <div>Loading: {isLoadingMore ? 'Yes' : 'No'}</div>
            <div>View Time: {Math.floor(getTotalViewTime() / 1000)}s</div>
          </div>
        )}

        {/* Loading More Indicator */}
        {isLoadingMore && (
          <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 bg-black/60 backdrop-blur-lg rounded-full px-4 py-2 text-white text-sm">
            <div className="flex items-center space-x-2">
              <LoadingSpinner size="sm" />
              <span>Loading more reels...</span>
            </div>
          </div>
        )}

        {/* Navigation Hints - Desktop */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 pointer-events-none hidden lg:block">
          <div className="bg-black/40 backdrop-blur-lg rounded-full px-4 py-2 text-white/80 text-xs font-medium border border-white/20">
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1">
                <span>↑↓</span>
                <span>Reels</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <span>←→</span>
                <span>Images</span>
              </span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <span>Space</span>
                <span>Play/Pause</span>
              </span>
            </div>
          </div>
        </div>

        {/* Swipe Indicators - Mobile */}
        <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 pointer-events-none sm:hidden">
          <div className="flex space-x-2">
            <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce"></div>
            <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
        
      </div>
    </div>
  );
};