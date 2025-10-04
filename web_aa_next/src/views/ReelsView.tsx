// src/views/ReelsView.tsx - Updated with Infinite Scroll & View Tracking

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useReelsViewModel } from '../viewmodels';
import { LoadingSpinner, Button, ReelItem } from '../components';
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
  const [incomingImageIndex, setIncomingImageIndex] = useState<number | null>(null);
  const [incomingDirection, setIncomingDirection] = useState<'left' | 'right' | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const currentReel = getCurrentReel();

  // Fullscreen UI state and bottom bar visibility
  const [isFullscreenControlsHidden, setIsFullscreenControlsHidden] = useState(false);
  // Remove auto-advance to improve UX and efficiency
  const handleAnyInteraction = () => {};
  
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
    const nextIdx = (currentImageIndex + 1) % currentReel.images.length;
    setIncomingImageIndex(nextIdx);
    setIncomingDirection('left');
    setTimeout(() => {
      setCurrentImageIndex(nextIdx);
      setIncomingImageIndex(null);
      setIncomingDirection(null);
    }, 300);
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length <= 1) return;
    const prevIdx = currentImageIndex === 0 ? currentReel.images.length - 1 : currentImageIndex - 1;
    setIncomingImageIndex(prevIdx);
    setIncomingDirection('right');
    setTimeout(() => {
      setCurrentImageIndex(prevIdx);
      setIncomingImageIndex(null);
      setIncomingDirection(null);
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

  // Gesture thresholds
  const H_SWIPE_THRESHOLD = 50; // px for horizontal image change
  const V_SWIPE_THRESHOLD = 50; // px for vertical reel change

  // Touch handlers: detect primary axis and trigger actions
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.touches[0];
    setTouchStartY(touch.clientY);
    setTouchStartX(touch.clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    // optional: prevent default to keep consistent feel
    e.preventDefault();
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.changedTouches[0];
    const deltaY = touch.clientY - touchStartY;
    const deltaX = touch.clientX - touchStartX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);

    if (absDeltaY < V_SWIPE_THRESHOLD && absDeltaX < H_SWIPE_THRESHOLD) return;

    if (absDeltaY > absDeltaX) {
      // Vertical: reel navigation
      if (deltaY > 0) {
        animatedPrevReel();
      } else {
        animatedNextReel();
      }
    } else {
      // Horizontal: image navigation
      if (deltaX > 0) {
        prevImage();
      } else {
        nextImage();
      }
    }
  };

  // Mouse handlers: simple swipe on mouse up based on delta
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setMouseStartY(e.clientY);
    setTouchStartY(e.clientY);
    setMouseStartX(e.clientX);
    setTouchStartX(e.clientX);
    setIsMouseDown(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isMouseDown) return;
    // no-op for now; using mouse up for decision
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (!isMouseDown) return;
    e.preventDefault();
    const deltaY = e.clientY - touchStartY;
    const deltaX = e.clientX - touchStartX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);

    if (absDeltaY >= V_SWIPE_THRESHOLD || absDeltaX >= H_SWIPE_THRESHOLD) {
      if (absDeltaY > absDeltaX) {
        if (deltaY > 0) animatedPrevReel(); else animatedNextReel();
      } else {
        if (deltaX > 0) prevImage(); else nextImage();
      }
    }
    setIsMouseDown(false);
  };

  // Wheel handler: vertical only (like Shorts)
  const wheelAccumRef = useRef(0);
  const WHEEL_THRESHOLD = 80; // daha kullanıcı dostu eşik
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    wheelAccumRef.current += e.deltaY;
    if (Math.abs(wheelAccumRef.current) < WHEEL_THRESHOLD) return;
    if (wheelAccumRef.current > 0) {
      animatedNextReel();
    } else {
      animatedPrevReel();
    }
    wheelAccumRef.current = 0; // sıfırla (throttle)
  };

  // Prevent body scroll when Reels is mounted
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    const originalHeight = document.body.style.height;
    document.body.style.overflow = 'hidden';
    document.body.style.height = '100vh';
    return () => {
      document.body.style.overflow = originalOverflow;
      document.body.style.height = originalHeight;
    };
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          animatedPrevReel();
          break;
        case 'ArrowDown':
          e.preventDefault();
          animatedNextReel();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          prevImage();
          break;
        case 'ArrowRight':
          e.preventDefault();
          nextImage();
          break;
        case ' ':
          e.preventDefault();
          togglePlayPause();
          break;
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [animatedNextReel, animatedPrevReel, nextImage, prevImage, togglePlayPause]);

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
      className="fixed inset-0 bg-black overflow-hidden select-none reels-container"
      style={{ 
        userSelect: 'none', 
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none',
        width: '100vw',
        height: '100vh',
        top: 0,
        left: 0
      } as React.CSSProperties}
      onTouchStart={(e) => { handleAnyInteraction(); handleTouchStart(e); }}
      onTouchMove={(e) => { handleAnyInteraction(); handleTouchMove(e); }}
      onTouchEnd={(e) => { handleAnyInteraction(); handleTouchEnd(e); }}
      onMouseDown={(e) => { handleAnyInteraction(); handleMouseDown(e); }}
      onMouseMove={(e) => { handleAnyInteraction(); handleMouseMove(e); }}
      onMouseUp={(e) => { handleAnyInteraction(); handleMouseUp(e); }}
      onWheel={(e) => { handleAnyInteraction(); handleWheel(e); }}
      onContextMenu={(e) => e.preventDefault()}
    >
      {/* UI toggle removed */}

      {/* YouTube Shorts Style Container */}
      <div className="relative h-full w-full">
        
        {/* Previous Reel (Behind) */}
        {prevReelData && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateY(${100 + slideOffset.y + (isMouseDown ? Math.max(0, mouseStartY - mouseStartY) : 0)}%)`,
              transition: isMouseDown ? 'none' : (isTransitioning ? 'transform 0.3s ease-out' : 'none'),
              zIndex: 1,
              opacity: isMouseDown ? Math.min(1, Math.max(0, mouseStartY - mouseStartY)) : 1
            }}
          >
            <ReelItem
              reel={{
                ...prevReelData,
                main_image: getReelImage(prevReelData)
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full opacity-50"
            />
          </div>
        )}

        {/* Side blurred previews (conditional) */}
        {currentReel?.images && currentReel.images.length > 0 && (
          <>
            {(() => {
              const imgCount = currentReel.images.length;
              const prevIdx = imgCount > 0 ? (currentImageIndex === 0 ? imgCount - 1 : currentImageIndex - 1) : 0;
              const nextIdx = imgCount > 0 ? ((currentImageIndex + 1) % imgCount) : 0;

              const isIncomingLeft = incomingDirection === 'right' && incomingImageIndex === prevIdx;
              const isIncomingRight = incomingDirection === 'left' && incomingImageIndex === nextIdx;

              const transition = 'transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), filter 0.45s, opacity 0.45s';

              const leftStyle: React.CSSProperties = isIncomingLeft
                ? {
                    transform: 'translateX(0%) rotateY(0deg) scale(1)',
                    filter: 'blur(0px)',
                    opacity: 1,
                    zIndex: 3,
                    transition
                  }
                : {
                    transform: 'translateX(-35%) rotateY(25deg) scale(0.9)',
                    filter: 'blur(8px)',
                    opacity: 0.35,
                    zIndex: 1,
                    transition
                  };

              const rightStyle: React.CSSProperties = isIncomingRight
                ? {
                    transform: 'translateX(0%) rotateY(0deg) scale(1)',
                    filter: 'blur(0px)',
                    opacity: 1,
                    zIndex: 3,
                    transition
                  }
                : {
                    transform: 'translateX(35%) rotateY(-25deg) scale(0.9)',
                    filter: 'blur(8px)',
                    opacity: 0.35,
                    zIndex: 1,
                    transition
                  };

              return (
                <>
                  {/* Left preview only if 2+ images */}
                  {imgCount > 1 && (
                    <ReelItem
                      reel={{
                        ...(currentReel || ({} as ReelData)),
                        main_image: getReelImage(currentReel as ReelData, prevIdx)
                      }}
                      isActive={false}
                      onPlay={() => {}}
                      onImageClick={() => {}}
                      className="absolute inset-0 w-full h-full"
                      style={leftStyle}
                    />
                  )}

                  {/* Right preview: always (if 1 image, shows same but blurred) */}
                  <ReelItem
                    reel={{
                      ...(currentReel || ({} as ReelData)),
                      main_image: getReelImage(currentReel as ReelData, nextIdx)
                    }}
                    isActive={false}
                    onPlay={() => {}}
                    onImageClick={() => {}}
                    className="absolute inset-0 w-full h-full"
                    style={rightStyle}
                  />
                  {/* Dots for current reel previews area (keeps old look) */}
                  <div className="absolute top-2 left-0 right-0 z-30 px-2 pointer-events-none">
                    <div className="flex space-x-1 max-w-sm mx-auto">
                      {currentReel.images.map((_, index) => (
                        <div
                          key={index}
                          className={`h-0.5 flex-1 rounded-full transition-all duration-300 ${
                            index === currentImageIndex
                              ? 'bg-white'
                              : index < currentImageIndex
                                ? 'bg-white/60'
                                : 'bg-white/20'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </>
              );
            })()}
          </>
        )}

        {/* Current Reel (Active) */}
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            transform: `translateY(${slideOffset.y}%)`,
            transition: isTransitioning ? 'transform 0.35s cubic-bezier(0.25, 0.8, 0.25, 1)' : 'none',
            zIndex: 4,
            perspective: '1200px',
            transformStyle: 'preserve-3d'
          }}
        >
          {currentReel && (
            <>
              {/* Foreground layer: circular slide out on horizontal change */}
              <ReelItem
                reel={{
                  ...(currentReel || ({} as ReelData)),
                  main_image: getReelImage(currentReel as ReelData, currentImageIndex)
                }}
                isActive={true}
                onPlay={togglePlayPause}
                onImageClick={togglePlayPause}
                className="absolute inset-0 w-full h-full"
                style={{
                  transform: incomingDirection
                    ? `translateX(${incomingDirection === 'left' ? '-35%' : '35%'}) rotateY(${incomingDirection === 'left' ? 25 : -25}deg) scale(0.9)`
                    : 'translateX(0%) rotateY(0deg) scale(1.2)',
                  filter: incomingDirection ? 'blur(8px)' : 'none',
                  opacity: incomingDirection ? 0.65 : 1,
                  transition: 'transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), filter 0.45s, opacity 0.45s',
                  boxShadow: '0 12px 36px rgba(0,0,0,0.4)'
                }}
              />
              {/* Dots for current reel (original place) */}
              {currentReel.images && currentReel.images.length > 1 && (
                <div className="absolute top-2 left-0 right-0 z-30 px-2 pointer-events-none">
                  <div className="flex space-x-1 max-w-sm mx-auto">
                    {currentReel.images.map((_, index) => (
                      <div
                        key={index}
                        className={`h-0.5 flex-1 rounded-full transition-all duration-300 ${
                          index === currentImageIndex 
                            ? 'bg-white' 
                            : index < currentImageIndex 
                              ? 'bg-white/60' 
                              : 'bg-white/20'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Next Reel (Front) */}
        {nextReelData && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateY(${-100 + slideOffset.y + (isMouseDown ? Math.min(0, mouseStartY - mouseStartY) : 0)}%)`,
              transition: isMouseDown ? 'none' : (isTransitioning ? 'transform 0.3s ease-out' : 'none'),
              zIndex: 1,
              opacity: isMouseDown ? Math.min(1, Math.max(0, -mouseStartY + mouseStartY)) : 1
            }}
          >
            <ReelItem
              reel={{
                ...nextReelData,
                main_image: getReelImage(nextReelData)
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full opacity-50"
            />
            {/* Dots for next reel preview */}
            {currentReel?.images && currentReel.images.length > 1 && (
              <div className="absolute top-2 left-0 right-0 z-30 px-2 pointer-events-none">
                <div className="flex space-x-1 max-w-sm mx-auto">
                  {currentReel.images.map((_, index) => (
                    <div
                      key={index}
                      className={`h-0.5 flex-1 rounded-full transition-all duration-300 ${
                        index === currentImageIndex 
                          ? 'bg-white' 
                          : index < currentImageIndex 
                            ? 'bg-white/60' 
                            : 'bg-white/20'
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Bottom progress removed */}

        {/* Stats Overlay removed per request */}

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
        
        {/* Global fixed dots removed to keep original look but present on all layers */}

      </div>
    </div>
  );
};