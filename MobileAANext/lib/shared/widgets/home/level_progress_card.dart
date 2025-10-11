// lib/mobile_platform/widgets/home/level_progress_card.dart
// ⛓️ Level & Node Progress Card - Vertical Chain

import 'package:flutter/material.dart';
import '../../../core/theme/aa_colors.dart';

class LevelProgressCard extends StatefulWidget {
  final int currentLevel;
  final int currentNode;
  final int nodesInLevel;
  final int currentXP;
  final int totalXP;

  const LevelProgressCard({
    Key? key,
    required this.currentLevel,
    required this.currentNode,
    required this.nodesInLevel,
    required this.currentXP,
    required this.totalXP,
  }) : super(key: key);

  @override
  State<LevelProgressCard> createState() => _LevelProgressCardState();
}

class _LevelProgressCardState extends State<LevelProgressCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: AAColors.cardShadow,
      ),
      child: Row(
        children: [
          // Sol: Seviye Numarası
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              gradient: AAColors.navyGradient,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AAColors.aaNavy.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  '${widget.currentLevel}',
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Text(
                  'SEVİYE',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(width: 16),

          // Orta: Düğüm Zinciri
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Düğüm İlerlemesi',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AAColors.grey700,
                  ),
                ),
                const SizedBox(height: 8),
                _buildNodeChain(),
                const SizedBox(height: 8),
                Text(
                  '${widget.currentXP}/100 XP',
                  style: TextStyle(
                    fontSize: 12,
                    color: AAColors.grey500,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(width: 8),

          // Sağ: Total XP
          Column(
            children: [
              Icon(Icons.stars, color: AAColors.aaRed, size: 24),
              const SizedBox(height: 4),
              Text(
                '${widget.totalXP}',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AAColors.aaRed,
                ),
              ),
              Text(
                'Toplam XP',
                style: TextStyle(
                  fontSize: 10,
                  color: AAColors.grey500,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNodeChain() {
    return SizedBox(
      height: 40,
      child: Row(
        children: List.generate(widget.nodesInLevel, (index) {
          final isCompleted = index < widget.currentNode;
          final isCurrent = index == widget.currentNode;
          final isLocked = index > widget.currentNode;

          return Expanded(
            child: Row(
              children: [
                // Düğüm
                Expanded(
                  child: _buildNode(
                    isCompleted: isCompleted,
                    isCurrent: isCurrent,
                    isLocked: isLocked,
                    nodeIndex: index,
                  ),
                ),
                // Bağlantı çizgisi (son düğüm hariç)
                if (index < widget.nodesInLevel - 1)
                  Container(
                    width: 8,
                    height: 2,
                    color: isCompleted ? AAColors.aaRed : AAColors.grey300,
                  ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildNode({
    required bool isCompleted,
    required bool isCurrent,
    required bool isLocked,
    required int nodeIndex,
  }) {
    Color color;
    Widget icon;

    if (isCompleted) {
      color = AAColors.aaRed;
      icon = const Icon(Icons.check, color: Colors.white, size: 14);
    } else if (isCurrent) {
      color = AAColors.aaNavy;
      // Animasyonlu progress
      icon = CircularProgressIndicator(
        value: widget.currentXP / 100,
        strokeWidth: 2,
        valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
        backgroundColor: Colors.white.withOpacity(0.3),
      );
    } else {
      color = AAColors.grey300;
      icon = Icon(Icons.lock_outline, color: AAColors.grey500, size: 14);
    }

    Widget node = Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        border: isCurrent
            ? Border.all(color: AAColors.aaNavy, width: 2)
            : null,
      ),
      child: Center(child: icon),
    );

    // Mevcut düğüme pulse animasyonu
    if (isCurrent) {
      return AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          return Transform.scale(
            scale: 1.0 + (_pulseController.value * 0.1),
            child: node,
          );
        },
      );
    }

    return node;
  }
}