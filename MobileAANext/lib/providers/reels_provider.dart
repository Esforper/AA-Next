// lib/providers/reels_provider.dart
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/reel_model.dart';

enum FeedStatus { initial, loading, loaded, loadingMore, error }

class ReelsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  // Reels listesi
  final List<Reel> _reels = [];
  int _current = 0;
  FeedStatus _status = FeedStatus.initial;
  
  // 🆕 Infinite scroll için yeni alanlar
  String? _nextCursor;
  bool _hasMore = true;
  bool _isLoadingMore = false;
  
  // Getters
  List<Reel> get reels => _reels;
  int get currentIndex => _current;
  Reel? get current => _reels.isEmpty ? null : _reels[_current];
  FeedStatus get status => _status;
  bool get hasMore => _hasMore;
  bool get isLoadingMore => _isLoadingMore;
  String? get nextCursor => _nextCursor;

  /// İlk yükleme - feed'i sıfırdan başlat
  Future<void> loadReels() async {
    if (_status == FeedStatus.loading) return;
    
    _status = FeedStatus.loading;
    _nextCursor = null;
    _hasMore = true;
    notifyListeners();

    try {
      // API'den ilk sayfa
      final response = await _apiService.fetchReels(limit: 20);
      
      _reels
        ..clear()
        ..addAll(response['reels'] as List<Reel>);
      _current = 0;

      // Pagination bilgisini al
      final pagination = response['pagination'] as Map<String, dynamic>?;
      if (pagination != null) {
        _hasMore = pagination['has_next'] as bool? ?? false;
        _nextCursor = pagination['next_cursor'] as String?;
      } else {
        _hasMore = false;
        _nextCursor = null;
      }

      _status = FeedStatus.loaded;
      debugPrint('✅ Feed loaded: ${_reels.length} reels, hasMore: $_hasMore');
      
    } catch (e, st) {
      debugPrint('❌ ReelsProvider.loadReels() error: $e');
      debugPrintStack(stackTrace: st);
      _status = FeedStatus.error;
      _hasMore = false;
    } finally {
      notifyListeners();
    }
  }

  /// 🆕 Daha fazla reel yükle (infinite scroll için)
  Future<void> loadMore() async {
    // Guard conditions
    if (!_hasMore) {
      debugPrint('⚠️ No more reels to load');
      return;
    }
    if (_isLoadingMore) {
      debugPrint('⚠️ Already loading more');
      return;
    }
    if (_nextCursor == null) {
      debugPrint('⚠️ No cursor available');
      return;
    }

    _isLoadingMore = true;
    _status = FeedStatus.loadingMore;
    notifyListeners();

    try {
      debugPrint('📥 Loading more reels with cursor: $_nextCursor');
      
      // API'den sonraki sayfa
      final response = await _apiService.fetchReels(
        limit: 20,
        cursor: _nextCursor,
      );
      
      final newReels = response['reels'] as List<Reel>;
      
      // Yeni reels'leri ekle
      _reels.addAll(newReels);

      // Pagination bilgisini güncelle
      final pagination = response['pagination'] as Map<String, dynamic>?;
      if (pagination != null) {
        _hasMore = pagination['has_next'] as bool? ?? false;
        _nextCursor = pagination['next_cursor'] as String?;
      } else {
        _hasMore = false;
        _nextCursor = null;
      }

      _status = FeedStatus.loaded;
      debugPrint('✅ Loaded ${newReels.length} more reels. Total: ${_reels.length}, hasMore: $_hasMore');
      
    } catch (e, st) {
      debugPrint('❌ ReelsProvider.loadMore() error: $e');
      debugPrintStack(stackTrace: st);
      // Hata durumunda state'i geri al
      _status = FeedStatus.loaded;
      _hasMore = false;
    } finally {
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  /// Index değiştir ve tracking yap
  void setIndex(int i) {
    if (i < 0 || i >= _reels.length || i == _current) return;
    _current = i;

    final reel = current;
    if (reel != null) {
      debugPrint('[Reels] Visible -> ${reel.id} (${i + 1}/${_reels.length})');
      
      // // View tracking
      // _apiService.trackView(
      //   reelId: reel.id,
      //   category: reel.category,
      // );

      // 🆕 Otomatik load more trigger
      // Eğer son 3 reel'den birine gelindiyse, yeni sayfa yükle
      if (_hasMore && !_isLoadingMore && i >= _reels.length - 3) {
        debugPrint('🔄 Auto-triggering loadMore (at index $i/${_reels.length})');
        loadMore();
      }
    }

    notifyListeners();
  }

  /// Manuel refresh (pull-to-refresh için)
  Future<void> refresh() async {
    debugPrint('🔄 Refreshing feed...');
    await loadReels();
  }

  @override
  void dispose() {
    debugPrint('🧹 ReelsProvider disposed');
    super.dispose();
  }
}