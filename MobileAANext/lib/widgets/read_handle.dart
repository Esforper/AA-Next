import 'package:flutter/material.dart';

/// Yukarı (up) = makale sheet, Sağa (right) = emoji panel.
enum HandleAction { up, right, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;

  /// Ray ölçüleri ve eşikler
  final Size trackSize; // daha yüksek yaptık: 140 x 110
  final double knobSize; // 40
  final double thresholdRight; // 28
  final double thresholdUp; // 28

  const ReadHandle({
    super.key,
    required this.onAction,
    this.trackSize = const Size(140, 110),
    this.knobSize = 40,
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
        // karar ver
        if (-_offset.dy >= widget.thresholdUp) {
          widget.onAction(HandleAction.up);
        } else if (_offset.dx >= widget.thresholdRight) {
          widget.onAction(HandleAction.right);
        } else {
          widget.onAction(HandleAction.none);
        }
        _animateBack();
      },
      child: Container(
        width: trackW,
        height: trackH,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.7),
          borderRadius: BorderRadius.circular(trackH / 2),
          boxShadow: const [
            BoxShadow(
                blurRadius: 8, color: Colors.black26, offset: Offset(0, 2)),
          ],
        ),
        child: Stack(
          alignment: Alignment.centerLeft,
          children: [
            Positioned(
              left: 12,
              child: Row(
                children: const [
                  Icon(Icons.arrow_upward, color: Colors.white70, size: 18),
                  SizedBox(width: 8),
                  Icon(Icons.emoji_emotions_outlined,
                      color: Colors.white70, size: 18),
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
                    fontSize: 11,
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
