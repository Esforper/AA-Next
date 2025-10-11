// lib/mobile_platform/widgets/home/streak_github_calendar.dart
// 🔥 GitHub-style Streak Calendar Widget

import 'package:flutter/material.dart';
import '../../../core/theme/aa_colors.dart';

class StreakGithubCalendar extends StatelessWidget {
  final Map<String, dynamic> calendarData; // date -> {xp, level}
  final int currentStreak;
  final int longestStreak;

  const StreakGithubCalendar({
    Key? key,
    required this.calendarData,
    required this.currentStreak,
    required this.longestStreak,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: AAColors.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Streak Takvimi',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AAColors.black,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Son 12 hafta',
                    style: TextStyle(
                      fontSize: 12,
                      color: AAColors.grey500,
                    ),
                  ),
                ],
              ),
              // Streak Stats
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  gradient: AAColors.redGradient,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.local_fire_department, color: Colors.white, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '$currentStreak gün',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Calendar Grid
          _buildCalendarGrid(),
          
          const SizedBox(height: 12),
          
          // Legend
          _buildLegend(),
          
          const SizedBox(height: 8),
          
          // Stats
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStat('Mevcut', '$currentStreak', AAColors.aaRed),
              _buildStat('En Uzun', '$longestStreak', AAColors.aaNavy),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCalendarGrid() {
    // Son 84 günü (12 hafta) al
    final now = DateTime.now();
    final days = <DateTime>[];
    
    for (int i = 83; i >= 0; i--) {
      days.add(now.subtract(Duration(days: i)));
    }
    
    // 7 satır (haftanın günleri) x 12 sütun (haftalar)
    return SizedBox(
      height: 100,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: List.generate(12, (weekIndex) {
          return Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(7, (dayIndex) {
              final dayIdx = weekIndex * 7 + dayIndex;
              if (dayIdx >= days.length) return const SizedBox.shrink();
              
              final day = days[dayIdx];
              final dateStr = _formatDate(day);
              final dayData = calendarData[dateStr];
              final level = dayData?['level'] ?? 0;
              
              return _buildDaySquare(day, level, dayData?['xp_earned'] ?? 0);
            }),
          );
        }),
      ),
    );
  }

  Widget _buildDaySquare(DateTime day, int level, int xp) {
    final color = _getColorForLevel(level);
    final isToday = _isToday(day);
    
    return Tooltip(
      message: '${_formatDateFull(day)}\n${xp > 0 ? "$xp XP" : "Aktivite yok"}',
      child: Container(
        width: 11,
        height: 11,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(2),
          border: isToday ? Border.all(color: AAColors.aaRed, width: 1.5) : null,
        ),
      ),
    );
  }

  Color _getColorForLevel(int level) {
    switch (level) {
      case 0:
        return AAColors.streakNone;
      case 1:
        return AAColors.streakLow;
      case 2:
        return AAColors.streakMed;
      case 3:
        return AAColors.streakHigh;
      default:
        return AAColors.streakNone;
    }
  }

  Widget _buildLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        Text('Az', style: TextStyle(fontSize: 10, color: AAColors.grey500)),
        const SizedBox(width: 4),
        _buildLegendSquare(AAColors.streakNone),
        _buildLegendSquare(AAColors.streakLow),
        _buildLegendSquare(AAColors.streakMed),
        _buildLegendSquare(AAColors.streakHigh),
        const SizedBox(width: 4),
        Text('Çok', style: TextStyle(fontSize: 10, color: AAColors.grey500)),
      ],
    );
  }

  Widget _buildLegendSquare(Color color) {
    return Container(
      width: 10,
      height: 10,
      margin: const EdgeInsets.symmetric(horizontal: 2),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }

  Widget _buildStat(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AAColors.grey500,
          ),
        ),
      ],
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  String _formatDateFull(DateTime date) {
    const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
    return '${date.day} ${months[date.month - 1]}';
  }

  bool _isToday(DateTime date) {
    final now = DateTime.now();
    return date.year == now.year && date.month == now.month && date.day == now.day;
  }
}