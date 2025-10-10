// lib/models/game_models.dart
// Haber Kapışması Oyunu - Data Modelleri

/// Matchmaking yanıtı - Rakip arama sonucu
class MatchmakingResponse {
  final bool success;
  final bool matched;
  final String? opponentId;
  final String? gameId;
  final int commonReelsCount;
  final int? estimatedWaitTimeSeconds;
  final String message;

  MatchmakingResponse({
    required this.success,
    required this.matched,
    this.opponentId,
    this.gameId,
    required this.commonReelsCount,
    this.estimatedWaitTimeSeconds,
    required this.message,
  });

  factory MatchmakingResponse.fromJson(Map<String, dynamic> json) {
    return MatchmakingResponse(
      success: json['success'] ?? false,
      matched: json['matched'] ?? false,
      opponentId: json['opponent_id'],
      gameId: json['game_id'],
      commonReelsCount: json['common_reels_count'] ?? 0,
      estimatedWaitTimeSeconds: json['estimated_wait_time_seconds'],
      message: json['message'] ?? '',
    );
  }
}

/// Oyun durumu - Oyun oturumu bilgileri
class GameSession {
  final bool success;
  final String gameId;
  final String status; // "waiting", "active", "finished"
  final String player1Id;
  final String player2Id;
  final int player1Score;
  final int player2Score;
  final int currentRound;
  final int totalRounds;
  final String createdAt;

  GameSession({
    required this.success,
    required this.gameId,
    required this.status,
    required this.player1Id,
    required this.player2Id,
    required this.player1Score,
    required this.player2Score,
    required this.currentRound,
    required this.totalRounds,
    required this.createdAt,
  });

  factory GameSession.fromJson(Map<String, dynamic> json) {
    return GameSession(
      success: json['success'] ?? true,
      gameId: json['game_id'] ?? '',
      status: json['status'] ?? 'waiting',
      player1Id: json['player1_id'] ?? '',
      player2Id: json['player2_id'] ?? '',
      player1Score: json['player1_score'] ?? 0,
      player2Score: json['player2_score'] ?? 0,
      currentRound: json['current_round'] ?? 0,
      totalRounds: json['total_rounds'] ?? 8,
      createdAt: json['created_at'] ?? '',
    );
  }

  /// Oyun aktif mi?
  bool get isActive => status == 'active';

  /// Oyun bitti mi?
  bool get isFinished => status == 'finished';
}

/// Oyun sorusu - Tek bir round'un sorusu
class GameQuestion {
  final bool success;
  final int roundNumber;
  final int totalRounds;
  final String questionText;
  final List<String> options; // 2 seçenek (karışık sırada)
  final int correctIndex; // Doğru cevabın index'i (0 veya 1)
  final String reelId;
  final String newsTitle;
  final String askerId; // Kim soruyor?

  GameQuestion({
    required this.success,
    required this.roundNumber,
    required this.totalRounds,
    required this.questionText,
    required this.options,
    required this.correctIndex,
    required this.reelId,
    required this.newsTitle,
    required this.askerId,
  });

  factory GameQuestion.fromJson(Map<String, dynamic> json) {
    return GameQuestion(
      success: json['success'] ?? true,
      roundNumber: json['round_number'] ?? 0,
      totalRounds: json['total_rounds'] ?? 8,
      questionText: json['question_text'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      correctIndex: json['correct_index'] ?? 0,
      reelId: json['reel_id'] ?? '',
      newsTitle: json['news_title'] ?? '',
      askerId: json['asker_id'] ?? '',
    );
  }

  /// Soru metni ile birlikte haber başlığını göster
  String get fullQuestion => '$questionText\n"$newsTitle"';
}

/// Cevap yanıtı - Soruya verilen cevap sonucu
class AnswerResponse {
  final bool success;
  final bool isCorrect;
  final int xpEarned;
  final int currentScore;
  final String responseMessage; // "Evet evet!" veya "Yanlış hatırlıyorsun"
  final String? emojiComment; // Emoji bazlı yorum
  final String newsUrl; // Haberin linki

  AnswerResponse({
    required this.success,
    required this.isCorrect,
    required this.xpEarned,
    required this.currentScore,
    required this.responseMessage,
    this.emojiComment,
    required this.newsUrl,
  });

  factory AnswerResponse.fromJson(Map<String, dynamic> json) {
    return AnswerResponse(
      success: json['success'] ?? true,
      isCorrect: json['is_correct'] ?? false,
      xpEarned: json['xp_earned'] ?? 0,
      currentScore: json['current_score'] ?? 0,
      responseMessage: json['response_message'] ?? '',
      emojiComment: json['emoji_comment'],
      newsUrl: json['news_url'] ?? '',
    );
  }
}

/// Oyun sonucu - Final skor ve detaylar
class GameResult {
  final bool success;
  final String gameId;
  final String? winnerId;
  final String result; // "win", "lose", "draw"
  final int myScore;
  final int opponentScore;
  final int totalXpEarned;
  final List<NewsDiscussed> newsDiscussed;

  GameResult({
    required this.success,
    required this.gameId,
    this.winnerId,
    required this.result,
    required this.myScore,
    required this.opponentScore,
    required this.totalXpEarned,
    required this.newsDiscussed,
  });

  factory GameResult.fromJson(Map<String, dynamic> json) {
    return GameResult(
      success: json['success'] ?? true,
      gameId: json['game_id'] ?? '',
      winnerId: json['winner_id'],
      result: json['result'] ?? 'draw',
      myScore: json['my_score'] ?? 0,
      opponentScore: json['opponent_score'] ?? 0,
      totalXpEarned: json['total_xp_earned'] ?? 0,
      newsDiscussed: (json['news_discussed'] as List<dynamic>?)
              ?.map((item) => NewsDiscussed.fromJson(item))
              .toList() ??
          [],
    );
  }

  /// Kazandın mı?
  bool get isWinner => result == 'win';

  /// Kaybettin mi?
  bool get isLoser => result == 'lose';

  /// Berabere mi?
  bool get isDraw => result == 'draw';

  /// Sonuç mesajı
  String get resultMessage {
    if (isWinner) return 'Kazandın! 🎉';
    if (isLoser) return 'Kaybettin 😢';
    return 'Berabere! 🤝';
  }
}

/// Oyunda bahsedilen haber
class NewsDiscussed {
  final String reelId;
  final String title;
  final String url;

  NewsDiscussed({
    required this.reelId,
    required this.title,
    required this.url,
  });

  factory NewsDiscussed.fromJson(Map<String, dynamic> json) {
    return NewsDiscussed(
      reelId: json['reel_id'] ?? '',
      title: json['title'] ?? '',
      url: json['url'] ?? '',
    );
  }
}

/// Oyun uygunluk kontrolü - Oyun oynayabilir mi?
class GameEligibility {
  final bool success;
  final bool eligible;
  final int currentCount;
  final int required;
  final int needed;
  final String message;

  GameEligibility({
    required this.success,
    required this.eligible,
    required this.currentCount,
    required this.required,
    required this.needed,
    required this.message,
  });

  factory GameEligibility.fromJson(Map<String, dynamic> json) {
    return GameEligibility(
      success: json['success'] ?? true,
      eligible: json['eligible'] ?? false,
      currentCount: json['current_count'] ?? 0,
      required: json['required'] ?? 8,
      needed: json['needed'] ?? 0,
      message: json['message'] ?? '',
    );
  }


}





  // Bu class'ı MatchmakingResponse'dan SONRA ekle:

/// Matchmaking durumu - Polling için
class MatchmakingStatusResponse {
  final bool success;
  final bool inQueue;
  final bool matched;
  final String? gameId;
  final String? opponentId;
  final int waitTimeSeconds;
  final int queuePosition;
  final int estimatedWait;
  final String message;

  MatchmakingStatusResponse({
    required this.success,
    required this.inQueue,
    required this.matched,
    this.gameId,
    this.opponentId,
    required this.waitTimeSeconds,
    required this.queuePosition,
    required this.estimatedWait,
    required this.message,
  });

  factory MatchmakingStatusResponse.fromJson(Map<String, dynamic> json) {
    return MatchmakingStatusResponse(
      success: json['success'] ?? false,
      inQueue: json['in_queue'] ?? false,
      matched: json['matched'] ?? false,
      gameId: json['game_id'],
      opponentId: json['opponent_id'],
      waitTimeSeconds: json['wait_time_seconds'] ?? 0,
      queuePosition: json['queue_position'] ?? 0,
      estimatedWait: json['estimated_wait'] ?? 0,
      message: json['message'] ?? '',
    );
  }
}
