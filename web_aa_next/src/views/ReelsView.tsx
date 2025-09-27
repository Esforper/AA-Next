import React, { useState, useEffect } from 'react';
import { useReelsViewModel } from '../viewmodels';
import { ReelItem, LoadingSpinner, Button } from '../components';
import clsx from 'clsx';

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
    seekAudio,
    fetchReels
  } = useReelsViewModel();

  const [showSubtitles, setShowSubtitles] = useState(true);
  const currentReel = reels[currentReelIndex];

  // Get current subtitle based on audio position
  const getCurrentSubtitle = () => {
    if (!currentReel?.subtitles || !audioState.isPlaying) return null;
    
    return currentReel.subtitles.find(
      sub => audioState.position >= sub.start && audioState.position <= sub.end
    );
  };

  const currentSubtitle = getCurrentSubtitle();

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
          if (audioState.isLoaded) {
            seekAudio(Math.max(0, audioState.position - 5));
          }
          break;
        case 'ArrowRight':
          e.preventDefault();
          if (audioState.isLoaded) {
            seekAudio(Math.min(audioState.duration, audioState.position + 5));
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [prevReel, nextReel, togglePlayPause, seekAudio, audioState]);

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
    <div className="relative h-screen bg-black overflow-hidden">
      {/* Main Reel Display */}
      <div className="relative h-full flex items-center justify-center">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center filter blur-sm"
          style={{ 
            backgroundImage: `url(${currentReel?.main_image})`,
            transform: 'scale(1.1)' // Prevent white edges from blur
          }}
        />
        
        {/* Content Container */}
        <div className="relative z-10 w-full h-full flex items-center justify-center">
          {/* Reel Card */}
          <div className="w-full max-w-md mx-4">
            <ReelItem
              reel={currentReel}
              isActive={true}
              onPlay={togglePlayPause}
              onImageClick={togglePlayPause}
              className="shadow-2xl"
            />
          </div>
        </div>

        {/* Navigation Controls */}
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex flex-col space-y-4 z-20">
          {/* Previous */}
          <button
            onClick={prevReel}
            className="w-12 h-12 bg-black bg-opacity-50 rounded-full flex items-center justify-center text-white hover:bg-opacity-70 transition-all"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" />
            </svg>
          </button>

          {/* Play/Pause */}
          <button
            onClick={togglePlayPause}
            className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white hover:bg-blue-700 transition-all shadow-lg"
          >
            {audioState.isPlaying ? (
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6 4h2v12H6V4zm6 0h2v12h-2V4z" />
              </svg>
            ) : (
              <svg className="w-8 h-8 ml-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5v10l8-5-8-5z" />
              </svg>
            )}
          </button>

          {/* Next */}
          <button
            onClick={nextReel}
            className="w-12 h-12 bg-black bg-opacity-50 rounded-full flex items-center justify-center text-white hover:bg-opacity-70 transition-all"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" />
            </svg>
          </button>
        </div>

        {/* Bottom Controls */}
        <div className="absolute bottom-4 left-0 right-0 z-20">
          {/* Audio Progress Bar */}
          {audioState.isLoaded && (
            <div className="mx-4 mb-4">
              <div className="flex items-center space-x-2 text-white text-sm">
                <span>
                  {Math.floor(audioState.position / 60)}:{(audioState.position % 60).toFixed(0).padStart(2, '0')}
                </span>
                <div className="flex-1 bg-gray-600 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-200"
                    style={{
                      width: `${(audioState.position / audioState.duration) * 100}%`
                    }}
                  />
                </div>
                <span>
                  {Math.floor(audioState.duration / 60)}:{(audioState.duration % 60).toFixed(0).padStart(2, '0')}
                </span>
              </div>
            </div>
          )}

          {/* Subtitles */}
          {showSubtitles && currentSubtitle && (
            <div className="mx-4 mb-4">
              <div className="bg-black bg-opacity-70 rounded-lg p-3 text-center">
                <p className="text-white text-lg">{currentSubtitle.text}</p>
              </div>
            </div>
          )}

          {/* Toggle Subtitles */}
          <div className="flex justify-center">
            <button
              onClick={() => setShowSubtitles(!showSubtitles)}
              className={clsx(
                'px-4 py-2 rounded-full text-sm font-medium transition-all',
                showSubtitles 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-black bg-opacity-50 text-white hover:bg-opacity-70'
              )}
            >
              {showSubtitles ? 'Alt yazıları gizle' : 'Alt yazıları göster'}
            </button>
          </div>
        </div>

        {/* Reel Counter */}
        <div className="absolute top-4 left-4 z-20">
          <div className="bg-black bg-opacity-50 rounded-full px-3 py-1 text-white text-sm">
            {currentReelIndex + 1} / {reels.length}
          </div>
        </div>
      </div>
    </div>
  );
};