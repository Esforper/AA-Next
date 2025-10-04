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
      create: (_) =>
          ReelsProvider(ApiService('http://10.0.2.2:8000'))..loadMock(),
      child: Consumer<ReelsProvider>(
        builder: (_, p, __) {
          return Scaffold(
            backgroundColor: Colors.black,
            body: SafeArea(
              child: Stack(
                children: [
                  PageView.builder(
                    scrollDirection: Axis.vertical,
                    itemCount: p.reels.length,
                    onPageChanged: p.onPageChanged,
                    itemBuilder: (_, i) => p.reels.isEmpty
                        ? const SizedBox.shrink()
                        : ReelCard(reel: p.reels[i]),
                  ),
                  if (p.reels.isEmpty)
                    const Center(child: CircularProgressIndicator()),
                  const PopupBar(
                    message:
                        'Premium emojiler kilitli. Kulübe geçince açılır ⭐',
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
