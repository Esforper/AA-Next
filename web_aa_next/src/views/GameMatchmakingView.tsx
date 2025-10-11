// GameMatchmakingView.tsx - Matchmaking/searching screen

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { GameApi } from '../api/gameApi';

export const GameMatchmakingView: React.FC = () => {
  const navigate = useNavigate();
  const [statusText, setStatusText] = useState('Rakip aranıyor...');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isSearching, setIsSearching] = useState(true);
  const pollingTimerRef = useRef<NodeJS.Timeout>();
  const statusTimerRef = useRef<NodeJS.Timeout>();
  const elapsedTimerRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    startMatchmaking();
    startStatusUpdates();
    
    // Cleanup on unmount
    return () => {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
      if (statusTimerRef.current) clearInterval(statusTimerRef.current);
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
      GameApi.cancelMatchmaking();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startMatchmaking = async () => {
    try {
      console.log('🎮 Starting matchmaking...');
      
      // Join queue
      const response = await GameApi.joinMatchmaking();
      
      console.log('📡 Queue response:', response);
      
      if (response.matched && response.game_id) {
        // Immediate match!
        console.log('✅ Immediate match found!');
        navigateToGame(response.game_id);
      } else if (response.success) {
        // Added to queue, start polling
        console.log('⏳ Added to queue, starting polling...');
        startPolling();
      } else {
        // Error
        console.log('❌ Error:', response.message);
        showError(response.message);
      }
    } catch (error) {
      console.error('❌ Matchmaking start error:', error);
      showError(error instanceof Error ? error.message : 'Eşleşme başlatılamadı');
    }
  };

  const startPolling = () => {
    // Start elapsed time counter
    elapsedTimerRef.current = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);

    // Poll every 3 seconds
    pollingTimerRef.current = setInterval(async () => {
      if (!isSearching) return;
      
      console.log('⏱️ Polling...');
      
      try {
        const status = await GameApi.getMatchmakingStatus();
        
        console.log('📊 Status check:', status);
        
        if (status.matched && status.game_id) {
          // Match found!
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
          console.log('🎉 Match found! Game ID:', status.game_id);
          navigateToGame(status.game_id);
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
      }
    }, 3000);

    // Timeout after 60 seconds
    setTimeout(() => {
      if (isSearching) {
        if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
        if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
        GameApi.cancelMatchmaking();
        showError('Rakip bulunamadı. Lütfen daha fazla haber izleyin.');
      }
    }, 60000);
  };

  const startStatusUpdates = () => {
    const statuses = [
      'Rakip aranıyor...',
      'En dişli rakipler taranıyor...',
      'Haber arşivleri karşılaştırılıyor...',
      'Neredeyse hazır!'
    ];
    let currentIndex = 0;
    
    statusTimerRef.current = setInterval(() => {
      currentIndex = (currentIndex + 1) % statuses.length;
      setStatusText(statuses[currentIndex]);
    }, 4000);
  };

  const navigateToGame = (gameId: string) => {
    setIsSearching(false);
    navigate(`/games/play/${gameId}`, { replace: true });
  };

  const showError = (message: string) => {
    setIsSearching(false);
    alert(message);
    navigate('/games/menu');
  };

  const handleCancel = async () => {
    console.log('🛑 Cancelling search...');
    setIsSearching(false);
    
    if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    if (statusTimerRef.current) clearInterval(statusTimerRef.current);
    if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    
    await GameApi.cancelMatchmaking();
    navigate('/games/menu');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="text-center max-w-md w-full">
        {/* Animated Icon */}
        <div className="mb-8 relative">
          <div className="w-24 h-24 mx-auto animate-spin-slow">
            <svg className="w-full h-full text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
        </div>

        {/* Status Text */}
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
          {statusText}
        </h2>

        {/* Elapsed Time */}
        <div className="text-gray-600 mb-2">
          Geçen süre: {elapsedSeconds} saniye
        </div>

        {/* Info Text */}
        <p className="text-gray-500 text-sm mb-8">
          Bu işlem 60 saniye sürebilir.
        </p>

        {/* Progress Bar */}
        <div className="mb-8 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div 
            className="bg-blue-600 h-full transition-all duration-1000"
            style={{ width: `${Math.min((elapsedSeconds / 60) * 100, 100)}%` }}
          ></div>
        </div>

        {/* Cancel Button */}
        <button
          onClick={handleCancel}
          className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors shadow-md hover:shadow-lg"
        >
          Aramayı İptal Et
        </button>

        {/* Fun Facts */}
        <div className="mt-12 p-4 bg-white/80 backdrop-blur-sm rounded-lg shadow-md text-left">
          <p className="text-xs text-gray-600 italic">
            💡 <strong>İpucu:</strong> Daha fazla haber izleyerek daha kolay rakip bulabilirsiniz!
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        .animate-spin-slow {
          animation: spin-slow 2s linear infinite;
        }
      `}</style>
    </div>
  );
};
