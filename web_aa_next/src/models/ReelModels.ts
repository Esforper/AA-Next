export interface SubtitleData {
  start: number;
  end: number;
  text: string;
}

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
}

export interface ReelResponse {
  success: boolean;
  reels: ReelData[];
  message?: string;
}