// lib/models/saved_reel.dart

class SavedReel {
  final String reelId;
  final String title;
  final String imageUrl;
  final DateTime savedAt;

  SavedReel({
    required this.reelId,
    required this.title,
    required this.imageUrl,
    required this.savedAt,
  });

  Map<String, dynamic> toJson() => {
        'reelId': reelId,
        'title': title,
        'imageUrl': imageUrl,
        'savedAt': savedAt.toIso8601String(),
      };

  factory SavedReel.fromJson(Map<String, dynamic> json) => SavedReel(
        reelId: json['reelId'],
        title: json['title'],
        imageUrl: json['imageUrl'],
        savedAt: DateTime.parse(json['savedAt']),
      );
}