// lib/shared/widgets/gamification/level_chain_display.dart
// Profesyonel UI/UX tasarımlı düğüm sistemi

import 'package:flutter/material.dart';

class LevelChainDisplay extends StatelessWidget {
  final int currentLevel;
  final int currentNode;
  final int totalNodes;
  final int currentXP;
  final bool compact;

  const LevelChainDisplay({
    Key? key,
    required this.currentLevel,
    required this.currentNode,
    required this.totalNodes,
    this.currentXP = 0,
    this.compact = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompact();
    }
    return _buildFull(context);
  }

  Widget _buildCompact() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFFFCD34D),
            const Color(0xFFFBBF24),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFFBBF24).withOpacity(0.4),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.3),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.bolt,
              size: 16,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            'Level $currentLevel',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFull(BuildContext context) {
    final levelProgress = totalNodes > 0 ? currentNode / totalNodes : 0.0;
    final nodeProgress = currentXP / 100;
    
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFFFFFBEB), // amber-50
            const Color(0xFFFEF3C7), // amber-100
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(0xFFFCD34D), // amber-300
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFFBBF24).withOpacity(0.2),
            blurRadius: 16,
            spreadRadius: 0,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [
                          Color(0xFFFCD34D), // amber-300
                          Color(0xFFFBBF24), // amber-400
                        ],
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFFBBF24).withOpacity(0.5),
                          blurRadius: 12,
                          spreadRadius: 0,
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.bolt,
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Level $currentLevel',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF92400E), // amber-900
                          letterSpacing: -0.5,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '$currentNode / $totalNodes düğüm',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF78716C), // stone-500
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: const Color(0xFFFCD34D),
                    width: 2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Text(
                  '${(levelProgress * 100).toInt()}%',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFB45309), // amber-700
                    letterSpacing: -0.5,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Düğüm zinciri
          _buildChainRow(nodeProgress),
          
          const SizedBox(height: 20),
          
          // Progress bar
          _buildProgressBar(levelProgress),
          
          const SizedBox(height: 16),
          
          // Info
          _buildInfoText(),
        ],
      ),
    );
  }

  Widget _buildChainRow(double nodeProgress) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (int i = 0; i < totalNodes; i++) ...[
            _buildNode(i, nodeProgress),
            if (i < totalNodes - 1) _buildConnector(i),
          ],
        ],
      ),
    );
  }

  Widget _buildNode(int index, double nodeProgress) {
    final isCompleted = index < currentNode;
    final isCurrent = index == currentNode;
    final isLocked = index > currentNode;
    
    return AnimatedContainer(
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeOutCubic,
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: isCompleted || isCurrent
            ? const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFFCD34D), // amber-300
                  Color(0xFFFBBF24), // amber-400
                  Color(0xFFF59E0B), // amber-500
                ],
              )
            : null,
        color: isLocked ? const Color(0xFFE7E5E4) : null, // stone-200
        border: Border.all(
          color: isCurrent 
              ? const Color(0xFFB45309) // amber-700
              : Colors.transparent,
          width: 3,
        ),
        boxShadow: isCompleted || isCurrent
            ? [
                BoxShadow(
                  color: const Color(0xFFFBBF24).withOpacity(0.4),
                  blurRadius: 12,
                  spreadRadius: 2,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Completed
          if (isCompleted)
            Container(
              padding: const EdgeInsets.all(2),
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_rounded,
                size: 28,
                color: Color(0xFFF59E0B),
              ),
            ),
          
          // Current with progress
          if (isCurrent)
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 36,
                  height: 36,
                  child: CircularProgressIndicator(
                    value: nodeProgress,
                    strokeWidth: 4,
                    backgroundColor: Colors.white.withOpacity(0.3),
                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                    strokeCap: StrokeCap.round,
                  ),
                ),
                Text(
                  '${(nodeProgress * 100).toInt()}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          
          // Locked
          if (isLocked)
            Icon(
              Icons.lock_outline_rounded,
              size: 24,
              color: Colors.grey[400],
            ),
        ],
      ),
    );
  }

  Widget _buildConnector(int index) {
    final isCompleted = index < currentNode;
    
    return Container(
      width: 32,
      height: 4,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        gradient: isCompleted
            ? const LinearGradient(
                colors: [
                  Color(0xFFFCD34D),
                  Color(0xFFFBBF24),
                ],
              )
            : null,
        color: isCompleted ? null : const Color(0xFFE7E5E4),
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }

  Widget _buildProgressBar(double progress) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Level İlerlemesi',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Color(0xFF78716C),
            letterSpacing: 0.3,
          ),
        ),
        const SizedBox(height: 10),
        Container(
          height: 12,
          decoration: BoxDecoration(
            color: const Color(0xFFF5F5F4), // stone-100
            borderRadius: BorderRadius.circular(6),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: Stack(
              children: [
                FractionallySizedBox(
                  widthFactor: progress,
                  child: Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Color(0xFFFCD34D),
                          Color(0xFFFBBF24),
                          Color(0xFFF59E0B),
                        ],
                      ),
                    ),
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: progress,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.white.withOpacity(0.5),
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

  Widget _buildInfoText() {
    final remainingNodes = totalNodes - currentNode;
    final remainingXP = (remainingNodes * 100) - currentXP;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.6),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Sonraki Level',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF78716C),
                ),
              ),
              const SizedBox(height: 2),
              Text(
                '$remainingNodes düğüm',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF92400E),
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [
                  Color(0xFFFCD34D),
                  Color(0xFFFBBF24),
                ],
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '$remainingXP XP',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}