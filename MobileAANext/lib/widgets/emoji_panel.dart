import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class EmojiPanel extends StatefulWidget {
  final List<String> publicEmojis; // alt yay
  final List<String> premiumEmojis; // üst yay
  final void Function(String emoji) onPick;
  final VoidCallback onTapPremium;

  // ⚙️ yeni: itemSize ile balon çapını kontrol edebiliyorsun
  final double itemSize;

  const EmojiPanel({
    super.key,
    required this.publicEmojis,
    required this.premiumEmojis,
    required this.onPick,
    required this.onTapPremium,
    this.itemSize = 44, // 56 → 44 (ekrandaki gibi daha kompakt)
  });

  @override
  State<EmojiPanel> createState() => _EmojiPanelState();
}

class _EmojiPanelState extends State<EmojiPanel>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ac;
  late final Animation<double> _fade;
  late final Animation<double> _slide;

  @override
  void initState() {
    super.initState();
    _ac = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 220))
      ..forward();
    _fade = CurvedAnimation(parent: _ac, curve: Curves.easeOut);
    _slide = Tween<double>(begin: 20, end: 0)
        .chain(CurveTween(curve: Curves.easeOut))
        .animate(_ac);
  }

  @override
  void dispose() {
    _ac.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;

    // 📐 yay yarıçapları (daha sıkı)
    final s = widget.itemSize;
    final double radiusPublic = math.min(width * 0.50, 120.0).toDouble(); // alt
    final radiusPremium = radiusPublic + s * 0.95; // üst → altın biraz dışı

    return SafeArea(
      top: false,
      child: AnimatedBuilder(
        animation: _ac,
        builder: (_, __) {
          return Opacity(
            opacity: _fade.value,
            child: Transform.translate(
              offset: Offset(0, _slide.value),
              child: SizedBox(
                height: 230, // 250 → 230
                child: Stack(
                  alignment: Alignment.bottomCenter,
                  children: [
                    if (widget.premiumEmojis.isNotEmpty)
                      _Fan(
                        items: widget.premiumEmojis
                            .map((e) => _EmojiItem(
                                  emoji: e,
                                  size: s,
                                  locked: true,
                                  onTap: widget.onTapPremium,
                                ))
                            .toList(),
                        radius: radiusPremium,
                        angleStart: math.pi * 1.14,
                        angleEnd: math.pi * 1.86,
                        itemSize: s,
                      ),
                    if (widget.publicEmojis.isNotEmpty)
                      _Fan(
                        items: widget.publicEmojis
                            .map((e) => _EmojiItem(
                                  emoji: e,
                                  size: s,
                                  onTap: () {
                                    HapticFeedback.lightImpact();
                                    widget.onPick(e);
                                  },
                                ))
                            .toList(),
                        radius: radiusPublic,
                        angleStart: math.pi * 1.10, // biraz daha geniş
                        angleEnd: math.pi * 1.90,
                        itemSize: s,
                      ),
                    // alt etiket
                    Positioned(
                      bottom: 10,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.35),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Padding(
                          padding:
                              EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          child: Text(
                            'Tepki ekle',
                            style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                                fontSize: 12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _Fan extends StatelessWidget {
  final List<Widget> items;
  final double radius;
  final double angleStart;
  final double angleEnd;
  final double itemSize;

  const _Fan({
    required this.items,
    required this.radius,
    required this.itemSize,
    this.angleStart = math.pi,
    this.angleEnd = 2 * math.pi,
  });

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final count = items.length;
    if (count == 0) return const SizedBox.shrink();

    final step = count == 1 ? 0 : (angleEnd - angleStart) / (count - 1);

    return Positioned.fill(
      child: Stack(
        children: List.generate(count, (i) {
          final angle = angleStart + step * i;
          final cx = radius * math.cos(angle);
          final cy = radius * math.sin(angle);
          final s = itemSize;

          return Positioned(
            left: (w / 2) + cx - (s / 2),
            bottom: 16 - cy - (s / 2),
            child: SizedBox(width: s, height: s, child: items[i]),
          );
        }),
      ),
    );
  }
}

class _EmojiItem extends StatefulWidget {
  final String emoji;
  final bool locked;
  final VoidCallback onTap;
  final double size;

  const _EmojiItem({
    required this.emoji,
    required this.size,
    this.locked = false,
    required this.onTap,
  });

  @override
  State<_EmojiItem> createState() => _EmojiItemState();
}

class _EmojiItemState extends State<_EmojiItem> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final bg = Theme.of(context).brightness == Brightness.dark
        ? Colors.white.withOpacity(0.95)
        : Colors.white;
    final s = widget.size;

    return Listener(
      onPointerDown: (_) => setState(() => _pressed = true),
      onPointerUp: (_) => setState(() => _pressed = false),
      onPointerCancel: (_) => setState(() => _pressed = false),
      child: AnimatedScale(
        scale: _pressed ? 0.95 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: Material(
          color: bg,
          shape: const CircleBorder(),
          elevation: 6,
          shadowColor: Colors.black26,
          child: InkWell(
            customBorder: const CircleBorder(),
            onTap: widget.onTap,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(width: s, height: s),
                Text(widget.emoji,
                    style: TextStyle(fontSize: s * 0.48)), // ~21px
                if (widget.locked)
                  Positioned(
                    right: 6,
                    bottom: 6,
                    child: Container(
                      padding: const EdgeInsets.all(2),
                      decoration: const BoxDecoration(
                        color: Colors.black54,
                        shape: BoxShape.circle,
                      ),
                      child:
                          const Icon(Icons.lock, size: 12, color: Colors.white),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
