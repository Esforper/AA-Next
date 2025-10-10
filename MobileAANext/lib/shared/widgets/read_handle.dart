// lib/shared/widgets/read_handle.dart
import 'package:flutter/material.dart';

/// 4 yön: Yukarı, Sağ, Aşağı, Sol
enum HandleAction { up, right, down, left, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;
  final Size trackSize;
  final double knobSize;
  final double threshold;

  const ReadHandle({
    super.key,
    required this.onAction,
    this.trackSize = const Size(160, 160),
    this.knobSize = 56,
    this.threshold = 35,
  });

  @override
  State<ReadHandle> createState() => _ReadHandleState();
}

class _ReadHandleState extends State<ReadHandle>
    with TickerProviderStateMixin {
  late final AnimationController _anim;
  late Animation<Offset> _spring;
  Offset _offset = Offset.zero;
  bool _isPressed = false;
  
  late final AnimationController _expandAnim;
  late final Animation<double> _expandScale;

  // ✅ AA Kurumsal Rengi
  static const Color aaBlue = Color(0xFF003D82);

  @override
  void initState() {
    super.initState();
    
    // Geri dönüş animasyonu
    _anim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 220),
    );
    _spring = Tween<Offset>(begin: Offset.zero, end: Offset.zero)
        .chain(CurveTween(curve: Curves.easeOutBack))
        .animate(_anim)
      ..addListener(() {
        if (mounted) setState(() {});
      })
      ..addStatusListener((s) {
        if (s == AnimationStatus.completed) {
          _offset = Offset.zero;
        }
      });

    // Dış daire açılma animasyonu
    _expandAnim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );
    
    _expandScale = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _expandAnim, curve: Curves.easeOutBack),
    )..addListener(() {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _anim.dispose();
    _expandAnim.dispose();
    super.dispose();
  }

  void _animateBack() {
    _anim.reset();
    _spring = Tween<Offset>(begin: _offset, end: Offset.zero)
        .chain(CurveTween(curve: Curves.easeOutBack))
        .animate(_anim);
    _anim.forward();
  }

  Offset _clampToTrack(Offset raw) {
    final w = widget.trackSize.width;
    final h = widget.trackSize.height;
    final r = widget.knobSize / 2;
    final maxX = (w / 2) - r - 8;
    final maxY = (h / 2) - r - 8;
    return Offset(
      raw.dx.clamp(-maxX, maxX),
      raw.dy.clamp(-maxY, maxY),
    );
  }

  HandleAction _detectDirection() {
    final dx = _offset.dx.abs();
    final dy = _offset.dy.abs();
    final threshold = widget.threshold;

    if (dx > dy) {
      if (_offset.dx > threshold) {
        return HandleAction.right;
      } else if (_offset.dx < -threshold) {
        return HandleAction.left;
      }
    } else {
      if (_offset.dy > threshold) {
        return HandleAction.down;
      } else if (_offset.dy < -threshold) {
        return HandleAction.up;
      }
    }
    
    return HandleAction.none;
  }

  @override
  Widget build(BuildContext context) {
    final trackW = widget.trackSize.width;
    final trackH = widget.trackSize.height;
    final pos = _anim.isAnimating ? _spring.value : _offset;

    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onPanStart: (_) {
        setState(() => _isPressed = true);
        _expandAnim.forward();
      },
      onPanUpdate: (d) {
        final next = _clampToTrack(_offset + d.delta);
        setState(() => _offset = next);
      },
      onPanEnd: (_) {
        setState(() => _isPressed = false);
        final action = _detectDirection();
        widget.onAction(action);
        _animateBack();
        _expandAnim.reverse();
      },
      onPanCancel: () {
        setState(() => _isPressed = false);
        _animateBack();
        _expandAnim.reverse();
      },
      child: SizedBox(
        width: trackW,
        height: trackH,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // ✅ DIŞ KARE (Daha karesel, AA mavi)
            AnimatedBuilder(
              animation: _expandScale,
              builder: (context, child) {
                final scale = _expandScale.value;
                
                if (scale == 0.0) return const SizedBox.shrink();
                
                return Transform.scale(
                  scale: scale,
                  child: Opacity(
                    opacity: scale.clamp(0.0, 1.0),
                    child: Container(
                      width: trackW,
                      height: trackH,
                      decoration: BoxDecoration(
                        color: aaBlue.withOpacity(0.85),
                        borderRadius: BorderRadius.circular(24), // ✅ Karesel
                        boxShadow: [
                          BoxShadow(
                            blurRadius: 12,
                            color: aaBlue.withOpacity(0.4),
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // 4 Yön İkonları (Beyaz)
                          Positioned(
                            top: 16,
                            child: Icon(
                              Icons.arrow_upward,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                          Positioned(
                            right: 16,
                            child: Icon(
                              Icons.emoji_emotions_outlined,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                          Positioned(
                            bottom: 16,
                            child: Icon(
                              Icons.share_outlined,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                          Positioned(
                            left: 16,
                            child: Icon(
                              Icons.bookmark_outline,
                              color: Colors.white,
                              size: 22,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),

            // ✅ ÇEKIRDEK (AA Logosu - Karesel)
            Transform.translate(
              offset: pos,
              child: Container(
                width: widget.knobSize,
                height: widget.knobSize,
                decoration: BoxDecoration(
                  color: aaBlue,
                  borderRadius: BorderRadius.circular(12), // ✅ Karesel
                  boxShadow: [
                    BoxShadow(
                      blurRadius: _isPressed ? 12 : 6,
                      color: Colors.black.withOpacity(0.3),
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: Text(
                  'AA',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}