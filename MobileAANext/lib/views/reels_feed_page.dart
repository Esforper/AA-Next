import 'package:flutter/material.dart';
import '../models/reel_model.dart';
import '../services/api_service.dart';
import '../widgets/reel_card.dart';

class ReelsFeedPage extends StatefulWidget {
  const ReelsFeedPage({Key? key}) : super(key: key);

  @override
  State<ReelsFeedPage> createState() => _ReelsFeedPageState();
}

class _ReelsFeedPageState extends State<ReelsFeedPage> {
  final _api = ApiService();
  late Future<List<Reel>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.fetchReels(count: 6);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: FutureBuilder<List<Reel>>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return Center(child: Text('Hata: ${snap.error}'));
          }
          final items = snap.data ?? const <Reel>[];
          if (items.isEmpty) {
            return const Center(child: Text('Reel bulunamadı'));
          }

          // Burada PageView kullanıyoruz ama dikey (vertical)
          return PageView.builder(
            scrollDirection: Axis.vertical, // 👈 Instagram tarzı
            itemCount: items.length,
            itemBuilder: (context, i) {
              return ReelCard(reel: items[i]);
            },
          );
        },
      ),
    );
  }
}
