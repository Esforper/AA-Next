// lib/web_platform/widgets/web_article_detail_panel.dart
// SAĞDAN AÇILAN DETAY PANELİ (WEB)
// Slide-in animation + backdrop + tam içerik

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../models/reel_model.dart';

class WebArticleDetailPanel extends StatefulWidget {
  final Reel reel;
  final VoidCallback onClose;

  const WebArticleDetailPanel({
    super.key,
    required this.reel,
    required this.onClose,
  });

  @override
  State<WebArticleDetailPanel> createState() => _WebArticleDetailPanelState();
}

class _WebArticleDetailPanelState extends State<WebArticleDetailPanel>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    
    // Animasyon controller
    _controller = AnimationController(
      duration: const Duration(milliseconds: 350),
      vsync: this,
    );

    // Slide-in from right
    _slideAnimation = Tween<Offset>(
      begin: const Offset(1.0, 0.0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    // Fade-in backdrop
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    ));

    // Animasyonu başlat
    _controller.forward();

    print('📰 Article detail panel opened: ${widget.reel.title}');
  }

  Future<void> _closePanel() async {
    print('❌ Closing article detail panel');
    await _controller.reverse();
    widget.onClose();
  }

  Future<void> _openSourceUrl() async {
    final url = widget.reel.url;
    if (url.isEmpty) {
      print('⚠️ No source URL available');
      return;
    }

    print('🔗 Opening source URL: $url');
    
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      print('❌ Cannot launch URL: $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Backdrop (blur + opacity)
        FadeTransition(
          opacity: _fadeAnimation,
          child: GestureDetector(
            onTap: _closePanel,
            child: Container(
              color: Colors.black.withOpacity(0.5),
            ),
          ),
        ),

        // Panel (slide from right)
        Align(
          alignment: Alignment.centerRight,
          child: SlideTransition(
            position: _slideAnimation,
            child: _buildPanel(),
          ),
        ),
      ],
    );
  }

  Widget _buildPanel() {
    return Container(
      width: MediaQuery.of(context).size.width * 0.35, // 35% genişlik
      height: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 30,
            offset: const Offset(-5, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          _buildHeader(),

          // Content
          Expanded(
            child: _buildContent(),
          ),

          // Footer (Kaynak link butonu)
          _buildFooter(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF003D82),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Başlık
          const Expanded(
            child: Text(
              'Haber Detayı',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),

          // Kapat butonu
          IconButton(
            onPressed: _closePanel,
            icon: const Icon(Icons.close, color: Colors.white),
            tooltip: 'Kapat (ESC)',
            iconSize: 28,
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Kategori badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF003D82).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              widget.reel.category.toUpperCase(),
              style: const TextStyle(
                color: Color(0xFF003D82),
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.5,
              ),
            ),
          ),

          const SizedBox(height: 20),

          // Başlık
          Text(
            widget.reel.title,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
              height: 1.3,
            ),
          ),

          const SizedBox(height: 16),

          // Tarih ve metadata
          Row(
            children: [
              Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 6),
              Text(
                _formatDate(widget.reel.publishedAt),
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 14,
                ),
              ),
              const SizedBox(width: 16)
              // Icon(Icons.remove_red_eye_outlined, size: 16, color: Colors.grey[600]),
              // const SizedBox(width: 6),
              // Text(
              //   // '${widget.reel.viewCount} görüntülenme',
              //   style: TextStyle(
              //     color: Colors.grey[600],
              //     fontSize: 14,
              //   ),
              // ),
            ],
          ),

          const SizedBox(height: 24),

          // Divider
          Divider(color: Colors.grey[300], thickness: 1),

          const SizedBox(height: 24),

          // Özet (bold)
          const Text(
            'Özet',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1F2937),
            ),
          ),

          const SizedBox(height: 12),

          Text(
            widget.reel.summary,
            style: TextStyle(
              fontSize: 15,
              color: Colors.grey[800],
              height: 1.6,
            ),
          ),

          const SizedBox(height: 32),

          // Tam metin (eğer varsa)
          if (widget.reel.fullText != null && widget.reel.fullText!.isNotEmpty) ...[
            const Text(
              'Tam Metin',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),

            const SizedBox(height: 12),

            Text(
              widget.reel.fullText!,
              style: TextStyle(
                fontSize: 15,
                color: Colors.grey[800],
                height: 1.6,
              ),
            ),

            const SizedBox(height: 32),
          ],

          // Etiketler (varsa)
          if (widget.reel.newsData.keywords.isNotEmpty) ...[
            const Text(
              'Etiketler',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1F2937),
              ),
            ),

            const SizedBox(height: 12),

            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: widget.reel.newsData.keywords.map((tag) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '#$tag',
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontSize: 13,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        border: Border(
          top: BorderSide(color: Colors.grey[300]!, width: 1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Kaynak link butonu
          ElevatedButton.icon(
            onPressed: _openSourceUrl,
            icon: const Icon(Icons.open_in_new),
            label: const Text('Orijinal Kaynağı Aç'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF003D82),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: 0,
            ),
          ),

          const SizedBox(height: 12),

          // Bilgi notu
          Row(
            children: [
              Icon(Icons.info_outline, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Tam haberi kaynak sitesinde okuyabilirsiniz',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

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
      return '${date.day}.${date.month}.${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    }
  }

  @override
  void dispose() {
    print('🗑️ Article detail panel disposed');
    _controller.dispose();
    super.dispose();
  }
}