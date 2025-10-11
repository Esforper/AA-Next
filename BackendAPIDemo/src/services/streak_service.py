# backend/src/services/streak_service.py
# 🔥 Streak Service - GitHub style contribution tracking

from typing import Dict, Optional
from datetime import date, datetime, timedelta
from pathlib import Path
import json

from ..models.streak_data import (
    StreakInfo, StreakCalendar, DayActivity, WeekStats, StreakResponse
)


class StreakService:
    """Streak hesaplama ve yönetim servisi"""
    
    def __init__(self):
        self.data_dir = Path("data/streaks")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ StreakService initialized: {self.data_dir}")
    
    def _get_file_path(self, user_id: str) -> Path:
        """Kullanıcı streak dosya yolu"""
        return self.data_dir / f"{user_id}_streak.json"
    
    async def get_streak_info(self, user_id: str) -> StreakResponse:
        """Kullanıcı streak bilgisini getir"""
        print(f"📊 Getting streak for user: {user_id}")
        
        # Dosyadan oku veya yeni oluştur
        streak_info = self._load_or_create(user_id)
        
        # Calendar data oluştur (son 12 hafta)
        calendar = self._build_calendar(user_id, weeks=12)
        
        # Bu haftanın istatistikleri
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        this_week = calendar.get_week_stats(week_start)
        
        print(f"🔥 Current streak: {streak_info.current_streak} days")
        
        return StreakResponse(
            success=True,
            streak_info=streak_info,
            calendar_data=calendar.calendar_data,
            this_week_stats=this_week
        )
    
    def _load_or_create(self, user_id: str) -> StreakInfo:
        """Streak bilgisini yükle veya oluştur"""
        file_path = self._get_file_path(user_id)
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return StreakInfo(**data)
        
        # Yeni kullanıcı
        return StreakInfo(user_id=user_id)
    
    def _build_calendar(self, user_id: str, weeks: int = 12) -> StreakCalendar:
        """GitHub tarzı calendar oluştur"""
        from ..services.gamification_service import gamification_service
        
        calendar_data = {}
        today = date.today()
        
        # Son X hafta için veri topla
        for i in range(weeks * 7):
            target_date = today - timedelta(days=i)
            date_str = target_date.isoformat()
            
            # O günün XP'sini al (gamification service'den)
            user = gamification_service._get_or_create_user(user_id)
            
            # XP history'den o günün verisini bul
            daily_xp = 0
            daily_reels = 0
            
            for xp_entry in user.xp_history:
                entry_date = datetime.fromisoformat(xp_entry['timestamp']).date()
                if entry_date == target_date:
                    daily_xp += xp_entry['xp_amount']
            
            # Activity oluştur
            activity = DayActivity(
                date=date_str,
                xp_earned=daily_xp,
                reels_watched=daily_reels,
                level=0
            )
            activity.level = activity.calculate_level()
            
            calendar_data[date_str] = activity
        
        return StreakCalendar(
            user_id=user_id,
            calendar_data=calendar_data,
            weeks_to_show=weeks
        )
    
    async def update_streak(self, user_id: str, xp_earned: int) -> StreakInfo:
        """XP kazanıldığında streak güncelle"""
        print(f"🔄 Updating streak for {user_id}: +{xp_earned} XP")
        
        streak_info = self._load_or_create(user_id)
        today_str = date.today().isoformat()
        
        # Bugün minimum karşılandı mı?
        if xp_earned >= streak_info.min_xp_required:
            
            # Son aktivite bugünse, streak değişmez
            if streak_info.last_activity_date == today_str:
                print(f"✅ Already counted today")
                self._save(streak_info)
                return streak_info
            
            # Dünse, streak devam
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if streak_info.last_activity_date == yesterday:
                streak_info.current_streak += 1
                print(f"🔥 Streak extended: {streak_info.current_streak}")
            
            # 2+ gün boşluksa, streak kırıldı
            elif streak_info.last_activity_date:
                last_date = date.fromisoformat(streak_info.last_activity_date)
                if (date.today() - last_date).days > 1:
                    print(f"💔 Streak broken! Starting fresh")
                    streak_info.current_streak = 1
            
            # İlk kez aktivite
            else:
                streak_info.current_streak = 1
                print(f"🎉 First streak day!")
            
            # Update stats
            streak_info.last_activity_date = today_str
            if streak_info.current_streak > streak_info.longest_streak:
                streak_info.longest_streak = streak_info.current_streak
        
        self._save(streak_info)
        return streak_info
    
    def _save(self, streak_info: StreakInfo):
        """Streak bilgisini kaydet"""
        file_path = self._get_file_path(streak_info.user_id)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(streak_info.dict(), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Streak saved: {file_path}")


# Global instance
streak_service = StreakService()