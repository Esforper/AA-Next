# backend/src/services/category_feed_service.py
# 🎯 Category-based Feed Service

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models.reels_tracking import ReelFeedItem
from .reels_analytics import reels_analytics_service


class CategoryFeedService:
    """Kategoriye özel feed oluşturma servisi"""
    
    # Kategori tanımları
    CATEGORIES = {
        'guncel': {'name': 'Güncel', 'icon': '📰', 'color': '#E30613'},
        'ekonomi': {'name': 'Ekonomi', 'icon': '💰', 'color': '#0052AD'},
        'spor': {'name': 'Spor', 'icon': '⚽', 'color': '#00C853'},
        'teknoloji': {'name': 'Teknoloji', 'icon': '💻', 'color': '#6200EA'},
        'kultur': {'name': 'Kültür', 'icon': '🎨', 'color': '#FF6D00'},
        'dunya': {'name': 'Dünya', 'icon': '🌍', 'color': '#00B8D4'},
        'politika': {'name': 'Politika', 'icon': '🏛️', 'color': '#003D82'},
        'saglik': {'name': 'Sağlık', 'icon': '🏥', 'color': '#00E676'},
        'egitim': {'name': 'Eğitim', 'icon': '📚', 'color': '#FF9800'},
        'yasam': {'name': 'Yaşam', 'icon': '🌟', 'color': '#9C27B0'},
    }
    
    def __init__(self):
        print("✅ CategoryFeedService initialized")
    
    async def get_category_feed(
        self,
        user_id: str,
        category: str,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kategoriye özel feed getir
        
        Args:
            user_id: Kullanıcı ID
            category: Kategori slug (guncel, ekonomi, etc)
            limit: Sonuç sayısı
            cursor: Pagination için
        """
        print(f"🎯 Getting {category} feed for user {user_id}")
        
        # Kategori geçerli mi?
        if category not in self.CATEGORIES:
            return {
                'success': False,
                'message': f'Invalid category: {category}',
                'available_categories': list(self.CATEGORIES.keys())
            }
        
        # O kategorideki tüm reels'leri al
        all_reels = await reels_analytics_service.get_reels_by_category(category)
        
        if not all_reels:
            print(f"⚠️ No reels found for category: {category}")
            return {
                'success': True,
                'reels': [],
                'category_info': self.CATEGORIES[category],
                'pagination': {'has_next': False},
                'message': f'No reels available in {category} category'
            }
        
        # Son 7 gün içindeki haberleri önceliklendir
        recent_cutoff = datetime.now() - timedelta(days=7)
        
        fresh_reels = [r for r in all_reels if r.published_at > recent_cutoff]
        older_reels = [r for r in all_reels if r.published_at <= recent_cutoff]
        
        # Karıştır ve birleştir (taze olanlar önce)
        import random
        random.shuffle(fresh_reels)
        random.shuffle(older_reels)
        sorted_reels = fresh_reels + older_reels
        
        print(f"📊 Total: {len(sorted_reels)} | Fresh: {len(fresh_reels)} | Older: {len(older_reels)}")
        
        # Pagination
        start_idx = 0
        if cursor:
            # Cursor'dan sonraki reels'leri bul
            for i, reel in enumerate(sorted_reels):
                if reel.id == cursor:
                    start_idx = i + 1
                    break
        
        # Limit kadar al
        page_reels = sorted_reels[start_idx:start_idx + limit]
        has_next = start_idx + limit < len(sorted_reels)
        next_cursor = page_reels[-1].id if page_reels and has_next else None
        
        print(f"✅ Returning {len(page_reels)} reels (has_next: {has_next})")
        
        return {
            'success': True,
            'reels': [self._serialize_reel(r) for r in page_reels],
            'category_info': self.CATEGORIES[category],
            'pagination': {
                'has_next': has_next,
                'next_cursor': next_cursor,
                'total_in_category': len(sorted_reels)
            }
        }
    
    def _serialize_reel(self, reel: ReelFeedItem) -> Dict:
        """Reel'i JSON serializable hale getir"""
        return {
            'id': reel.id,
            'news_data': {
                'title': reel.news_data.title,
                'summary': reel.news_data.summary,
                'category': reel.news_data.category,
                'url': reel.news_data.url,
                'published_at': reel.news_data.published_at.isoformat(),
                'images': reel.news_data.images or [],
                'tags': reel.news_data.tags or []
            },
            'audio_url': reel.audio_url,
            'duration_seconds': reel.duration_seconds,
            'published_at': reel.published_at.isoformat(),
            'is_fresh': (datetime.now() - reel.published_at).days <= 1
        }
    
    async def get_all_categories(self) -> Dict[str, Any]:
        """Tüm kategorileri ve istatistiklerini getir"""
        print("📋 Getting all categories")
        
        categories_with_stats = []
        
        for cat_id, cat_info in self.CATEGORIES.items():
            # Her kategorideki reel sayısını hesapla
            reels = await reels_analytics_service.get_reels_by_category(cat_id)
            
            categories_with_stats.append({
                'id': cat_id,
                'name': cat_info['name'],
                'icon': cat_info['icon'],
                'color': cat_info['color'],
                'total_reels': len(reels),
                'has_content': len(reels) > 0
            })
        
        # Reel sayısına göre sırala (çoktan aza)
        categories_with_stats.sort(key=lambda x: x['total_reels'], reverse=True)
        
        print(f"✅ Returning {len(categories_with_stats)} categories")
        
        return {
            'success': True,
            'categories': categories_with_stats,
            'total_categories': len(categories_with_stats)
        }


# Global instance
category_feed_service = CategoryFeedService()