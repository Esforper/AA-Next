import { useState, useEffect, useCallback } from 'react';
import { AuthApi } from '../api/authApi';
import {
  User,
  LoginRequest,
  RegisterRequest,
  ProfileUpdateRequest,
  ChangePasswordRequest,
  AuthState
} from '../models/AuthModels';

/**
 * Auth ViewModel
 * Kullanıcı kimlik doğrulama ve yetkilendirme işlemleri için business logic
 */
export const useAuthViewModel = () => {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  // LocalStorage keys
  const TOKEN_KEY = 'aa_auth_token';
  const USER_KEY = 'aa_user';

  /**
   * Initialize - Token varsa kullanıcıyı yükle
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = localStorage.getItem(TOKEN_KEY);
        const savedUser = localStorage.getItem(USER_KEY);

        if (savedToken && savedUser) {
          // Verify token with backend
          try {
            const user = await AuthApi.getCurrentUser(savedToken);
            setState({
              user,
              token: savedToken,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
          } catch (error) {
            // Token geçersiz, temizle
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            setState({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            });
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initAuth();
  }, []);

  /**
   * Login - Kullanıcı girişi
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await AuthApi.login(credentials);

      if (response.success && response.token && response.user) {
        // Save to localStorage
        localStorage.setItem(TOKEN_KEY, response.token.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(response.user));

        setState({
          user: response.user,
          token: response.token.access_token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });

        return { success: true, message: response.message };
      } else {
        throw new Error(response.message || 'Giriş başarısız');
      }
    } catch (error: any) {
      let errorMessage = error?.message || 'Giriş sırasında bir hata oluştu';
      // Detaylı hata eşlemeleri
      if (/password/i.test(errorMessage) && /invalid|wrong/i.test(errorMessage)) {
        errorMessage = 'E-posta veya şifre hatalı. Şifrenizde en az 8 karakter, bir harf ve bir rakam olmalı.';
      } else if (/not found|kayıtlı kullanıcı bulunamadı/i.test(errorMessage)) {
        errorMessage = 'Bu e-posta ile kullanıcı bulunamadı. Lütfen önce kayıt olun.';
      }
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, message: errorMessage };
    }
  }, []);

  /**
   * Register - Kullanıcı kaydı
   */
  const register = useCallback(async (userData: RegisterRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await AuthApi.register(userData);

      if (response.success && response.token && response.user) {
        // Save to localStorage
        localStorage.setItem(TOKEN_KEY, response.token.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(response.user));

        setState({
          user: response.user,
          token: response.token.access_token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });

        return { success: true, message: response.message };
      } else {
        throw new Error(response.message || 'Kayıt başarısız');
      }
    } catch (error: any) {
      let errorMessage = error?.message || 'Kayıt sırasında bir hata oluştu';
      // Alan doğrulamaları
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const passRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/; // 8+ karakter, harf ve rakam
      if (!emailRegex.test(userData.email)) {
        errorMessage = 'Geçerli bir e-posta adresi giriniz.';
      } else if (!passRegex.test(userData.password)) {
        errorMessage = 'Şifreniz en az 8 karakter olmalı ve harf ile rakam içermelidir.';
      } else if (!userData.username || userData.username.trim().length < 3) {
        errorMessage = 'Kullanıcı adı en az 3 karakter olmalıdır.';
      } else if (/email.*kayıtlı/i.test(errorMessage)) {
        errorMessage = 'Bu e-posta adresi zaten kayıtlı. Farklı bir e-posta deneyin.';
      } else if (/kullanıcı adı.*alınmış/i.test(errorMessage)) {
        errorMessage = 'Bu kullanıcı adı zaten alınmış. Başka bir kullanıcı adı seçin.';
      }
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, message: errorMessage };
    }
  }, []);

  /**
   * Logout - Çıkış
   */
  const logout = useCallback(async () => {
    try {
      if (state.token) {
        await AuthApi.logout(state.token);
      }
    } catch (error) {
      // Ignore logout errors
    } finally {
      // Clear localStorage
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);

      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      });
    }
  }, [state.token]);

  /**
   * Update Profile - Profil güncelleme
   */
  const updateProfile = useCallback(async (updates: ProfileUpdateRequest) => {
    if (!state.token) {
      return { success: false, message: 'Oturum açmanız gerekiyor' };
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const updatedUser = await AuthApi.updateProfile(state.token, updates);
      
      // Update localStorage
      localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));

      setState(prev => ({
        ...prev,
        user: updatedUser,
        isLoading: false
      }));

      return { success: true, message: 'Profil güncellendi' };
    } catch (error: any) {
      const errorMessage = error?.message || 'Profil güncellenemedi';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, message: errorMessage };
    }
  }, [state.token]);

  /**
   * Change Password - Şifre değiştirme
   */
  const changePassword = useCallback(async (passwords: ChangePasswordRequest) => {
    if (!state.token) {
      return { success: false, message: 'Oturum açmanız gerekiyor' };
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await AuthApi.changePassword(state.token, passwords);
      
      setState(prev => ({ ...prev, isLoading: false }));

      return { success: true, message: response.message || 'Şifre değiştirildi' };
    } catch (error: any) {
      const errorMessage = error?.message || 'Şifre değiştirilemedi';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      return { success: false, message: errorMessage };
    }
  }, [state.token]);

  /**
   * Clear Error
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    // State
    user: state.user,
    token: state.token,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError
  };
};

