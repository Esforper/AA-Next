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

  // Hybrid Storage - hem localStorage hem sessionStorage
  const TOKEN_KEY = 'aa_auth_token';
  const USER_KEY = 'aa_user';

  // Storage helper functions
  const getStorageValue = (key: string): string | null => {
    // Önce localStorage'dan kontrol et (kalıcı)
    const localValue = localStorage.getItem(key);
    if (localValue) return localValue;
    
    // Yoksa sessionStorage'dan al (geçici)
    return sessionStorage.getItem(key);
  };

  const setStorageValue = (key: string, value: string): void => {
    // Her ikisine de kaydet
    localStorage.setItem(key, value);
    sessionStorage.setItem(key, value);
  };

  const removeStorageValue = (key: string): void => {
    // Her ikisinden de sil
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  };

  /**
   * Initialize - Token varsa kullanıcıyı yükle
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = getStorageValue(TOKEN_KEY);
        const savedUser = getStorageValue(USER_KEY);

        // Debug: Auth initialization
        if (process.env.NODE_ENV === 'development') {
          console.log('🔍 Auth Init Debug:', {
            hasToken: !!savedToken,
            hasUser: !!savedUser,
            tokenLength: savedToken?.length,
            userData: savedUser ? JSON.parse(savedUser) : null
          });
        }

        if (savedToken && savedUser) {
          // Parse saved user first
          const parsedUser = JSON.parse(savedUser);
          
          // Set auth state immediately with cached data (optimistic update)
          setState({
            user: parsedUser,
            token: savedToken,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });

          // Verify token with backend in background (optional)
          try {
            if (process.env.NODE_ENV === 'development') {
              console.log('🔄 Verifying token with backend...');
            }
            const user = await AuthApi.getCurrentUser(savedToken);
            if (process.env.NODE_ENV === 'development') {
              console.log('✅ Token verified, user:', user.username);
            }
            // Update with fresh data from backend
            setState({
              user,
              token: savedToken,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
            // Sync to storage
            setStorageValue(USER_KEY, JSON.stringify(user));
          } catch (error) {
            // Token verification failed, but keep user logged in with cached data
            // Only logout if it's a 401/403 (unauthorized)
            if (process.env.NODE_ENV === 'development') {
              console.log('⚠️ Token verification failed (keeping cached session):', error);
            }
            // Don't remove token unless it's explicitly unauthorized
            // This allows offline/network error scenarios
          }
        } else {
          if (process.env.NODE_ENV === 'development') {
            console.log('⚠️ No token or user data found');
          }
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
        // Save to hybrid storage (hem kalıcı hem güvenli)
        setStorageValue(TOKEN_KEY, response.token.access_token);
        setStorageValue(USER_KEY, JSON.stringify(response.user));

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
        // Save to hybrid storage (hem kalıcı hem güvenli)
        setStorageValue(TOKEN_KEY, response.token.access_token);
        setStorageValue(USER_KEY, JSON.stringify(response.user));

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
      // Clear hybrid storage
      removeStorageValue(TOKEN_KEY);
      removeStorageValue(USER_KEY);

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
      
      // Update hybrid storage
      setStorageValue(USER_KEY, JSON.stringify(updatedUser));

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

