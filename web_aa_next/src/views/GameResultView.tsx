// GameResultView.tsx - Game results screen

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GameApi } from '../api/gameApi';
import { GameResult } from '../models/GameModels';
import { Card } from '../components';

export const GameResultView: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<GameResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (gameId) {
      loadResult();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId]);

  const loadResult = async () => {
    try {
      const gameResult = await GameApi.getGameResult(gameId!);
      setResult(gameResult);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sonuçlar yüklenemedi');
      setLoading(false);
    }
  };

  const getResultIcon = () => {
    if (!result) return '🎮';
    if (result.result === 'win') return '🏆';
    if (result.result === 'lose') return '😢';
    return '🤝';
  };

  const getResultTitle = () => {
    if (!result) return 'Sonuçlar';
    if (result.result === 'win') return 'Kazandın!';
    if (result.result === 'lose') return 'Kaybettin';
    return 'Berabere!';
  };

  const getResultColor = () => {
    if (!result) return 'text-gray-900';
    if (result.result === 'win') return 'text-green-600';
    if (result.result === 'lose') return 'text-red-600';
    return 'text-blue-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Sonuçlar yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Hata</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/games/menu')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Geri Dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Main Result Card */}
        <Card padding="lg" shadow="lg" className="text-center mb-6">
          {/* Icon */}
          <div className="text-8xl mb-6 animate-bounce-once">
            {getResultIcon()}
          </div>

          {/* Title */}
          <h1 className={`text-4xl sm:text-5xl font-bold mb-4 ${getResultColor()}`}>
            {getResultTitle()}
          </h1>

          {/* Score Display */}
          <div className="flex items-center justify-center gap-8 mb-8">
            <div className="text-center">
              <div className="text-gray-600 text-sm mb-1">Sen</div>
              <div className="text-4xl font-bold text-gray-900">
                {result?.my_score || 0}
              </div>
            </div>
            <div className="text-3xl text-gray-400">-</div>
            <div className="text-center">
              <div className="text-gray-600 text-sm mb-1">Rakip</div>
              <div className="text-4xl font-bold text-gray-900">
                {result?.opponent_score || 0}
              </div>
            </div>
          </div>

          {/* XP Earned */}
          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-4 mb-6">
            <div className="text-sm text-gray-700 mb-1">Kazandığın XP</div>
            <div className="text-3xl font-bold text-orange-600">
              +{result?.total_xp_earned || 0} XP
            </div>
          </div>

          {/* News Discussed */}
          {result && result.news_discussed.length > 0 && (
            <div className="text-left mb-6">
              <h3 className="font-semibold text-gray-900 mb-3 text-lg">
                📰 Bahsedilen Haberler:
              </h3>
              <div className="space-y-2">
                {result.news_discussed.map((news, index) => (
                  <a
                    key={index}
                    href={news.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <div className="text-sm text-gray-900 font-medium">
                      {news.title}
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      Haberi oku →
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => navigate('/games/menu')}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors shadow-md hover:shadow-lg"
            >
              Tekrar Oyna
            </button>
            <button
              onClick={() => navigate('/games')}
              className="flex-1 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg font-semibold transition-colors"
            >
              Oyunlar
            </button>
          </div>
        </Card>

        {/* Fun Fact */}
        <div className="text-center">
          <div className="inline-block bg-white/80 backdrop-blur-sm rounded-lg px-6 py-3 shadow-md">
            <p className="text-sm text-gray-600">
              {result?.result === 'win' 
                ? '🎉 Harika bir performans! Daha fazla haber izleyerek gelişmeye devam et.'
                : result?.result === 'lose'
                ? '💪 Üzülme! Daha fazla haber izleyerek rakiplerini geçebilirsin.'
                : '🤝 Eşit performans! İkiniz de haberleri yakından takip ediyorsunuz.'}
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes bounce-once {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-20px);
          }
        }
        .animate-bounce-once {
          animation: bounce-once 1s ease-in-out;
        }
      `}</style>
    </div>
  );
};
