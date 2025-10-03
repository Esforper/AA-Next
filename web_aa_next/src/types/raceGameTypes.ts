// src/types/raceGameTypes.ts

/**
 * Haber Yarış Oyunu - Type Definitions
 * Paralel şerit sistemi ile 4-5 oyuncunun yarıştığı haftalık haber takip yarışı
 */

// ============ ENUMS ============

export enum WatchStatus {
  UNWATCHED = "unwatched",           // İzlenmemiş
  WATCHED_IMMEDIATE = "immediate",   // 0-24 saat içinde izlendi (Yeşil)
  WATCHED_LATE = "late"              // 24+ saat sonra izlendi (Sarı)
}

export enum PlayerLane {
  LANE_1 = 0,
  LANE_2 = 1,
  LANE_3 = 2,
  LANE_4 = 3,
  LANE_5 = 4
}

export enum NewsCategory {
  EKONOMI = "ekonomi",
  SPOR = "spor",
  TEKNOLOJI = "teknoloji",
  GUNCEL = "guncel",
  KULTUR = "kultur",
  SAGLIK = "saglik",
  EGITIM = "egitim",
  SAVUNMA = "savunma"
}

// ============ INTERFACES ============

/**
 * Haber Node - Yol üzerindeki her haber noktası
 */
export interface NewsNodeData {
  id: string;                        // Unique node ID
  reel_id: string;                   // Backend reel ID
  title: string;                     // Haber başlığı
  summary: string;                   // Kısa özet
  category: NewsCategory;            // Kategori
  
  // Zaman bilgisi
  published_at: string;              // ISO date string
  week_day: number;                  // 1-7 (Pazartesi-Pazar)
  order_in_week: number;             // Hafta içindeki sıra (0-n)
  
  // Node pozisyon bilgisi (yol üzerinde)
  position: {
    index: number;                   // Node sırası (0, 1, 2, ...)
    progress: number;                // Yol boyunca ilerleme (0.0 - 1.0)
  };
  
  // Her oyuncu için izlenme durumu
  player_views: {
    [player_id: string]: PlayerNewsView;
  };
  
  // İlişkili haberler (NLP ile bağlantılı)
  related_news_ids: string[];        // İlişkili haber ID'leri
  
  // Görsel
  thumbnail_url?: string;
}

/**
 * Oyuncunun bir haberi izleme durumu
 */
export interface PlayerNewsView {
  watched: boolean;                  // İzlendi mi?
  watched_at?: string;               // İzlenme zamanı (ISO)
  watch_status: WatchStatus;         // Yeşil/Sarı/İzlenmedi
  duration_seconds?: number;         // İzleme süresi
}

/**
 * Oyuncu verisi
 */
export interface RacePlayer {
  id: string;                        // User ID
  name: string;                      // Kullanıcı adı
  avatar_url: string;                // Profil fotoğrafı
  lane: PlayerLane;                  // Hangi şeritte (0-4)
  
  // İlerleme bilgisi
  total_watched: number;             // Toplam izlenen haber
  current_node_index: number;        // Şu anki node pozisyonu (0-n)
  progress_percentage: number;       // Haftalık ilerleme % (0-100)
  
  // Sıralama
  rank: number;                      // 1-5 arası sıralama
  points: number;                    // Toplam puan
  
  // Performans
  immediate_watch_count: number;     // Yeşil izleme sayısı
  late_watch_count: number;          // Sarı izleme sayısı
  
  // UI için
  color: string;                     // Avatar rengi (#hex)
  is_current_user: boolean;          // Aktif kullanıcı mı?
}

/**
 * Haftalık yarış verisi
 */
export interface WeeklyRaceData {
  // Hafta bilgisi
  week_id: string;                   // "2025-W02"
  week_start: string;                // "2025-01-06"
  week_end: string;                  // "2025-01-12"
  current_day: number;               // 1-7 (bugün hangi gün)
  
  // Kategori
  category: NewsCategory;
  category_display_name: string;     // "Ekonomi Haberleri"
  
  // Haberler (node'lar)
  news_nodes: NewsNodeData[];        // Tüm haftalık haberler (sıralı)
  total_news_count: number;          // Toplam haber sayısı
  
  // Yarışan oyuncular
  players: RacePlayer[];             // 4-5 oyuncu (sıralı: rank'e göre)
  current_user_id: string;           // Aktif kullanıcının ID'si
  
  // Yarış durumu
  is_active: boolean;                // Yarış aktif mi?
  time_remaining_hours: number;      // Kalan süre (saat)
  
  // Meta
  created_at: string;
  last_updated: string;
}

/**
 * Node detay modal için veri
 */
export interface NodeDetailData {
  node: NewsNodeData;                // Ana haber
  related_nodes: NewsNodeData[];     // İlişkili haberler
  nlp_connections: NLPConnection[];  // NLP bağlantı açıklamaları
  
  // Tüm oyuncuların bu haberi izleme durumu
  all_player_views: {
    player: RacePlayer;
    view_status: PlayerNewsView;
  }[];
}

/**
 * NLP bağlantı açıklaması
 */
export interface NLPConnection {
  from_news_id: string;
  to_news_id: string;
  connection_type: "same_entity" | "same_event" | "same_topic" | "consequence";
  similarity_score: number;          // 0.0 - 1.0
  explanation?: string;              // "Her iki haber de 'Merkez Bankası' ile ilgili"
}

/**
 * Yol çizimi için koordinat
 */
export interface PathPoint {
  x: number;
  y: number;
  node_index?: number;               // Bu noktada bir node var mı?
}

/**
 * Şerit (lane) bilgisi
 */
export interface LaneInfo {
  lane_id: PlayerLane;
  y_offset: number;                  // Y ekseninde offset (paralel şeritler için)
  color: string;                     // Şerit rengi
  player?: RacePlayer;               // Bu şeritteki oyuncu
}

/**
 * Zoom/Pan state
 */
export interface ViewportState {
  scale: number;                     // 0.5 - 3.0
  offset_x: number;                  // Pan X
  offset_y: number;                  // Pan Y
  zoom_level: "far" | "medium" | "close"; // Zoom seviyesi
}

/**
 * UI State
 */
export interface RaceGameUIState {
  viewport: ViewportState;
  selected_node_id?: string;         // Seçili node (modal için)
  hovered_node_id?: string;          // Hover edilen node
  show_all_players_status: boolean;  // Diğer oyuncuların durumunu göster
  animation_speed: number;           // Animasyon hızı (1.0 = normal)
}

// ============ UTILITY TYPES ============

/**
 * Renk hesaplama için yardımcı
 */
export type NodeColorScheme = {
  unwatched: string;      // #e5e7eb (gri)
  immediate: string;      // #10b981 (yeşil)
  late: string;          // #fbbf24 (sarı-yeşil)
};

/**
 * Avatar renk paleti
 */
export type PlayerColorPalette = {
  primary: string;
  light: string;
  dark: string;
};

// ============ CONSTANTS ============

export const NODE_COLORS: NodeColorScheme = {
  unwatched: "#e5e7eb",
  immediate: "#10b981",
  late: "#fbbf24"
};

export const PLAYER_COLORS: Record<number, PlayerColorPalette> = {
  0: { primary: "#3b82f6", light: "#93c5fd", dark: "#1e40af" }, // Mavi
  1: { primary: "#ef4444", light: "#fca5a5", dark: "#991b1b" }, // Kırmızı
  2: { primary: "#8b5cf6", light: "#c4b5fd", dark: "#5b21b6" }, // Mor
  3: { primary: "#f59e0b", light: "#fcd34d", dark: "#b45309" }, // Turuncu
  4: { primary: "#ec4899", light: "#f9a8d4", dark: "#9d174d" }  // Pembe
};

export const CATEGORY_COLORS: Record<NewsCategory, string> = {
  [NewsCategory.EKONOMI]: "#10b981",
  [NewsCategory.SPOR]: "#3b82f6",
  [NewsCategory.TEKNOLOJI]: "#8b5cf6",
  [NewsCategory.GUNCEL]: "#ef4444",
  [NewsCategory.KULTUR]: "#ec4899",
  [NewsCategory.SAGLIK]: "#14b8a6",
  [NewsCategory.EGITIM]: "#f59e0b",
  [NewsCategory.SAVUNMA]: "#6366f1"
};

// ============ HELPER FUNCTIONS (Type Guards) ============

export function isWatchedImmediate(view: PlayerNewsView): boolean {
  return view.watch_status === WatchStatus.WATCHED_IMMEDIATE;
}

export function isWatchedLate(view: PlayerNewsView): boolean {
  return view.watch_status === WatchStatus.WATCHED_LATE;
}

export function isUnwatched(view: PlayerNewsView): boolean {
  return view.watch_status === WatchStatus.UNWATCHED;
}

export function getNodeColor(view: PlayerNewsView): string {
  switch (view.watch_status) {
    case WatchStatus.WATCHED_IMMEDIATE:
      return NODE_COLORS.immediate;
    case WatchStatus.WATCHED_LATE:
      return NODE_COLORS.late;
    default:
      return NODE_COLORS.unwatched;
  }
}

export function calculateWatchStatus(
  published_at: string,
  watched_at?: string
): WatchStatus {
  if (!watched_at) return WatchStatus.UNWATCHED;
  
  const publishTime = new Date(published_at).getTime();
  const watchTime = new Date(watched_at).getTime();
  const diffHours = (watchTime - publishTime) / (1000 * 60 * 60);
  
  return diffHours <= 24 ? WatchStatus.WATCHED_IMMEDIATE : WatchStatus.WATCHED_LATE;
}

