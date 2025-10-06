// lib/widgets/reel_card.dart — Yeni yapıya tamamen uyumlu sürüm
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/reel_model.dart';
import '../providers/reels_provider.dart';
import 'image_carousel.dart';
import 'read_handle.dart';
import 'emoji_panel.dart';
import 'article_overlay.dart';
import 'voice_button.dart';

class ReelCard extends StatefulWidget {
  final Reel reel;
  const ReelCard({super.key, required this.reel});

  @override
  State<ReelCard> createState() => _ReelCardState();
}

class _ReelCardState extends State<ReelCard>
    with AutomaticKeepAliveClientMixin {
  bool showEmojis = false;

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final provider = context.watch<ReelsProvider>();

    return Stack(
      fit: StackFit.expand,
      children: [
        _buildContent(context),

        // Eğer ileride sesli okuma aktif edersen:
        Positioned(
          left: 12,
          top: 0,
          bottom: 0,
          child: Center(
            child: VoiceButton(
              speaking: false,
              onToggle: () {},
            ),
          ),
        ),

        // Emoji paneli
        if (showEmojis)
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: EmojiPanel(
              publicEmojis: const ['👍', '😂', '🔥', '😮'],
              premiumEmojis: const ['💎', '🚀', '😍'],
              onPick: (emoji) {
                setState(() => showEmojis = false);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Tepki gönderildi: $emoji')),
                );
              },
              onTapPremium: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Premium emojiye erişim yok 😅')),
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _buildContent(BuildContext context) {
    final provider = context.read<ReelsProvider>();
    final reel = widget.reel;

    return Column(
      children: [
        // görsel alanı
        Expanded(
          child: ClipRRect(
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(12),
              bottomRight: Radius.circular(12),
            ),
            child: ImageCarousel(
              urls: reel.imageUrls,
              onPageChanged: (_) {},
            ),
          ),
        ),

        // başlık & özet alanı
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          color: Colors.black,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                reel.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                reel.summary,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 10),

              // handle (yukarı=detay, sağa=emoji)
              ReadHandle(
                onAction: (action) {
                  switch (action) {
                    case HandleAction.up:
                      provider.openDetail(true);
                      showModalBottomSheet(
                        context: context,
                        isScrollControlled: true,
                        showDragHandle: true,
                        builder: (_) => ArticleOverlay(
                          title: reel.title,
                          body:
                              '${reel.summary}\n\n(Haberin devamı burada gösterilecek)',
                          onClose: () => provider.openDetail(false),
                        ),
                      );
                      break;
                    case HandleAction.right:
                      setState(() => showEmojis = true);
                      break;
                    case HandleAction.none:
                      break;
                  }
                },
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ],
    );
  }
}
