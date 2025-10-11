// GameMenuView.tsx - Main multiplayer game menu

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GameApi } from '../api/gameApi';
import { GameEligibility } from '../models/GameModels';
import { Card } from '../components';

export const GameMenuView: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [eligibility, setEligibility] = useState<GameEligibility | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check authentication first
    const token = localStorage.getItem('aa_auth_token') || sessionStorage.getItem('aa_auth_token');
    if (!token) {
      setIsAuthenticated(false);
      setLoading(false);
      setError('Oyun oynamak için giriş yapmalısınız.');
      return;
    }
    
    setIsAuthenticated(true);
    checkEligibility();
  }, []);

  const checkEligibility = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await GameApi.checkEligibility();
      setEligibility(result);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Bir hata oluştu';
      if (errorMsg.includes('401')) {
        setError('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
        setIsAuthenticated(false);
      } else {
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFindOpponent = () => {
    navigate('/games/matchmaking');
  };

  const handlePlayWithBot = async () => {
    try {
      setLoading(true);
      const result = await GameApi.createBotMatch();
      navigate(`/games/play/${result.game_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bot maç oluşturulamadı');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !eligibility) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Header */}
      <div className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate('/games')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">
            Haber Kapışması
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {error && !isAuthenticated && (
          <Card padding="lg" shadow="lg" className="text-center bg-yellow-50 border-2 border-yellow-200">
            <div className="text-6xl mb-4">🔒</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Giriş Gerekli</h2>
            <p className="text-gray-700 mb-6">{error}</p>
            <button
              onClick={() => navigate('/profile')}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors shadow-md hover:shadow-lg"
            >
              Giriş Yap / Kayıt Ol
            </button>
          </Card>
        )}

        {isAuthenticated && (
          <>
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            <Card padding="lg" shadow="lg" className="text-center">
              {/* Icon */}
              <div className="text-6xl sm:text-8xl mb-6">
                {eligibility?.eligible ? '🎮' : 'ℹ️'}
              </div>

              {/* Title */}
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
                {eligibility?.eligible ? 'Oyuna Hazırsın!' : 'Henüz Hazır Değilsin'}
              </h2>

              {/* Message */}
              <p className="text-gray-600 text-base sm:text-lg mb-8 leading-relaxed">
                {eligibility?.message || 'Yükleniyor...'}
              </p>

              {/* Actions */}
              <div className="space-y-4">
                {eligibility?.eligible ? (
              <>
                {/* Test: Bot ile Oyna */}
                <button
                  onClick={handlePlayWithBot}
                  disabled={loading}
                  className="w-full sm:w-auto px-8 py-4 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-bold text-lg transition-colors shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <span className="text-2xl">🤖</span>
                  <span>Test: Bot ile Oyna</span>
                </button>

                {/* Rakip Bul */}
                <button
                  onClick={handleFindOpponent}
                  disabled={loading}
                  className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold text-lg transition-colors shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <span className="text-2xl">🔍</span>
                  <span>Rakip Bul</span>
                </button>
              </>
            ) : (
              <button
                onClick={checkEligibility}
                disabled={loading}
                className="w-full sm:w-auto px-8 py-4 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-bold text-lg transition-colors shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <span className="text-2xl">🔄</span>
                <span>Tekrar Kontrol Et</span>
              </button>
            )}
          </div>

          {/* Info Box */}
          <div className="mt-8 p-4 sm:p-6 bg-blue-50 rounded-lg text-left">
            <h3 className="font-semibold text-gray-900 mb-3 text-base sm:text-lg">
              🎯 Oyun Hakkında:
            </h3>
            <ul className="space-y-2 text-sm sm:text-base text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>İki oyuncu birbirine soru sorar</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Sorular izlediğiniz haberlerden seçilir</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Her doğru cevap +20 XP kazandırır</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-1">✓</span>
                <span>Toplam 8 round oynanır</span>
              </li>
            </ul>
              </div>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};
