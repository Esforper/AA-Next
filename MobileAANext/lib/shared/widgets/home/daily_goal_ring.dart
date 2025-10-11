// lib/mobile_platform/widgets/home/daily_goal_ring.dart
// 🎯 Daily Goal Ring - Circular Progress

import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../../core/theme/aa_colors.dart';

class DailyGoalRing extends StatefulWidget {
  final int xpEarnedToday;
  final int dailyGoal;
  final bool goalCompleted;

  const DailyGoalRing({
    Key? key,
    required this.xpEarnedToday,
    required this.dailyGoal,
    required this.goalCompleted,
  }) : super(key: key);

  @override
  State<DailyGoalRing> createState() => _DailyGoalRingState();
}

class _DailyGoalRingState extends State<DailyGoalRing>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _progressAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    final progress = (widget.xpEarnedToday / widget.dailyGoal).clamp(0.0, 1.0);
    _progressAnimation = Tween<double>(begin: 0.0, end: progress).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic),
    );

    _animController.forward();
  }

  @override
  void didUpdateWidget(DailyGoalRing oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.xpEarnedToday != widget.xpEarnedToday) {
      final newProgress = (widget.xpEarnedToday / widget.dailyGoal).clamp(0.0, 1.0);
      _progressAnimation = Tween<double>(
        begin: _progressAnimation.value,
        end: newProgress,
      ).animate(
        CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic),
      );
      _animController.forward(from: 0.0);
    }
  }

  @override
  void dispose() {
    _animController.dispose();
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
      child: Column(
        children: [
          // Başlık
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Günlük Hedef',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AAColors.black,
                ),
              ),
              if (widget.goalCompleted)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AAColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.check_circle, color: AAColors.success, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        'Tamamlandı!',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AAColors.success,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),

          const SizedBox(height: 24),

          // Ring Progress
          Center(
            child: AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return CustomPaint(
                  size: const Size(160, 160),
                  painter: _RingPainter(
                    progress: _progressAnimation.value,
                    goalCompleted: widget.goalCompleted,
                  ),
                  child: SizedBox(
                    width: 160,
                    height: 160,
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '${widget.xpEarnedToday}',
                            style: TextStyle(
                              fontSize: 40,
                              fontWeight: FontWeight.bold,
                              color: widget.goalCompleted
                                  ? AAColors.success
                                  : AAColors.aaRed,
                            ),
                          ),
                          Text(
                            'XP',
                            style: TextStyle(
                              fontSize: 14,
                              color: AAColors.grey500,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 16),

          // Alt bilgi
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.flag_outlined, size: 16, color: AAColors.grey500),
              const SizedBox(width: 4),
              Text(
                'Hedef: ${widget.dailyGoal} XP',
                style: TextStyle(
                  fontSize: 14,
                  color: AAColors.grey700,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '(${((widget.xpEarnedToday / widget.dailyGoal) * 100).clamp(0, 100).toInt()}%)',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AAColors.aaNavy,
                ),
              ),
            ],
          ),

          if (!widget.goalCompleted) ...[
            const SizedBox(height: 8),
            Text(
              'Kalan: ${(widget.dailyGoal - widget.xpEarnedToday).clamp(0, widget.dailyGoal)} XP',
              style: TextStyle(
                fontSize: 12,
                color: AAColors.grey500,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final double progress;
  final bool goalCompleted;

  _RingPainter({
    required this.progress,
    required this.goalCompleted,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 10;

    // Background ring
    final bgPaint = Paint()
      ..color = AAColors.grey200
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Progress ring
    final progressPaint = Paint()
      ..shader = LinearGradient(
        colors: goalCompleted
            ? [AAColors.success, AAColors.success.withOpacity(0.7)]
            : [AAColors.aaRed, AAColors.redLight],
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    final sweepAngle = 2 * math.pi * progress;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2, // Start from top
      sweepAngle,
      false,
      progressPaint,
    );

    // Kutlama efekti (hedef tamamlandıysa)
    if (goalCompleted) {
      final sparkPaint = Paint()
        ..color = AAColors.success.withOpacity(0.3)
        ..style = PaintingStyle.fill;

      // Küçük yıldızlar
      for (int i = 0; i < 8; i++) {
        final angle = (2 * math.pi / 8) * i;
        final sparkCenter = Offset(
          center.dx + (radius + 15) * math.cos(angle),
          center.dy + (radius + 15) * math.sin(angle),
        );
        canvas.drawCircle(sparkCenter, 3, sparkPaint);
      }
    }
  }

  @override
  bool shouldRepaint(_RingPainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.goalCompleted != goalCompleted;
  }
}