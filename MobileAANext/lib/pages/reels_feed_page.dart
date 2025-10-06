import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../widgets/popup_bar.dart';
import '../widgets/image_carousel.dart';
import '../providers/reels_provider.dart';
import '../widgets/article_overlay.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../services/api_service.dart';

class ReelsFeedPage extends StatelessWidget {
  const ReelsFeedPage({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<ReelsProvider>();

    return Scaffold(
      appBar: const PopupBar(),
      body: p.reels.isEmpty
          ? const Center(child: Text('Gösterilecek haber bulunamadı.'))
          : PageView.builder(
              scrollDirection: Axis.vertical, // reels geçişi
              itemCount: p.reels.length,
              onPageChanged: p.setIndex,
              itemBuilder: (context, index) {
                final reel = p.reels[index];

                return Stack(
                  children: [
                    // sabit içerik
                    Padding(
                      padding: const EdgeInsets.only(bottom: 90),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 8),
                          ImageCarousel(urls: reel.imageUrls),
                          const SizedBox(height: 12),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Text(
                              reel.title,
                              style: const TextStyle(
                                  fontSize: 20, fontWeight: FontWeight.w800),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Text(
                              reel.summary,
                              maxLines: 4,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(height: 1.35),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Handle (↑ detay sheet, → emoji fan)
                    ReadHandle(
                      onAction: (a) async {
                        switch (a) {
                          case HandleAction.up:
                            // full content: paragraf dizisini birleştir
                            final text = reel.fullText;
                            await showModalBottomSheet(
                              context: context,
                              isScrollControlled: true,
                              backgroundColor: Colors.transparent,
                              builder: (_) => ArticleOverlay(
                                title: reel.title,
                                body: text,
                                onClose: () => Navigator.pop(context),
                              ),
                            );
                            break;

                          case HandleAction.right:
                            await showModalBottomSheet(
                              context: context,
                              backgroundColor: Colors.transparent,
                              barrierColor: Colors.black45,
                              builder: (_) => Container(
                                color: Colors.transparent,
                                child: SafeArea(
                                  top: false,
                                  child: EmojiPanel(
                                    publicEmojis: const [
                                      '👍',
                                      '😂',
                                      '🔥',
                                      '😮'
                                    ],
                                    premiumEmojis: const [
                                      '💎',
                                      '🚀',
                                      '😍',
                                      '🤯'
                                    ],
                                    onPick: (e) async {
                                      Navigator.pop(context);
                                      await ApiService.trackView(
                                        reelId: reel.id,
                                        emojiReaction: e,
                                        category: reel.category,
                                      );
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        SnackBar(
                                            content:
                                                Text('Tepkin kaydedildi: $e')),
                                      );
                                    },
                                    onTapPremium: () {
                                      Navigator.pop(context);
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        const SnackBar(
                                            content: Text(
                                                'Premium emojiler kilitli')),
                                      );
                                    },
                                  ),
                                ),
                              ),
                            );
                            break;

                          case HandleAction.none:
                            break;
                        }
                      },
                    ),
                  ],
                );
              },
            ),
    );
  }
}
