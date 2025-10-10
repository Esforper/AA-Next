import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:visibility_detector/visibility_detector.dart';
import '../models/reading_preferences.dart';
import '../services/reading_analytics_service.dart';
import '../services/reading_preferences_service.dart';
import '../services/api_service.dart';
import 'article_image_viewer.dart';
import 'reading_settings_panel.dart';

/// Profesyonel haber okuma arayüzü
/// Şık tasarım, gelişmiş tipografi ve paragraf arası görseller
class ArticleReaderSheet extends StatefulWidget {
  final String articleId;
  final String title;
  final String body;
  final List<String> imageUrls;
  final String? category;
  final String? publishedDate;
  final int? readingTimeMinutes;
  final VoidCallback onClose;
  final VoidCallback? onBookmark;
  final VoidCallback? onShare;

  const ArticleReaderSheet({
    super.key,
    required this.articleId,
    required this.title,
    required this.body,
    this.imageUrls = const [],
    this.category,
    this.publishedDate,
    this.readingTimeMinutes,
    required this.onClose,
    this.onBookmark,
    this.onShare,
  });

  @override
  State<ArticleReaderSheet> createState() => _ArticleReaderSheetState();
}

class _ArticleReaderSheetState extends State<ArticleReaderSheet> {
  bool _isBookmarked = false;
  double _scrollProgress = 0.0;
  final _prefsService = ReadingPreferencesService.instance;
  ReadingPreferences? _readingPrefs;
  bool _showScrollToTopButton = false;

  // Analytics
  late final ReadingAnalyticsService _analyticsService;
  
  // Scroll tracking
  double _maxScrollDepth = 0.0;
  
  // Share/Save tracking
  bool _sharedFromDetail = false;
  bool _savedFromDetail = false;
  
  // API service
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _loadPreferences();

    // Analitik servisini başlat
    _analyticsService = ReadingAnalyticsService(articleId: widget.articleId);
    _analyticsService.startTracking();
    
    debugPrint('📖 Detail view opened: ${widget.articleId}');
  }

  @override
  void dispose() {
    _analyticsService.stopTracking();
    super.dispose();
  }

  /// Scroll tracking fonksiyonu
  void _onScroll(ScrollController controller) {
    if (!controller.hasClients) return;
    
    final maxScroll = controller.position.maxScrollExtent;
    if (maxScroll == 0) return;
    
    final currentScroll = controller.offset;
    final scrollDepth = (currentScroll / maxScroll).clamp(0.0, 1.0);
    
    if (scrollDepth > _maxScrollDepth) {
      _maxScrollDepth = scrollDepth;
      _analyticsService.updateScrollProgress(_maxScrollDepth);
      
      // Her %10'da bir log
      if ((_maxScrollDepth * 10).floor() > ((_maxScrollDepth - 0.01) * 10).floor()) {
        debugPrint('📊 Scroll depth: ${(_maxScrollDepth * 100).toStringAsFixed(0)}%');
      }
    }
  }

  /// Bookmark handler - tracking ekle
  void _onBookmarkTap() {
    setState(() => _isBookmarked = !_isBookmarked);
    
    if (_isBookmarked) {
      _savedFromDetail = true;
      debugPrint('💾 Saved from detail');
    }
    
    widget.onBookmark?.call();
  }

  /// Share handler - tracking ekle
  void _onShareTap() {
    _sharedFromDetail = true;
    debugPrint('📤 Shared from detail');
    widget.onShare?.call();
  }

  /// Close handler - backend'e gönder
  void _onClose() async {
    _analyticsService.stopTracking();
    
    // Backend'e detail view tracking gönder
    final readDuration = DateTime.now().difference(_analyticsService.startTime);
    
    debugPrint('📖 Detail view closing:');
    debugPrint('  ├─ Article: ${widget.articleId}');
    debugPrint('  ├─ Duration: ${readDuration.inMilliseconds}ms');
    debugPrint('  ├─ Scroll depth: ${(_maxScrollDepth * 100).toStringAsFixed(1)}%');
    debugPrint('  ├─ Shared: $_sharedFromDetail');
    debugPrint('  └─ Saved: $_savedFromDetail');
    
    // Backend'e gönder (async, kullanıcıyı bekletme)
    _apiService.trackDetailView(
      reelId: widget.articleId,
      readDurationMs: readDuration.inMilliseconds,
      scrollDepth: _maxScrollDepth,
      sharedFromDetail: _sharedFromDetail,
      savedFromDetail: _savedFromDetail,
    );
    
    // Modal'ı kapat
    widget.onClose();
  }

  Future<void> _loadPreferences() async {
    final prefs = await _prefsService.loadPreferences();
    if (mounted) {
      setState(() {
        _readingPrefs = prefs;
      });
    }
  }

  void _openSettingsPanel() {
    if (_readingPrefs == null) return;
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => ReadingSettingsPanel(
        initialPreferences: _readingPrefs!,
        onChanged: (newPrefs) {
          setState(() {
            _readingPrefs = newPrefs;
          });
        },
      ),
    );
  }

  void _openImageViewer(String imageUrl, String heroTag) {
    Navigator.of(context).push(
      PageRouteBuilder(
        opaque: false,
        barrierDismissible: true,
        pageBuilder: (context, _, __) {
          return ArticleImageViewer(
            imageUrl: imageUrl,
            heroTag: heroTag,
          );
        },
      ),
    );
  }

  TextStyle _getTitleStyle() {
    if (_readingPrefs == null) {
      return const TextStyle(
        fontSize: 26,
        fontWeight: FontWeight.w800,
        height: 1.3,
        letterSpacing: -0.5,
        color: Color(0xFF1A1A1A),
      );
    }
    
    double fontSize;
    switch (_readingPrefs!.fontSize) {
      case AppFontSize.small:
        fontSize = 22;
        break;
      case AppFontSize.medium:
        fontSize = 26;
        break;
      case AppFontSize.large:
        fontSize = 30;
        break;
    }
    
    String? fontFamily;
    switch (_readingPrefs!.fontFamily) {
      case AppFontFamily.serif:
        fontFamily = 'Georgia';
        break;
      case AppFontFamily.sansSerif:
        fontFamily = 'Roboto';
        break;
      case AppFontFamily.system:
        fontFamily = null;
        break;
    }
    
    return TextStyle(
      fontSize: fontSize,
      fontFamily: fontFamily,
      fontWeight: FontWeight.w800,
      height: 1.3,
      letterSpacing: -0.5,
      color: const Color(0xFF1A1A1A),
    );
  }

  TextStyle _getBodyStyle() {
    if (_readingPrefs == null) {
      return const TextStyle(
        fontSize: 17,
        height: 1.7,
        color: Color(0xFF2D2D2D),
        letterSpacing: 0.2,
      );
    }
    
    double fontSize;
    switch (_readingPrefs!.fontSize) {
      case AppFontSize.small:
        fontSize = 15;
        break;
      case AppFontSize.medium:
        fontSize = 17;
        break;
      case AppFontSize.large:
        fontSize = 19;
        break;
    }
    
    String? fontFamily;
    switch (_readingPrefs!.fontFamily) {
      case AppFontFamily.serif:
        fontFamily = 'Georgia';
        break;
      case AppFontFamily.sansSerif:
        fontFamily = 'Roboto';
        break;
      case AppFontFamily.system:
        fontFamily = null;
        break;
    }
    
    double height;
    switch (_readingPrefs!.lineHeight) {
      case AppLineHeight.compact:
        height = 1.5;
        break;
      case AppLineHeight.normal:
        height = 1.7;
        break;
      case AppLineHeight.relaxed:
        height = 1.9;
        break;
    }
    
    return TextStyle(
      fontSize: fontSize,
      fontFamily: fontFamily,
      height: height,
      color: const Color(0xFF2D2D2D),
      letterSpacing: 0.2,
    );
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.25,
      minChildSize: 0.18,
      maxChildSize: 0.96,
      snap: true,
      snapSizes: const [0.25, 0.96],
      builder: (context, scrollController) {
        // ✅ Scroll listener'ı ekle (bir kere)
        if (!scrollController.hasListeners) {
          scrollController.addListener(() => _onScroll(scrollController));
        }
        
        return NotificationListener<ScrollNotification>(
          onNotification: (notification) {
            if (notification is ScrollUpdateNotification) {
              final maxScroll = scrollController.position.maxScrollExtent;
              final currentScroll = scrollController.position.pixels;
              final progress = maxScroll > 0.0 ? currentScroll / maxScroll : 0.0;
              
              setState(() {
                _scrollProgress = progress;
              });

              // Scroll to top button visibility
              if (currentScroll > 400 && !_showScrollToTopButton) {
                setState(() {
                  _showScrollToTopButton = true;
                });
              } else if (currentScroll <= 400 && _showScrollToTopButton) {
                setState(() {
                  _showScrollToTopButton = false;
                });
              }
            }
            return false;
          },
          child: Stack(
            children: [
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(24),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.15),
                      blurRadius: 20,
                      offset: const Offset(0, -5),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(24),
                  ),
                  child: Column(
                    children: [
                      // Progress indicator
                      if (_scrollProgress > 0.05)
                        LinearProgressIndicator(
                          value: _scrollProgress,
                          backgroundColor: Colors.grey[200],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Theme.of(context).primaryColor,
                          ),
                          minHeight: 3,
                        ),
                      
                      // Handle
                      Padding(
                        padding: const EdgeInsets.only(top: 12, bottom: 8),
                        child: Container(
                          width: 48,
                          height: 5,
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                      
                      // Content
                      Expanded(
                        child: CustomScrollView(
                          controller: scrollController,
                          physics: const BouncingScrollPhysics(),
                          slivers: [
                            // Hero image
                            if (widget.imageUrls.isNotEmpty)
                              SliverAppBar(
                                expandedHeight: 220.0,
                                backgroundColor: Colors.white,
                                elevation: 0,
                                stretch: true,
                                automaticallyImplyLeading: false,
                                flexibleSpace: FlexibleSpaceBar(
                                  stretchModes: const [
                                    StretchMode.zoomBackground,
                                  ],
                                  background: _buildHeroImage(),
                                ),
                              ),
                            
                            // Header
                            SliverToBoxAdapter(child: _buildHeader()),
                            
                            // Metadata
                            SliverToBoxAdapter(child: _buildMetadata()),
                            
                            // Title
                            SliverToBoxAdapter(child: _buildTitle()),
                            
                            // Body
                            ..._buildDynamicBodySlivers(),
                            
                            // Bottom spacing
                            const SliverToBoxAdapter(
                              child: SizedBox(height: 80),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              // Scroll to top button
              _buildScrollToTopButton(scrollController),
            ],
          ),
        );
      },
    );
  }

  Widget _buildScrollToTopButton(ScrollController scrollController) {
    return Positioned(
      bottom: 20,
      right: 20,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 300),
        opacity: _showScrollToTopButton ? 1.0 : 0.0,
        child: IgnorePointer(
          ignoring: !_showScrollToTopButton,
          child: FloatingActionButton(
            onPressed: () {
              scrollController.animateTo(
                0,
                duration: const Duration(milliseconds: 500),
                curve: Curves.easeInOut,
              );
            },
            mini: true,
            backgroundColor: Theme.of(context).primaryColor,
            child: const Icon(Icons.arrow_upward, color: Colors.white),
          ),
        ),
      ),
    );
  }

  List<Widget> _buildDynamicBodySlivers() {
    if (widget.body.isEmpty) {
      return [const SliverToBoxAdapter(child: SizedBox.shrink())];
    }
    
    final List<Widget> slivers = [];
    final paragraphs = widget.body.split(RegExp(r'\n\s*\n'));
    final contentImages = widget.imageUrls.length > 1
        ? widget.imageUrls.sublist(1)
        : <String>[];
    
    int imageIndex = 0;
    const imageInsertInterval = 2;
    
    for (int i = 0; i < paragraphs.length; i++) {
      final paragraphText = paragraphs[i].trim();
      
      if (paragraphText.isNotEmpty) {
        slivers.add(
          SliverToBoxAdapter(
            child: _FadeInOnVisible(
              key: ValueKey('paragraph_$i'),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 8.0,
                ),
                child: Text(
                  paragraphText,
                  style: _getBodyStyle(),
                ),
              ),
            ),
          ),
        );
      }
      
      // Insert image after every N paragraphs
      if ((i + 1) % imageInsertInterval == 0 &&
          imageIndex < contentImages.length) {
        final imageUrl = contentImages[imageIndex];
        final heroTag = 'article_image_${imageUrl.hashCode}_$imageIndex';
        
        slivers.add(
          SliverToBoxAdapter(
            child: _FadeInOnVisible(
              key: ValueKey(heroTag),
              child: _buildInContentImage(imageUrl, heroTag),
            ),
          ),
        );
        
        imageIndex++;
      }
    }
    
    return slivers;
  }

  Widget _buildInContentImage(String imageUrl, String heroTag) {
    return GestureDetector(
      onTap: () => _openImageViewer(imageUrl, heroTag),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Hero(
          tag: heroTag,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                height: 220,
                color: Colors.grey[200],
                child: const Center(child: CircularProgressIndicator()),
              ),
              errorWidget: (context, url, error) => Container(
                height: 220,
                color: Colors.grey[200],
                child: Icon(
                  Icons.image_not_supported_outlined,
                  color: Colors.grey[400],
                  size: 50,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroImage() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.network(
              widget.imageUrls.first,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => Container(
                color: Colors.grey[200],
                child: Icon(
                  Icons.image_outlined,
                  size: 64,
                  color: Colors.grey[400],
                ),
              ),
            ),
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      Colors.black.withOpacity(0.1),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          if (widget.category != null)
            _buildCategoryBadge()
          else
            const SizedBox(width: 40),
          Row(
            children: [
              // Settings button
              IconButton(
                onPressed: _readingPrefs == null ? null : _openSettingsPanel,
                icon: Icon(
                  Icons.text_fields_outlined,
                  color: Colors.grey[600],
                ),
                tooltip: 'Okuma Ayarları',
              ),
              
              // ✅ Bookmark button - YENİ HANDLER
              IconButton(
                onPressed: _onBookmarkTap,
                icon: Icon(
                  _isBookmarked ? Icons.bookmark : Icons.bookmark_border,
                  color: _isBookmarked ? Colors.amber[700] : Colors.grey[600],
                ),
                tooltip: 'Kaydet',
              ),
              
              // ✅ Share button - YENİ HANDLER
              if (widget.onShare != null)
                IconButton(
                  onPressed: _onShareTap,
                  icon: Icon(
                    Icons.share_outlined,
                    color: Colors.grey[600],
                  ),
                  tooltip: 'Paylaş',
                ),
              
              // ✅ Close button - YENİ HANDLER
              IconButton(
                onPressed: _onClose,
                icon: Icon(
                  Icons.close,
                  color: Colors.grey[600],
                ),
                tooltip: 'Kapat',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTitle() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
      child: Text(
        widget.title,
        style: _getTitleStyle(),
      ),
    );
  }

  Widget _buildCategoryBadge() {
    final categoryColors = {
      'ekonomi': Colors.green,
      'spor': Colors.orange,
      'teknoloji': Colors.blue,
      'politika': Colors.red,
      'kultur': Colors.purple,
      'saglik': Colors.teal,
    };
    
    final color = categoryColors[widget.category?.toLowerCase()] ?? Colors.grey;
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        widget.category!.toUpperCase(),
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildMetadata() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          if (widget.publishedDate != null) ...[
            Icon(
              Icons.access_time_outlined,
              size: 14,
              color: Colors.grey[500],
            ),
            const SizedBox(width: 4),
            Text(
              widget.publishedDate!,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
          if (widget.publishedDate != null &&
              widget.readingTimeMinutes != null) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Container(
                width: 3,
                height: 3,
                decoration: BoxDecoration(
                  color: Colors.grey[400],
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ],
          if (widget.readingTimeMinutes != null) ...[
            Icon(
              Icons.menu_book_outlined,
              size: 14,
              color: Colors.grey[500],
            ),
            const SizedBox(width: 4),
            Text(
              '${widget.readingTimeMinutes} dk okuma',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// Fade-in animation widget
class _FadeInOnVisible extends StatefulWidget {
  final Widget child;

  const _FadeInOnVisible({
    required Key key,
    required this.child,
  }) : super(key: key);

  @override
  _FadeInOnVisibleState createState() => _FadeInOnVisibleState();
}

class _FadeInOnVisibleState extends State<_FadeInOnVisible>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  bool _hasAnimated = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeIn,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: widget.key!,
      onVisibilityChanged: (visibilityInfo) {
        if (visibilityInfo.visibleFraction > 0.1 && !_hasAnimated) {
          setState(() {
            _hasAnimated = true;
          });
          _controller.forward();
        }
      },
      child: FadeTransition(
        opacity: _animation,
        child: widget.child,
      ),
    );
  }
}