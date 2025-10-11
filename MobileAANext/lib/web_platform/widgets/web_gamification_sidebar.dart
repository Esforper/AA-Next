// lib/web_platform/widgets/web_gamification_sidebar.dart
// WEB İÇİN GAMIFICATION SIDEBAR - Level Chain + Daily Progress
// Mobile LevelChainDisplay + DailyProgressCard kombine

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/gamification_provider.dart';

class WebGamificationSidebar extends StatelessWidget {
  const WebGamificationSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 280,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(-2, 0),
          ),
        ],
      ),
      child: Consumer<GamificationProvider>(
        builder: (context, provider, _) {
          final state = provider.state;
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                const Text(
                  'İlerleme',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F2937),
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Daily Progress Card
                _buildDailyProgress(state),
                
                const SizedBox(height: 24),
                
                // Level Chain Display
                _buildLevelChain(state),
                
                const SizedBox(height: 24),
                
                // Streak Info
                _buildStreakInfo(state),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDailyProgress(state) {
    final currentXP = state.xpEarnedToday;
    final goalXP = state.dailyXPGoal;
    final progress = (currentXP / goalXP).clamp(0.0, 1.0);
    final goalCompleted = state.dailyGoalCompleted;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: goalCompleted
              ? [Colors.green[50]!, Colors.green[100]!]
              : [Colors.indigo[50]!, Colors.indigo[100]!],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: goalCompleted ? Colors.green[300]! : Colors.indigo[300]!,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title
          Row(
            children: [
              Text(
                goalCompleted ? '🎉' : '📊',
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  goalCompleted ? 'Günlük Hedef!' : 'Günlük İlerleme',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: goalCompleted ? Colors.green[800] : Colors.indigo[800],
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Progress Bar
          Stack(
            children: [
              // Background
              Container(
                height: 12,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(6),
                ),
              ),
              // Progress
              FractionallySizedBox(
                widthFactor: progress,
                child: Container(
                  height: 12,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: goalCompleted
                          ? [Colors.green[400]!, Colors.green[600]!]
                          : [Colors.indigo[400]!, Colors.indigo[600]!],
                    ),
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // XP Text
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$currentXP / $goalXP XP',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[700],
                ),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: goalCompleted ? Colors.green[700] : Colors.indigo[700],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Stats
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('📰', state.reelsWatchedToday),
              _buildStatItem('😊', state.emojisGivenToday),
              _buildStatItem('📖', state.detailsReadToday),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String emoji, int count) {
    return Column(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(height: 4),
        Text(
          '$count',
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1F2937),
          ),
        ),
      ],
    );
  }

  Widget _buildLevelChain(state) {
    final currentLevel = state.currentLevel;
    final currentNode = state.currentNode;
    final totalNodes = state.nodesInLevel;
    final currentXP = state.currentXP;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFFFBEB), // amber-50
            Color(0xFFFEF3C7), // amber-100
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFFCD34D), // amber-300
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Level Badge
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFFCD34D), Color(0xFFFBBF24)],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('⚡', style: TextStyle(fontSize: 18)),
                    const SizedBox(width: 6),
                    Text(
                      'Level $currentLevel',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF78350F), // amber-900
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              Text(
                '$currentNode/$totalNodes',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[700],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Node Chain (Düğüm sistemi)
          _buildNodeChain(currentNode, totalNodes),
          
          const SizedBox(height: 12),
          
          // Current Node Progress
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Node ${currentNode + 1}',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey[700],
                    ),
                  ),
                  Text(
                    '$currentXP / 100 XP',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: Colors.amber[800],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Stack(
                children: [
                  Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: (currentXP / 100).clamp(0.0, 1.0),
                    child: Container(
                      height: 8,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFBBF24), Color(0xFFF59E0B)],
                        ),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNodeChain(int currentNode, int totalNodes) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: List.generate(totalNodes, (index) {
        final isCompleted = index < currentNode;
        final isCurrent = index == currentNode;
        
        return Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            gradient: isCompleted || isCurrent
                ? const LinearGradient(
                    colors: [Color(0xFFFBBF24), Color(0xFFF59E0B)],
                  )
                : null,
            color: isCompleted || isCurrent ? null : Colors.grey[300],
            shape: BoxShape.circle,
            border: Border.all(
              color: isCurrent ? Colors.amber[700]! : Colors.transparent,
              width: 2,
            ),
            boxShadow: isCompleted || isCurrent
                ? [
                    BoxShadow(
                      color: const Color(0xFFFBBF24).withValues(alpha: 0.3),
                      blurRadius: 8,
                      spreadRadius: 0,
                    ),
                  ]
                : null,
          ),
          child: Center(
            child: isCompleted
                ? const Icon(Icons.check, color: Colors.white, size: 16)
                : isCurrent
                    ? const Icon(Icons.play_arrow, color: Colors.white, size: 16)
                    : Text(
                        '${index + 1}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[600],
                        ),
                      ),
          ),
        );
      }),
    );
  }

  Widget _buildStreakInfo(state) {
    final streakDays = state.currentStreak;
    final percentile = state.streakPercentile;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange[50],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange[300]!,
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.orange[100],
              shape: BoxShape.circle,
            ),
            child: const Text('🔥', style: TextStyle(fontSize: 24)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$streakDays Gün Streak',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[900],
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  percentile > 0
                      ? 'Top $percentile% 🎯'
                      : 'Devam et!',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}