// lib/widgets/gamification/reels_xp_overlay.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/gamification_provider.dart';

/// Reels XP Overlay
/// Reels sayfası üstünde gözüken progress bar'lar
/// - Düğüm progress (0-100 XP)
/// - Level progress (tüm düğümler)
class ReelsXPOverlay extends StatelessWidget {
  const ReelsXPOverlay({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<GamificationProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black.withOpacity(0.7),
                Colors.black.withOpacity(0.3),
                Colors.transparent,
              ],
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Level ve düğüm bilgisi
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Level badge
                  _buildLevelBadge(provider),
                  
                  const SizedBox(width: 12),
                  
                  // Düğüm bilgisi
                  Expanded(
                    child: _buildNodeInfo(provider),
                  ),
                ],
              ),
              
              const SizedBox(height: 10),
              
              // Düğüm progress bar
              _buildNodeProgressBar(provider),
              
              const SizedBox(height: 8),
              
              // Level progress bar
              _buildLevelProgressBar(provider),
            ],
          ),
        );
      },
    );
  }
  
  // ============ LEVEL BADGE ============
  
  Widget _buildLevelBadge(GamificationProvider provider) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.amber[400]!, Colors.orange[500]!],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.4),
            blurRadius: 8,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            '⚡',
            style: TextStyle(fontSize: 18),
          ),
          const SizedBox(width: 6),
          Text(
            'Lv ${provider.currentLevel}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 15,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
  
  // ============ DÜĞÜM BİLGİSİ ============
  
  Widget _buildNodeInfo(GamificationProvider provider) {
    final state = provider.state;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.6),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Düğüm gösterimi
          Text(
            '${state.currentNode + 1}/${state.nodesInLevel} Düğüm',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(width: 8),
          
          // XP gösterimi
          Text(
            '${state.currentXP}/100',
            style: TextStyle(
              color: Colors.amber[300],
              fontSize: 13,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
  
  // ============ DÜĞÜM PROGRESS BAR ============
  
  Widget _buildNodeProgressBar(GamificationProvider provider) {
    final progress = provider.nodeProgress;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Düğüm İlerlemesi',
              style: TextStyle(
                color: Colors.white.withOpacity(0.9),
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              '${(progress * 100).toInt()}%',
              style: TextStyle(
                color: Colors.amber[300],
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 6),
        
        // Progress bar
        Container(
          height: 8,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(4),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: Stack(
              children: [
                // Background
                Container(color: Colors.white.withOpacity(0.1)),
                
                // Progress fill
                FractionallySizedBox(
                  widthFactor: progress,
                  alignment: Alignment.centerLeft,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.amber[400]!,
                          Colors.orange[500]!,
                        ],
                      ),
                    ),
                  ),
                ),
                
                // Shine effect
                FractionallySizedBox(
                  widthFactor: progress,
                  alignment: Alignment.centerLeft,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.white.withOpacity(0.4),
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
      ],
    );
  }
  
  // ============ LEVEL PROGRESS BAR ============
  
  Widget _buildLevelProgressBar(GamificationProvider provider) {
    final state = provider.state;
    final progress = provider.levelProgress;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Level ${state.currentLevel} İlerlemesi',
              style: TextStyle(
                color: Colors.white.withOpacity(0.9),
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              '${state.xpEarnedInLevel}/${state.xpNeededForLevel} XP',
              style: TextStyle(
                color: Colors.blue[300],
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 6),
        
        // Progress bar
        Container(
          height: 6,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(3),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: Stack(
              children: [
                // Background
                Container(color: Colors.white.withOpacity(0.1)),
                
                // Progress fill
                FractionallySizedBox(
                  widthFactor: progress,
                  alignment: Alignment.centerLeft,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.blue[400]!,
                          Colors.indigo[500]!,
                        ],
                      ),
                    ),
                  ),
                ),
                
                // Shine effect
                FractionallySizedBox(
                  widthFactor: progress,
                  alignment: Alignment.centerLeft,
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
      ],
    );
  }
}