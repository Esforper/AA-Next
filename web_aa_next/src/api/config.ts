// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    REELS: {
      MIX: '/api/reels/mix',
      READY: '/api/agenda/ready'
    },
    ARTICLES: {
      LIST: '/api/articles',
      DETAIL: '/api/articles'
    },
    AUTH: {
      LOGIN: '/api/auth/login'
    }
  },
  DEFAULT_TIMEOUT: 10000
};

// Create axios instance if needed
export const createApiUrl = (endpoint: string, params?: Record<string, string | number>): string => {
  const url = new URL(endpoint, API_CONFIG.BASE_URL);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value.toString());
    });
  }
  
  return url.toString();
};