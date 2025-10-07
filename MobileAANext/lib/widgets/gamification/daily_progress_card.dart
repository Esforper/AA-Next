// lib/widgets/gamification/daily_progress_card.dart

import 'package:flutter/material.dart';
import 'xp_progress_bar.dart';
import 'streak_display.dart';

/// Daily Progress Card
/// Ana sayfada günlük ilerleme gösterimi
class DailyProgressCard extends StatelessWidget {
  final int currentXP;
  final int goalXP;
  final int streakDays;
  final int percentile;
  final bool goalCompleted;

  const DailyProgressCard({
    Key? key,
    required this.currentXP,
    required this.goalXP,
    required this.streakDays,
    this.percentile = 0,
    this.goalCompleted = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: goalCompleted
              ? [Colors.green[50]!, Colors.teal[50]!]
              : [Colors.blue[50]!, Colors.indigo[50]!],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: goalCompleted 
                ? Colors.green.withOpacity(0.15)
                : Colors.blue.withOpacity(0.15),
            blurRadius: 20,
            spreadRadius: 2,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          goalCompleted ? '🎉' : '📊',
                          style: const TextStyle(fontSize: 24),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          goalCompleted ? 'Günlük Hedef Tamamlandı!' : 'Günlük İlerleme',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: goalCompleted 
                                ? Colors.green[800]
                                : Colors.indigo[800],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _getMotivationalText(),
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // XP Progress
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: XPProgressBar(
              currentXP: currentXP,
              goalXP: goalXP,
            ),
          ),

          const SizedBox(height: 16),

          // Divider
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Divider(
              color: Colors.grey[300],
              thickness: 1,
            ),
          ),

          const SizedBox(height: 12),

          // Streak Display (compact in card)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    icon: '🔥',
                    label: 'Streak',
                    value: '$streakDays gün',
                    color: Colors.orange,
                  ),
                ),
                Container(
                  width: 1,
                  height: 40,
                  color: Colors.grey[300],
                ),
                Expanded(
                  child: _buildStatItem(
                    icon: '🎯',
                    label: 'Sıralama',
                    value: percentile > 0 ? 'Top %$percentile' : '-',
                    color: Colors.purple,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Action button
          if (!goalCompleted)
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    // Navigate to reels
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue[600],
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 0,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        'Haber İzlemeye Başla',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.arrow_forward, size: 18),
                    ],
                  ),
                ),
              ),
            )
          else
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.green[100],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green[300]!, width: 1.5),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.check_circle, color: Colors.green[700], size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'Harika! Yarın tekrar gel',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[800],
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required String icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Text(
          icon,
          style: const TextStyle(fontSize: 24),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  String _getMotivationalText() {
    final progress = currentXP / goalXP;
    
    if (goalCompleted) {
      return 'Streak\'in devam ediyor! 🎊';
    } else if (progress >= 0.8) {
      return 'Neredeyse tamam! Son bir haber daha 💪';
    } else if (progress >= 0.5) {
      return 'Yarı yoldasın, devam et! 🚀';
    } else if (progress >= 0.2) {
      return 'İyi başladın, momentum kazanıyorsun! ⭐';
    } else {
      return 'Bugün henüz başlamadın, hadi başlayalım! 🌟';
    }
  }
}