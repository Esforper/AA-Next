import React, { useState, useEffect, useRef } from 'react';
import { useReelsViewModel } from '../viewmodels';
import { ReelItem, LoadingSpinner, Button } from '../components';
import { ReelData } from '../models';

export const ReelsView: React.FC = () => {
  const {
    reels,
    currentReelIndex,
    loading,
    error,
    audioState,
    nextReel,
    prevReel,
    togglePlayPause,
    fetchReels
  } = useReelsViewModel();

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
  const [nextReelData, setNextReelData] = useState<ReelData | null>(null);
  const [prevReelData, setPrevReelData] = useState<ReelData | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const currentReel = reels[currentReelIndex];

  // Calculate next and previous reels for preview
  const getNextReel = () => {
    const nextIndex = (currentReelIndex + 1) % reels.length;
    return reels[nextIndex] || null;
  };

  const getPrevReel = () => {
    const prevIndex = (currentReelIndex - 1 + reels.length) % reels.length;
    return reels[prevIndex] || null;
  };

  // Update preview reels when current reel changes
  useEffect(() => {
    setNextReelData(getNextReel());
    setPrevReelData(getPrevReel());
  }, [currentReelIndex, reels]);


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

  // Handle image navigation with slide animations
  const nextImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0 || isTransitioning) return;
    setIsTransitioning(true);
    setSwipeDirection('left');
    setSlideOffset({ x: -100, y: 0 });
    
    setTimeout(() => {
      setCurrentImageIndex((prev) => (prev + 1) % currentReel.images.length);
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
    }, 300);
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0 || isTransitioning) return;
    setIsTransitioning(true);
    setSwipeDirection('right');
    setSlideOffset({ x: 100, y: 0 });
    
    setTimeout(() => {
      setCurrentImageIndex((prev) => 
        prev === 0 ? currentReel.images.length - 1 : prev - 1
      );
      setSlideOffset({ x: 0, y: 0 });
      setIsTransitioning(false);
      setSwipeDirection(null);
    }, 300);
  };

  // YouTube Shorts style navigation
  const animatedNextReel = () => {
    if (isTransitioning) return;
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
  }, [currentReelIndex]);

  // Update preview reels when current reel changes
  useEffect(() => {
    setNextReelData(getNextReel());
    setPrevReelData(getPrevReel());
  }, [currentReelIndex, reels]);

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
    
    // Determine scroll direction with better logic
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    // If movement is significant, determine direction
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
    
    // Minimum swipe distance
    const minSwipeDistance = 50;
    
    // Check if it's a valid swipe
    if (absDeltaY < minSwipeDistance && absDeltaX < minSwipeDistance) {
      return; // Not a valid swipe
    }
    
    // Determine primary direction
    if (absDeltaY > absDeltaX) {
      // Vertical swipe - Reels navigation
      if (deltaY > 0) {
        // Swipe down - Previous reel
        animatedPrevReel();
      } else {
        // Swipe up - Next reel
        animatedNextReel();
      }
    } else {
      // Horizontal swipe - Image navigation
      if (deltaX > 0) {
        // Swipe right - Previous image
        prevImage();
      } else {
        // Swipe left - Next image
        nextImage();
      }
    }
  };

  // Mouse event handlers for desktop
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
    
    // Minimum swipe distance
    const minSwipeDistance = 50;
    
    // Check if it's a valid swipe
    if (absDeltaY < minSwipeDistance && absDeltaX < minSwipeDistance) {
      setIsMouseDown(false);
      return; // Not a valid swipe
    }
    
    // Determine primary direction
    if (absDeltaY > absDeltaX) {
      // Vertical swipe - Reels navigation
      if (deltaY > 0) {
        // Swipe down - Previous reel
        animatedPrevReel();
      } else {
        // Swipe up - Next reel
        animatedNextReel();
      }
    } else {
      // Horizontal swipe - Image navigation
      if (deltaX > 0) {
        // Swipe right - Previous image
        prevImage();
      } else {
        // Swipe left - Next image
        nextImage();
      }
    }
    
    setIsMouseDown(false);
  };

  // Wheel event handler for mouse wheel scrolling
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    const deltaY = e.deltaY;
    const deltaX = e.deltaX;
    const absDeltaY = Math.abs(deltaY);
    const absDeltaX = Math.abs(deltaX);
    
    // Determine primary direction
    if (absDeltaY > absDeltaX) {
      // Vertical wheel - Reels navigation
      if (deltaY > 0) {
        // Wheel down - Next reel
        animatedNextReel();
      } else {
        // Wheel up - Previous reel
        animatedPrevReel();
      }
    } else {
      // Horizontal wheel - Image navigation
      if (deltaX > 0) {
        // Wheel right - Next image
        nextImage();
      } else {
        // Wheel left - Previous image
        prevImage();
      }
    }
  };

  // Handle keyboard navigation
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
  }, [prevReel, nextReel, togglePlayPause, prevImage, nextImage]);

  if (loading && reels.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black">
        <div className="animate-pulse">
          <LoadingSpinner size="lg" className="text-white" />
        </div>
      </div>
    );
  }

  if (error && reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white px-4">
        <div className="text-center animate-fade-in">
          <h2 className="text-xl font-semibold mb-2 animate-bounce">
            Reels Yüklenemedi
          </h2>
          <p className="text-gray-300 mb-4 animate-pulse">{error}</p>
          <Button 
            onClick={fetchReels} 
            variant="primary"
            className="animate-pulse hover:animate-none"
          >
            Tekrar Dene
          </Button>
        </div>
      </div>
    );
  }

  if (reels.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black text-white">
        <p>Henüz reel bulunmuyor</p>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="relative h-screen bg-black overflow-hidden select-none reels-container"
      style={{
        userSelect: 'none', 
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none'
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
                main_image: getReelImage(prevReelData, 0)
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full opacity-50"
            />
          </div>
        )}

        {/* Current Reel (Main) */}
        <div 
          className={`absolute inset-0 w-full h-full ${
            isTransitioning && swipeDirection === 'left' ? 'animate-slide-left-out' :
            isTransitioning && swipeDirection === 'right' ? 'animate-slide-right-out' :
            ''
          }`}
          style={{
            transform: `translate(${slideOffset.x}%, ${slideOffset.y}%)`,
            transition: isTransitioning ? 'transform 0.3s ease-out' : 'none',
            zIndex: 2
          }}
        >
          <ReelItem
            reel={{
              ...currentReel,
              main_image: getCurrentImage()
            }}
            isActive={true}
            onPlay={togglePlayPause}
            onImageClick={togglePlayPause}
            className="absolute inset-0 w-full h-full"
          />
        </div>

        {/* Next Reel (Behind) */}
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
                main_image: getReelImage(nextReelData, 0)
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full opacity-50"
            />
          </div>
        )}



        {/* UI Overlay - Fixed Position */}
        <div className="absolute inset-0 z-30 pointer-events-none">
          {/* Reel Counter */}
          <div className="absolute top-4 left-4 pointer-events-auto">
            <div className="bg-black bg-opacity-70 rounded-full px-3 py-1 text-white text-sm backdrop-blur-sm">
              {currentReelIndex + 1} / {reels.length}
            </div>
          </div>

          {/* Image Indicators */}
          {currentReel?.images && currentReel.images.length > 1 && (
            <div className="absolute top-4 right-4 pointer-events-auto">
              <div className="bg-black bg-opacity-70 rounded-full px-3 py-1 text-white text-sm backdrop-blur-sm">
                {currentImageIndex + 1} / {currentReel.images.length}
              </div>
            </div>
          )}

          {/* Image Dots */}
          {currentReel?.images && currentReel.images.length > 1 && (
            <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 pointer-events-auto">
              <div className="flex space-x-2">
                {currentReel.images.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentImageIndex 
                        ? 'bg-white scale-125' 
                        : 'bg-white bg-opacity-50 scale-100'
                    }`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};