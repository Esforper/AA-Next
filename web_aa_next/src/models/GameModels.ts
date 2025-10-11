// GameModels.ts - Multiplayer Game Models (Ported from Flutter)

/**
 * Matchmaking Response - Rakip arama sonucu
 */
export interface MatchmakingResponse {
  success: boolean;
  matched: boolean;
  opponent_id?: string;
  game_id?: string;
  common_reels_count: number;
  estimated_wait_time_seconds?: number;
  message: string;
}

/**
 * Matchmaking Status Response - Polling için
 */
export interface MatchmakingStatusResponse {
  success: boolean;
  in_queue: boolean;
  matched: boolean;
  game_id?: string;
  opponent_id?: string;
  wait_time_seconds: number;
  queue_position: number;
  estimated_wait: number;
  message: string;
}

/**
 * Game Eligibility - Oyun oynayabilir mi?
 */
export interface GameEligibility {
  success: boolean;
  eligible: boolean;
  current_count: number;
  required: number;
  needed: number;
  message: string;
}

/**
 * Game Session - Oyun oturumu bilgileri
 */
export interface GameSession {
  success: boolean;
  game_id: string;
  status: 'waiting' | 'active' | 'finished';
  player1_id: string;
  player2_id: string;
  player1_score: number;
  player2_score: number;
  current_round: number;
  total_rounds: number;
  created_at: string;
}

/**
 * Game Question - Tek bir round'un sorusu
 */
export interface GameQuestion {
  success: boolean;
  round_number: number;
  total_rounds: number;
  question_text: string;
  options: string[]; // 2 seçenek (karışık sırada)
  correct_index: number; // Doğru cevabın index'i (0 veya 1)
  reel_id: string;
  news_title: string;
  asker_id: string; // Kim soruyor?
}

/**
 * Answer Response - Soruya verilen cevap sonucu
 */
export interface AnswerResponse {
  success: boolean;
  is_correct: boolean;
  xp_earned: number;
  current_score: number;
  response_message: string; // "Evet evet!" veya "Yanlış hatırlıyorsun"
  emoji_comment?: string; // Emoji bazlı yorum
  news_url: string; // Haberin linki
}

/**
 * News Discussed - Oyunda bahsedilen haber
 */
export interface NewsDiscussed {
  reel_id: string;
  title: string;
  url: string;
}

/**
 * Game Result - Final skor ve detaylar
 */
export interface GameResult {
  success: boolean;
  game_id: string;
  winner_id?: string;
  result: 'win' | 'lose' | 'draw';
  my_score: number;
  opponent_score: number;
  total_xp_earned: number;
  news_discussed: NewsDiscussed[];
}

/**
 * Game History Item - Liste için
 */
export interface GameHistoryItem {
  game_id: string;
  opponent_id: string;
  result: 'win' | 'lose' | 'draw';
  my_score: number;
  opponent_score: number;
  played_at: string; // ISO datetime string
  news_count: number;
}

/**
 * Game History Detail - Tek oyun için
 */
export interface GameHistoryDetail {
  success: boolean;
  game_id: string;
  player1_id: string;
  player2_id: string;
  player1_score: number;
  player2_score: number;
  winner_id?: string;
  created_at: string;
  finished_at?: string;
  total_rounds: number;
  round_history: Record<string, unknown>[]; // Round detayları
  news_discussed: NewsDiscussed[];
}

/**
 * Chat Bubble - UI için mesaj balonu
 */
export interface ChatBubble {
  isFromMe: boolean;
  text: string;
  isQuestion?: boolean;
  isAnswer?: boolean;
  isCorrect?: boolean;
  hasEmoji?: boolean;
  timestamp: Date;
}
