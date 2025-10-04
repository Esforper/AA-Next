import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/reel_model.dart';
import '../providers/reels_provider.dart';
import 'image_carousel.dart';
import 'read_button.dart';
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
    final p = context.watch<ReelsProvider>();
    final speaking = p.speakingReelId == widget.reel.id;

    return Stack(
      fit: StackFit.expand,
      children: [
        _buildContent(context),
        Positioned(
          left: 12,
          top: 0,
          bottom: 0,
          child: Center(
            child: VoiceButton(
              speaking: speaking,
              onToggle: () => p.speakSummary(widget.reel),
            ),
          ),
        ),
        EmojiPanel(
          visible: showEmojis,
          onPick: (emoji) {
            setState(() => showEmojis = false);
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Tepki gönderildi: $emoji')),
            );
          },
        ),
        Positioned.fill(
          child: ArticleOverlay(
            open: p.overlayOpen,
            content: widget.reel.fullContent,
            onClose: () => p.setOverlay(false),
          ),
        ),
      ],
    );
  }

  Widget _buildContent(BuildContext context) {
    final p = context.read<ReelsProvider>();
    return Column(
      children: [
        Expanded(
          child: ClipRRect(
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(12),
              bottomRight: Radius.circular(12),
            ),
            child: ImageCarousel(
              images: widget.reel.images,
              mainImage: widget.reel.mainImage,
            ),
          ),
        ),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          color: Colors.black,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.reel.title,
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
                widget.reel.summary,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(color: Colors.white.withOpacity(.9)),
              ),
              const SizedBox(height: 10),
              ReadButton(
                onOpenOverlay: () => p.setOverlay(true),
                onRevealEmojis: () => setState(() => showEmojis = true),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ],
    );
  }
}
