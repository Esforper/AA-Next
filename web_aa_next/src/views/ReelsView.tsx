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
  const [imageAnimation, setImageAnimation] = useState<'slide-left-in' | 'slide-right-in' | null>(null);
  
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

  // Handle image navigation with side-by-side slide animations
  const nextImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0 || isTransitioning) return;
    setIsTransitioning(true);
    setSwipeDirection('left');
    setImageAnimation('slide-left-in');
    
    // Start sliding current image out to left
    setSlideOffset({ x: -100, y: 0 });
    
    setTimeout(() => {
      // Change image and start sliding new image in from right
      setCurrentImageIndex((prev) => (prev + 1) % currentReel.images.length);
      setSlideOffset({ x: 100, y: 0 }); // New image starts from right
      
      // Smooth slide new image to center
      setTimeout(() => {
        setSlideOffset({ x: 0, y: 0 }); // New image slides to center
        setIsTransitioning(false);
        setSwipeDirection(null);
        setImageAnimation(null);
      }, 100); // Longer delay for smoother transition
    }, 400); // Slower, more user-friendly timing
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0 || isTransitioning) return;
    setIsTransitioning(true);
    setSwipeDirection('right');
    setImageAnimation('slide-right-in');
    
    // Start sliding current image out to right
    setSlideOffset({ x: 100, y: 0 });
    
    setTimeout(() => {
      // Change image and start sliding new image in from left
      setCurrentImageIndex((prev) => 
        prev === 0 ? currentReel.images.length - 1 : prev - 1
      );
      setSlideOffset({ x: -100, y: 0 }); // New image starts from left
      
      // Smooth slide new image to center
      setTimeout(() => {
        setSlideOffset({ x: 0, y: 0 }); // New image slides to center
        setIsTransitioning(false);
        setSwipeDirection(null);
        setImageAnimation(null);
      }, 100); // Longer delay for smoother transition
    }, 400); // Slower, more user-friendly timing
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
        WebkitTouchCallout: 'none',
        minHeight: '100dvh' // Dynamic viewport height for mobile
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
                ...currentReel,
                main_image: getReelImage(currentReel, currentImageIndex === 0 ? currentReel.images.length - 1 : currentImageIndex - 1)
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
                ...currentReel,
                main_image: getReelImage(currentReel, (currentImageIndex + 1) % currentReel.images.length)
              }}
              isActive={false}
              onPlay={() => {}}
              onImageClick={() => {}}
              className="absolute inset-0 w-full h-full"
            />
          </div>
        )}

        {/* Current Reel (Main) - Enhanced with Overflow Blur */}
        <div 
          className={`absolute inset-0 w-full h-full ${
            isTransitioning && swipeDirection === 'left' ? 'animate-slide-left-out' :
            isTransitioning && swipeDirection === 'right' ? 'animate-slide-right-out' :
            ''
          }`}
          style={{
            transform: `translate(${slideOffset.x}%, ${slideOffset.y}%) scale(${isTransitioning ? 0.98 : 1})`,
            transition: isTransitioning ? 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none',
            zIndex: 2,
            filter: isTransitioning ? 'blur(0.3px)' : 'blur(0px)'
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
            className={`absolute inset-0 w-full h-full ${
              imageAnimation ? `animate-${imageAnimation}` : ''
            }`}
          />
          
          {/* Enhanced Edge Blur Effects - YouTube Shorts Style */}
          <div className="absolute inset-0 pointer-events-none z-10">
            {/* Left Edge Blur - Enhanced */}
            <div 
              className="absolute left-0 top-0 w-16 h-full"
              style={{
                background: 'linear-gradient(90deg, rgba(0,0,0,0.3) 0%, transparent 100%)',
                filter: 'blur(2px)'
              }}
            />
            
            {/* Right Edge Blur - Enhanced */}
            <div 
              className="absolute right-0 top-0 w-16 h-full"
              style={{
                background: 'linear-gradient(270deg, rgba(0,0,0,0.3) 0%, transparent 100%)',
                filter: 'blur(2px)'
              }}
            />
            
            {/* Top Edge Blur - Instagram Stories Style */}
            <div 
              className="absolute top-0 left-0 right-0 h-20"
              style={{
                background: 'linear-gradient(180deg, rgba(0,0,0,0.2) 0%, transparent 100%)',
                filter: 'blur(1px)'
              }}
            />
          </div>
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



        {/* Modern UI Overlay - YouTube Shorts & Instagram Style */}
        <div className="absolute inset-0 z-30 pointer-events-none">
          {/* Top Status Bar - YouTube Shorts Style */}
          <div className="absolute top-0 left-0 right-0 pointer-events-none">
            {/* Progress Indicators for Multiple Images */}
            {currentReel?.images && currentReel.images.length > 1 && (
              <div className="flex space-x-1 p-2">
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
            )}
          </div>


          {/* Bottom Progress Bar - YouTube Shorts Style */}
          <div className="absolute bottom-0 left-0 right-0 pointer-events-auto">
            <div className="h-1 bg-black/20">
              <div 
                className="h-full bg-gradient-to-r from-red-500 via-pink-500 to-purple-500 transition-all duration-700 ease-out shadow-lg"
                style={{ width: `${((currentReelIndex + 1) / reels.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Navigation Controls - Desktop Only */}
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
              </div>
            </div>
          </div>

          {/* Swipe Indicators - Mobile Only */}
          <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 pointer-events-none sm:hidden">
            <div className="flex space-x-2">
              <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce"></div>
              <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-1 h-1 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};