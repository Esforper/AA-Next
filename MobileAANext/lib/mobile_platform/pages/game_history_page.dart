import 'package:flutter/material.dart';
import '../../models/game_models.dart';
import '../../services/game_service.dart';
import 'package:url_launcher/url_launcher.dart';

/// Oyun Geçmişi Sayfası
class GameHistoryPage extends StatefulWidget {
  const GameHistoryPage({Key? key}) : super(key: key);

  @override
  State<GameHistoryPage> createState() => _GameHistoryPageState();
}

class _GameHistoryPageState extends State<GameHistoryPage> {
  final GameService _gameService = GameService();
  late Future<List<GameHistoryItem>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _historyFuture = _gameService.getGameHistory(limit: 20);
  }

  void _refreshHistory() {
    setState(() {
      _historyFuture = _gameService.getGameHistory(limit: 20);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Oyun Geçmişi'),
        backgroundColor: const Color(0xFF075E54),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshHistory,
            tooltip: 'Yenile',
          ),
        ],
      ),
      body: FutureBuilder<List<GameHistoryItem>>(
        future: _historyFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Hata: ${snapshot.error}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _refreshHistory,
                    child: const Text('Tekrar Dene'),
                  ),
                ],
              ),
            );
          }

          final history = snapshot.data ?? [];

          if (history.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history, size: 80, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text(
                    'Henüz oyun geçmişin yok',
                    style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'İlk oyununu oynamak için rakip bul!',
                    style: TextStyle(fontSize: 14, color: Colors.grey[500]),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.gamepad),
                    label: const Text('Oyun Oyna'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF075E54),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: history.length,
            itemBuilder: (context, index) {
              return _buildHistoryCard(history[index]);
            },
          );
        },
      ),
    );
  }

  Widget _buildHistoryCard(GameHistoryItem game) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: InkWell(
        onTap: () => _navigateToDetail(game.gameId),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Sonuç ikonu
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: game.resultColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: game.resultColor,
                    width: 2,
                  ),
                ),
                child: Center(
                  child: Text(
                    game.resultIcon,
                    style: const TextStyle(fontSize: 32),
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Oyun bilgileri
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Rakip ID (gerçekte isim olacak)
                    Text(
                      'vs ${game.opponentId.substring(0, 8)}...',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    
                    const SizedBox(height: 4),
                    
                    // Skor
                    Row(
                      children: [
                        Text(
                          '${game.myScore}',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: game.myScore > game.opponentScore 
                                ? Colors.green 
                                : Colors.grey,
                          ),
                        ),
                        const Text(' - ', style: TextStyle(fontSize: 16)),
                        Text(
                          '${game.opponentScore}',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: game.opponentScore > game.myScore 
                                ? Colors.green 
                                : Colors.grey,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '(${game.newsCount} haber)',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 4),
                    
                    // Tarih
                    Text(
                      game.formattedDate,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              
              // Ok ikonu
              Icon(
                Icons.chevron_right,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToDetail(String gameId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => GameHistoryDetailPage(gameId: gameId),
      ),
    );
  }
}

/// Oyun Geçmişi Detay Sayfası
class GameHistoryDetailPage extends StatefulWidget {
  final String gameId;

  const GameHistoryDetailPage({Key? key, required this.gameId})
      : super(key: key);

  @override
  State<GameHistoryDetailPage> createState() => _GameHistoryDetailPageState();
}

class _GameHistoryDetailPageState extends State<GameHistoryDetailPage> {
  final GameService _gameService = GameService();
  late Future<GameHistoryDetail> _detailFuture;

  @override
  void initState() {
    super.initState();
    _detailFuture = _gameService.getGameHistoryDetail(widget.gameId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Oyun Detayı'),
        backgroundColor: const Color(0xFF075E54),
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<GameHistoryDetail>(
        future: _detailFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    'Hata: ${snapshot.error}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red),
                  ),
                ],
              ),
            );
          }

          final detail = snapshot.data!;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Skor kartı
                _buildScoreCard(detail),
                
                const SizedBox(height: 24),
                
                // Bahsedilen haberler
                _buildNewsSection(detail),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildScoreCard(GameHistoryDetail detail) {
    // Şu anki kullanıcının ID'sini almak için (basitleştirilmiş)
    // Gerçekte AuthService'den alınmalı
    final myUserId = detail.player1Id; // Geçici
    final result = detail.getResult(myUserId);
    final myScore = detail.getMyScore(myUserId);
    final opponentScore = detail.getOpponentScore(myUserId);

    Color resultColor;
    String resultText;
    IconData resultIcon;

    if (result == 'win') {
      resultColor = Colors.amber;
      resultText = 'Kazandın! 🎉';
      resultIcon = Icons.emoji_events;
    } else if (result == 'lose') {
      resultColor = Colors.grey;
      resultText = 'Kaybettin 😢';
      resultIcon = Icons.trending_down;
    } else {
      resultColor = Colors.blue;
      resultText = 'Berabere 🤝';
      resultIcon = Icons.handshake;
    }

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(resultIcon, size: 64, color: resultColor),
            const SizedBox(height: 12),
            Text(
              resultText,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: resultColor,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Column(
                  children: [
                    const Text('Ben', style: TextStyle(fontSize: 16)),
                    const SizedBox(height: 4),
                    Text(
                      '$myScore XP',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const Text('-', style: TextStyle(fontSize: 32)),
                Column(
                  children: [
                    const Text('Rakip', style: TextStyle(fontSize: 16)),
                    const SizedBox(height: 4),
                    Text(
                      '$opponentScore XP',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNewsSection(GameHistoryDetail detail) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Bahsedilen Haberler',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...detail.newsDiscussed.asMap().entries.map((entry) {
          final index = entry.key;
          final news = entry.value;
          return _buildNewsCard(index + 1, news);
        }).toList(),
      ],
    );
  }

  Widget _buildNewsCard(int number, NewsDiscussed news) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _openNewsUrl(news.url),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Numara
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: const Color(0xFF075E54),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Center(
                  child: Text(
                    '$number',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Haber başlığı
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      news.title,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.link, size: 14, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          'Haberi aç',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              
              Icon(Icons.open_in_new, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openNewsUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Haber açılamadı')),
      );
    }
  }
}