import 'package:flutter/material.dart';

class ReadButton extends StatefulWidget {
  final VoidCallback onOpenOverlay;
  final VoidCallback onRevealEmojis;
  const ReadButton({
    super.key,
    required this.onOpenOverlay,
    required this.onRevealEmojis,
  });

  @override
  State<ReadButton> createState() => _ReadButtonState();
}

class _ReadButtonState extends State<ReadButton> {
  double _dx = 0, _dy = 0;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onOpenOverlay,
      onLongPressStart: (_) => _dy = 0,
      onLongPressMoveUpdate: (d) {
        _dy += d.offsetFromOrigin.dy;
        if (_dy < -40) widget.onOpenOverlay();
      },
      onHorizontalDragUpdate: (d) {
        _dx += d.delta.dx;
        if (_dx > 40) {
          _dx = 0;
          widget.onRevealEmojis();
        }
      },
      onHorizontalDragEnd: (_) => _dx = 0,
      child: Container(
        height: 56,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(.75),
          borderRadius: BorderRadius.circular(28),
        ),
        child: const Text(
          'Devamını oku ↟',
          style: TextStyle(color: Colors.white, fontSize: 16),
        ),
      ),
    );
  }
}
