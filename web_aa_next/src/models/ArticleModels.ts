export interface ArticleData {
  id: string;
  title: string;
  content: string;
  category: string;
  images: string[];
  main_image: string;
  author?: string;
  location?: string;
  published_date: string;
  tags: string[];
  nextArticleId?: string;
  prevArticleId?: string;
  summary?: string;
}

export interface ArticleResponse {
  success: boolean;
  articles: ArticleData[];
  message?: string;
}

export interface ArticleDetailResponse {
  success: boolean;
  article: ArticleData;
  message?: string;
}