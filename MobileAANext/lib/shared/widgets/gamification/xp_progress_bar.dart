// lib/widgets/gamification/xp_progress_bar.dart

import 'package:flutter/material.dart';

/// XP Progress Bar Widget
/// Günlük hedef gösterimi
class XPProgressBar extends StatelessWidget {
  final int currentXP;
  final int goalXP;
  final bool compact; // Küçük versiyon için

  const XPProgressBar({
    Key? key,
    required this.currentXP,
    required this.goalXP,
    this.compact = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final progress = (currentXP / goalXP).clamp(0.0, 1.0);
    final isCompleted = currentXP >= goalXP;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        // Progress bar
        Container(
          height: compact ? 6 : 8,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(compact ? 3 : 4),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(compact ? 3 : 4),
            child: Stack(
              children: [
                // Background
                Container(color: Colors.grey[200]),
                
                // Progress fill
                FractionallySizedBox(
                  widthFactor: progress,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isCompleted
                            ? [Colors.green[400]!, Colors.green[600]!]
                            : [Colors.blue[400]!, Colors.blue[600]!],
                      ),
                    ),
                  ),
                ),
                
                // Shine effect
                if (!compact)
                  FractionallySizedBox(
                    widthFactor: progress,
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.white.withOpacity(0.3),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
        
        // XP Text
        if (!compact) ...[
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$currentXP / $goalXP XP',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isCompleted ? Colors.green[700] : Colors.grey[700],
                ),
              ),
              if (isCompleted)
                Row(
                  children: [
                    Icon(Icons.check_circle, 
                      size: 14, 
                      color: Colors.green[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Tamamlandı!',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Colors.green[700],
                      ),
                    ),
                  ],
                )
              else
                Text(
                  '${(progress * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                  ),
                ),
            ],
          ),
        ],
      ],
    );
  }
}