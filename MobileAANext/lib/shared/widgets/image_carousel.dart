import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class ImageCarousel extends StatefulWidget {
  final List<String> urls;
  final ValueChanged<int>? onPageChanged;
  const ImageCarousel({super.key, required this.urls, this.onPageChanged});

  @override
  State<ImageCarousel> createState() => _ImageCarouselState();
}

class _ImageCarouselState extends State<ImageCarousel> {
  final _pageCtrl = PageController();
  double _nudge = 0.0;
  int _index = 0;

  @override
  void dispose() {
    _pageCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final h = MediaQuery.sizeOf(context).height;
    final boxH = h * 0.36; // ⬅️ daha kısa

    final urls = widget.urls
        .where((u) =>
            u.isNotEmpty &&
            (u.startsWith('http://') || u.startsWith('https://')))
        .toList();

    if (urls.isEmpty) {
      return SizedBox(
        height: boxH,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: Container(
              color: const Color(0x11000000),
              child: const Center(child: Icon(Icons.image_outlined, size: 48)),
            ),
          ),
        ),
      );
    }

    return SizedBox(
      height: boxH,
      child: Stack(
        children: [
          PageView.builder(
            controller: _pageCtrl,
            itemCount: urls.length,
            onPageChanged: (i) {
              setState(() => _index = i);
              widget.onPageChanged?.call(i);
            },
            itemBuilder: (_, i) {
              final url = urls[i];
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: LayoutBuilder(
                    builder: (context, c) {
                      return GestureDetector(
                        onTapDown: (d) {
                          final left = d.localPosition.dx < c.maxWidth / 2;
                          setState(() => _nudge = left ? -0.06 : 0.06);
                        },
                        onTapUp: (_) => setState(() => _nudge = 0),
                        onTapCancel: () => setState(() => _nudge = 0),
                        child: TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0, end: _nudge),
                          duration: const Duration(milliseconds: 160),
                          curve: Curves.easeOut,
                          builder: (_, v, child) => FractionalTranslation(
                              translation: Offset(v, 0), child: child),
                          child: CachedNetworkImage(
                            imageUrl: url,
                            fit: BoxFit.cover,
                            placeholder: (_, __) =>
                                const ColoredBox(color: Color(0x11000000)),
                            errorWidget: (_, __, ___) =>
                                const ColoredBox(color: Color(0x11000000)),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              );
            },
          ),

          // dot indicator
          Positioned(
            right: 24,
            bottom: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(.35),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                children: List.generate(urls.length, (i) {
                  final active = i == _index;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    width: active ? 10 : 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: active ? Colors.white : Colors.white54,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
