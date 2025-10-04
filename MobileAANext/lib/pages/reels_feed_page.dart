// lib/pages/reels_feed_page.dart - SON HALİ

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/reels_provider.dart';
import '../services/api_service.dart';
import '../widgets/reel_card.dart';
import '../widgets/popup_bar.dart';

class ReelsFeedPage extends StatelessWidget {
  const ReelsFeedPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      // 1. ApiService.auto() ile platforma özel doğru IP/host adresini otomatik bulmasını sağla.
      // 2. Mock verileri yerine fetchInitialFeed() ile gerçek verilerin ilk sayfasını çek.
      create: (_) => ReelsProvider(ApiService.auto())..fetchInitialFeed(),
      
      child: Consumer<ReelsProvider>(
        builder: (context, reelsProvider, child) {
          return Scaffold(
            backgroundColor: Colors.black,
            body: SafeArea(
              child: Stack(
                children: [
                  // Reel listesi boşsa ve hala yükleniyorsa, bekleme indicator'ı göster.
                  if (reelsProvider.reels.isEmpty)
                    const Center(child: CircularProgressIndicator(color: Colors.white))
                  else
                    // PageView, provider'daki reel listesini kullanarak sayfaları oluşturur.
                    PageView.builder(
                      scrollDirection: Axis.vertical,
                      itemCount: reelsProvider.reels.length,
                      // Kullanıcı sayfa değiştirdiğinde provider'a haber ver.
                      onPageChanged: reelsProvider.onPageChanged,
                      itemBuilder: (context, index) {
                        return ReelCard(reel: reelsProvider.reels[index]);
                      },
                    ),
                  
                  // PopupBar gibi diğer UI elemanları olduğu gibi kalabilir.
                  const PopupBar(
                    message: 'Premium emojiler kilitli. Kulübe geçince açılır ⭐',
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}