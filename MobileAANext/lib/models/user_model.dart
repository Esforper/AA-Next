// lib/models/user_model.dart

/// User ve Authentication Model'leri
/// Backend'den gelen JSON'ları parse eder

class User {
  final String id;
  final String email;
  final String username;
  final String? fullName;
  final String? avatarUrl;
  final String? bio;
  final String role;
  final String status;
  final DateTime createdAt;
  final DateTime? lastLogin;

  User({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    this.avatarUrl,
    this.bio,
    required this.role,
    required this.status,
    required this.createdAt,
    this.lastLogin,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      bio: json['bio'] as String?,
      role: json['role'] as String? ?? 'user',
      status: json['status'] as String? ?? 'active',
      createdAt: DateTime.parse(json['created_at'] as String),
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'full_name': fullName,
      'avatar_url': avatarUrl,
      'bio': bio,
      'role': role,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
    };
  }
}

class AuthToken {
  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final DateTime issuedAt;

  AuthToken({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    DateTime? issuedAt,
  }) : issuedAt = issuedAt ?? DateTime.now();

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresIn: json['expires_in'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'issued_at': issuedAt.toIso8601String(),
    };
  }

  /// Token'ın geçerliliğini kontrol et
  bool get isExpired {
    final expireTime = issuedAt.add(Duration(seconds: expiresIn));
    return DateTime.now().isAfter(expireTime);
  }

  /// Token ne kadar süre geçerli (kalan süre)
  Duration get remainingTime {
    final expireTime = issuedAt.add(Duration(seconds: expiresIn));
    final remaining = expireTime.difference(DateTime.now());
    return remaining.isNegative ? Duration.zero : remaining;
  }
}

class LoginResponse {
  final bool success;
  final String message;
  final User user;
  final AuthToken token;

  LoginResponse({
    required this.success,
    required this.message,
    required this.user,
    required this.token,
  });

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return LoginResponse(
      success: json['success'] as bool? ?? true,
      message: json['message'] as String? ?? 'Login successful',
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      token: AuthToken.fromJson(json['token'] as Map<String, dynamic>),
    );
  }
}

class RegisterResponse {
  final bool success;
  final String message;
  final User user;
  final AuthToken? token;

  RegisterResponse({
    required this.success,
    required this.message,
    required this.user,
    this.token,
  });

  factory RegisterResponse.fromJson(Map<String, dynamic> json) {
    return RegisterResponse(
      success: json['success'] as bool? ?? true,
      message: json['message'] as String? ?? 'Registration successful',
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      token: json['token'] != null
          ? AuthToken.fromJson(json['token'] as Map<String, dynamic>)
          : null,
    );
  }
}