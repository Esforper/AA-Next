import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

/// Bir görseli tam ekran olarak gösteren, "lightbox" tarzı bir widget.
/// Tıklandığında pürüzsüz bir geçiş animasyonu (Hero) ve
/// yakınlaştırma/uzaklaştırma (InteractiveViewer) özellikleri sunar.
class ArticleImageViewer extends StatelessWidget {
  /// Gösterilecek görselin URL'si.
  final String imageUrl;

  /// Hero animasyonu için benzersiz bir etiket.
  /// Bu etiket, küçük görsel ile bu tam ekran görsel arasında
  /// bağlantı kurarak animasyonun çalışmasını sağlar.
  final String heroTag;

  const ArticleImageViewer({
    super.key,
    required this.imageUrl,
    required this.heroTag,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Arka planı karartarak görsele odaklanmayı sağlar.
      backgroundColor: Colors.black.withOpacity(0.85),
      // Kapatma butonu için transparan bir AppBar.
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        // Geri butonu yerine özel bir kapatma ikonu.
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white, size: 30),
          onPressed: () {
            Navigator.pop(context);
          },
          tooltip: 'Kapat',
        ),
      ),
      body: Center(
        // Hero widget'ı, `heroTag` eşleşmesiyle animasyonlu geçişi sağlar.
        child: Hero(
          tag: heroTag,
          // InteractiveViewer, içindeki widget'a (görsel)
          // dokunmatik hareketlerle (pinch, pan) etkileşim yeteneği kazandırır.
          child: InteractiveViewer(
            minScale: 1.0,
            maxScale: 4.0, // Maksimum 4 kat yakınlaştırma
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              fit: BoxFit.contain,
              // Yüklenirken gösterilecek olan placeholder.
              placeholder: (context, url) =>
                  const Center(child: CircularProgressIndicator(color: Colors.white)),
              // Hata durumunda gösterilecek olan ikon.
              errorWidget: (context, url, error) =>
                  const Icon(Icons.broken_image, color: Colors.white60, size: 80),
            ),
          ),
        ),
      ),
    );
  }
}
