export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

export interface TabItem {
  id: string;
  name: string;
  title: string;
  icon: string;
  iconFocused: string;
}

export interface AudioState {
  isPlaying: boolean;
  position: number;
  duration: number;
  isLoaded: boolean;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
  cursor?: string;
}