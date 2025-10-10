import 'package:flutter/material.dart';
import '../models/game_models.dart';
import '../services/game_service.dart';
// Anasayfa veya oyun menüsü yolu projenize göre güncellenecek
import '../pages/game_menu_page.dart'; 
import '../pages/reels_feed_page.dart';

class GameResultPage extends StatefulWidget {
  final String gameId;
  const GameResultPage({Key? key, required this.gameId}) : super(key: key);

  @override
  _GameResultPageState createState() => _GameResultPageState();
}

class _GameResultPageState extends State<GameResultPage> {
  late Future<GameResult> _resultFuture;

  @override
  void initState() {
    super.initState();
    _resultFuture = GameService().getGameResult(widget.gameId);
  }
  
  void _playAgain() {
    // Oyun menüsüne yönlendir, aradaki tüm oyun ekranlarını kapat
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const GameMenuPage()),
      (Route<dynamic> route) => false,
    );
  }

  void _goToHome() {
    // TODO: Uygulamanızdaki ana sayfa widget'ı ile değiştirin
    // Örnek olarak ReelsFeedPage kullanıldı
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const ReelsFeedPage()),
      (Route<dynamic> route) => false,
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Oyun Sonucu'),
        automaticallyImplyLeading: false,
      ),
      body: FutureBuilder<GameResult>(
        future: _resultFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Sonuçlar yüklenemedi: ${snapshot.error}'));
          }
          if (!snapshot.hasData) {
            return const Center(child: Text('Sonuç bulunamadı.'));
          }

          final result = snapshot.data!;
          return _buildResultContent(result);
        },
      ),
    );
  }
  
  Widget _buildResultContent(GameResult result) {
    IconData resultIcon;
    String resultText;
    Color resultColor;

    switch (result.result) {
      case 'win':
        resultIcon = Icons.emoji_events;
        resultText = 'Kazandın!';
        resultColor = Colors.amber;
        break;
      case 'lose':
        resultIcon = Icons.sentiment_dissatisfied;
        resultText = 'Kaybettin';
        resultColor = Colors.red.shade300;
        break;
      default: // draw
        resultIcon = Icons.handshake;
        resultText = 'Berabere';
        resultColor = Colors.blueGrey;
    }
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // 1. Sonuç Başlığı
          Icon(resultIcon, size: 100, color: resultColor),
          const SizedBox(height: 16),
          Text(resultText, style: Theme.of(context).textTheme.displaySmall?.copyWith(color: resultColor, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          
          // 2. Skor ve XP
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _infoColumn('Senin Skorun', result.myScore.toString()),
                  _infoColumn('Rakip Skoru', result.opponentScore.toString()),
                  _infoColumn('Kazanılan XP', '+${result.totalXpEarned}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 3. Konuşulan Haberler
          const Text("Oyunda Bahsedilen Haberler", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const Divider(),
          Expanded(
            child: ListView.builder(
              itemCount: result.newsDiscussed.length,
              itemBuilder: (context, index) {
                final news = result.newsDiscussed[index];
                return ListTile(
                  leading: const Icon(Icons.article_outlined),
                  title: Text(news.title),
                  // onTap: () { /* TODO: Haber detayına git */ },
                );
              },
            ),
          ),
          
          // 4. Butonlar
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _goToHome,
                  child: const Text('Ana Sayfa'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton(
                  onPressed: _playAgain,
                  child: const Text('Tekrar Oyna'),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
  
  Widget _infoColumn(String title, String value) {
    return Column(
      children: [
        Text(title, style: const TextStyle(color: Colors.grey, fontSize: 14)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      ],
    );
  }
}