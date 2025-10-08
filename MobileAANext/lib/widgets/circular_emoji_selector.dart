// lib/widgets/circular_emoji_selector.dart
// Yarım daire şeklinde 2 sıralı emoji selector

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Circular Emoji Selector - Navigasyon butonu etrafında yarım çember
/// - 2 sıralı (iç + dış yarım çember)
/// - Pizza dilimi gibi bölünmüş
/// - Basılı tutunca açılır
class CircularEmojiSelector extends StatefulWidget {
  final List<String> innerEmojis;    // İç çember (public)
  final List<String> outerEmojis;    // Dış çember (premium)
  final void Function(String emoji) onEmojiPick;
  final VoidCallback onPremiumTap;
  final bool isVisible;              // Açık/kapalı durumu
  final double centerButtonSize;     // Navigasyon butonu boyutu

  const CircularEmojiSelector({
    Key? key,
    required this.innerEmojis,
    required this.outerEmojis,
    required this.onEmojiPick,
    required this.onPremiumTap,
    this.isVisible = false,
    this.centerButtonSize = 56,
  }) : super(key: key);

  @override
  State<CircularEmojiSelector> createState() => _CircularEmojiSelectorState();
}

class _CircularEmojiSelectorState extends State<CircularEmojiSelector>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _scaleAnim;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    
    _scaleAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOutBack),
    );
    
    _fadeAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOut),
    );
  }

  @override
  void didUpdateWidget(CircularEmojiSelector oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    if (widget.isVisible != oldWidget.isVisible) {
      if (widget.isVisible) {
        _animController.forward();
      } else {
        _animController.reverse();
      }
    }
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isVisible && _animController.status == AnimationStatus.dismissed) {
      return const SizedBox.shrink();
    }
    
    return AnimatedBuilder(
      animation: _animController,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeAnim.value,
          child: Transform.scale(
            scale: _scaleAnim.value,
            child: _buildEmojiCircles(),
          ),
        );
      },
    );
  }

  Widget _buildEmojiCircles() {
    // Yarıçaplar hesaplama (navigasyon butonundan uzaklık)
    final innerRadius = 80.0;   // İç yarım çember
    final outerRadius = 130.0;  // Dış yarım çember  
    final emojiSize = 44.0;

    return SizedBox(
      width: (outerRadius + emojiSize) * 2,
      height: outerRadius + emojiSize,
      child: Stack(
        alignment: Alignment.bottomCenter,
        clipBehavior: Clip.none,
        children: [
          // Dış çember emojileri (Premium) - Navigasyon etrafında
          if (widget.outerEmojis.isNotEmpty)
            _buildEmojiArc(
              emojis: widget.outerEmojis,
              radius: outerRadius,
              size: emojiSize,
              isPremium: true,
            ),
          
          // İç çember emojileri (Public) - Navigasyon etrafında
          if (widget.innerEmojis.isNotEmpty)
            _buildEmojiArc(
              emojis: widget.innerEmojis,
              radius: innerRadius,
              size: emojiSize,
              isPremium: false,
            ),
        ],
      ),
    );
  }

  Widget _buildEmojiArc({
    required List<String> emojis,
    required double radius,
    required double size,
    required bool isPremium,
  }) {
    final count = emojis.length;
    if (count == 0) return const SizedBox.shrink();

    // Yarım daire: π (180°) → 0 (0°)
    const startAngle = math.pi;
    const endAngle = 0.0;
    const totalAngle = startAngle - endAngle;
    final angleStep = totalAngle / (count + 1); // +1 için eşit boşluklar
    
    // ✅ Container genişliğini hesapla
    final containerWidth = (radius + size) * 2;

    return Stack(
      clipBehavior: Clip.none,
      children: List.generate(count, (index) {
        // Her emoji için açı hesapla
        final angle = startAngle - (angleStep * (index + 1));
        
        // Polar koordinatları kartezyen'e çevir
        final x = radius * math.cos(angle);
        final y = -radius * math.sin(angle); // - çünkü Y aşağı pozitif
        
        return Positioned(
          left: containerWidth / 2 + x - size / 2,
          bottom: y - size / 2,
          child: _EmojiSlice(
            emoji: emojis[index],
            size: size,
            isPremium: isPremium,
            onTap: isPremium
                ? widget.onPremiumTap
                : () {
                    HapticFeedback.lightImpact();
                    widget.onEmojiPick(emojis[index]);
                  },
          ),
        );
      }),
    );
  }
}

// ============ ARKA PLAN YARIM DAİRE ============

class _SemiCircleBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.7)
      ..style = PaintingStyle.fill;

    final rect = Rect.fromLTWH(0, 0, size.width, size.height * 2);
    
    canvas.drawArc(
      rect,
      math.pi,      // Start angle (180°)
      math.pi,      // Sweep angle (180°)
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ============ EMOJİ DİLİMİ ============

class _EmojiSlice extends StatefulWidget {
  final String emoji;
  final double size;
  final bool isPremium;
  final VoidCallback onTap;

  const _EmojiSlice({
    required this.emoji,
    required this.size,
    required this.isPremium,
    required this.onTap,
  });

  @override
  State<_EmojiSlice> createState() => _EmojiSliceState();
}

class _EmojiSliceState extends State<_EmojiSlice> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) {
        setState(() => _pressed = false);
        widget.onTap();
      },
      onTapCancel: () => setState(() => _pressed = false),
      child: AnimatedScale(
        scale: _pressed ? 0.9 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.2),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Emoji
              Text(
                widget.emoji,
                style: TextStyle(fontSize: widget.size * 0.5),
              ),
              
              // Premium kilit
              if (widget.isPremium)
                Positioned(
                  right: 4,
                  bottom: 4,
                  child: Container(
                    padding: const EdgeInsets.all(3),
                    decoration: const BoxDecoration(
                      color: Colors.black87,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.lock,
                      size: 10,
                      color: Colors.white,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}