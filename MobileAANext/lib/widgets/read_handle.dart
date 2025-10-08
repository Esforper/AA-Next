import 'package:flutter/material.dart';

/// 4 yön: Yukarı, Sağ, Aşağı, Sol
enum HandleAction { up, right, down, left, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;
  final Size trackSize;
  final double knobSize;
  final double threshold; // Tek eşik değeri (4 yön için)

  const ReadHandle({
    super.key,
    required this.onAction,
    this.trackSize = const Size(140, 140), // Kare yapıldı (4 yön için)
    this.knobSize = 40,
    this.threshold = 35, // Daha yüksek eşik
  });

  @override
  State<ReadHandle> createState() => _ReadHandleState();
}

class _ReadHandleState extends State<ReadHandle>
    with SingleTickerProviderStateMixin {
  late final AnimationController _anim;
  late Animation<Offset> _spring;
  Offset _offset = Offset.zero;

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 220),
    );
    _spring = Tween<Offset>(begin: Offset.zero, end: Offset.zero)
        .chain(CurveTween(curve: Curves.easeOutBack))
        .animate(_anim)
      ..addListener(() => setState(() {}))
      ..addStatusListener((s) {
        if (s == AnimationStatus.completed) _offset = Offset.zero;
      });
  }

  @override
  void dispose() {
    _anim.dispose();
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

    // Hangi eksen daha baskın?
    if (dx > dy) {
      // Yatay hareket
      if (_offset.dx > threshold) {
        return HandleAction.right;
      } else if (_offset.dx < -threshold) {
        return HandleAction.left;
      }
    } else {
      // Dikey hareket
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
      onPanUpdate: (d) {
        final next = _clampToTrack(_offset + d.delta);
        setState(() => _offset = next);
      },
      onPanEnd: (_) {
        final action = _detectDirection();
        widget.onAction(action);
        _animateBack();
      },
      child: Container(
        width: trackW,
        height: trackH,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.7),
          shape: BoxShape.circle, // Daire şekli (4 yön için)
          boxShadow: const [
            BoxShadow(
                blurRadius: 8, color: Colors.black38, offset: Offset(0, 3)),
          ],
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            // 4 Yön İkonları
            Positioned(
              top: 12,
              child: Icon(Icons.arrow_upward, color: Colors.white70, size: 18),
            ),
            Positioned(
              right: 12,
              child: Icon(Icons.emoji_emotions_outlined,
                  color: Colors.white70, size: 18),
            ),
            Positioned(
              bottom: 12,
              child: Icon(Icons.share_outlined, color: Colors.white70, size: 18),
            ),
            Positioned(
              left: 12,
              child: Icon(Icons.bookmark_outline, color: Colors.white70, size: 18),
            ),

            // Hareketli Kulp
            Transform.translate(
              offset: pos,
              child: Container(
                width: widget.knobSize,
                height: widget.knobSize,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: const [
                    BoxShadow(
                      blurRadius: 4,
                      color: Colors.black26,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: const Icon(
                  Icons.drag_indicator,
                  color: Colors.black87,
                  size: 20,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}