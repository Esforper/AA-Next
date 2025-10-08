// lib/pages/register_page.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'reels_feed_page.dart';

/// Register Page - Modern ve profesyonel tasarım
class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _usernameController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _usernameController.dispose();
    _fullNameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    if (_passwordController.text != _confirmPasswordController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Şifreler eşleşmiyor'),
          backgroundColor: Colors.red.shade600,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
      return;
    }

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.register(
      email: _emailController.text.trim(),
      username: _usernameController.text.trim(),
      password: _passwordController.text,
      fullName: _fullNameController.text.trim().isEmpty
          ? null
          : _fullNameController.text.trim(),
    );

    if (!mounted) return;

    if (success) {
      // Başarılı kayıt
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Kayıt başarılı! Hoş geldiniz 🎉'),
          backgroundColor: Colors.green.shade600,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );

      // ReelsFeedPage'e yönlendir
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const ReelsFeedPage()),
        (route) => false,
      );
    } else {
      // Hata göster
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(authProvider.errorMessage ?? 'Kayıt başarısız'),
          backgroundColor: Colors.red.shade600,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.indigo.shade900,
              Colors.indigo.shade600,
              Colors.purple.shade400,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Back Button
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
              ),

              // Scrollable Content
              Expanded(
                child: Center(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // Logo
                          Container(
                            width: 90,
                            height: 90,
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(22),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.2),
                                  blurRadius: 15,
                                  offset: const Offset(0, 8),
                                ),
                              ],
                            ),
                            child: Icon(
                              Icons.person_add_outlined,
                              size: 50,
                              color: Colors.indigo.shade700,
                            ),
                          ),

                          const SizedBox(height: 24),

                          // Title
                          const Text(
                            'Hesap Oluşturun',
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),

                          const SizedBox(height: 8),

                          Text(
                            'Birkaç adımda başlayın',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.white.withOpacity(0.8),
                            ),
                          ),

                          const SizedBox(height: 40),

                          // Email Field
                          _buildTextField(
                            controller: _emailController,
                            label: 'E-posta',
                            hint: 'ornek@email.com',
                            icon: Icons.email_outlined,
                            keyboardType: TextInputType.emailAddress,
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'E-posta gerekli';
                              }
                              if (!value.contains('@')) {
                                return 'Geçerli bir e-posta girin';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 16),

                          // Username Field
                          _buildTextField(
                            controller: _usernameController,
                            label: 'Kullanıcı Adı',
                            hint: 'kullaniciadi',
                            icon: Icons.alternate_email,
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Kullanıcı adı gerekli';
                              }
                              if (value.length < 3) {
                                return 'En az 3 karakter olmalı';
                              }
                              if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
                                return 'Sadece harf, rakam ve _ kullanın';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 16),

                          // Full Name Field (Opsiyonel)
                          _buildTextField(
                            controller: _fullNameController,
                            label: 'Ad Soyad (Opsiyonel)',
                            hint: 'Ahmet Yılmaz',
                            icon: Icons.person_outline,
                            required: false,
                          ),

                          const SizedBox(height: 16),

                          // Password Field
                          _buildTextField(
                            controller: _passwordController,
                            label: 'Şifre',
                            hint: '••••••••',
                            icon: Icons.lock_outline,
                            obscureText: _obscurePassword,
                            onToggleObscure: () {
                              setState(() {
                                _obscurePassword = !_obscurePassword;
                              });
                            },
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Şifre gerekli';
                              }
                              if (value.length < 8) {
                                return 'En az 8 karakter olmalı';
                              }
                              if (!RegExp(r'[0-9]').hasMatch(value)) {
                                return 'En az bir rakam içermeli';
                              }
                              if (!RegExp(r'[a-zA-Z]').hasMatch(value)) {
                                return 'En az bir harf içermeli';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 16),

                          // Confirm Password Field
                          _buildTextField(
                            controller: _confirmPasswordController,
                            label: 'Şifre Tekrar',
                            hint: '••••••••',
                            icon: Icons.lock_outline,
                            obscureText: _obscureConfirmPassword,
                            textInputAction: TextInputAction.done,
                            onFieldSubmitted: (_) => _handleRegister(),
                            onToggleObscure: () {
                              setState(() {
                                _obscureConfirmPassword =
                                    !_obscureConfirmPassword;
                              });
                            },
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Şifre tekrarı gerekli';
                              }
                              return null;
                            },
                          ),

                          const SizedBox(height: 32),

                          // Register Button
                          Consumer<AuthProvider>(
                            builder: (context, auth, _) {
                              return SizedBox(
                                width: double.infinity,
                                height: 56,
                                child: ElevatedButton(
                                  onPressed:
                                      auth.isLoading ? null : _handleRegister,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.white,
                                    foregroundColor: Colors.indigo.shade700,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(16),
                                    ),
                                    elevation: 5,
                                    shadowColor:
                                        Colors.black.withOpacity(0.3),
                                  ),
                                  child: auth.isLoading
                                      ? SizedBox(
                                          height: 24,
                                          width: 24,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2.5,
                                            valueColor:
                                                AlwaysStoppedAnimation(
                                              Colors.indigo.shade700,
                                            ),
                                          ),
                                        )
                                      : const Text(
                                          'Kayıt Ol',
                                          style: TextStyle(
                                            fontSize: 18,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                ),
                              );
                            },
                          ),

                          const SizedBox(height: 24),

                          // Login Link
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                'Zaten hesabınız var mı? ',
                                style: TextStyle(
                                  color: Colors.white.withOpacity(0.8),
                                  fontSize: 15,
                                ),
                              ),
                              TextButton(
                                onPressed: () => Navigator.of(context).pop(),
                                style: TextButton.styleFrom(
                                  padding:
                                      const EdgeInsets.symmetric(horizontal: 8),
                                ),
                                child: const Text(
                                  'Giriş Yapın',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 15,
                                    fontWeight: FontWeight.bold,
                                    decoration: TextDecoration.underline,
                                    decorationColor: Colors.white,
                                  ),
                                ),
                              ),
                            ],
                          ),

                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    TextInputType? keyboardType,
    bool obscureText = false,
    VoidCallback? onToggleObscure,
    String? Function(String?)? validator,
    bool required = true,
    TextInputAction? textInputAction,
    Function(String)? onFieldSubmitted,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: keyboardType,
        obscureText: obscureText,
        textInputAction: textInputAction ?? TextInputAction.next,
        onFieldSubmitted: onFieldSubmitted,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          prefixIcon: Icon(icon, color: Colors.indigo.shade600),
          suffixIcon: onToggleObscure != null
              ? IconButton(
                  icon: Icon(
                    obscureText
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    color: Colors.grey.shade600,
                  ),
                  onPressed: onToggleObscure,
                )
              : null,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
        ),
        validator: required ? validator : null,
      ),
    );
  }
}