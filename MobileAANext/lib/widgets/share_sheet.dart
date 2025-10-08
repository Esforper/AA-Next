// lib/widgets/share_sheet.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../models/chat_room.dart';

class ShareSheet extends StatefulWidget {
  final String newsId;
  final String newsTitle;
  final String newsImageUrl;

  const ShareSheet({
    super.key,
    required this.newsId,
    required this.newsTitle,
    required this.newsImageUrl,
  });

  @override
  State<ShareSheet> createState() => _ShareSheetState();
}

class _ShareSheetState extends State<ShareSheet> {
  String _selectedEmoji = '❤️';
  bool _includeDetail = false;

  final List<String> _emojis = ['❤️', '😮', '🔥', '👍', '😂', '😢'];

  @override
  Widget build(BuildContext context) {
    final chatProvider = context.watch<ChatProvider>();
    final rooms = chatProvider.rooms;

    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Başlık
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                const Text(
                  '📤',
                  style: TextStyle(fontSize: 24),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Haberi Paylaş',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),

          const Divider(),

          // Haber önizleme
          Padding(
            padding: const EdgeInsets.all(16),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      widget.newsImageUrl,
                      width: 60,
                      height: 60,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                        width: 60,
                        height: 60,
                        color: Colors.grey[300],
                        child: const Icon(Icons.image),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      widget.newsTitle,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Emoji seçimi
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Emoji ile paylaş:',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  children: _emojis.map((emoji) {
                    final isSelected = emoji == _selectedEmoji;
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedEmoji = emoji;
                        });
                      },
                      child: Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          color: isSelected ? Colors.blue[50] : Colors.grey[100],
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: isSelected ? Colors.blue : Colors.transparent,
                            width: 2,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            emoji,
                            style: const TextStyle(fontSize: 24),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Detay toggle
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    'Haber detaylarını da ekle',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[700],
                    ),
                  ),
                ),
                Switch(
                  value: _includeDetail,
                  onChanged: (val) {
                    setState(() {
                      _includeDetail = val;
                    });
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 8),
          const Divider(),

          // Odalar listesi
          if (rooms.isEmpty)
            const Padding(
              padding: EdgeInsets.all(32),
              child: Text(
                'Henüz oda yok\n(Mock data yüklenmedi)',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
            )
          else
            SizedBox(
              height: 200,
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: rooms.length + 1, // +1 genel paylaş için
                itemBuilder: (context, index) {
                  // Genel paylaş butonu (ilk item)
                  if (index == 0) {
                    return ListTile(
                      leading: Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          color: Colors.green[50],
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.ios_share,
                          color: Colors.green[700],
                        ),
                      ),
                      title: const Text(
                        'Genel Paylaş',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      subtitle: const Text('WhatsApp, Telegram, vb.'),
                      onTap: () {
                        Navigator.pop(context);
                        _showGeneralShare(context);
                      },
                    );
                  }

                  // Odalar
                  final room = rooms[index - 1];
                  return ListTile(
                    leading: Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        color: Colors.blue[50],
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          room.emoji,
                          style: const TextStyle(fontSize: 24),
                        ),
                      ),
                    ),
                    title: Text(
                      room.name,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: Text('${room.memberIds.length} üye'),
                    trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () {
                      _shareToRoom(context, room.id);
                    },
                  );
                },
              ),
            ),

          const SizedBox(height: 16),
        ],
      ),
    );
  }

  void _shareToRoom(BuildContext context, String roomId) {
    final chatProvider = context.read<ChatProvider>();

    chatProvider.shareNewsToRoom(
      roomId: roomId,
      newsId: widget.newsId,
      newsTitle: widget.newsTitle,
      newsImageUrl: widget.newsImageUrl,
      emoji: _selectedEmoji,
      includeDetail: _includeDetail,
    );

    Navigator.pop(context);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Haber paylaşıldı! $_selectedEmoji'),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showGeneralShare(BuildContext context) {
    // Genel paylaşım (sistem share sheet)
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Genel paylaşım özelliği yakında eklenecek!'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}