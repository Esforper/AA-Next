// lib/views/saved_reels_view.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/saved_reels_provider.dart';
import '../../providers/reels_provider.dart';

class SavedReelsView extends StatelessWidget {
  const SavedReelsView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Kaydedilenler'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        actions: [
          Consumer<SavedReelsProvider>(
            builder: (context, savedProv, _) {
              if (savedProv.savedReels.isEmpty) return const SizedBox.shrink();
              
              return IconButton(
                onPressed: () {
                  _showClearDialog(context, savedProv);
                },
                icon: const Icon(Icons.delete_outline),
                tooltip: 'Tümünü Sil',
              );
            },
          ),
        ],
      ),
      body: Consumer<SavedReelsProvider>(
        builder: (context, savedProv, _) {
          final savedReels = savedProv.savedReels;

          // Boş durum
          if (savedReels.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    '🔖',
                    style: TextStyle(fontSize: 80),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Henüz kaydettiğin haber yok',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[700],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Reels\'te haberi sola kaydırarak kaydet',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            );
          }

          // Kayıtlı reels listesi
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: savedReels.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final saved = savedReels[index];

              return Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.all(12),
                  // Thumbnail
                  leading: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.network(
                      saved.imageUrl,
                      width: 70,
                      height: 70,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                        width: 70,
                        height: 70,
                        color: Colors.grey[300],
                        child: Icon(
                          Icons.image_not_supported,
                          color: Colors.grey[500],
                        ),
                      ),
                    ),
                  ),
                  // Başlık ve tarih
                  title: Text(
                    saved.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Row(
                      children: [
                        Icon(
                          Icons.access_time,
                          size: 14,
                          color: Colors.grey[500],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(saved.savedAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Sil butonu
                  trailing: IconButton(
                    icon: Icon(
                      Icons.delete_outline,
                      color: Colors.red[400],
                    ),
                    onPressed: () {
                      savedProv.unsaveReel(saved.reelId);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Kayıt kaldırıldı'),
                          duration: Duration(seconds: 2),
                        ),
                      );
                    },
                  ),
                  // Tıklanınca reels'e git
                  onTap: () {
                    _openInReels(context, saved.reelId);
                  },
                ),
              );
            },
          );
        },
      ),
    );
  }

  // Tarih formatı
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 60) {
      return '${diff.inMinutes} dakika önce';
    } else if (diff.inHours < 24) {
      return '${diff.inHours} saat önce';
    } else if (diff.inDays < 7) {
      return '${diff.inDays} gün önce';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  // Reels'te aç
  void _openInReels(BuildContext context, String reelId) {
    final reelsProv = context.read<ReelsProvider>();
    final index = reelsProv.reels.indexWhere((r) => r.id == reelId);

    if (index != -1) {
      // Reel bulundu, index'e git
      reelsProv.setIndex(index);
      
      // Ana sayfaya dön (MainNavigator)
      Navigator.of(context).popUntil((route) => route.isFirst);
      
      // Reels tab'ına geç (index 1)
      // Not: MainNavigator'da tabları kontrol etmek için bir mekanizma gerekebilir
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Haber açılıyor...'),
          duration: Duration(seconds: 1),
        ),
      );
    } else {
      // Reel listede yok
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Haber bulunamadı'),
          backgroundColor: Colors.orange,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  // Tümünü sil dialog
  void _showClearDialog(BuildContext context, SavedReelsProvider savedProv) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('⚠️ Tümünü Sil'),
        content: const Text(
          'Tüm kayıtlı haberleri silmek istediğine emin misin?\n\nBu işlem geri alınamaz.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton(
            onPressed: () {
              savedProv.clearAll();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Tüm kayıtlar silindi'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Sil'),
          ),
        ],
      ),
    );
  }
}