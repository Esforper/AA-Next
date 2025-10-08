// lib/pages/auth_page.dart
// Birleşik Login/Register Sayfası - Modern Tasarım


/*
BU DOSYA KULLANILMIYOR, YEDEK OLARAK SAKLANIYOR.
*/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'reels_feed_page.dart';

class AuthPage extends StatefulWidget {
  const AuthPage({super.key});

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _loginFormKey = GlobalKey<FormState>();
  final _registerFormKey = GlobalKey<FormState>();

  // Login Controllers
  final _loginEmailController = TextEditingController();
  final _loginPasswordController = TextEditingController();

  // Register Controllers
  final _regEmailController = TextEditingController();
  final _regUsernameController = TextEditingController();
  final _regPasswordController = TextEditingController();
  final _regConfirmPasswordController = TextEditingController();
  final _regFullNameController = TextEditingController();

  bool _obscureLoginPassword = true;
  bool _obscureRegPassword = true;
  bool _obscureRegConfirmPassword = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _loginEmailController.dispose();
    _loginPasswordController.dispose();
    _regEmailController.dispose();
    _regUsernameController.dispose();
    _regPasswordController.dispose();
    _regConfirmPasswordController.dispose();
    _regFullNameController.dispose();
    super.dispose();
  }

  // Login Handler
  Future<void> _handleLogin() async {
    if (!_loginFormKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.login(
      email: _loginEmailController.text.trim(),
      password: _loginPasswordController.text,
    );

    if (!mounted) return;

    if (success) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const ReelsFeedPage()),
      );
    } else {
      _showSnackBar(auth.errorMessage ?? 'Giriş başarısız', isError: true);
    }
  }

  // Register Handler
  Future<void> _handleRegister() async {
    if (!_registerFormKey.currentState!.validate()) return;

    if (_regPasswordController.text != _regConfirmPasswordController.text) {
      _showSnackBar('Şifreler eşleşmiyor', isError: true);
      return;
    }

    final auth = context.read<AuthProvider>();
    final success = await auth.register(
      email: _regEmailController.text.trim(),
      username: _regUsernameController.text.trim(),
      password: _regPasswordController.text,
      fullName: _regFullNameController.text.trim().isEmpty
          ? null
          : _regFullNameController.text.trim(),
    );

    if (!mounted) return;

    if (success) {
      _showSnackBar('Kayıt başarılı! Hoş geldiniz 🎉', isError: false);
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const ReelsFeedPage()),
        (route) => false,
      );
    } else {
      _showSnackBar(auth.errorMessage ?? 'Kayıt başarısız', isError: true);
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade600 : Colors.green.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
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
              Colors.indigo.shade700,
              Colors.indigo.shade900,
              Colors.purple.shade900,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 40),
              
              // Logo/Icon
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Icon(
                  Icons.play_circle_outline,
                  size: 60,
                  color: Colors.white,
                ),
              ),

              const SizedBox(height: 20),

              const Text(
                'AA-Next',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 2,
                ),
              ),

              const SizedBox(height: 40),

              // TabBar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 40),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(30),
                  ),
                  labelColor: Colors.indigo.shade700,
                  unselectedLabelColor: Colors.white,
                  labelStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  tabs: const [
                    Tab(text: 'Giriş'),
                    Tab(text: 'Kayıt'),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // TabBarView
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildLoginTab(),
                    _buildRegisterTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Login Tab
  Widget _buildLoginTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 30),
      child: Form(
        key: _loginFormKey,
        child: Column(
          children: [
            _buildTextField(
              controller: _loginEmailController,
              label: 'E-posta',
              icon: Icons.email_outlined,
              keyboardType: TextInputType.emailAddress,
              validator: (v) => v == null || v.isEmpty
                  ? 'E-posta gerekli'
                  : !v.contains('@')
                      ? 'Geçerli e-posta girin'
                      : null,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _loginPasswordController,
              label: 'Şifre',
              icon: Icons.lock_outline,
              obscureText: _obscureLoginPassword,
              onToggle: () => setState(() => _obscureLoginPassword = !_obscureLoginPassword),
              onSubmit: (_) => _handleLogin(),
              validator: (v) => v == null || v.isEmpty ? 'Şifre gerekli' : null,
            ),
            const SizedBox(height: 30),
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                return SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: auth.isLoading ? null : _handleLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.indigo.shade700,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 5,
                    ),
                    child: auth.isLoading
                        ? SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              valueColor: AlwaysStoppedAnimation(Colors.indigo.shade700),
                            ),
                          )
                        : const Text(
                            'Giriş Yap',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  // Register Tab
  Widget _buildRegisterTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 30),
      child: Form(
        key: _registerFormKey,
        child: Column(
          children: [
            _buildTextField(
              controller: _regEmailController,
              label: 'E-posta',
              icon: Icons.email_outlined,
              keyboardType: TextInputType.emailAddress,
              validator: (v) => v == null || v.isEmpty
                  ? 'E-posta gerekli'
                  : !v.contains('@')
                      ? 'Geçerli e-posta girin'
                      : null,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _regUsernameController,
              label: 'Kullanıcı Adı',
              icon: Icons.alternate_email,
              validator: (v) {
                if (v == null || v.isEmpty) return 'Kullanıcı adı gerekli';
                if (v.length < 3) return 'En az 3 karakter';
                if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(v)) return 'Sadece harf, rakam ve _';
                return null;
              },
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _regFullNameController,
              label: 'Ad Soyad (Opsiyonel)',
              icon: Icons.person_outline,
              required: false,
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _regPasswordController,
              label: 'Şifre',
              icon: Icons.lock_outline,
              obscureText: _obscureRegPassword,
              onToggle: () => setState(() => _obscureRegPassword = !_obscureRegPassword),
              validator: (v) {
                if (v == null || v.isEmpty) return 'Şifre gerekli';
                if (v.length < 8) return 'En az 8 karakter';
                if (!RegExp(r'[0-9]').hasMatch(v)) return 'En az bir rakam';
                if (!RegExp(r'[a-zA-Z]').hasMatch(v)) return 'En az bir harf';
                return null;
              },
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _regConfirmPasswordController,
              label: 'Şifre Tekrar',
              icon: Icons.lock_outline,
              obscureText: _obscureRegConfirmPassword,
              onToggle: () => setState(() => _obscureRegConfirmPassword = !_obscureRegConfirmPassword),
              onSubmit: (_) => _handleRegister(),
              validator: (v) => v == null || v.isEmpty ? 'Şifre tekrarı gerekli' : null,
            ),
            const SizedBox(height: 30),
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                return SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: auth.isLoading ? null : _handleRegister,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.indigo.shade700,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 5,
                    ),
                    child: auth.isLoading
                        ? SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              valueColor: AlwaysStoppedAnimation(Colors.indigo.shade700),
                            ),
                          )
                        : const Text(
                            'Kayıt Ol',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                  ),
                );
              },
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  // TextField Builder
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscureText = false,
    bool required = true,
    TextInputType? keyboardType,
    VoidCallback? onToggle,
    Function(String)? onSubmit,
    String? Function(String?)? validator,
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
        obscureText: obscureText,
        keyboardType: keyboardType,
        textInputAction: onSubmit != null ? TextInputAction.done : TextInputAction.next,
        onFieldSubmitted: onSubmit,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon, color: Colors.indigo.shade600),
          suffixIcon: onToggle != null
              ? IconButton(
                  icon: Icon(
                    obscureText ? Icons.visibility_off : Icons.visibility,
                    color: Colors.grey.shade600,
                  ),
                  onPressed: onToggle,
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          filled: true,
          fillColor: Colors.white,
        ),
        validator: required ? validator : null,
      ),
    );
  }
}