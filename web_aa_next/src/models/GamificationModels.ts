// GamificationModels.ts - Flutter gamification_state.dart'tan uyarlandı

export interface ReelInteraction {
  watched: boolean;            // Reel izlendi mi
  detailViewed: boolean;       // Detay görüntülendi mi
  shared: boolean;            // Paylaşıldı mı
  lastInteractionDate: string; // Son etkileşim tarihi
}

export interface GamificationState extends Record<string, unknown> {
  // XP & Level
  currentXP: number;           // Mevcut düğümdeki XP (0-100)
  dailyXPGoal: number;         // Günlük hedef (300 XP)
  totalXP: number;             // Tüm zamanlar toplam XP
  currentLevel: number;        // Seviye (1-100)
  xpToNextLevel: number;       // Bir sonraki seviyeye kadar gereken XP
  currentNode: number;         // Mevcut düğüm pozisyonu (0-based)
  nodesInLevel: number;        // Bu seviyedeki toplam düğüm sayısı
  
  // Streak
  currentStreak: number;       // Güncel streak (gün)
  lastActivityDate: string | null;
  streakPercentile: number;    // Kullanıcıların %X'inden iyi
  
  // Daily Progress
  reelsWatchedToday: number;
  emojisGivenToday: number;
  detailsReadToday: number;
  sharesGivenToday: number;
  xpEarnedToday: number;
  dailyGoalCompleted: boolean;
  
  // Computed properties (ViewModel'de hesaplanacak)
  dailyProgress?: number;      // 0..1
  nodeProgress?: number;       // 0..1
  levelProgress?: number;      // 0..1
}

export interface AddXpRequest {
  user_id: string;
  xp_amount: number;
  source: 'reel_watched' | 'emoji_given' | 'detail_read' | 'share_given' | 'test';
  metadata?: Record<string, unknown>;
}

export interface AddXpResponse {
  success: boolean;
  message?: string;
  data?: {
    new_xp: number;
    new_level?: number;
    level_up?: boolean;
    achievement_unlocked?: string;
  };
}

export interface LevelResponse {
  success: boolean;
  data?: GamificationState;
  message?: string;
}

export interface UserStatsResponse {
  success: boolean;
  data?: {
    total_reels_watched: number;
    total_emojis_given: number;
    total_details_read: number;
    total_shares: number;
    avg_daily_xp: number;
    longest_streak: number;
    current_rank?: number;
    total_users?: number;
  };
  message?: string;
}

export interface DailyProgressResponse {
  success: boolean;
  data?: {
    xp_earned_today: number;
    daily_goal: number;
    goal_completed: boolean;
    reels_watched: number;
    streak: number;
  };
  message?: string;
}

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  avatar_url?: string;
  total_xp: number;
  current_level: number;
  current_streak: number;
  rank: number;
}

export interface LeaderboardResponse {
  success: boolean;
  data?: {
    leaderboard: LeaderboardEntry[];
    user_rank?: number;
    period: string;
    updated_at: string;
  };
  message?: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  unlocked: boolean;
  unlocked_at?: string;
  progress?: number;
  required?: number;
}

export interface AchievementsResponse {
  success: boolean;
  data?: {
    achievements: Achievement[];
    total_unlocked: number;
  };
  message?: string;
}
