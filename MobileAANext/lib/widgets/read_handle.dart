import 'package:flutter/material.dart';

enum HandleAction { none, up, right }

class ReadHandle extends StatefulWidget {
  final void Function(HandleAction action) onAction;
  const ReadHandle({super.key, required this.onAction});

  @override
  State<ReadHandle> createState() => _ReadHandleState();
}

class _ReadHandleState extends State<ReadHandle> {
  Offset _delta = Offset.zero;

  static const double _maxRight = 120;
  static const double _maxLeft = -80;
  static const double _maxUp = -150;

  void _set(Offset next) {
    setState(() {
      _delta = Offset(
        next.dx.clamp(_maxLeft, _maxRight),
        next.dy.clamp(_maxUp, 0),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    const double size = 68;

    return Align(
      alignment: Alignment.bottomCenter,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque, // child öncelik kazanır
        onHorizontalDragUpdate: (d) => _set(_delta + Offset(d.delta.dx, 0)),
        onVerticalDragUpdate: (d) => _set(_delta + Offset(0, d.delta.dy)),
        onHorizontalDragEnd: (_) => _finish(),
        onVerticalDragEnd: (_) => _finish(),
        child: SizedBox(
          width: 120, height: 120, // daha kolay tutma alanı
          child: Center(
            child: Transform.translate(
              offset: _delta,
              child: Container(
                width: size,
                height: size,
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                        color: Colors.black26,
                        blurRadius: 12,
                        offset: Offset(0, 6))
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Image.asset(
                    'lib/assets/images/aa_logo.png', // AA logosu
                    fit: BoxFit.contain,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _finish() {
    final a = _detectAction(_delta);
    widget.onAction(a);
    setState(() => _delta = Offset.zero);
  }

  HandleAction _detectAction(Offset d) {
    if (d.dy < -60 && d.dy.abs() > d.dx.abs()) return HandleAction.up;
    if (d.dx > 60 && d.dx.abs() > d.dy.abs()) return HandleAction.right;
    return HandleAction.none;
  }
}
