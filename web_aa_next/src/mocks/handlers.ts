import { rest } from 'msw';

// Mock data
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
    },
    {
      "id": "2",
      "title": "Spor Haberleri - Futbol Dünyası",
      "content": "Son maçların analizi ve transfer gelişmeleri.",
      "category": "spor",
      "images": [
        "https://picsum.photos/400/600?random=3",
        "https://picsum.photos/400/600?random=4"
      ],
      "main_image": "https://picsum.photos/400/600?random=3",
      "audio_url": "/audio/test2.mp3",
      "subtitles": [
        { "start": 0, "end": 3, "text": "Futbol dünyasında heyecanlı gelişmeler." },
        { "start": 3, "end": 6, "text": "Transfer dönemi yaklaşıyor." },
        { "start": 6, "end": 9, "text": "Takımlar güçlenmek için çalışıyor." }
      ],
      "estimated_duration": 25,
      "tags": ["futbol", "spor", "transfer"],
      "author": "Sports Writer",
      "location": "Ankara"
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
    },
    {
      "id": "2",
      "title": "Sürdürülebilir Enerji Kaynaklarının Geleceği",
      "content": "Renewable energy sources and their impact on the global economy.",
      "category": "çevre",
      "images": [
        "https://picsum.photos/800/400?random=12"
      ],
      "main_image": "https://picsum.photos/800/400?random=12",
      "author": "Environment Reporter",
      "location": "Copenhagen",
      "published_date": "2024-01-16T14:30:00Z",
      "tags": ["enerji", "çevre", "sürdürülebilirlik"],
      "prevArticleId": "1",
      "nextArticleId": "3",
      "summary": "Yenilenebilir enerji kaynaklarının ekonomik etkileri."
    }
  ]
};

export const handlers = [
  // Reels endpoints
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