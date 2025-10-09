export interface SubtitleData {
  start: number;
  end: number;
  text: string;
}

// Backend ScrapedNewsItem model
export interface ScrapedNewsItem {
  title: string;
  summary: string;
  full_content: string;
  url: string;
  category: string;
  author?: string;
  location?: string;
  published_date: string;
  scraped_date: string;
  main_image?: string;
  images: string[];
  videos: string[];
  tags: string[];
  keywords: string[];
  meta_description?: string;
  word_count: number;
  character_count: number;
  estimated_reading_time: number;
  source: string;
  scraping_quality: string;
  content_language: string;
}

// Backend MockupReelOutput model
export interface MockupReelOutput {
  id: string;
  news_data: ScrapedNewsItem;
  tts_content: string;
  voice_used: string;
  model_used: string;
  audio_url: string;
  duration_seconds: number;
  file_size_mb: number;
  character_count: number;
  estimated_cost: number;
  processing_time_seconds: number;
  status: string;
  created_at: string;
}

// Legacy ReelData for compatibility
export interface ReelData {
  id: string;
  title: string;
  content: string;
  category: string;
  images: string[];
  main_image: string;
  audio_url: string;
  subtitles: SubtitleData[];
  estimated_duration: number;
  tags: string[];
  author?: string;
  location?: string;
  summary?: string;
  published_at?: string; // ekledik: sıralama için tarih
}

// Backend API Response models
export interface ScrapedNewsResponse {
  success: boolean;
  message: string;
  news_items: ScrapedNewsItem[];
  total_count: number;
  scraping_info: {
    scraping_time: string;
    source: string;
    quality: string;
    errors: number;
  };
}

export interface GenerateReelsResponse {
  success: boolean;
  message: string;
  reels: MockupReelOutput[];
  summary: {
    total_reels: number;
    total_characters: number;
    total_estimated_cost: number;
    total_duration_seconds: number;
    average_duration: number;
    voice_used: string;
  };
}

export interface NewsDetailResponse {
  success: boolean;
  news_item: ScrapedNewsItem;
  tts_preview: {
    content: string;
    character_count: number;
    estimated_duration: number;
    estimated_cost: number;
  };
}

export interface CategoriesResponse {
  success: boolean;
  categories: Record<string, number>;
  available_categories: string[];
  total_news: number;
}

export interface StatsResponse {
  success: boolean;
  mockup_statistics: {
    total_news_items: number;
    content_stats: {
      total_characters: number;
      total_words: number;
      average_words_per_article: number;
    };
    tts_stats: {
      total_tts_characters: number;
      estimated_total_cost: number;
      average_cost_per_reel: number;
    };
    categories: Record<string, number>;
    authors: Record<string, number>;
  };
}

export interface ReelResponse {
  success: boolean;
  reels: ReelData[];
  message?: string;
}