import { rest } from 'msw';

// Mock data matching backend structure
const mockScrapedNews = [
  {
    "title": "Engelsiz Gazze projesi kapsamında sanatla dayanışma etkinliği düzenlendi",
    "summary": "Uluslararası Doktorlar Derneği (AID) ve ÖNDER Ankara İmam Hatipliler Derneği tarafından Gazzelilere protez desteği sağlamak amacıyla başlatılan 'Engelsiz Gazze' projesi kapsamında sanat etkinlikleri düzenlendi.",
    "full_content": "Uluslararası Doktorlar Derneği (AID) ve ÖNDER Ankara İmam Hatipliler Derneği tarafından Gazzelilere protez desteği sağlamak amacıyla başlatılan \"Engelsiz Gazze\" projesi kapsamında sanat etkinlikleri düzenlendi.\n\nAnkara'da düzenlenen etkinlikte, Gazze'deki insanlık dramına dikkat çekmek ve protez ihtiyacı olan kişilere destek sağlamak amacıyla çeşitli sanat gösterileri yapıldı.",
    "url": "https://www.aa.com.tr/tr/guncel/engelsiz-gazze-projesi-kapsaminda-sanatla-dayanisma-etkinligi-duzenlendi/3700959",
    "category": "guncel",
    "author": "Mehmet Yalçın",
    "location": "Ankara",
    "published_date": "2024-09-27T14:30:00Z",
    "scraped_date": "2024-09-27T15:30:45Z",
    "main_image": "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/thumbs_b_c_1234567890.jpg",
    "images": [
      "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/gazze_etkinlik_1.jpg",
      "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/gazze_etkinlik_2.jpg"
    ],
    "videos": [],
    "tags": ["Gazze", "protez", "dayanışma", "sanat", "AID", "ÖNDER"],
    "keywords": ["engelsiz gazze", "protez desteği", "sanat etkinliği", "uluslararası doktorlar derneği"],
    "meta_description": "Engelsiz Gazze projesi kapsamında Ankara'da sanat etkinliği düzenlendi",
    "word_count": 150,
    "character_count": 800,
    "estimated_reading_time": 1,
    "source": "aa",
    "scraping_quality": "high",
    "content_language": "tr"
  },
  {
    "title": "Troya'da çıkartılan 4 bin 500 yıllık altın broş antik kentteki önemli buluntular arasına girdi",
    "summary": "Troya Antik Kenti Kazı Başkan Yardımcısı Prof. Dr. Reyhan Körpe, Çanakkale'de 160 yılı aşkın süredir devam eden Troya kazılarında 4 bin 500 yıllık altın halkalı broş ile son derece ender bir yeşim taşının bulunmasına ilişkin açıklama yaptı.",
    "full_content": "Çanakkale'de 160 yılı aşkın süredir devam eden Troya Antik Kenti kazılarında tarihi öneme sahip yeni buluntular gün yüzüne çıkarıldı.\n\nTroya Antik Kenti Kazı Başkan Yardımcısı Prof. Dr. Reyhan Körpe, kazı çalışmaları sırasında bulunan 4 bin 500 yıllık altın halkalı broş ve ender yeşim taşının, antik kentteki en önemli buluntular arasında yer aldığını belirtti.",
    "url": "https://www.aa.com.tr/tr/guncel/troyada-cikartilan-4-bin-500-yillik-altin-bros-antik-kentteki-onemli-buluntular-arasina-girdi/3700953",
    "category": "kultur",
    "author": "Ayşe Demir",
    "location": "Çanakkale",
    "published_date": "2024-09-27T13:45:00Z",
    "scraped_date": "2024-09-27T15:30:45Z",
    "main_image": "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/thumbs_b_c_9876543210.jpg",
    "images": [
      "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/troya_bros_1.jpg",
      "https://cdnuploads.aa.com.tr/uploads/Contents/2024/09/27/troya_kazi_1.jpg"
    ],
    "videos": [],
    "tags": ["Troya", "altın broş", "arkeoloji", "antik kent", "kazı", "yeşim taşı"],
    "keywords": ["troya antik kenti", "4 bin 500 yıllık", "altın broş", "arkeolojik buluntu"],
    "meta_description": "Troya'da 4 bin 500 yıllık altın broş ve ender yeşim taşı bulundu",
    "word_count": 200,
    "character_count": 1000,
    "estimated_reading_time": 1,
    "source": "aa",
    "scraping_quality": "high",
    "content_language": "tr"
  }
];

// Legacy mock data for compatibility
const mockData = {
  "reels": [
    {
      "id": "1",
      "title": "Teknoloji Haberleri - AI'nin Geleceği",
      "content": "Yapay zeka teknolojilerinin gelişimi hakkında kapsamlı bir analiz.",
      "category": "teknoloji",
      "images": [
        "https://picsum.photos/400/600?random=1",
        "https://picsum.photos/400/600?random=2"
      ],
      "main_image": "https://picsum.photos/400/600?random=1",
      "audio_url": "/audio/test1.mp3",
      "subtitles": [
        { "start": 0, "end": 3, "text": "Yapay zeka günümüzde hızla gelişmektedir." },
        { "start": 3, "end": 6, "text": "Bu teknoloji birçok sektörü etkilemektedir." },
        { "start": 6, "end": 9, "text": "Geleceğe dair umut verici gelişmeler var." }
      ],
      "estimated_duration": 30,
      "tags": ["ai", "teknoloji", "gelecek"],
      "author": "Tech Reporter",
      "location": "İstanbul"
    }
  ],
  "articles": [
    {
      "id": "1",
      "title": "Teknoloji Dünyasında Yeni Trendler",
      "content": "2024 yılında teknoloji sektöründe beklenen gelişmeler ve trendler hakkında detaylı bir inceleme.",
      "category": "teknoloji",
      "images": [
        "https://picsum.photos/800/400?random=10",
        "https://picsum.photos/800/400?random=11"
      ],
      "main_image": "https://picsum.photos/800/400?random=10",
      "author": "Tech Editor",
      "location": "Silicon Valley",
      "published_date": "2024-01-15T10:00:00Z",
      "tags": ["teknoloji", "trend", "2024"],
      "nextArticleId": "2",
      "summary": "Teknoloji sektöründeki son gelişmeler ve gelecek öngörüleri."
    }
  ]
};

export const handlers = [
  // Backend API endpoints matching reels_mockup.py
  rest.get('/api/reels/mockup/scraped-news', (req, res, ctx) => {
    const count = parseInt(req.url.searchParams.get('count') || '3');
    const category = req.url.searchParams.get('category');
    
    let filteredNews = mockScrapedNews;
    if (category) {
      filteredNews = mockScrapedNews.filter(news => news.category === category);
    }
    
    const selectedNews = filteredNews.slice(0, count);
    
    return res(
      ctx.json({
        success: true,
        message: `Retrieved ${selectedNews.length} scraped news items`,
        news_items: selectedNews,
        total_count: selectedNews.length,
        scraping_info: {
          scraping_time: "2024-09-27T15:30:45Z",
          source: "aa.com.tr",
          quality: "high",
          errors: 0
        }
      })
    );
  }),

  rest.get('/api/reels/mockup/generate-reels', (req, res, ctx) => {
    const count = parseInt(req.url.searchParams.get('count') || '3');
    const voice = req.url.searchParams.get('voice') || 'alloy';
    const category = req.url.searchParams.get('category');
    
    let filteredNews = mockScrapedNews;
    if (category) {
      filteredNews = mockScrapedNews.filter(news => news.category === category);
    }
    
    const selectedNews = filteredNews.slice(0, count);
    
    // Generate mock reels from scraped news
    const reels = selectedNews.map((news, index) => ({
      id: `reel_${index + 1}_${voice}`,
      news_data: news,
      tts_content: `${news.title}. ${news.summary}`,
      voice_used: voice,
      model_used: "tts-1",
      audio_url: `/audio/reel_${index + 1}_${voice}.mp3`,
      duration_seconds: Math.max(15, Math.floor(news.character_count / 150 * 60)),
      file_size_mb: Math.max(0.5, Math.floor(news.character_count / 150 * 60) * 0.5),
      character_count: news.character_count,
      estimated_cost: (news.character_count / 1_000_000) * 0.015,
      processing_time_seconds: 2.5,
      status: "completed",
      created_at: new Date().toISOString()
    }));
    
    const totalChars = reels.reduce((sum, reel) => sum + reel.character_count, 0);
    const totalCost = reels.reduce((sum, reel) => sum + reel.estimated_cost, 0);
    const totalDuration = reels.reduce((sum, reel) => sum + reel.duration_seconds, 0);
    
    return res(
      ctx.json({
        success: true,
        message: `Generated ${reels.length} reels from scraped news`,
        reels,
        summary: {
          total_reels: reels.length,
          total_characters: totalChars,
          total_estimated_cost: Math.round(totalCost * 1000000) / 1000000,
          total_duration_seconds: totalDuration,
          average_duration: Math.round(totalDuration / reels.length * 10) / 10,
          voice_used: voice
        }
      })
    );
  }),

  rest.get('/api/reels/mockup/news-detail/:id', (req, res, ctx) => {
    const { id } = req.params;
    const newsIndex = parseInt(Array.isArray(id) ? id[0] : id);
    
    if (newsIndex < 0 || newsIndex >= mockScrapedNews.length) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          message: "News not found"
        })
      );
    }
    
    const news = mockScrapedNews[newsIndex];
    const ttsPreview = `${news.title}. ${news.summary}`;
    
    return res(
      ctx.json({
        success: true,
        news_item: news,
        tts_preview: {
          content: ttsPreview,
          character_count: ttsPreview.length,
          estimated_duration: Math.floor(ttsPreview.split(' ').length / 150 * 60),
          estimated_cost: (ttsPreview.length / 1_000_000) * 0.015
        }
      })
    );
  }),

  rest.get('/api/reels/mockup/categories', (req, res, ctx) => {
    const categories: Record<string, number> = {};
    mockScrapedNews.forEach(news => {
      categories[news.category] = (categories[news.category] || 0) + 1;
    });
    
    return res(
      ctx.json({
        success: true,
        categories,
        available_categories: Object.keys(categories),
        total_news: mockScrapedNews.length
      })
    );
  }),

  rest.get('/api/reels/mockup/stats', (req, res, ctx) => {
    const totalChars = mockScrapedNews.reduce((sum, news) => sum + news.character_count, 0);
    const totalWords = mockScrapedNews.reduce((sum, news) => sum + news.word_count, 0);
    const categories: Record<string, number> = {};
    const authors: Record<string, number> = {};
    
    mockScrapedNews.forEach(news => {
      categories[news.category] = (categories[news.category] || 0) + 1;
      if (news.author) {
        authors[news.author] = (authors[news.author] || 0) + 1;
      }
    });
    
    const ttsChars = mockScrapedNews.reduce((sum, news) => 
      sum + `${news.title}. ${news.summary}`.length, 0);
    const totalTtsCost = (ttsChars / 1_000_000) * 0.015;
    
    return res(
      ctx.json({
        success: true,
        mockup_statistics: {
          total_news_items: mockScrapedNews.length,
          content_stats: {
            total_characters: totalChars,
            total_words: totalWords,
            average_words_per_article: Math.round(totalWords / mockScrapedNews.length)
          },
          tts_stats: {
            total_tts_characters: ttsChars,
            estimated_total_cost: Math.round(totalTtsCost * 1000000) / 1000000,
            average_cost_per_reel: Math.round(totalTtsCost / mockScrapedNews.length * 1000000) / 1000000
          },
          categories,
          authors
        }
      })
    );
  }),

  // Legacy endpoints for compatibility
  rest.get('/api/reels/mix', (req, res, ctx) => {
    const count = parseInt(req.url.searchParams.get('count') || '10');
    
    return res(
      ctx.json({
        success: true,
        reels: mockData.reels.slice(0, count)
      })
    );
  }),

  rest.get('/api/agenda/ready', (req, res, ctx) => {
    const limit = parseInt(req.url.searchParams.get('limit') || '15');
    
    return res(
      ctx.json({
        success: true,
        reels: mockData.reels.slice(0, limit)
      })
    );
  }),

  // Articles endpoints
  rest.get('/api/articles', (req, res, ctx) => {
    const limit = parseInt(req.url.searchParams.get('limit') || '20');
    const offset = parseInt(req.url.searchParams.get('offset') || '0');
    
    return res(
      ctx.json({
        success: true,
        articles: mockData.articles.slice(offset, offset + limit)
      })
    );
  }),

  rest.get('/api/articles/:id', (req, res, ctx) => {
    const { id } = req.params;
    const article = mockData.articles.find(a => a.id === id);
    
    if (!article) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          message: 'Article not found'
        })
      );
    }
    
    return res(
      ctx.json({
        success: true,
        article
      })
    );
  }),

  // Auth endpoints (placeholder)
  rest.post('/api/auth/login', async (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        token: 'mock-jwt-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com'
        }
      })
    );
  })
];