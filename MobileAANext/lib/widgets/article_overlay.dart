import 'package:flutter/material.dart';

class ArticleOverlay extends StatelessWidget {
  final bool open;
  final String content;
  final VoidCallback onClose;
  const ArticleOverlay({
    super.key,
    required this.open,
    required this.content,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      ignoring: !open,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 180),
        opacity: open ? 1 : 0,
        child: Stack(
          children: [
            Positioned.fill(
              child: ColoredBox(color: Colors.black.withOpacity(.45)),
            ),
            Positioned.fill(
              child: DraggableScrollableSheet(
                initialChildSize: .35,
                minChildSize: .2,
                maxChildSize: .95,
                builder: (_, ctrl) => Material(
                  color: Colors.white,
                  borderRadius:
                      const BorderRadius.vertical(top: Radius.circular(20)),
                  child: Column(
                    children: [
                      Container(
                        height: 5,
                        width: 44,
                        margin: const EdgeInsets.only(top: 8),
                        decoration: BoxDecoration(
                          color: Colors.grey[300],
                          borderRadius: BorderRadius.circular(3),
                        ),
                      ),
                      Expanded(
                        child: SingleChildScrollView(
                          controller: ctrl,
                          padding: const EdgeInsets.all(16),
                          child: Text(
                            content,
                            style: const TextStyle(fontSize: 16, height: 1.45),
                          ),
                        ),
                      ),
                      TextButton(
                          onPressed: onClose, child: const Text('Kapat')),
                    ],
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
