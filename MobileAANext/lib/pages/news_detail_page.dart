import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../models/reel_model.dart';

class NewsDetailPage extends StatefulWidget {
  const NewsDetailPage({super.key, required this.reel});
  final Reel reel;

  @override
  State<NewsDetailPage> createState() => _NewsDetailPageState();
}

class _NewsDetailPageState extends State<NewsDetailPage> {
  late final WebViewController _web;

  @override
  void initState() {
    super.initState();
    _web = WebViewController()..setJavaScriptMode(JavaScriptMode.unrestricted);

    if (widget.reel.url.isNotEmpty) {
      _web.loadRequest(Uri.parse(widget.reel.url));
    }
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.reel;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Haber Detayı'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (r.category.isNotEmpty)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white10,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(r.category.toUpperCase(),
                        style:
                            const TextStyle(letterSpacing: 1.2, fontSize: 12)),
                  ),
                const SizedBox(height: 10),
                Text(r.title,
                    style: const TextStyle(
                        fontSize: 22, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                // Seslendirilen kısım kalın
                Text(r.summary,
                    style: const TextStyle(
                        fontSize: 16, fontWeight: FontWeight.w700)),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: r.url.isNotEmpty
                ? WebViewWidget(controller: _web)
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                        'Bu haber için URL bulunamadı.\n\nÖzet:\n${r.summary}',
                        style: const TextStyle(fontSize: 16)),
                  ),
          ),
        ],
      ),
    );
  }
}
