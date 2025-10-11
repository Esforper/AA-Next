// GamePlayView.tsx - Main gameplay screen with WhatsApp-style chat

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GameApi } from '../api/gameApi';
import { GameSession, GameQuestion, ChatBubble } from '../models/GameModels';

export const GamePlayView: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [session, setSession] = useState<GameSession | null>(null);
  const [myUserId, setMyUserId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<GameQuestion | null>(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [waitingForResponse, setWaitingForResponse] = useState(false);
  const [chatBubbles, setChatBubbles] = useState<ChatBubble[]>([]);
  
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (gameId) {
      initializeGame();
    }
    
    return () => {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId]);

  const initializeGame = async () => {
    try {
      // Get user ID from localStorage (check both localStorage and sessionStorage)
      let userId = 'anonymous';
      const localUser = localStorage.getItem('aa_user');
      const sessionUser = sessionStorage.getItem('aa_user');
      const userStr = localUser || sessionUser;
      
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          userId = user.id || 'anonymous';
        } catch (e) {
          console.error('Failed to parse user data:', e);
        }
      }
      setMyUserId(userId);
      
      // Get game status
      const gameSession = await GameApi.getGameStatus(gameId!);
      setSession(gameSession);
      setLoading(false);
      
      // Load first question
      await loadQuestion(0);
      
      // Start polling for updates (simple version without WebSocket)
      startPolling();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Oyun yüklenemedi');
      setLoading(false);
    }
  };

  const startPolling = () => {
    pollingTimerRef.current = setInterval(async () => {
      try {
        const gameSession = await GameApi.getGameStatus(gameId!);
        setSession(gameSession);
        
        if (gameSession.status === 'finished') {
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          navigateToResult();
        }
      } catch (err) {
        console.error('❌ Polling error:', err);
      }
    }, 3000);
  };

  const loadQuestion = async (round: number) => {
    if (round >= (session?.total_rounds || 8)) {
      navigateToResult();
      return;
    }
    
    try {
      const question = await GameApi.getQuestion(gameId!, round);
      setCurrentQuestion(question);
      setCurrentRound(round);
      setWaitingForResponse(false);
      
      // Add question to chat
      addChatBubble({
        isFromMe: question.asker_id === myUserId,
        text: `${question.question_text}\n\n"${question.news_title}"`,
        isQuestion: true,
        timestamp: new Date(),
      });
      
      scrollToBottom();
      
    } catch (err) {
      console.error('❌ Load question error:', err);
      setError('Soru yüklenemedi');
    }
  };

  const submitAnswer = async (selectedIndex: number, isPass: boolean = false) => {
    if (waitingForResponse || !currentQuestion) return;
    
    setWaitingForResponse(true);
    
    // Add selected answer to chat
    if (!isPass) {
      addChatBubble({
        isFromMe: true,
        text: currentQuestion.options[selectedIndex],
        isAnswer: true,
        timestamp: new Date(),
      });
    } else {
      addChatBubble({
        isFromMe: true,
        text: 'Pas geçtim',
        isAnswer: true,
        timestamp: new Date(),
      });
    }
    
    scrollToBottom();
    
    try {
      const response = await GameApi.answerQuestion(
        gameId!,
        currentRound,
        selectedIndex,
        isPass
      );
      
      // Add response message to chat
      addChatBubble({
        isFromMe: false,
        text: response.response_message,
        isCorrect: response.is_correct,
        timestamp: new Date(),
      });
      
      if (response.emoji_comment) {
        setTimeout(() => {
          addChatBubble({
            isFromMe: false,
            text: response.emoji_comment!,
            hasEmoji: true,
            timestamp: new Date(),
          });
        }, 500);
      }
      
      scrollToBottom();
      
      // Update score manually (polling will update it too)
      if (session) {
        const newScore = response.current_score;
        setSession({
          ...session,
          [myUserId === session.player1_id ? 'player1_score' : 'player2_score']: newScore,
          current_round: currentRound + 1,
        });
      }
      
      // Load next question after delay
      setTimeout(() => {
        const nextRound = currentRound + 1;
        if (nextRound < (session?.total_rounds || 8)) {
          loadQuestion(nextRound);
        } else {
          navigateToResult();
        }
      }, 1500);
      
    } catch (err) {
      console.error('❌ Submit answer error:', err);
      setError('Cevap gönderilemedi');
      setWaitingForResponse(false);
    }
  };

  const addChatBubble = (bubble: ChatBubble) => {
    setChatBubbles(prev => [...prev, bubble]);
  };

  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }, 100);
  };

  const navigateToResult = () => {
    navigate(`/games/result/${gameId}`, { replace: true });
  };

  const shouldShowOptions = (): boolean => {
    if (!currentQuestion || waitingForResponse || !session || !myUserId) return false;
    
    const isPlayer1 = myUserId === session.player1_id;
    
    // Round-based turn:
    // Even rounds (0,2,4,6): Player1 asks, Player2 answers
    // Odd rounds (1,3,5,7): Player2 asks, Player1 answers
    const shouldAnswer = (currentRound % 2 === 0) ? !isPlayer1 : isPlayer1;
    
    return shouldAnswer;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Oyun yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (error && !session) {
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

  const myScore = myUserId === session?.player1_id ? session?.player1_score || 0 : session?.player2_score || 0;
  const opponentScore = myUserId === session?.player1_id ? session?.player2_score || 0 : session?.player1_score || 0;

  return (
    <div className="flex flex-col h-screen bg-[#ECE5DD]">
      {/* Header */}
      <div className="bg-[#075E54] text-white py-3 px-4 sm:py-4 sm:px-6 shadow-md">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/games/menu')}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <div className="font-semibold text-base sm:text-lg">Haber Kapışması</div>
              <div className="text-xs sm:text-sm opacity-90">
                Round {currentRound + 1}/{session?.total_rounds || 8}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm sm:text-base">
            <div className="text-center">
              <div className="text-xs opacity-75">Ben</div>
              <div className="font-bold">{myScore} XP</div>
            </div>
            <div className="text-lg">-</div>
            <div className="text-center">
              <div className="text-xs opacity-75">Rakip</div>
              <div className="font-bold">{opponentScore} XP</div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3 max-w-6xl w-full mx-auto">
        {chatBubbles.map((bubble, index) => (
          <div
            key={index}
            className={`flex ${bubble.isFromMe ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] sm:max-w-[60%] rounded-lg p-3 shadow-md ${
                bubble.isFromMe ? 'bg-[#DCF8C6]' : 'bg-white'
              }`}
            >
              {bubble.hasEmoji && (
                <div className="text-2xl mb-2">💬</div>
              )}
              <div className={`text-sm sm:text-base ${bubble.isQuestion ? 'font-medium' : ''}`}>
                {bubble.text}
              </div>
              {bubble.isCorrect !== undefined && (
                <div className={`flex items-center gap-2 mt-2 text-xs sm:text-sm ${
                  bubble.isCorrect ? 'text-green-600' : 'text-red-600'
                }`}>
                  {bubble.isCorrect ? '✓' : '✗'}
                  <span className="font-semibold">
                    {bubble.isCorrect ? 'Doğru! +20 XP' : 'Yanlış'}
                  </span>
                </div>
              )}
              <div className="text-xs text-black/50 mt-1">
                {bubble.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Options Area */}
      {shouldShowOptions() && currentQuestion && (
        <div className="bg-white border-t border-gray-300 p-4 max-w-6xl w-full mx-auto">
          <div className="font-semibold text-gray-900 mb-3 text-sm sm:text-base">Cevabını seç:</div>
          <div className="space-y-2">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => submitAnswer(index)}
                className="w-full p-3 bg-[#075E54] hover:bg-[#064d44] text-white rounded-lg text-left transition-colors text-sm sm:text-base"
              >
                {option}
              </button>
            ))}
            <button
              onClick={() => submitAnswer(0, true)}
              className="w-full p-2 text-gray-600 hover:text-gray-800 text-sm transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
              Pas Geç
            </button>
          </div>
        </div>
      )}

      {/* Waiting Indicator */}
      {waitingForResponse && (
        <div className="bg-gray-100 border-t border-gray-300 p-3 max-w-6xl w-full mx-auto">
          <div className="flex items-center justify-center gap-2 text-gray-600 text-sm">
            <div className="w-5 h-5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Rakip düşünüyor...</span>
          </div>
        </div>
      )}

      {error && session && (
        <div className="bg-red-50 border-t border-red-200 p-3 max-w-6xl w-full mx-auto">
          <div className="text-red-700 text-sm text-center">{error}</div>
        </div>
      )}
    </div>
  );
};
