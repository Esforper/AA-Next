// lib/widgets/gamification/reels_xp_overlay.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/gamification_provider.dart';

/// Reels XP Overlay - Temizlenmiş ve Minimal
/// - Tek satır: Level sayısı + Düğüm görseli + Düğüm sayısı + XP
/// - Progress bar gizli, puan alınca animasyonlu açılır
class ReelsXPOverlay extends StatefulWidget {
  const ReelsXPOverlay({Key? key}) : super(key: key);

  @override
  State<ReelsXPOverlay> createState() => _ReelsXPOverlayState();
}

class _ReelsXPOverlayState extends State<ReelsXPOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _progressAnimController;
  late Animation<double> _progressHeightAnim;
  bool _showProgress = false;
  int _lastTotalXP = 0;

  @override
  void initState() {
    super.initState();
    
    // Progress bar açılma/kapanma animasyonu
    _progressAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    
    _progressHeightAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _progressAnimController, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    _progressAnimController.dispose();
    super.dispose();
  }

  void _checkXPChange(GamificationProvider provider) {
    final currentXP = provider.state.totalXP;
    
    // XP artışı varsa progress bar'ı göster
    if (currentXP > _lastTotalXP) {
      // ✅ Build sonrasında setState çağır
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        
        setState(() => _showProgress = true);
        _progressAnimController.forward();
        
        // 3 saniye sonra gizle
        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            _progressAnimController.reverse().then((_) {
              if (mounted) {
                setState(() => _showProgress = false);
              }
            });
          }
        });
      });
    }
    
    _lastTotalXP = currentXP;
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GamificationProvider>(
      builder: (context, provider, _) {
        _checkXPChange(provider);
        
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
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
              // ✅ TEK SATIR: Level + Düğümler + Sayı + XP
              _buildCompactInfo(provider),
              
              // ✅ PROGRESS BAR (Animasyonlu açılır/kapanır)
              AnimatedBuilder(
                animation: _progressHeightAnim,
                builder: (context, child) {
                  if (!_showProgress && _progressHeightAnim.value == 0) {
                    return const SizedBox.shrink();
                  }
                  
                  return SizeTransition(
                    sizeFactor: _progressHeightAnim,
                    axisAlignment: -1,
                    child: Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: _buildNodeProgressBar(provider),
                    ),
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }

  // ============ COMPACT INFO (Tek Satır) ============
  
  Widget _buildCompactInfo(GamificationProvider provider) {
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
        mainAxisSize: MainAxisSize.min,
        children: [
          // ⚡ Level sayısı (sadece sayı)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.amber[400]!, Colors.orange[500]!],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Text('⚡', style: TextStyle(fontSize: 14)),
                const SizedBox(width: 4),
                Text(
                  '${state.currentLevel}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(width: 12),
          
          // ●●○○○ Düğüm görseli
          _buildNodeDots(state.currentNode, state.nodesInLevel),
          
          const SizedBox(width: 12),
          
          // 2/5 Düğüm sayısı
          Text(
            '${state.currentNode + 1}/${state.nodesInLevel}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(width: 12),
          
          // 45 XP
          Text(
            '${state.currentXP} XP',
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

  // ============ DÜĞÜM NOKTALARI ============
  
  Widget _buildNodeDots(int current, int total) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(total, (index) {
        final isCompleted = index < current;
        final isCurrent = index == current;
        
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 2),
          child: Container(
            width: isCurrent ? 10 : 8,
            height: isCurrent ? 10 : 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCompleted
                  ? Colors.amber[400]
                  : isCurrent
                      ? Colors.amber[200]
                      : Colors.white.withOpacity(0.3),
              border: isCurrent
                  ? Border.all(color: Colors.amber[300]!, width: 2)
                  : null,
            ),
          ),
        );
      }),
    );
  }

  // ============ PROGRESS BAR (Sadece Düğüm) ============
  
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
}