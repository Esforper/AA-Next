import React, { useState } from 'react';
import { Card, Button } from '../components';
import { useAuthViewModel } from '../viewmodels';
import clsx from 'clsx';

type ViewMode = 'main' | 'login' | 'register';

export const ProfileView: React.FC = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError
  } = useAuthViewModel();

  const [viewMode, setViewMode] = useState<ViewMode>('main');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    full_name: ''
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [formLoading, setFormLoading] = useState(false);

  // Form input change handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setFormError(null);
    clearError();
  };

  // Login handler
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormLoading(true);

    if (!formData.email || !formData.password) {
      setFormError('Email ve şifre gereklidir');
      setFormLoading(false);
      return;
    }

    const result = await login({
      email: formData.email,
      password: formData.password
    });

    setFormLoading(false);

    if (result.success) {
      setFormData({ email: '', password: '', username: '', full_name: '' });
      setViewMode('main');
    } else {
      setFormError(result.message);
    }
  };

  // Register handler
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormLoading(true);

    if (!formData.email || !formData.password || !formData.username) {
      setFormError('Email, kullanıcı adı ve şifre gereklidir');
      setFormLoading(false);
      return;
    }

    // Password validation
    if (formData.password.length < 6) {
      setFormError('Şifre en az 6 karakter olmalıdır');
      setFormLoading(false);
      return;
    }

    const result = await register({
      email: formData.email,
      username: formData.username,
      password: formData.password,
      full_name: formData.full_name || undefined
    });

    setFormLoading(false);

    if (result.success) {
      setFormData({ email: '', password: '', username: '', full_name: '' });
      setViewMode('main');
    } else {
      setFormError(result.message);
    }
  };

  // Logout handler
  const handleLogout = async () => {
    await logout();
    setViewMode('main');
  };

  // Back to main
  const handleBackToMain = () => {
    setViewMode('main');
    setFormData({ email: '', password: '', username: '', full_name: '' });
    setFormError(null);
    clearError();
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Content */}
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Page Header - Minimal */}
        {viewMode !== 'main' && (
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {viewMode === 'login' ? 'Giriş Yap' : 'Kayıt Ol'}
          </h1>
            <button
              onClick={handleBackToMain}
              className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium flex items-center space-x-1"
            >
              <span>←</span>
              <span>Geri</span>
            </button>
        </div>
        )}
        {/* Main View - Not Authenticated */}
        {viewMode === 'main' && !isAuthenticated && (
          <div className="bg-white rounded-lg-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 sm:p-8">
              <div className="text-center mb-6">
                <div className="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-lg-full flex items-center justify-center">
                  <span className="text-4xl">👤</span>
      </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                  Hoş Geldiniz
            </h2>
                <p className="text-gray-600 text-sm sm:text-base">
                  Devam etmek için giriş yapın veya hesap oluşturun
            </p>
          </div>

              {/* Auth Buttons - AA Style */}
              <div className="space-y-3">
                <button
                  onClick={() => setViewMode('login')}
                  className="w-full py-3 px-6 bg-aa-blue text-white font-semibold rounded-lg hover:bg-aa-blue-dark transition-colors duration-200"
                >
              Giriş Yap
                </button>
                <button
                  onClick={() => setViewMode('register')}
                  className="w-full py-3 px-6 bg-white text-gray-700 font-semibold rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors duration-200"
                >
              Kayıt Ol
                </button>
              </div>
            </div>

            {/* Info Section */}
            <div className="bg-gray-50 px-6 sm:px-8 py-4 border-t border-gray-200">
              <p className="text-gray-600 text-xs sm:text-sm leading-relaxed">
                <strong className="text-gray-900">Anadolu Ajansı</strong> ile güncel haberlere ulaşın. 
                Hesabınızla favori haberlerinizi kaydedebilir ve kişiselleştirilmiş içerikler görebilirsiniz.
              </p>
            </div>
          </div>
        )}

        {/* Main View - Authenticated */}
        {viewMode === 'main' && isAuthenticated && user && (
          <div className="space-y-4">
            {/* User Profile Card */}
            <div className="bg-white rounded-lg-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 sm:p-8">
                <div className="text-center mb-6">
                  <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-lg-full flex items-center justify-center">
                    <span className="text-5xl">
                      {user.avatar_url ? '🖼️' : '👤'}
                    </span>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1">
                    {user.full_name || user.username}
                  </h2>
                  <p className="text-gray-600 text-sm">@{user.username}</p>
                  {user.bio && (
                    <p className="mt-3 text-gray-700 text-sm">{user.bio}</p>
                  )}
                </div>

                {/* User Info Table */}
                <div className="space-y-3 mb-6 pb-6 border-b border-gray-200">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 font-medium">Email</span>
                    <span className="text-gray-900">{user.email}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 font-medium">Rol</span>
                    <span className={clsx(
                      'px-3 py-1 rounded-lg-full text-xs font-semibold',
                      user.role === 'admin' 
                        ? 'bg-aa-blue text-white' 
                        : 'bg-gray-200 text-gray-800'
                    )}>
                      {user.role === 'admin' ? '👑 Yönetici' : 'Kullanıcı'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600 font-medium">Durum</span>
                    <span className={clsx(
                      'px-3 py-1 rounded-lg-full text-xs font-semibold',
                      user.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-200 text-gray-600'
                    )}>
                      {user.is_active ? '✓ Aktif' : 'Pasif'}
                    </span>
                  </div>
                </div>

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  disabled={isLoading}
                  className="w-full py-3 px-6 bg-gray-700 text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Çıkış Yapılıyor...' : 'Çıkış Yap'}
                </button>
              </div>
          </div>

            {/* Features Coming Soon */}
            <div className="bg-white rounded-lg-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <span className="text-gray-500 mr-2">⚡</span>
                Yakında Eklenecek Özellikler
            </h3>
              <ul className="space-y-2">
                {['Profil düzenleme', 'Okuma geçmişi', 'Favori haberler', 'Bildirim ayarları', 'Tema seçimi'].map((feature, index) => (
                  <li key={index} className="flex items-center text-sm text-gray-700 py-1">
                    <span className="text-gray-400 mr-3 text-lg">•</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
          </div>
        )}

        {/* Login Form */}
        {viewMode === 'login' && (
          <div className="bg-white rounded-lg-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 sm:p-8">
              <form onSubmit={handleLogin} className="space-y-5">
                {/* Error Display */}
                {(formError || error) && (
                  <div className="p-4 bg-red-50 border-l-4 border-aa-blue rounded-lg">
                    <p className="text-red-800 text-sm font-medium">{formError || error}</p>
                  </div>
                )}

                {/* Email Input */}
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Adresi
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="ornek@email.com"
                  />
                </div>

                {/* Password Input */}
                <div>
                  <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                    Şifre
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="••••••••"
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={formLoading}
                  className="w-full py-3 px-6 bg-aa-blue text-white font-semibold rounded-lg hover:bg-aa-blue-dark transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm mt-6"
                >
                  {formLoading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
                </button>

                {/* Switch to Register */}
                <div className="text-center pt-4 border-t border-gray-200 mt-6">
                  <p className="text-sm text-gray-600">
                    Hesabınız yok mu?{' '}
                    <button
                      type="button"
                      onClick={() => setViewMode('register')}
                      className="text-aa-blue font-semibold hover:underline transition-all"
                    >
                      Kayıt Ol
                    </button>
                  </p>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Register Form */}
        {viewMode === 'register' && (
          <div className="bg-white rounded-lg-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 sm:p-8">
              <form onSubmit={handleRegister} className="space-y-4">
                {/* Error Display */}
                {(formError || error) && (
                  <div className="p-4 bg-red-50 border-l-4 border-aa-blue rounded-lg">
                    <p className="text-red-800 text-sm font-medium">{formError || error}</p>
                  </div>
                )}

                {/* Email Input */}
                <div>
                  <label htmlFor="reg-email" className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Adresi <span className="text-aa-blue">*</span>
                  </label>
                  <input
                    type="email"
                    id="reg-email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="ornek@email.com"
                  />
                </div>

                {/* Username Input */}
                <div>
                  <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
                    Kullanıcı Adı <span className="text-aa-blue">*</span>
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="kullaniciadi"
                  />
                </div>

                {/* Full Name Input (Optional) */}
                <div>
                  <label htmlFor="full_name" className="block text-sm font-semibold text-gray-700 mb-2">
                    Ad Soyad
                  </label>
                  <input
                    type="text"
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="Ad Soyad (opsiyonel)"
                  />
                </div>

                {/* Password Input */}
                <div>
                  <label htmlFor="reg-password" className="block text-sm font-semibold text-gray-700 mb-2">
                    Şifre <span className="text-aa-blue">*</span>
                  </label>
                  <input
                    type="password"
                    id="reg-password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aa-blue focus:border-transparent outline-none transition-all text-sm"
                    placeholder="En az 6 karakter"
                  />
                  <p className="text-xs text-gray-500 mt-1">Minimum 6 karakter olmalıdır</p>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={formLoading}
                  className="w-full py-3 px-6 bg-aa-blue text-white font-semibold rounded-lg hover:bg-aa-blue-dark transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm mt-6"
                >
                  {formLoading ? 'Kayıt Yapılıyor...' : 'Kayıt Ol'}
                </button>

                {/* Switch to Login */}
                <div className="text-center pt-4 border-t border-gray-200 mt-6">
                  <p className="text-sm text-gray-600">
                    Zaten hesabınız var mı?{' '}
                    <button
                      type="button"
                      onClick={() => setViewMode('login')}
                      className="text-aa-blue font-semibold hover:underline transition-all"
                    >
                      Giriş Yap
                    </button>
                  </p>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
