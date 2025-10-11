// lib/pages/reels_feed_page.dart
// ESKİ ARAYÜZ + YENİ İNFİNİTE SCROLL
import '../../services/audio_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import '../../shared/widgets/article_reader_sheet.dart'; 
import '../../providers/reels_provider.dart';
import '../../providers/saved_reels_provider.dart';
import '../../providers/gamification_provider.dart';
import '../../models/reel_model.dart';
import '../../shared/widgets/image_carousel.dart';
import '../../shared/widgets/emoji_panel.dart';
import '../../shared/widgets/read_handle.dart';
import '../../shared/widgets/gamification/reels_xp_overlay.dart';
import '../../shared/widgets/gamification/floating_xp.dart';
import '../../shared/widgets/subtitle_widget.dart';
import '../../services/reel_tracker_service.dart';
import '../../core/constants/emoji_constants.dart';
class ReelsFeedPage extends StatefulWidget {
  const ReelsFeedPage({super.key});

  @override
  State<ReelsFeedPage> createState() => _ReelsFeedPageState();
}

class _ReelsFeedPageState extends State<ReelsFeedPage> with WidgetsBindingObserver {
  final List<FloatingXPData> _floatingXPList = [];
  DateTime? _reelStartTime;
  bool _hasEarnedWatchXP = false;
  String? _currentReelId;
  bool _subtitlesEnabled = true;
  
  // 🆕 PageController
  late PageController _pageController;
  bool _isInitialized = false;

  ReelTrackerService? _currentTracker;

  // ✅ YENİ: Emoji panel state
  bool _showEmojis = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _pageController = PageController();
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ReelsProvider>();
      if (provider.reels.isNotEmpty && !_isInitialized) {
        _isInitialized = true;
        _startReelTracking(provider.current!);
        final audioService = context.read<AudioService>();
        final firstReel = provider.current!;
        _startReelTracking(firstReel);
        if (firstReel.audioUrl.isNotEmpty) {
          audioService.play(firstReel.audioUrl, firstReel.id);
        }
      }
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final audioService = context.read<AudioService>();
    if (state == AppLifecycleState.paused) {
      if (!audioService.isPlaying) {
        audioService.resume();
      }
    }
  }

void _startReelTracking(Reel reel) {
  debugPrint('');
  debugPrint('▶️ [START TRACKING]');
  
  // Önceki tracker'ı durdur (varsa)
  _stopCurrentTracker();
  
  // Yeni tracker oluştur
  _currentTracker = ReelTrackerService(
    reelId: reel.id,
    category: reel.category,
  );
  _currentTracker!.start();
  
  // Gamification için RESET
  _reelStartTime = DateTime.now();
  _hasEarnedWatchXP = false;
  _currentReelId = reel.id;
  
  debugPrint('   ├─ Reel ID: ${reel.id}');
  debugPrint('   ├─ Start Time: $_reelStartTime');
  debugPrint('   ├─ _hasEarnedWatchXP: $_hasEarnedWatchXP');
  debugPrint('   └─ Tracker: STARTED');
  debugPrint('');
}




    /// ✅ YENİ: Mevcut tracker'ı durdur
  Future<void> _stopCurrentTracker() async {
    if (_currentTracker == null || _currentTracker!.isStopped) return;
    
    try {
      final audioService = context.read<AudioService>();
      final completed = audioService.isCompleted();
      
      debugPrint('🛑 Stopping tracker...');
      debugPrint('  ├─ Reel: ${_currentTracker!.reelId}');
      debugPrint('  ├─ Duration: ${_currentTracker!.currentDurationMs}ms');
      debugPrint('  ├─ Completed: $completed');
      debugPrint('  └─ Pause count: ${audioService.pauseCountForCurrentReel}');
      
      await _currentTracker!.stop(completed: completed);
      
    } catch (e) {
      debugPrint('❌ Error stopping tracker: $e');
    }
  }

  /// ✅ GÜNCELLEME: Page değişimi
/// ✅ GÜNCELLEME: Page değişimi + DETAYLI DEBUG
void _onPageChanged(int index) async {
  debugPrint('');
  debugPrint('═══════════════════════════════════════════');
  debugPrint('🔄 [PAGE CHANGED] Index: $index');
  debugPrint('═══════════════════════════════════════════');
  
  final reelsProvider = context.read<ReelsProvider>();
  final audioService = context.read<AudioService>();
  
  // ✅ Önceki tracker'ı durdur ve backend'e gönder
  debugPrint('🛑 [STEP 1] Stopping current tracker...');
  await _stopCurrentTracker();
  
  // ✅ XP KONTROLÜ - DETAYLI DEBUG
  debugPrint('');
  debugPrint('🎮 [STEP 2] XP Check:');
  debugPrint('   ├─ _hasEarnedWatchXP: $_hasEarnedWatchXP');
  debugPrint('   ├─ _reelStartTime: $_reelStartTime');
  debugPrint('   └─ _currentReelId: $_currentReelId');
  
  if (!_hasEarnedWatchXP && _reelStartTime != null && _currentReelId != null) {
    final duration = DateTime.now().difference(_reelStartTime!);
    final durationSeconds = duration.inSeconds;
    
    debugPrint('   ├─ Duration: ${durationSeconds}s');
    
    if (durationSeconds >= 3) {
      debugPrint('   ✅ AWARDING XP!');
      
      final gamificationProvider = context.read<GamificationProvider>();
      
      // ✅ XP öncesi state
      debugPrint('   ├─ Before XP:');
      debugPrint('   │  ├─ Total XP: ${gamificationProvider.state.totalXP}');
      debugPrint('   │  ├─ Level: ${gamificationProvider.state.currentLevel}');
      debugPrint('   │  └─ Today XP: ${gamificationProvider.state.xpEarnedToday}');
      
      // ✅ Backend'e XP isteği gönder
      gamificationProvider.onReelWatched(_currentReelId!);
      
      // ✅ XP sonrası state
      debugPrint('   ├─ After XP:');
      debugPrint('   │  ├─ Total XP: ${gamificationProvider.state.totalXP}');
      debugPrint('   │  ├─ Level: ${gamificationProvider.state.currentLevel}');
      debugPrint('   │  └─ Today XP: ${gamificationProvider.state.xpEarnedToday}');
      
      _hasEarnedWatchXP = true;
      debugPrint('   └─ Flag set: _hasEarnedWatchXP = true');
    } else {
      debugPrint('   ⏭️ SKIPPED - Duration too short (${durationSeconds}s < 3s)');
    }
  } else {
    debugPrint('   ⏭️ SKIPPED - Conditions not met:');
    if (_hasEarnedWatchXP) debugPrint('      └─ Already earned XP for this reel');
    if (_reelStartTime == null) debugPrint('      └─ No start time');
    if (_currentReelId == null) debugPrint('      └─ No reel ID');
  }
  
  // ✅ Index güncelle
  debugPrint('');
  debugPrint('📍 [STEP 3] Updating index to: $index');
  reelsProvider.setIndex(index);
  
  // ✅ Emoji panelini kapat
  if (_showEmojis) {
    debugPrint('😊 [STEP 4] Closing emoji panel');
    setState(() => _showEmojis = false);
  }
  
  // ✅ Yeni reel'in tracking'ini başlat
  if (reelsProvider.current != null) {
    final newReel = reelsProvider.current!;
    
    debugPrint('');
    debugPrint('🎬 [STEP 5] Starting new reel:');
    debugPrint('   ├─ ID: ${newReel.id}');
    // ✅ FIX: Title kısaysa hata vermesin
    final titlePreview = newReel.title.length > 30 
        ? '${newReel.title.substring(0, 30)}...' 
        : newReel.title;
    debugPrint('   ├─ Title: $titlePreview');
    debugPrint('   └─ Audio: ${newReel.audioUrl.isNotEmpty ? "✅" : "❌"}');
    
    _startReelTracking(newReel);
    
    // ✅ Yeni reel'in sesini çal
    if (newReel.audioUrl.isNotEmpty) {
      debugPrint('🎵 Playing audio...');
      audioService.play(newReel.audioUrl, newReel.id);
    }
  }
  
  // ✅ Infinite scroll check
  if (index >= reelsProvider.reels.length - 3 && 
      !reelsProvider.isLoadingMore && 
      reelsProvider.hasMore) {
    debugPrint('📜 [STEP 6] Loading more reels...');
    reelsProvider.loadMore();
  }
  
  debugPrint('═══════════════════════════════════════════');
  debugPrint('');
}

  /// ✅ YENİ: Emoji seçildiğinde
  void _onEmojiSelected(String emoji, Reel reel) {
    // 1. Tracker'a kaydet
    if (_currentTracker != null) {
      _currentTracker!.onEmoji(emoji);
      debugPrint('❤️ Emoji tracked: $emoji for ${reel.id}');
    }
    
    // 2. Gamification
    final gamificationProvider = context.read<GamificationProvider>();
    final success = gamificationProvider.onEmojiGiven(reel.id);
    
    if (success) {
      _showFloatingXP(5, 'emoji_given');
      
      if (mounted) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(
            SnackBar(
              content: Text('Tepkiniz gönderildi: $emoji +5 XP'),
              duration: const Duration(seconds: 2),
              behavior: SnackBarBehavior.floating,
              backgroundColor: Colors.pink[600],
            ),
          );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context)
          ..hideCurrentSnackBar()
          ..showSnackBar(
            const SnackBar(
              content: Text('Bu habere zaten emoji attın!'),
              duration: Duration(seconds: 2),
              behavior: SnackBarBehavior.floating,
            ),
          );
      }
    }
    
    // 3. Panel'i kapat
    setState(() => _showEmojis = false);
  }
Future<void> _onShareTapped(Reel reel) async {
  // 1. Tracker'a kaydet
  if (_currentTracker != null) {
    _currentTracker!.onShare();
    debugPrint('📤 Share tracked for ${reel.id}');
  }
  
  // 2. Gamification
  final gamificationProvider = context.read<GamificationProvider>();
  
  if (gamificationProvider.hasShareGiven(reel.id)) {
    if (mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Bu haberi zaten paylaştın!'),
            duration: Duration(seconds: 2),
          ),
        );
    }
    return;
  }
  
 // 3. ✅ Share.share() - result yok, void döndürüyor
  try {
    await Share.share(
      '${reel.title}\n\n${reel.summary}\n\nAA Haber uygulamasından paylaşıldı.',
      subject: reel.title,
    );
    
    // ✅ Share.share() başarılı olduğunu varsay (void döndüğü için)
    // Kullanıcı share dialog'u açtıysa başarılıdır
    gamificationProvider.onShareGiven(reel.id);
    _showFloatingXP(10, 'share_given');
    
    if (mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Haber paylaşıldı! +10 XP'),
            duration: Duration(seconds: 2),
            backgroundColor: Colors.green,
          ),
        );
    }
  } catch (e) {
    debugPrint('❌ Share error: $e');
    if (mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Paylaşım başarısız oldu'),
            duration: Duration(seconds: 2),
            backgroundColor: Colors.red,
          ),
        );
    }
  }
}


/// ✅ YENİ: Kaydetme yapıldığında çağrılır
void _onSaveTapped(Reel reel) {
  // 1. Tracker'a kaydet
  if (_currentTracker != null) {
    _currentTracker!.onSave();
    debugPrint('💾 Save tracked for ${reel.id}');
  }
  
  // 2. Saved reels provider'a ekle/çıkar
  final savedReelsProvider = context.read<SavedReelsProvider>();
  final isSaved = savedReelsProvider.isSaved(reel.id);
  
  if (isSaved) {
    // Kaydedilmişten çıkar
    savedReelsProvider.unsaveReel(reel.id);
    
    if (mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Kaydedilenlerden çıkarıldı'),
            duration: Duration(seconds: 2),
          ),
        );
    }
  } else {
    // Kaydet
    savedReelsProvider.saveReel(
      reelId: reel.id,
      title: reel.title,
      imageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls.first : '',
      content: reel.fullContent.join('\n\n'),
    );
    
    if (mounted) {
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(
            content: Text('Kaydedilenlere eklendi 💾'),
            duration: Duration(seconds: 2),
            backgroundColor: Colors.blue,
          ),
        );
    }
  }
}


void _showFloatingXP(int amount, String source) {
  print('🎯 DEBUG: _showFloatingXP çağrıldı - amount: $amount, source: $source');
  
  // State'e floating XP ekle
  setState(() {
    _floatingXPList.add(FloatingXPData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      amount: amount,
      source: source,
      position: Offset(
        MediaQuery.of(context).size.width / 2 - 60,
        MediaQuery.of(context).size.height / 2 - 100,
      ),
    ));
  });
  
  print('✅ DEBUG: Floating XP eklendi, liste boyutu: ${_floatingXPList.length}');
  
  // 2 saniye sonra listeden çıkar
  Future.delayed(const Duration(milliseconds: 2000), () {
    if (mounted) {
      setState(() {
        _floatingXPList.removeWhere((xp) => 
          xp.id == _floatingXPList.first.id
        );
      });
      print('🗑️ DEBUG: Floating XP silindi, liste boyutu: ${_floatingXPList.length}');
    }
  });
}

@override
Widget build(BuildContext context) {
  final provider = context.watch<ReelsProvider>();

  if (provider.status == FeedStatus.initial) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final p = context.read<ReelsProvider>();
      if (p.status == FeedStatus.initial) {
        p.loadReels();
      }
    });
  }

  return Scaffold(
    backgroundColor: const Color(0xFF003D82),
    extendBodyBehindAppBar: true,
    appBar: AppBar(
      backgroundColor: Colors.transparent,
      elevation: 0,
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // AA Logosu
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.15),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: const Text(
              'AA',
              style: TextStyle(
                color: Color(0xFF003D82),
                fontSize: 16,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Başlık
          const Text(
            'Reels',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: Icon(
            _subtitlesEnabled ? Icons.closed_caption : Icons.closed_caption_disabled,
            color: Colors.white,
          ),
          onPressed: () => setState(() => _subtitlesEnabled = !_subtitlesEnabled),
          tooltip: _subtitlesEnabled ? 'Alt yazıları gizle' : 'Alt yazıları göster',
        ),
      ],
    ),
    // ✅ BODY - STACK İLE OVERLAY EKLENDI
    body: Stack(
  children: [
    _buildBody(context, provider),

    // Üst XP overlay (level, node, progress)
    const Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(child: ReelsXPOverlay()),
    ),
    
    // 🆕 Floating XP animasyonları
    ..._floatingXPList.map((xpData) => 
      FloatingXP(
        key: ValueKey(xpData.id),
        xpAmount: xpData.amount,
        startPosition: xpData.position,
        source: xpData.source,
        onComplete: () {
          print('🎬 DEBUG: FloatingXP animasyonu tamamlandı: ${xpData.id}');
        },
      )
    ).toList(),
  ],
),


  );
}

/// ✅ YENİ METOD: PageView'i ayrı metoda çıkar
Widget _buildReelsPageView(ReelsProvider provider) {
  if (provider.status == FeedStatus.loading) {
    return const Center(
      child: CircularProgressIndicator(color: Colors.white),
    );
  }

  if (provider.status == FeedStatus.error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.white, size: 64),
          const SizedBox(height: 16),
          const Text(
            'Bir hata oluştu',  // ✅ Sabit mesaj
            style: TextStyle(color: Colors.white, fontSize: 16),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => provider.loadReels(),
            icon: const Icon(Icons.refresh),
            label: const Text('Tekrar Dene'),
          ),
        ],
      ),
    );
  }

  if (provider.reels.isEmpty) {
    return const Center(
      child: Text(
        'Henüz içerik yok',
        style: TextStyle(color: Colors.white, fontSize: 16),
      ),
    );
  }

  return PageView.builder(
    controller: _pageController,
    scrollDirection: Axis.vertical,
    onPageChanged: _onPageChanged,
    itemCount: provider.reels.length,
    itemBuilder: (context, index) {
      final reel = provider.reels[index];
      // ✅ Zaten var olan _buildBody metodunu kullan
      return _buildReelContent(reel, index);
    },
  );
}


/// ✅ Tek bir reel'in içeriği
/// ✅ Tek bir reel'in içeriği
Widget _buildReelContent(Reel reel, int index) {
  final audioService = context.watch<AudioService>();
  
  return GestureDetector(
    onTap: () {
      if (_showEmojis) {
        setState(() => _showEmojis = false);
      }
    },
    child: Stack(
      children: [
        // Arka plan görsel
        ImageCarousel(urls: reel.imageUrls),  // ✅ imageUrls → urls
        
        // Gradient overlay
        Positioned.fill(
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withOpacity(0.7),
                ],
              ),
            ),
          ),
        ),
        
        // Alt yazı (subtitle)
        if (_subtitlesEnabled && reel.subtitles != null)
          Positioned(
            bottom: 120,
            left: 0,
            right: 0,
            child: SubtitleWidget(
              subtitles: reel.subtitles!,
              currentPosition: audioService.position,
              isVisible: _subtitlesEnabled,
            ),
          ),
        
        // İçerik burada devam eder...
      ],
    ),
  );
}

// reels_feed_page.dart içine ekle
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




  Widget _buildBody(BuildContext context, ReelsProvider provider) {
    switch (provider.status) {
      case FeedStatus.initial:
      case FeedStatus.loading:
        return const Center(child: CircularProgressIndicator());

      case FeedStatus.error:
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text('Yükleme hatası'),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => context.read<ReelsProvider>().loadReels(),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        );

      case FeedStatus.loaded:
      case FeedStatus.loadingMore:
        final reels = provider.reels;
        if (reels.isEmpty) {
          return const Center(child: Text('Gösterilecek içerik yok.'));
        }

        return RefreshIndicator(
          onRefresh: () => provider.refresh(),
          child: Stack(
            children: [
              PageView.builder(
                controller: _pageController,
                scrollDirection: Axis.vertical,
                onPageChanged: _onPageChanged,
                itemCount: reels.length,
                itemBuilder: (context, index) {
                  final reel = reels[index];
                  return _buildReelItem(reel);
                },
              ),

              // 🆕 Loading indicator
              if (provider.status == FeedStatus.loadingMore)
                Positioned(
                  bottom: 80,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                          SizedBox(width: 8),
                          Text('Daha fazla yükleniyor...', style: TextStyle(color: Colors.white, fontSize: 12)),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
    }
  }

  // ✅ ESKİ TASARIM KORUNDU
Widget _buildReelItem(Reel reel) {
  return Stack(
    fit: StackFit.expand,
    children: [
      // ✅ ARKA PLAN - AA Mavi
      Positioned.fill(
        child: Container(
          color: const Color(0xFF003D82),
        ),
      ),

      // ✅ GÖRSEL - Daha büyük, karesel, aşağı doğru genişledi
      Positioned.fill(
        top: 90,
        bottom: 200, // 240 → 200 (daha aşağı)
        child: Center(
          child: AspectRatio(
            aspectRatio: 4 / 3, // 16:9 → 4:3 (daha karesel)
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: ImageCarousel(urls: reel.imageUrls),
            ),
          ),
        ),
      ),

      // ✅ BAŞLIK VE METABİLGİLER
      Positioned(
        left: 16,
        right: 16,
        bottom: 140, // 180 → 140
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Başlık
              Text(
                reel.title,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                  height: 1.35,
                  letterSpacing: -0.3,
                ),
              ),
              
              const SizedBox(height: 12),
              
              // Kategori ve Tarih
              Row(
                children: [
                  // Kategori
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0xFF003D82).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: const BoxDecoration(
                            color: Color(0xFF003D82),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          reel.category.toUpperCase(),
                          style: const TextStyle(
                            color: Color(0xFF003D82),
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(width: 12),
                  
                  // Tarih
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.access_time_rounded,
                        size: 14,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _formatDate(reel.publishedAt),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),

      // ✅ ALTYAZI
      if (_subtitlesEnabled && reel.subtitles != null && reel.subtitles!.isNotEmpty)
        Positioned(
          left: 16,
          right: 16,
          bottom: 100, // 130 → 100
          child: Consumer<AudioService>(
            builder: (context, audioService, _) {
              if (!audioService.isPlaying && audioService.position.inSeconds == 0) {
                return const SizedBox.shrink();
              }
              
              return SubtitleWidget(
                subtitles: reel.subtitles!,
                currentPosition: audioService.position,
                isVisible: _subtitlesEnabled,
              );
            },
          ),
        ),

      // ✅ READ HANDLE - ÇOK AŞAĞI (navigation'a çok yakın)
      Positioned(
        bottom: 30, // 100 → 30 🔥
        left: 0,
        right: 0,
        child: Center(
          child: ReadHandle(
            threshold: 35,
            onAction: (action) {
              final currentReel = reel;
              
              switch (action) {
                case HandleAction.up:
                  showModalBottomSheet(
                    context: context,
                    isScrollControlled: true,
                    backgroundColor: Colors.transparent,
                    builder: (context) => ArticleReaderSheet(
                      articleId: currentReel.id,
                      title: currentReel.title,
                      body: currentReel.fullContent.join('\n\n'),
                      imageUrls: currentReel.imageUrls,
                      category: currentReel.category,
                      publishedDate: _formatDate(currentReel.publishedAt),
                      onClose: () => Navigator.pop(context),
                    ),
                  );
                  break;
                
                case HandleAction.right:
                  setState(() => _showEmojis = true);
                  break;
                
                case HandleAction.down:
                  _onShareTapped(currentReel);
                  break;
                
                case HandleAction.left:
                  _onSaveTapped(currentReel);
                  break;
                
                case HandleAction.none:
                  break;
              }
            },
          ),
        ),
      ),

      // ✅ Emoji Panel
      if (_showEmojis)
        Positioned(
          bottom: 100, // 180 → 100
          left: 0,
          right: 0,
          child: Center(
            child: EmojiPanel(
              publicEmojis: EmojiConstants.publicEmojis,
              premiumEmojis: EmojiConstants.premiumEmojis,
              onPick: (emoji) {
                _onEmojiSelected(emoji, reel);
                setState(() => _showEmojis = false);
              },
              onTapPremium: () {
                setState(() => _showEmojis = false);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Premium emojiler şimdilik kilitli.'),
                    duration: Duration(seconds: 2),
                  ),
                );
              },
            ),
          ),
        ),
    ],
  );
}

  void _openArticle(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => ArticleReaderSheet(
        articleId: reel.id,
        title: reel.title,
        body: reel.fullText,
        imageUrls: reel.imageUrls,
        category: reel.category,
        onClose: () => Navigator.pop(context),
        onBookmark: () => _saveReel(context, reel),
        onShare: () => _onShareTap(context, reel),
      ),
    );
  }

  void _openEmojis(BuildContext context, Reel reel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => EmojiPanel(
        publicEmojis: const ['👍', '❤️', '🔥', '⭐', '👏'],
        premiumEmojis: const ['😍', '🤔', '😮', '🎉', '💎'],
        onPick: (emoji) {
          Navigator.pop(context);  // Modal'ı kapat
          
          // ✅ YENİ HANDLER'I ÇAĞIR:
          _onEmojiSelected(emoji, reel);
        },
        onTapPremium: () {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Premium emojiler şimdilik kilitli.')),
          );
        },
      ),
    );
  }

  void _onShareTap(BuildContext context, Reel reel) {
    Share.share(
      '${reel.title}\n\n${reel.summary}\n\nDaha fazlası için AANext uygulamasını indir!',
      subject: reel.title,
    );
  }

  void _saveReel(BuildContext context, Reel reel) {
    context.read<SavedReelsProvider>().saveReel(
      reelId: reel.id,
      title: reel.title,
      content: reel.summary,
      imageUrl: reel.imageUrls.isNotEmpty ? reel.imageUrls.first : '',
    );
    
    if (!context.mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.bookmark_added, color: Colors.white),
              SizedBox(width: 8),
              Text('Haber kaydedildi!'),
            ],
          ),
          backgroundColor: Colors.green[700],
          duration: const Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
  }

  @override
  void dispose() {
    _stopCurrentTracker();
    WidgetsBinding.instance.removeObserver(this);
    _pageController.dispose();
    FloatingXPOverlay.remove();
    super.dispose();
  }
} 


// 6️⃣ _ReelView CLASS'I TAMAMEN DEĞİŞSİN (satır 485 civarı)
class _ReelView extends StatelessWidget {
  final Reel reel;
  final bool subtitlesEnabled;

  const _ReelView({
    required this.reel,
    required this.subtitlesEnabled,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // GÖRSEL
        Positioned.fill(
          top: 0,
          bottom: 160,
          child: Center(
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: ClipRect(
                child: SizedBox.expand(
                  child: ImageCarousel(urls: reel.imageUrls),
                ),
              ),
            ),
          ),
        ),

        // ALT YAZI (Ses ile senkronize)
        if (reel.subtitles != null && reel.subtitles!.isNotEmpty && subtitlesEnabled)
          Positioned(
            left: 0,
            right: 0,
            bottom: 240,
            child: Consumer<AudioService>(
              builder: (context, audioService, _) {
                return SubtitleWidget(
                  subtitles: reel.subtitles!,
                  currentPosition: audioService.position,
                  isVisible: subtitlesEnabled,
                );
              },
            ),
          ),

        // Başlık ve özet
        Positioned(
          left: 0,
          right: 0,
          bottom: 10,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withOpacity(0.8),
                  Colors.transparent,
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.3),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Text(
                    reel.title,
                    maxLines: 4,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                      height: 1.2,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}


String? _getCategoryFromReel(Reel reel) {
  // Reel modelinde category zaten var
  return reel.category;
}



/// Okuma süresini hesapla (kelime sayısından)
int _calculateReadingTime(String text) {
  // Ortalama okuma hızı: 200 kelime/dakika
  final wordCount = text.split(' ').length;
  final minutes = (wordCount / 200).ceil();
  return minutes < 1 ? 1 : minutes;
}


/// Yayın tarihini formatla
String? _formatPublishedDate(Reel reel) {
  // Reel modelinde publishedAt var
  final now = DateTime.now();
  final diff = now.difference(reel.publishedAt);
  
  if (diff.inMinutes < 60) {
    return '${diff.inMinutes} dakika önce';
  } else if (diff.inHours < 24) {
    return '${diff.inHours} saat önce';
  } else if (diff.inDays < 7) {
    return '${diff.inDays} gün önce';
  } else {
    return '${reel.publishedAt.day}.${reel.publishedAt.month}.${reel.publishedAt.year}';
  }
}
class FloatingXPData {
  final String id;
  final int amount;
  final String source;
  final Offset position;
  
  FloatingXPData({
    required this.id,
    required this.amount,
    required this.source,
    required this.position,
  });
}