import 'package:flutter/material.dart';

/// Yukarı çekince açılan okuma barı (sheet).
class ArticleOverlay extends StatelessWidget {
  final String title;
  final String body;
  final VoidCallback onClose;

  const ArticleOverlay({
    super.key,
    required this.title,
    required this.body,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.22,
      minChildSize: 0.15,
      maxChildSize: 0.95,
      snap: true,
      builder: (context, scrollCtrl) {
        return Material(
          elevation: 12,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          child: SafeArea(
            top: false,
            child: Column(
              children: [
                const SizedBox(height: 8),
                Container(
                    width: 44,
                    height: 5,
                    decoration: BoxDecoration(
                        color: Colors.black26,
                        borderRadius: BorderRadius.circular(12))),
                ListTile(
                  title: Text(title,
                      style: const TextStyle(fontWeight: FontWeight.w800)),
                  trailing: IconButton(
                      icon: const Icon(Icons.close), onPressed: onClose),
                ),
                const Divider(height: 0),
                Expanded(
                  child: SingleChildScrollView(
                    controller: scrollCtrl,
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
                    child: Text(body, style: const TextStyle(height: 1.35)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
