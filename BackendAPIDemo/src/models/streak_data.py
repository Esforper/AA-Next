# backend/src/models/streak_data.py
# 🔥 Streak Data Models - GitHub style contribution

from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import date, datetime

class DayActivity(BaseModel):
    """Bir günün aktivite verisi"""
    date: str = Field(..., description="ISO format date (YYYY-MM-DD)")
    xp_earned: int = Field(default=0, ge=0, description="O gün kazanılan XP")
    reels_watched: int = Field(default=0, ge=0, description="İzlenen reel sayısı")
    level: int = Field(default=0, description="Gün içindeki seviye (0=yok, 1=düşük, 2=orta, 3=yüksek)")
    
    def calculate_level(self) -> int:
        """XP'ye göre seviye hesapla (GitHub tarzı)"""
        if self.xp_earned == 0:
            return 0
        elif self.xp_earned < 100:
            return 0  # Minimum karşılanmadı
        elif self.xp_earned < 200:
            return 1  # Düşük
        elif self.xp_earned < 300:
            return 2  # Orta
        else:
            return 3  # Yüksek


class WeekStats(BaseModel):
    """Haftalık istatistikler"""
    week_start: str = Field(..., description="Haftanın başlangıcı (ISO format)")
    days_active: int = Field(default=0, ge=0, le=7)
    total_xp: int = Field(default=0, ge=0)
    total_reels: int = Field(default=0, ge=0)
    avg_xp_per_day: float = Field(default=0.0, ge=0)


class StreakCalendar(BaseModel):
    """GitHub tarzı contribution calendar"""
    user_id: str
    calendar_data: Dict[str, DayActivity] = Field(
        default_factory=dict,
        description="Date -> Activity mapping"
    )
    weeks_to_show: int = Field(default=12, description="Gösterilecek hafta sayısı")
    
    def get_activity_for_date(self, target_date: date) -> Optional[DayActivity]:
        """Belirli bir tarih için aktivite getir"""
        date_str = target_date.isoformat()
        return self.calendar_data.get(date_str)
    
    def get_week_stats(self, week_start: date) -> WeekStats:
        """Bir haftanın istatistiklerini hesapla"""
        from datetime import timedelta
        
        days_active = 0
        total_xp = 0
        total_reels = 0
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            activity = self.get_activity_for_date(day)
            
            if activity and activity.xp_earned >= 100:  # Minimum karşılandı mı?
                days_active += 1
                total_xp += activity.xp_earned
                total_reels += activity.reels_watched
        
        avg_xp = total_xp / 7 if days_active > 0 else 0.0
        
        return WeekStats(
            week_start=week_start.isoformat(),
            days_active=days_active,
            total_xp=total_xp,
            total_reels=total_reels,
            avg_xp_per_day=avg_xp
        )


class StreakInfo(BaseModel):
    """Kullanıcı streak bilgisi"""
    user_id: str
    current_streak: int = Field(default=0, ge=0, description="Mevcut streak (gün)")
    longest_streak: int = Field(default=0, ge=0, description="En uzun streak")
    last_activity_date: Optional[str] = Field(None, description="Son aktivite tarihi")
    
    # Günlük minimum gereksinim
    min_xp_required: int = Field(default=100, description="Streak için günlük min XP")
    min_reels_required: int = Field(default=3, description="Streak için günlük min reel")
    
    # Bu hafta
    this_week_days_active: int = Field(default=0, ge=0, le=7)
    this_week_xp: int = Field(default=0, ge=0)
    
    # Calendar
    calendar: Optional[StreakCalendar] = None
    
    def is_streak_alive(self) -> bool:
        """Streak hala devam ediyor mu?"""
        if not self.last_activity_date:
            return False
        
        from datetime import date
        last_date = date.fromisoformat(self.last_activity_date)
        today = date.today()
        days_diff = (today - last_date).days
        
        # Son 2 gün içinde aktivite varsa streak canlı
        return days_diff <= 1


class StreakResponse(BaseModel):
    """API Response for streak data"""
    success: bool = True
    streak_info: StreakInfo
    calendar_data: Dict[str, DayActivity] = Field(default_factory=dict)
    this_week_stats: Optional[WeekStats] = None
    message: str = "Streak data retrieved successfully"