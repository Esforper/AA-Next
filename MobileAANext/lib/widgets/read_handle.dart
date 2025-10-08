// lib/widgets/read_handle.dart
// GÜNCELLEME: 4 yön (yukarı, sağ, aşağı, sol) + orta pozisyon

import 'package:flutter/material.dart';

/// 4 yönlü handle
enum HandleAction { up, right, down, left, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;

    this.trackSize = const Size(160, 160), // Daha büyük (4 yön için)
    this.knobSize = 50,
    this.threshold = 35,
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
      duration: const Duration(milliseconds: 250),
        .chain(CurveTween(curve: Curves.easeOutBack))
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
        // 4 yön kontrolü
        final absX = _offset.dx.abs();
        final absY = _offset.dy.abs();

        if (absX > absY) {
          // Yatay hareket
          if (_offset.dx > widget.threshold) {
            widget.onAction(HandleAction.right); // Emoji
          } else if (_offset.dx < -widget.threshold) {
            widget.onAction(HandleAction.left); // Kaydet
          } else {
            widget.onAction(HandleAction.none);
          }
        } else {
          // Dikey hareket
          if (-_offset.dy > widget.threshold) {
            widget.onAction(HandleAction.up); // Detail
          } else if (_offset.dy > widget.threshold) {
            widget.onAction(HandleAction.down); // Paylaş
          } else {
            widget.onAction(HandleAction.none);
          }
        }

        _animateBack();
      },
      child: Container(
        width: trackW,
        height: trackH,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.3), // Dış çember (silik)
          shape: BoxShape.circle,
          border: Border.all(
            color: Colors.white.withOpacity(0.3),
            width: 2,
          ),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            // 4 yön ikonları
            Positioned(
              top: 12,
              child: Icon(
                Icons.arrow_upward,
                color: Colors.white.withOpacity(0.7),
                size: 20,
              ),
            ),
            Positioned(
              right: 12,
              child: Icon(
                Icons.emoji_emotions_outlined,
                color: Colors.white.withOpacity(0.7),
                size: 20,
              ),
            ),
            Positioned(
              bottom: 12,
              child: Icon(
                Icons.share_outlined,
                color: Colors.white.withOpacity(0.7),
                size: 20,
              ),
            ),
            Positioned(
              left: 12,
              child: Icon(
                Icons.bookmark_outline,
                color: Colors.white.withOpacity(0.7),
                size: 20,
              ),
            ),

            // Ortadaki kulp (beyaz yuvarlak)
            Transform.translate(
              offset: pos,
              child: Container(
                width: widget.knobSize,
                height: widget.knobSize,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 12,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: const Text(
                  'Sürükle',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: Colors.black87,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
