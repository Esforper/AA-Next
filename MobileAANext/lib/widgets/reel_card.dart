import 'package:flutter/material.dart';
import '../models/reel_model.dart';
import 'image_carousel.dart';
import 'read_handle.dart';
import 'emoji_panel.dart';
// DÜZELTME 1: Eski widget yerine yeni oluşturduğumuz ArticleReaderSheet'i import ediyoruz.
import 'article_reader_sheet.dart'; 
// DÜZELTME 2: Artık kullanılmayan eski import'u siliyoruz.
// import 'article_overlay.dart'; 
import '../services/api_service.dart';

class ReelCard extends StatefulWidget {
  final Reel reel;
  const ReelCard({super.key, required this.reel});

  @override
  State<ReelCard> createState() => _ReelCardState();
}

class _ReelCardState extends State<ReelCard>
    with AutomaticKeepAliveClientMixin {
  bool _showEmojis = false;

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final reel = widget.reel;

    return Stack(
      fit: StackFit.expand,
      children: [
        // İçerik
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

        // 4 Yönlü Handle (sağ-alt)
        Positioned(
          right: 16,
          bottom: 24,
          child: ReadHandle(
            onAction: (action) { // 'async' kaldırıldı
              switch (action) {
                case HandleAction.up:
                  // ⬆️ YUKARΙ: Detay Makale Aç
                  debugPrint('[Handle] UP - Article Detail');
                  showModalBottomSheet(
                    context: context,
                    isScrollControlled: true,
                    backgroundColor: Colors.transparent,
                    builder: (_) => ArticleReaderSheet(
                      articleId: reel.id,
                      title: reel.title,
                      body: reel.fullText,
                      // HATA BURADAYDI: Parametre 'imageUrl' -> 'imageUrls' olarak düzeltildi.
                      imageUrls: reel.imageUrls,
                      onClose: () => Navigator.pop(context),
                    ),
                  );
                  break;

                case HandleAction.right:
                  debugPrint('[Handle] RIGHT - Emoji Panel');
                  setState(() => _showEmojis = true);
                  break;

                case HandleAction.down:
                  debugPrint('[Handle] DOWN - Share');
                  ScaffoldMessenger.of(context)
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      // DÜZELTME 4: 'const' eklenerek performans artırıldı.
                      const SnackBar(
                        content: Text('Paylaşım özelliği yakında...'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  break;

                case HandleAction.left:
                  debugPrint('[Handle] LEFT - Save');
                  ScaffoldMessenger.of(context)
                    ..hideCurrentSnackBar()
                    ..showSnackBar(
                      // DÜZELTME 4: 'const' eklenerek performans artırıldı.
                      const SnackBar(
                        content: Text('İçerik kaydedildi! 📚'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  break;

                case HandleAction.none:
                  debugPrint('[Handle] NONE - No action');
                  break;
              }
            },
          ),
        ),

        // Emoji paneli (koşullu göster)
        if (_showEmojis)
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: EmojiPanel(
              publicEmojis: const ['👍', '❤️', '🔥', '😂', '😮'],
              premiumEmojis: const ['💎', '🏆', '⚡', '🌟'],
              onPick: (emoji) async {
                setState(() => _showEmojis = false);
                
                await ApiService().trackEmoji(
                  reelId: reel.id,
                  emoji: emoji,
                  category: reel.category,
                );
                
                // mounted kontrolü async işlemden sonra yapıldığı için doğrudur.
                if (!mounted) return;
                ScaffoldMessenger.of(context)
                  ..hideCurrentSnackBar()
                  ..showSnackBar(
                    SnackBar(content: Text('Tepkiniz gönderildi: $emoji')),
                  );
              },
              onTapPremium: () {
                setState(() => _showEmojis = false);
                ScaffoldMessenger.of(context)
                  ..hideCurrentSnackBar()
                  ..showSnackBar(
                    const SnackBar(
                      content: Text('Premium emojiler şimdilik kilitli.'),
                    ),
                  );
              },
            ),
          ),
      ],
    );
  }
}


