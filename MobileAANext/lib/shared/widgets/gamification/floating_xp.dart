// lib/widgets/gamification/floating_xp.dart

import 'package:flutter/material.dart';

/// Floating XP Animation
/// XP kazanınca yukarı uçan animasyon
class FloatingXP extends StatefulWidget {
  final int xpAmount;
  final Offset startPosition;
  final VoidCallback? onComplete;
  final String? source; // 'reel', 'emoji', 'detail', 'share'

  const FloatingXP({
    Key? key,
    required this.xpAmount,
    required this.startPosition,
    this.onComplete,
    this.source,
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
      duration: const Duration(milliseconds: 1500),
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
      end: const Offset(0, -3.0),
    ).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeOut,
      ),
    );

    // Scale bounce animation
    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.3), weight: 25),
      TweenSequenceItem(tween: Tween(begin: 1.3, end: 1.0), weight: 15),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 60),
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
                child: _buildXPWidget(),
              ),
            ),
          );
        },
      ),
    );
  }
  
  // ============ XP WIDGET ============
  
  Widget _buildXPWidget() {
    final color = _getColorForSource();
    final icon = _getIconForSource();
    
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 10,
      ),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            color.withOpacity(0.95),
            color.withOpacity(0.85),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.6),
            blurRadius: 12,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Text(
              icon,
              style: const TextStyle(fontSize: 20),
            ),
            const SizedBox(width: 8),
          ],
          Text(
            '+${widget.xpAmount} XP',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
  
  // ============ SOURCE'A GÖRE RENK ============
  
  Color _getColorForSource() {
    switch (widget.source) {
      case 'reel_watched':
        return Colors.blue[600]!;
      case 'emoji_given':
        return Colors.pink[500]!;
      case 'detail_read':
        return Colors.purple[600]!;
      case 'share_given':
        return Colors.green[600]!;
      default:
        return Colors.blue[600]!;
    }
  }
  
  // ============ SOURCE'A GÖRE ICON ============
  
  String? _getIconForSource() {
    switch (widget.source) {
      case 'reel_watched':
        return '👀';
      case 'emoji_given':
        return '❤️';
      case 'detail_read':
        return '📖';
      case 'share_given':
        return '🔗';
      default:
        return null;
    }
  }
}

// ============ OVERLAY MANAGER ============

/// Floating XP Overlay Manager
/// Ekranda floating XP gösterimi için yardımcı sınıf
class FloatingXPOverlay {
  static OverlayEntry? _currentOverlay;
  
  /// XP animasyonu göster
  static void show(
    BuildContext context, {
    required int xpAmount,
    Offset? position,
    String? source,
  }) {
    // Önceki overlay'i temizle
    remove();
    
    // Pozisyon belirlenmemişse ekran ortasında göster
    final screenSize = MediaQuery.of(context).size;
    final defaultPosition = Offset(
      screenSize.width / 2 - 60,
      screenSize.height / 2 - 100,
    );
    
    final overlayState = Overlay.of(context);
    
    _currentOverlay = OverlayEntry(
      builder: (context) => FloatingXP(
        xpAmount: xpAmount,
        startPosition: position ?? defaultPosition,
        source: source,
        onComplete: () {
          remove();
        },
      ),
    );
    
    overlayState.insert(_currentOverlay!);
  }
  
  /// Overlay'i kaldır
  static void remove() {
    _currentOverlay?.remove();
    _currentOverlay = null;
  }
  
  /// Birden fazla XP animasyonu göster (cascade efekti)
  static void showMultiple(
    BuildContext context, {
    required List<Map<String, dynamic>> xpList,
  }) {
    for (int i = 0; i < xpList.length; i++) {
      Future.delayed(Duration(milliseconds: i * 200), () {
        final xpData = xpList[i];
        show(
          context,
          xpAmount: xpData['amount'] as int,
          position: xpData['position'] as Offset?,
          source: xpData['source'] as String?,
        );
      });
    }
  }
}

// ============ HELPER WIDGET ============

/// XP Feedback Snackbar
/// Basit geri bildirim için snackbar
class XPSnackbar {
  static void show(
    BuildContext context, {
    required int xpAmount,
    required String message,
    String? source,
  }) {
    final color = _getColorForSource(source);
    final icon = _getIconForSource(source);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Text(
                icon,
                style: const TextStyle(fontSize: 20),
              ),
              const SizedBox(width: 8),
            ],
            Text(
              '$message +$xpAmount XP',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ],
        ),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        backgroundColor: color,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.all(16),
      ),
    );
  }
  
  static Color _getColorForSource(String? source) {
    switch (source) {
      case 'reel_watched':
        return Colors.blue[600]!;
      case 'emoji_given':
        return Colors.pink[500]!;
      case 'detail_read':
        return Colors.purple[600]!;
      case 'share_given':
        return Colors.green[600]!;
      default:
        return Colors.blue[600]!;
    }
  }
  
  static String? _getIconForSource(String? source) {
    switch (source) {
      case 'reel_watched':
        return '👀';
      case 'emoji_given':
        return '❤️';
      case 'detail_read':
        return '📖';
      case 'share_given':
        return '🔗';
      default:
        return null;
    }
  }
}