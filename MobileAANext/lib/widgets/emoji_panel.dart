import 'dart:math' as math;
import 'package:flutter/material.dart';

class EmojiPanel extends StatelessWidget {
  final List<String> publicEmojis; // alt yay
  final List<String> premiumEmojis; // üst yay
  final void Function(String emoji) onPick;
  final VoidCallback onTapPremium;

  const EmojiPanel({
    super.key,
    required this.publicEmojis,
    required this.premiumEmojis,
    required this.onPick,
    required this.onTapPremium,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 230,
      child: Stack(
        alignment: Alignment.bottomCenter,
        children: [
          _Fan(
            radius: 150,
            items: premiumEmojis
                .map((e) => _Item(e, locked: true, onTap: () => onTapPremium()))
                .toList(),
          ),
          _Fan(
            radius: 110,
            items: publicEmojis
                .map((e) => _Item(e, onTap: () => onPick(e)))
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _Fan extends StatelessWidget {
  final double radius;
  final List<Widget> items;
  const _Fan({required this.radius, required this.items});

  @override
  Widget build(BuildContext context) {
    final count = items.length;
    final start = math.pi,
        end = 2 * math.pi,
        step = (end - start) / (count + 1);
    final w = MediaQuery.of(context).size.width;

    return Positioned.fill(
      child: Stack(
        children: List.generate(count, (i) {
          final a = start + step * (i + 1);
          final cx = radius * math.cos(a);
          final cy = radius * math.sin(a);
          return Positioned(
            left: w / 2 + cx - 28,
            bottom: 12 + cy - 28,
            child: items[i],
          );
        }),
      ),
    );
  }
}

class _Item extends StatelessWidget {
  final String emoji;
  final bool locked;
  final VoidCallback onTap;
  const _Item(this.emoji, {this.locked = false, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Opacity(
        opacity: locked ? 0.6 : 1,
        child: Stack(
          alignment: Alignment.center,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10)],
              ),
            ),
            Text(emoji, style: const TextStyle(fontSize: 24)),
            if (locked)
              const Positioned(
                  right: 8, bottom: 8, child: Icon(Icons.lock, size: 14)),
          ],
        ),
      ),
    );
  }
}
