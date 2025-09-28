import React, { useState, useEffect, useRef } from 'react';
import { useReelsViewModel } from '../viewmodels';
import { ReelItem, LoadingSpinner, Button } from '../components';

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
  
  const containerRef = useRef<HTMLDivElement>(null);
  const currentReel = reels[currentReelIndex];


  // Get current image to display
  const getCurrentImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0) {
      return currentReel?.main_image || '';
    }
    return currentReel.images[currentImageIndex] || currentReel.main_image || '';
  };

  // Handle image navigation
  const nextImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0) return;
    setCurrentImageIndex((prev) => (prev + 1) % currentReel.images.length);
  };

  const prevImage = () => {
    if (!currentReel?.images || currentReel.images.length === 0) return;
    setCurrentImageIndex((prev) => 
      prev === 0 ? currentReel.images.length - 1 : prev - 1
    );
  };

  // Reset image index when reel changes
  useEffect(() => {
    setCurrentImageIndex(0);
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
        prevReel();
      } else {
        // Swipe up - Next reel
        nextReel();
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
        prevReel();
      } else {
        // Swipe up - Next reel
        nextReel();
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
        nextReel();
      } else {
        // Wheel up - Previous reel
        prevReel();
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
          prevReel();
          break;
        case 'ArrowDown':
          e.preventDefault();
          nextReel();
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
        <LoadingSpinner size="lg" className="text-white" />
      </div>
    );
  }

  if (error && reels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white px-4">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">
            Reels Yüklenemedi
          </h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <Button onClick={fetchReels} variant="primary">
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
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      style={{ 
        userSelect: 'none', 
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none'
      } as React.CSSProperties}
      onContextMenu={(e) => e.preventDefault()}
    >
      {/* Main Reel Display */}
      <div className="relative h-full flex items-center justify-center">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center filter blur-sm transition-all duration-300"
          style={{ 
            backgroundImage: `url(${getCurrentImage()})`,
            transform: 'scale(1.1)' // Prevent white edges from blur
          }}
        />
        
        {/* Full Screen Reel Display */}
        <ReelItem
          reel={currentReel}
          isActive={true}
          onPlay={togglePlayPause}
          onImageClick={togglePlayPause}
          className="absolute inset-0 w-full h-full"
        />



        {/* Reel Counter */}
        <div className="absolute top-4 left-4 z-20">
          <div className="bg-black bg-opacity-50 rounded-full px-3 py-1 text-white text-sm">
            {currentReelIndex + 1} / {reels.length}
          </div>
        </div>

        {/* Image Indicators */}
        {currentReel?.images && currentReel.images.length > 1 && (
          <div className="absolute top-4 right-4 z-20">
            <div className="bg-black bg-opacity-50 rounded-full px-3 py-1 text-white text-sm">
              {currentImageIndex + 1} / {currentReel.images.length}
            </div>
          </div>
        )}

        {/* Image Dots */}
        {currentReel?.images && currentReel.images.length > 1 && (
          <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 z-20">
            <div className="flex space-x-2">
              {currentReel.images.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentImageIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentImageIndex 
                      ? 'bg-white' 
                      : 'bg-white bg-opacity-50'
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