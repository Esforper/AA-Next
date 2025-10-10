// lib/widgets/gamification/level_chain_display.dart

import 'package:flutter/material.dart';

/// Level Chain Display Widget
/// Düğüm şeklinde level gösterimi
/// Her düğüm = 100 XP
class LevelChainDisplay extends StatelessWidget {
  final int currentLevel;
  final int currentNode;
  final int totalNodes;
  final int currentXP; // Mevcut düğümdeki XP (0-100)
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

  // ============ COMPACT VERSION ============
  // Reels üstünde kullanılıyor (artık overlay var ama yedek)
  
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
          const Text(
            '⚡',
            style: TextStyle(fontSize: 14),
          ),
          const SizedBox(width: 4),
          Text(
            'Lv $currentLevel',
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

  // ============ FULL VERSION ============
  // Ana sayfa ve profil sayfasında kullanılıyor
  
  Widget _buildFull(BuildContext context) {
    final levelProgress = totalNodes > 0 ? currentNode / totalNodes : 0.0;
    final nodeProgress = currentXP / 100;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.amber[50]!,
            Colors.orange[50]!,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.amber[200]!, width: 2),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.2),
            blurRadius: 12,
            spreadRadius: 2,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Level info
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.amber[400]!, Colors.orange[500]!],
                      ),
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.amber.withOpacity(0.4),
                          blurRadius: 8,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                    child: const Text(
                      '⚡',
                      style: TextStyle(fontSize: 24),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Level $currentLevel',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[900],
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '$currentNode / $totalNodes düğüm',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              
              // Progress percentage
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber[300]!, width: 2),
                ),
                child: Text(
                  '${(levelProgress * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[700],
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Chain visualization
          _buildChainRow(nodeProgress),
          
          const SizedBox(height: 16),
          
          // Progress bar
          _buildLevelProgressBar(levelProgress),
          
          const SizedBox(height: 12),
          
          // Info text
          _buildInfoText(),
        ],
      ),
    );
  }
  
  // ============ CHAIN GÖRSEL ============
  
  Widget _buildChainRow(double nodeProgress) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (int i = 0; i < totalNodes; i++) ...[
          _buildChainNode(i, nodeProgress),
          
          // Connector (son node'dan sonra gösterme)
          if (i < totalNodes - 1) _buildConnector(i),
        ],
      ],
    );
  }
  
  // Tek bir düğüm
  Widget _buildChainNode(int index, double nodeProgress) {
    final isCompleted = index < currentNode;
    final isCurrent = index == currentNode;
    
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: isCompleted || isCurrent
            ? LinearGradient(
                colors: [Colors.amber[400]!, Colors.orange[500]!],
              )
            : null,
        color: isCompleted || isCurrent ? null : Colors.grey[300],
        border: Border.all(
          color: isCurrent ? Colors.orange[700]! : Colors.transparent,
          width: 3,
        ),
        boxShadow: isCompleted || isCurrent
            ? [
                BoxShadow(
                  color: Colors.amber.withOpacity(0.5),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Stack(
        children: [
          // Completed check
          if (isCompleted)
            const Center(
              child: Icon(
                Icons.check,
                size: 20,
                color: Colors.white,
              ),
            ),
          
          // Current node progress
          if (isCurrent)
            Center(
              child: SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  value: nodeProgress,
                  strokeWidth: 3,
                  backgroundColor: Colors.white.withOpacity(0.3),
                  valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
            ),
          
          // Empty node
          if (!isCompleted && !isCurrent)
            Center(
              child: Container(
                width: 14,
                height: 14,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.grey[400],
                ),
              ),
            ),
        ],
      ),
    );
  }
  
  // Bağlantı çizgisi
  Widget _buildConnector(int index) {
    final isCompleted = index < currentNode;
    
    return Container(
      width: 16,
      height: 4,
      margin: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        gradient: isCompleted
            ? LinearGradient(
                colors: [Colors.amber[400]!, Colors.orange[500]!],
              )
            : null,
        color: isCompleted ? null : Colors.grey[300],
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }
  
  // ============ LEVEL PROGRESS BAR ============
  
  Widget _buildLevelProgressBar(double progress) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Level İlerlemesi',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        Container(
          height: 10,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(5),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(5),
            child: Stack(
              children: [
                // Progress fill
                FractionallySizedBox(
                  widthFactor: progress,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.amber[400]!, Colors.orange[500]!],
                      ),
                    ),
                  ),
                ),
                
                // Shine effect
                FractionallySizedBox(
                  widthFactor: progress,
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
  
  // ============ INFO TEXT ============
  
  Widget _buildInfoText() {
    final remainingNodes = totalNodes - currentNode;
    final remainingXP = (remainingNodes * 100) - currentXP;
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Sonraki level: $remainingNodes düğüm',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: Colors.grey[600],
          ),
        ),
        Text(
          '$remainingXP XP kaldı',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.orange[700],
          ),
        ),
      ],
    );
  }
}