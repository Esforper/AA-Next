import 'package:flutter/material.dart';

/// Yukarı (up) = makale sheet, Sağa (right) = emoji panel.
enum HandleAction { up, right, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;

  /// Ray ölçüleri ve eşikler
  final Size trackSize; // önceki: 140 x 110 -> daha kompakt
  final double knobSize; // önceki: 40 -> 36
  final double thresholdRight; // 28
  final double thresholdUp; // 28

  const ReadHandle({
    super.key,
    required this.onAction,
    this.trackSize = const Size(110, 72),
    this.knobSize = 36,
    this.thresholdRight = 28,
    this.thresholdUp = 28,
  });

  @override
  State<ReadHandle> createState() => _ReadHandleState();
}

class _ReadHandleState extends State<ReadHandle>
    with SingleTickerProviderStateMixin {
  late final AnimationController _anim;
  late Animation<Offset> _spring;
  Offset _offset = Offset.zero; // merkezden sapma (+x sağ, +y aşağı)

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

  // Kulpu ray içinde tut
  Offset _clampToTrack(Offset raw) {
    final w = widget.trackSize.width;
    final h = widget.trackSize.height;
    final r = widget.knobSize / 2;
    final maxX = (w / 2) - r - 4;
    final maxY = (h / 2) - r - 4;
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
        // Eşikleri mevcut ray boyutuna göre dinamikleştir
        final r = widget.knobSize / 2;
        final maxX = (widget.trackSize.width / 2) - r - 4;
        final maxY = (widget.trackSize.height / 2) - r - 4;
        final double effRight = widget.thresholdRight <= maxX * 0.9
            ? widget.thresholdRight
            : (maxX * 0.9);
        final double effUp = widget.thresholdUp <= maxY * 0.9
            ? widget.thresholdUp
            : (maxY * 0.9);

        // karar ver
        if (-_offset.dy >= effUp) {
          widget.onAction(HandleAction.up);
        } else if (_offset.dx >= effRight) {
          widget.onAction(HandleAction.right);
        } else {
          widget.onAction(HandleAction.none);
        }
        _animateBack();
      },
      child: Container(
        width: trackW,
        height: trackH,
        padding: const EdgeInsets.symmetric(horizontal: 6),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.65),
          borderRadius: BorderRadius.circular(trackH / 2),
          boxShadow: const [
            BoxShadow(
                blurRadius: 6, color: Colors.black26, offset: Offset(0, 2)),
          ],
        ),
        child: Stack(
          alignment: Alignment.centerLeft,
          children: [
            Positioned(
              left: 10,
              child: Row(
                children: const [
                  Icon(Icons.arrow_upward, color: Colors.white70, size: 16),
                  SizedBox(width: 6),
                  Icon(Icons.emoji_emotions_outlined,
                      color: Colors.white70, size: 16),
                ],
              ),
            ),
            Transform.translate(
              offset: pos,
              child: Container(
                width: widget.knobSize,
                height: widget.knobSize,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(widget.knobSize / 2),
                ),
                alignment: Alignment.center,
                child: const Text(
                  'Read',
                  style: TextStyle(
                    fontSize: 10.5,
                    fontWeight: FontWeight.w700,
                    color: Colors.black87,
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
