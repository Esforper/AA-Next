// lib/widgets/gamification/floating_xp.dart

import 'package:flutter/material.dart';

/// Floating XP Animation
/// XP kazanınca yukarı uçan text
class FloatingXP extends StatefulWidget {
  final int xpAmount;
  final Offset startPosition;
  final VoidCallback? onComplete;

  const FloatingXP({
    Key? key,
    required this.xpAmount,
    required this.startPosition,
    this.onComplete,
  }) : super(key: key);

  @override
  State<FloatingXP> createState() => _FloatingXPState();
}

class _FloatingXPState extends State<FloatingXP>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    // Fade out animation
    _fadeAnimation = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.5, 1.0, curve: Curves.easeOut),
      ),
    );

    // Slide up animation
    _slideAnimation = Tween<Offset>(
      begin: Offset.zero,
      end: const Offset(0, -2.5),
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeOut,
      ),
    );

    // Scale bounce animation
    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.2), weight: 30),
      TweenSequenceItem(tween: Tween(begin: 1.2, end: 1.0), weight: 20),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 50),
    ]).animate(_controller);

    _controller.forward().then((_) {
      widget.onComplete?.call();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: widget.startPosition.dx,
      top: widget.startPosition.dy,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return FadeTransition(
            opacity: _fadeAnimation,
            child: SlideTransition(
              position: _slideAnimation,
              child: ScaleTransition(
                scale: _scaleAnimation,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.blue[400]!,
                        Colors.blue[600]!,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blue.withOpacity(0.4),
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        '⭐',
                        style: TextStyle(fontSize: 16),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '+${widget.xpAmount} XP',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Floating XP Overlay Manager
/// Ekrana floating XP eklemek için helper
class FloatingXPOverlay {
  static OverlayEntry? _currentEntry;

  static void show(
    BuildContext context, {
    required int xpAmount,
    Offset? position,
  }) {
    // Önceki animasyonu kaldır
    remove();

    final overlay = Overlay.of(context);
    final renderBox = context.findRenderObject() as RenderBox?;
    
    // Pozisyon hesapla (varsayılan: ekran ortası)
    final defaultPosition = position ?? 
      Offset(
        MediaQuery.of(context).size.width / 2 - 50,
        MediaQuery.of(context).size.height / 2 - 100,
      );

    _currentEntry = OverlayEntry(
      builder: (context) => FloatingXP(
        xpAmount: xpAmount,
        startPosition: defaultPosition,
        onComplete: remove,
      ),
    );

    overlay.insert(_currentEntry!);
  }

  static void remove() {
    _currentEntry?.remove();
    _currentEntry = null;
  }
}