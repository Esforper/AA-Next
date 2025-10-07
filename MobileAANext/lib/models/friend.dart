// lib/models/friend.dart

class Friend {
  final String id;
  final String name;
  final String avatar;
  final bool isOnline;

  Friend({
    required this.id,
    required this.name,
    required this.avatar,
    this.isOnline = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'avatar': avatar,
        'isOnline': isOnline,
      };

  factory Friend.fromJson(Map<String, dynamic> json) => Friend(
        id: json['id'],
        name: json['name'],
        avatar: json['avatar'],
        isOnline: json['isOnline'] ?? false,
      );

  // Mock data generator
  static List<Friend> getMockFriends() => [
        Friend(
          id: 'friend_1',
          name: 'Ahmet',
          avatar: '👨',
          isOnline: true,
        ),
        Friend(
          id: 'friend_2',
          name: 'Ayşe',
          avatar: '👩',
          isOnline: true,
        ),
        Friend(
          id: 'friend_3',
          name: 'Mehmet',
          avatar: '🧑',
          isOnline: false,
        ),
        Friend(
          id: 'friend_4',
          name: 'Zeynep',
          avatar: '👧',
          isOnline: true,
        ),
        Friend(
          id: 'friend_5',
          name: 'Can',
          avatar: '👦',
          isOnline: false,
        ),
      ];
}