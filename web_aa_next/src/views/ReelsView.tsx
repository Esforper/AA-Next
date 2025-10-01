// src/views/ReelsView.tsx - Updated with Infinite Scroll & View Tracking

import React, { useState, useEffect, useRef } from 'react';
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
    const nextIdx = (currentImageIndex + 1) % currentReel.images.length;
    setIncomingImageIndex(nextIdx);
    setIncomingDirection('left');
    // After brief transition, commit switch
    setTimeout(() => {
      setCurrentImageIndex(nextIdx);
      setIncomingImageIndex(null);
      setIncomingDirection(null);
      setIsTransitioning(false);
    }, 250);
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length <= 1) return;
    if (isTransitioning) return;
    setIsTransitioning(true);
    const prevIdx = currentImageIndex === 0 ? currentReel.images.length - 1 : currentImageIndex - 1;
    setIncomingImageIndex(prevIdx);
    setIncomingDirection('right');
    setTimeout(() => {
      setCurrentImageIndex(prevIdx);
      setIncomingImageIndex(null);
      setIncomingDirection(null);
      setIsTransitioning(false);
    }, 250);
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

        {/* Left Preview Image - Instagram Stories Style */}
        {currentReel?.images && currentReel.images.length > 1 && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateX(-20%) scale(0.85)`,
              zIndex: 1,
              filter: 'blur(3px)',
              opacity: 0.3
            }}
          >
            <ReelItem
              reel={{
                ...(currentReel || ({} as ReelData)),
                main_image: getReelImage(currentReel as ReelData, currentImageIndex === 0 ? (currentReel!.images.length - 1) : (currentImageIndex - 1))
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full"
            />
          </div>
        )}

        {/* Right Preview Image - Instagram Stories Style */}
        {currentReel?.images && currentReel.images.length > 1 && (
          <div 
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `translateX(20%) scale(0.85)`,
              zIndex: 1,
              filter: 'blur(3px)',
              opacity: 0.3
            }}
          >
            <ReelItem
              reel={{
                ...(currentReel || ({} as ReelData)),
                main_image: getReelImage(currentReel as ReelData, (currentImageIndex + 1) % (currentReel!.images.length))
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full"
            />
          </div>
        )}

        {/* Current Reel (Active) */}
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            transform: `translate(0%, ${slideOffset.y}%)`,
            transition: isTransitioning ? 'all 0.25s ease-out' : 'none',
            zIndex: 2,
            perspective: '1200px'
          }}
        >
          {currentReel && currentReel.images && currentReel.images.length > 0 ? (
            <>
              {(() => {
                const count = currentReel.images.length;
                const leftIdx = (currentImageIndex - 1 + count) % count;
                const centerIdx = currentImageIndex;
                const rightIdx = (currentImageIndex + 1) % count;

                const baseLeft = { tx: -30, scale: 0.9, blur: 6, rotY: 15, z: 1 };
                const baseCenter = { tx: 0, scale: 1, blur: 0, rotY: 0, z: 3 };
                const baseRight = { tx: 30, scale: 0.9, blur: 6, rotY: -15, z: 2 };

                let left = { ...baseLeft };
                let center = { ...baseCenter };
                let right = { ...baseRight };

                if (isTransitioning && incomingDirection === 'right') {
                  // Move left -> center, center -> right
                  left = { ...baseCenter };
                  center = { ...baseRight };
                  right = { ...baseRight };
                } else if (isTransitioning && incomingDirection === 'left') {
                  // Move right -> center, center -> left
                  right = { ...baseCenter };
                  center = { ...baseLeft };
                  left = { ...baseLeft };
                }

                const styleFor = (slot: typeof baseCenter) => ({
                  transform: `translateX(${slot.tx}%) scale(${slot.scale}) rotateY(${slot.rotY}deg)`,
                  filter: `blur(${slot.blur}px)`,
                  transition: 'transform 0.25s ease-out, filter 0.25s ease-out',
                  zIndex: slot.z as unknown as number,
                  boxShadow: slot.blur === 0 ? '0 10px 30px rgba(0,0,0,0.35)' : 'none'
                } as React.CSSProperties);

                return (
                  <>
                    {/* LEFT (prev) */}
                    <ReelItem
                      reel={{
                        ...(currentReel || ({} as ReelData)),
                        main_image: getReelImage(currentReel as ReelData, leftIdx)
                      }}
                      isActive={false}
                      onPlay={() => {}}
                      onImageClick={() => {}}
                      className="absolute inset-0 w-full h-full"
                      style={styleFor(left)}
                    />

                    {/* CENTER (current) */}
                    <ReelItem
                      reel={{
                        ...(currentReel || ({} as ReelData)),
                        main_image: getReelImage(currentReel as ReelData, centerIdx)
                      }}
                      isActive={true}
                      onPlay={togglePlayPause}
                      onImageClick={togglePlayPause}
                      className="absolute inset-0 w-full h-full"
                      style={styleFor(center)}
                    />

                    {/* RIGHT (next) */}
                    <ReelItem
                      reel={{
                        ...(currentReel || ({} as ReelData)),
                        main_image: getReelImage(currentReel as ReelData, rightIdx)
                      }}
                      isActive={false}
                      onPlay={() => {}}
                      onImageClick={() => {}}
                      className="absolute inset-0 w-full h-full"
                      style={styleFor(right)}
                    />

                    {/* Overlay for readability */}
                    <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 4 }}>
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
                    </div>
                  </>
                );
              })()}
            </>
          ) : (
            // Fallback single image
            <ReelItem
              reel={{
                ...(currentReel || ({} as ReelData)),
                main_image: getReelImage(currentReel as ReelData, 0)
              }}
              isActive={true}
              onPlay={togglePlayPause}
              onImageClick={togglePlayPause}
              className="absolute inset-0 w-full h-full"
            />
          )}
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
        
        {/* Image Navigation Dots */}
        {currentReel?.images && currentReel.images.length > 1 && (
          <div className="absolute top-2 left-0 right-0 z-30 px-2">
            <div className="flex space-x-1">
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
    </div>
  );
};