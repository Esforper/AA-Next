// lib/services/auth_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../models/user_model.dart';

/// Authentication Service
/// Backend auth API'leri ile iletişim + Token yönetimi
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final _storage = const FlutterSecureStorage();
  
  // ✅ .env dosyasından al
  String get _baseUrl {
    final backendIp = dotenv.env['API_URL'] ?? 'localhost';
    final backendPort = dotenv.env['BACKEND_PORT'] ?? '8000';
    return '$backendIp';
  }


  // Storage keys
  static const _tokenKey = 'auth_token';
  static const _userKey = 'user_data';

  /// Register - Yeni kullanıcı kaydı
  Future<RegisterResponse> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    try {
      print('🔗 Register URL: $_baseUrl/api/auth/register'); // Debug
      
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'username': username,
          'password': password,
          if (fullName != null) 'full_name': fullName,
        }),
      );

      print('📡 Register Response: ${response.statusCode}'); // Debug

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        final registerResponse = RegisterResponse.fromJson(data);
        
        // Token varsa kaydet (backend direkt login yapıyorsa)
        if (registerResponse.token != null) {
          await _saveToken(registerResponse.token!);
          await _saveUser(registerResponse.user);
        }
        
        return registerResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Registration failed');
      }
    } catch (e) {
      print('❌ Register error: $e'); // Debug
      throw Exception('Registration error: $e');
    }
  }

  /// Login - Kullanıcı girişi
  Future<LoginResponse> login({
    required String email,
    required String password,
  }) async {
    try {
      print('🔗 Login URL: $_baseUrl/api/auth/login'); // Debug
      
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );

      print('📡 Login Response: ${response.statusCode}'); // Debug

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final loginResponse = LoginResponse.fromJson(data);
        
        // Token ve user'ı kaydet
        await _saveToken(loginResponse.token);
        await _saveUser(loginResponse.user);
        
        return loginResponse;
      } else {
        final error = jsonDecode(response.body);
        print('❌ Login error response: ${error['detail']}'); // Debug
        throw Exception(error['detail'] ?? 'Login failed');
      }
    } catch (e) {
      print('❌ Login error: $e'); // Debug
      throw Exception('Login error: $e');
    }
  }

  /// Logout - Çıkış yap
  Future<void> logout() async {
    try {
      final token = await getToken();
      if (token != null) {
        // Backend'e logout isteği gönder
        await http.post(
          Uri.parse('$_baseUrl/api/auth/logout'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${token.accessToken}',
          },
        );
      }
    } catch (e) {
      // Logout hatası olsa bile local'den sil
      print('Logout error: $e');
    } finally {
      // Local storage'ı temizle
      await _clearAuth();
    }
  }

  /// Token'ı kaydet
  Future<void> _saveToken(AuthToken token) async {
    await _storage.write(key: _tokenKey, value: jsonEncode(token.toJson()));
  }

  /// User'ı kaydet
  Future<void> _saveUser(User user) async {
    await _storage.write(key: _userKey, value: jsonEncode(user.toJson()));
  }

  /// Token'ı al
  Future<AuthToken?> getToken() async {
    try {
      final tokenStr = await _storage.read(key: _tokenKey);
      if (tokenStr == null) return null;
      
      final tokenData = jsonDecode(tokenStr);
      final token = AuthToken.fromJson(tokenData);
      
      // Token expire kontrolü
      if (token.isExpired) {
        await _clearAuth();
        return null;
      }
      
      return token;
    } catch (e) {
      print('Get token error: $e');
      return null;
    }
  }

  /// User'ı al
  Future<User?> getUser() async {
    try {
      final userStr = await _storage.read(key: _userKey);
      if (userStr == null) return null;
      
      final userData = jsonDecode(userStr);
      return User.fromJson(userData);
    } catch (e) {
      print('Get user error: $e');
      return null;
    }
  }

  /// Kullanıcı giriş yapmış mı kontrol et
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && !token.isExpired;
  }

  /// Auth bilgilerini temizle
  Future<void> _clearAuth() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _userKey);
  }

  /// Email kontrol et (kayıtlı mı?)
  Future<bool> checkEmail(String email) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/auth/check-email/$email'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['exists'] == true;
      }
      return false;
    } catch (e) {
      print('Check email error: $e');
      return false;
    }
  }

  /// Username kontrol et (kayıtlı mı?)
  Future<bool> checkUsername(String username) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/auth/check-username/$username'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['exists'] == true;
      }
      return false;
    } catch (e) {
      print('Check username error: $e');
      return false;
    }
  }
}