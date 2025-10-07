// lib/widgets/gamification/level_chain_display.dart

import 'package:flutter/material.dart';

/// Level Chain Display Widget
/// Zincir şeklinde level gösterimi
class LevelChainDisplay extends StatelessWidget {
  final int currentLevel;
  final int currentChain;
  final int totalChains;
  final bool compact;

  const LevelChainDisplay({
    Key? key,
    required this.currentLevel,
    required this.currentChain,
    required this.totalChains,
    this.compact = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompact();
    }
    return _buildFull(context);
  }

  // Compact version (Reels üstünde)
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
            '⚡',
            style: const TextStyle(fontSize: 14),
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

  // Full version (Profile ve Home sayfasında)
  Widget _buildFull(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.amber[50]!,
            Colors.orange[50]!,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amber[200]!, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Level header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [Colors.amber[400]!, Colors.orange[500]!],
                      ),
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.amber.withOpacity(0.3),
                          blurRadius: 8,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                    child: const Text(
                      '⚡',
                      style: TextStyle(fontSize: 20),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Level $currentLevel',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[800],
                        ),
                      ),
                      Text(
                        '$currentChain / $totalChains zincir',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
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
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber[300]!),
                ),
                child: Text(
                  '${((currentChain / totalChains) * 100).toInt()}%',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[700],
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Chain visualization
          _buildChainRow(),
          
          const SizedBox(height: 8),
          
          // Next level info
          Text(
            'Sonraki level: ${totalChains - currentChain} zincir kaldı',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  // Chain görselleştirmesi
  Widget _buildChainRow() {
    return Row(
      children: [
        for (int i = 0; i < totalChains; i++) ...[
          // Chain node
          _buildChainNode(i),
          
          // Connector (son node'dan sonra gösterme)
          if (i < totalChains - 1) _buildConnector(i),
        ],
      ],
    );
  }

  // Tek bir chain node
  Widget _buildChainNode(int index) {
    final isCompleted = index < currentChain;
    final isCurrent = index == currentChain;
    
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: isCompleted ? Colors.amber[400] : Colors.grey[300],
        border: Border.all(
          color: isCurrent ? Colors.orange[600]! : Colors.transparent,
          width: 3,
        ),
        boxShadow: isCompleted || isCurrent
            ? [
                BoxShadow(
                  color: Colors.amber.withOpacity(0.4),
                  blurRadius: 8,
                  spreadRadius: 1,
                ),
              ]
            : null,
      ),
      child: Center(
        child: isCompleted
            ? Icon(
                Icons.check,
                size: 16,
                color: Colors.white,
              )
            : Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isCurrent ? Colors.orange[600] : Colors.grey[400],
                ),
              ),
      ),
    );
  }

  // Connector line
  Widget _buildConnector(int index) {
    final isCompleted = index < currentChain;
    
    return Expanded(
      child: Container(
        height: 3,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: isCompleted ? Colors.amber[400] : Colors.grey[300],
          borderRadius: BorderRadius.circular(2),
        ),
      ),
    );
  }
}