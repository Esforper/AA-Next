import 'package:flutter/material.dart';

class EmojiPanel extends StatelessWidget {
  final bool visible;
  final void Function(String emoji) onPick;
  const EmojiPanel({super.key, required this.visible, required this.onPick});

  @override
  Widget build(BuildContext context) {
    final free = ['👍', '❤️', '😂', '😮', '😢', '👏'];
    final premium = ['🔥', '💎', '🚀', '👑'];

    return AnimatedPositioned(
      duration: const Duration(milliseconds: 220),
      right: visible ? 16 : -220,
      bottom: 16,
      width: 200,
      child: Material(
        elevation: 10,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: premium
                    .map((e) => Opacity(
                          opacity: .55,
                          child: Stack(
                            alignment: Alignment.topRight,
                            children: [
                              Padding(
                                padding: const EdgeInsets.all(6.0),
                                child: Text(e,
                                    style: const TextStyle(fontSize: 22)),
                              ),
                              const Icon(Icons.lock, size: 14),
                            ],
                          ),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: free
                    .map((e) => InkWell(
                          onTap: () => onPick(e),
                          child: Padding(
                            padding: const EdgeInsets.all(6.0),
                            child:
                                Text(e, style: const TextStyle(fontSize: 22)),
                          ),
                        ))
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
