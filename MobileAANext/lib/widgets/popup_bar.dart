import 'package:flutter/material.dart';

class PopupBar extends StatefulWidget {
  final String message;
  const PopupBar({super.key, required this.message});

  @override
  State<PopupBar> createState() => _PopupBarState();
}

class _PopupBarState extends State<PopupBar> {
  bool visible = true;

  @override
  Widget build(BuildContext context) {
    return AnimatedSlide(
      duration: const Duration(milliseconds: 200),
      offset: visible ? Offset.zero : const Offset(0, -1),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        color: Colors.black.withOpacity(.75),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: Colors.white, size: 18),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                widget.message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close, color: Colors.white),
              onPressed: () => setState(() => visible = false),
            ),
          ],
        ),
      ),
    );
  }
}
