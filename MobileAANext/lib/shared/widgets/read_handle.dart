import 'package:flutter/material.dart';

/// 4 yön: Yukarı, Sağ, Aşağı, Sol
enum HandleAction { up, right, down, left, none }

class ReadHandle extends StatefulWidget {
  final ValueChanged<HandleAction> onAction;
  final Size trackSize;
  final double knobSize;
  final double threshold;

  const ReadHandle({
    super.key,
    required this.onAction,
    this.trackSize = const Size(160, 160),
    this.knobSize = 56,
    this.threshold = 35,
  });

  @override
  State<ReadHandle> createState() => _ReadHandleState();
}

class _ReadHandleState extends State<ReadHandle>
    with TickerProviderStateMixin {
  late final AnimationController _anim;
  late Animation<Offset> _spring;
  Offset _offset = Offset.zero;
  bool _isPressed = false;
  
  late final AnimationController _expandAnim;
  late final Animation<double> _expandScale;

  @override
  void initState() {
    super.initState();
    
    // Geri dönüş animasyonu
    _anim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 220),
    );
    _spring = Tween<Offset>(begin: Offset.zero, end: Offset.zero)
        .chain(CurveTween(curve: Curves.easeOutBack))
        .animate(_anim)
      ..addListener(() {
        if (mounted) setState(() {});
      })
      ..addStatusListener((s) {
        if (s == AnimationStatus.completed) {
          _offset = Offset.zero;
        }
      });

    // Dış daire açılma animasyonu
    _expandAnim = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
    );
    
    _expandScale = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _expandAnim, curve: Curves.easeOutBack),
    )..addListener(() {
      if (mounted) setState(() {});
    });
    
    debugPrint('[ReadHandle] Animasyonlar initialize edildi');
  }

  @override
  void dispose() {
    _anim.dispose();
    _expandAnim.dispose();
    super.dispose();
  }

  void _animateBack() {
    _anim.reset();
    _spring = Tween<Offset>(begin: _offset, end: Offset.zero)
        .chain(CurveTween(curve: Curves.easeOutBack))
        .animate(_anim);
    _anim.forward();
  }

  Offset _clampToTrack(Offset raw) {
    final w = widget.trackSize.width;
    final h = widget.trackSize.height;
    final r = widget.knobSize / 2;
    final maxX = (w / 2) - r - 8;
    final maxY = (h / 2) - r - 8;
    return Offset(
      raw.dx.clamp(-maxX, maxX),
      raw.dy.clamp(-maxY, maxY),
    );
  }

  HandleAction _detectDirection() {
    final dx = _offset.dx.abs();
    final dy = _offset.dy.abs();
    final threshold = widget.threshold;

    if (dx > dy) {
      if (_offset.dx > threshold) {
        return HandleAction.right;
      } else if (_offset.dx < -threshold) {
        return HandleAction.left;
      }
    } else {
      if (_offset.dy > threshold) {
        return HandleAction.down;
      } else if (_offset.dy < -threshold) {
        return HandleAction.up;
      }
    }
    
    return HandleAction.none;
  }

  @override
  Widget build(BuildContext context) {
    final trackW = widget.trackSize.width;
    final trackH = widget.trackSize.height;
    final pos = _anim.isAnimating ? _spring.value : _offset;

    debugPrint('[ReadHandle] Build - isPressed: $_isPressed, expandValue: ${_expandScale.value}');

    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onPanStart: (_) {
        debugPrint('[ReadHandle] PAN START');
        setState(() => _isPressed = true);
        _expandAnim.forward();
      },
      onPanUpdate: (d) {
        final next = _clampToTrack(_offset + d.delta);
        setState(() => _offset = next);
      },
      onPanEnd: (_) {
        debugPrint('[ReadHandle] PAN END');
        setState(() => _isPressed = false);
        final action = _detectDirection();
        widget.onAction(action);
        _animateBack();
        _expandAnim.reverse();
      },
      onPanCancel: () {
        debugPrint('[ReadHandle] PAN CANCEL');
        setState(() => _isPressed = false);
        _animateBack();
        _expandAnim.reverse();
      },
      child: SizedBox(
        width: trackW,
        height: trackH,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // DIŞ DAİRE (Animasyonlu açılır/kapanır)
            AnimatedBuilder(
              animation: _expandScale,
              builder: (context, child) {
                final scale = _expandScale.value;
                debugPrint('[ReadHandle] AnimatedBuilder scale: $scale');
                
                if (scale == 0.0) return const SizedBox.shrink();
                
                return Transform.scale(
                  scale: scale,
                  child: Opacity(
                    opacity: scale.clamp(0.0, 1.0),
                    child: Container(
                      width: trackW,
                      height: trackH,
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        shape: BoxShape.circle,
                        boxShadow: const [
                          BoxShadow(
                            blurRadius: 8,
                            color: Colors.black38,
                            offset: Offset(0, 3),
                          ),
                        ],
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // 4 Yön İkonları
                          Positioned(
                            top: 16,
                            child: Icon(
                              Icons.arrow_upward,
                              color: Colors.white70,
                              size: 20,
                            ),
                          ),
                          Positioned(
                            right: 16,
                            child: Icon(
                              Icons.emoji_emotions_outlined,
                              color: Colors.white70,
                              size: 20,
                            ),
                          ),
                          Positioned(
                            bottom: 16,
                            child: Icon(
                              Icons.share_outlined,
                              color: Colors.white70,
                              size: 20,
                            ),
                          ),
                          Positioned(
                            left: 16,
                            child: Icon(
                              Icons.bookmark_outline,
                              color: Colors.white70,
                              size: 20,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),

            // ÇEKIRDEK (Beyaz yuvarlak - her zaman görünür)
            Transform.translate(
              offset: pos,
              child: Container(
                width: widget.knobSize,
                height: widget.knobSize,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      blurRadius: _isPressed ? 8 : 4,
                      color: Colors.black26,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: Icon(
                  Icons.drag_indicator,
                  color: Colors.black87,
                  size: 24,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}