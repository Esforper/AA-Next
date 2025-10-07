// lib/widgets/gamification/streak_display.dart

import 'package:flutter/material.dart';

/// Streak Display Widget
/// 🔥 Günlük seri gösterimi
class StreakDisplay extends StatelessWidget {
  final int streakDays;
  final int percentile; // Kullanıcıların %X'i
  final bool compact;

  const StreakDisplay({
    Key? key,
    required this.streakDays,
    this.percentile = 0,
    this.compact = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompact();
    }
    return _buildFull(context);
  }

  // Compact version (Reels üstünde kullanılacak)
  Widget _buildCompact() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.6),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '🔥',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(width: 4),
          Text(
            '$streakDays gün',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  // Full version (Ana sayfada kullanılacak)
  Widget _buildFull(BuildContext context) {
    final color = _getStreakColor();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.1), color.withOpacity(0.05)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Row(
            children: [
              Text(
                '🔥',
                style: const TextStyle(fontSize: 28),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '$streakDays Günlük Seri',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  if (percentile > 0) ...[
                    const SizedBox(height: 2),
                    Text(
                      'Kullanıcıların %$percentile\'inden iyisin! 🎯',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Milestone gösterimi
          _buildMilestoneProgress(),
        ],
      ),
    );
  }

  // Streak milestone progress
  Widget _buildMilestoneProgress() {
    final milestones = [7, 14, 30, 100];
    final nextMilestone = milestones.firstWhere(
      (m) => m > streakDays,
      orElse: () => 100,
    );
    final previousMilestone = streakDays >= 7 
        ? milestones.lastWhere((m) => m <= streakDays, orElse: () => 0)
        : 0;
    
    final progress = previousMilestone > 0
        ? (streakDays - previousMilestone) / (nextMilestone - previousMilestone)
        : streakDays / nextMilestone;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Sonraki hedef: $nextMilestone gün',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress.clamp(0.0, 1.0),
            minHeight: 6,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(_getStreakColor()),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '${nextMilestone - streakDays} gün kaldı',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w500,
            color: Colors.grey[500],
          ),
        ),
      ],
    );
  }

  // Streak'e göre renk
  Color _getStreakColor() {
    if (streakDays >= 30) return Colors.purple[600]!;
    if (streakDays >= 14) return Colors.orange[700]!;
    if (streakDays >= 7) return Colors.orange[600]!;
    if (streakDays >= 3) return Colors.orange[500]!;
    return Colors.orange[400]!;
  }
}