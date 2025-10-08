// lib/providers/auth_provider.dart

import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

/// Authentication State Provider
/// Kullanıcı durumunu yönetir (login/logout/register)
class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();

  User? _user;
  AuthToken? _token;
  bool _isLoading = false;
  String? _errorMessage;
  bool _isInitialized = false;

  // Getters
  User? get user => _user;
  AuthToken? get token => _token;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _user != null && _token != null;
  bool get isInitialized => _isInitialized;

  /// Provider başlangıcında token kontrolü yap
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    _isLoading = true;
    notifyListeners();

    try {
      final token = await _authService.getToken();
      final user = await _authService.getUser();

      if (token != null && user != null && !token.isExpired) {
        _token = token;
        _user = user;
      } else {
        // Token expire veya yok, temizle
        await _authService.logout();
      }
    } catch (e) {
      print('Initialize error: $e');
      _errorMessage = 'Başlatma hatası';
    } finally {
      _isLoading = false;
      _isInitialized = true;
      notifyListeners();
    }
  }

  /// Register - Yeni kullanıcı kaydı
  Future<bool> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _authService.register(
        email: email,
        username: username,
        password: password,
        fullName: fullName,
      );

      if (response.token != null) {
        _user = response.user;
        _token = response.token;
      } else {
        _user = response.user;
        // Token yoksa direkt login yap
        return await login(email: email, password: password);
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = _parseErrorMessage(e.toString());
      notifyListeners();
      return false;
    }
  }

  /// Login - Kullanıcı girişi
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _authService.login(
        email: email,
        password: password,
      );

      _user = response.user;
      _token = response.token;

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = _parseErrorMessage(e.toString());
      notifyListeners();
      return false;
    }
  }

  /// Logout - Çıkış yap
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.logout();
    } catch (e) {
      print('Logout error: $e');
    } finally {
      _user = null;
      _token = null;
      _errorMessage = null;
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Email kontrolü (kayıtlı mı?)
  Future<bool> checkEmail(String email) async {
    try {
      return await _authService.checkEmail(email);
    } catch (e) {
      return false;
    }
  }

  /// Username kontrolü (kayıtlı mı?)
  Future<bool> checkUsername(String username) async {
    try {
      return await _authService.checkUsername(username);
    } catch (e) {
      return false;
    }
  }

  /// Error mesajını temizle
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Error mesajını parse et (kullanıcı dostu yap)
  String _parseErrorMessage(String error) {
    if (error.contains('Email already registered')) {
      return 'Bu e-posta zaten kayıtlı';
    } else if (error.contains('Username already taken')) {
      return 'Bu kullanıcı adı zaten kullanılıyor';
    } else if (error.contains('Invalid email or password')) {
      return 'E-posta veya şifre hatalı';
    } else if (error.contains('Account is banned')) {
      return 'Hesabınız askıya alınmış';
    } else if (error.contains('Network')) {
      return 'İnternet bağlantısı hatası';
    } else if (error.contains('timeout')) {
      return 'Sunucu yanıt vermiyor';
    } else {
      return 'Bir hata oluştu. Lütfen tekrar deneyin';
    }
  }
}