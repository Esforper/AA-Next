// News models matching backend Reels.py news API contract

export type NewsCategory = 'Politics' | 'Economy' | 'Sports' | 'Technology' | 'General';

export interface NewsItem {
  id: string;
  title: string;
  description: string; // short description/summary
  content?: string; // full content (optional in list)
  imageUrl?: string;
  url?: string; // canonical link to detail
  category: NewsCategory | string;
  publishedAt?: string;
  author?: string;
  source?: string;
}

export interface NewsListResponse {
  success: boolean;
  message?: string;
  data: NewsItem[];
  pagination?: {
    limit?: number;
    offset?: number;
    total?: number;
    hasMore?: boolean;
  };
}

export interface NewsQueryParams {
  category?: string;
  limit?: number;
  offset?: number;
  q?: string; // search query
}


