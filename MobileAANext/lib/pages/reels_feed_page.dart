import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/reels_provider.dart';
import '../models/reel_model.dart';
import '../widgets/image_carousel.dart';
import '../widgets/article_overlay.dart';
import '../widgets/emoji_panel.dart';
import '../widgets/read_handle.dart';
import '../widgets/popup_bar.dart';
import '../services/api_service.dart';

class ReelsFeedPage extends StatelessWidget {
  const ReelsFeedPage({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ReelsProvider>();

    if (provider.status == FeedStatus.initial) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        final p = context.read<ReelsProvider>();
        if (p.status == FeedStatus.initial) {
          p.loadReels();
        }
      });
    }

    return Scaffold(
      appBar: const PopupBar(),
      body: Stack(
        children: [
          _buildBody(context, provider),

          Positioned(
            right: 16,
            bottom: 24,
            child: ReadHandle(
              threshold: 35, // ✅ Tek parametre (4 yön için)
              onAction: (action) {
                final reels = provider.reels;
                if (reels.isEmpty) return;
                final reel = reels[provider.currentIndex];

                switch (action) {
                  case HandleAction.up:
                    debugPrint('[Handle] UP detected');
                    _openArticle(context, reel);
                    break;
                  case HandleAction.right:
                    debugPrint('[Handle] RIGHT detected');
                    _openEmojis(context, reel);
                    break;
                  case HandleAction.down:
                    debugPrint('[Handle] DOWN - Share');
                    ScaffoldMessenger.of(context)
                      ..hideCurrentSnackBar()
                      ..showSnackBar(
                        const SnackBar(content: Text('Paylaşım yakında...')),
                      );
                    break;
                  case HandleAction.left:
                    debugPrint('[Handle] LEFT - Save');
                    ScaffoldMessenger.of(context)
                      ..hideCurrentSnackBar()
                      ..showSnackBar(
                        const SnackBar(content: Text('İçerik kaydedildi! 📚')),
                      );
                    break;
                  case HandleAction.none:
                    debugPrint('[Handle] NONE');
                    break;
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  void _openArticle(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ArticleOverlay(
        title: reel.title,
        body: reel.fullText,
        onClose: () => Navigator.pop(context),
      ),
    );
  }

  void _openEmojis(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      barrierColor: Colors.black.withOpacity(0.2),
      builder: (_) => EmojiPanel(
        publicEmojis: const ['👍', '❤️', '🔥', '⭐', '👏'],
        premiumEmojis: const ['😍', '🤔', '😮', '🎉', '💎'],
        onPick: (emoji) async {
          Navigator.pop(context);
          await ApiService().trackView(
            reelId: reel.id,
            emojiReaction: emoji,
            category: reel.category,
          );
          if (!context.mounted) return;
          ScaffoldMessenger.of(context)
            ..hideCurrentSnackBar()
            ..showSnackBar(
              SnackBar(content: Text('Tepkiniz gönderildi: $emoji')),
            );
        },
        onTapPremium: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context)
            ..hideCurrentSnackBar()
            ..showSnackBar(
              const SnackBar(
                  content: Text('Premium emojiler şimdilik kilitli.')),
            );
        },
      ),
    );
  }

  Widget _buildBody(BuildContext context, ReelsProvider provider) {
    switch (provider.status) {
      case FeedStatus.initial:
      case FeedStatus.loading:
        return const Center(child: CircularProgressIndicator());

      case FeedStatus.error:
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Haberler yüklenemedi.'),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => context.read<ReelsProvider>().loadReels(),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        );

      case FeedStatus.loaded:
        final reels = provider.reels;
        if (reels.isEmpty) {
          return const Center(child: Text('Gösterilecek içerik yok.'));
        }
        return PageView.builder(
          scrollDirection: Axis.vertical,
          physics: const PageScrollPhysics(),
          allowImplicitScrolling: true,
          itemCount: reels.length,
          onPageChanged: (i) => context.read<ReelsProvider>().setIndex(i),
          itemBuilder: (context, i) {
            final reel = reels[i];
            return KeyedSubtree(
              key: ValueKey(reel.id),
              child: _ReelView(reel: reel),
            );
          },
        );
    }
  }
}

class _ReelView extends StatelessWidget {
  final Reel reel;
  const _ReelView({required this.reel});

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        Positioned.fill(
          bottom: 90,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 8),
              Expanded(child: ImageCarousel(urls: reel.imageUrls)),
              const SizedBox(height: 12),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  reel.title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  reel.summary,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(height: 1.4, color: Colors.black87),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}