import { API_CONFIG } from './config';
import {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  User,
  ProfileUpdateRequest,
  ChangePasswordRequest
} from '../models/AuthModels';
import { ApiResponse } from '../models/CommonModels';

/**
 * Mock Users Storage Helper
 */
class MockUsersStore {
  private static USERS_KEY = 'aa_mock_users';

  static getAll(): User[] {
    try {
      const stored = localStorage.getItem(this.USERS_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  static findByEmail(email: string): User | null {
    const users = this.getAll();
    return users.find(u => u.email === email) || null;
  }

  static add(user: User): void {
    const users = this.getAll();
    // Email ile kayıtlı kullanıcı varsa güncelle, yoksa ekle
    const index = users.findIndex(u => u.email === user.email);
    if (index >= 0) {
      users[index] = user;
    } else {
      users.push(user);
    }
    localStorage.setItem(this.USERS_KEY, JSON.stringify(users));
  }

  static clear(): void {
    localStorage.removeItem(this.USERS_KEY);
  }
}

/**
 * Auth API Client
 * Backend API Auth endpoints integration
 */
export class AuthApi {
  /**
   * Login - Kullanıcı girişi
   */
  static async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(credentials),
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      // Backend auth henüz aktif değilse mock data kullan
      if (!response.ok && response.status === 404) {
        console.warn('Auth API not available, using mock data');
        
        // Mock users store'dan kayıtlı kullanıcıyı bul
        const registeredUser = MockUsersStore.findByEmail(credentials.email);
        
        if (!registeredUser) {
          throw new Error('Bu email ile kayıtlı kullanıcı bulunamadı. Lütfen önce kayıt olun.');
        }
        
        // Kayıtlı kullanıcı bulundu
        const mockUser: LoginResponse = {
          success: true,
          message: 'Giriş başarılı',
          user: registeredUser,
          token: {
            access_token: `mock_token_${Date.now()}`,
            token_type: 'bearer',
            expires_in: 86400
          }
        };
        
        return mockUser;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Giriş başarısız');
      }

      return data as LoginResponse;
    } catch (error: any) {
      // Backend ulaşılamıyorsa mock kullan
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        console.warn('Backend unreachable, using mock auth');
        
        // Mock users store'dan kayıtlı kullanıcıyı bul
        const registeredUser = MockUsersStore.findByEmail(credentials.email);
        
        if (!registeredUser) {
          throw new Error('Bu email ile kayıtlı kullanıcı bulunamadı. Lütfen önce kayıt olun.');
        }
        
        const mockUser: LoginResponse = {
          success: true,
          message: 'Giriş başarılı',
          user: registeredUser,
          token: {
            access_token: `mock_token_${Date.now()}`,
            token_type: 'bearer',
            expires_in: 86400
          }
        };
        
        return mockUser;
      }
      
      throw new Error(error?.message || 'Giriş sırasında bir hata oluştu');
    }
  }

  /**
   * Register - Kullanıcı kaydı
   */
  static async register(userData: RegisterRequest): Promise<RegisterResponse> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(userData),
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      // Backend auth henüz aktif değilse mock data kullan
      if (!response.ok && response.status === 404) {
        console.warn('Auth API not available, using mock data');
        
        // Email zaten kayıtlı mı kontrol et
        const existingUser = MockUsersStore.findByEmail(userData.email);
        if (existingUser) {
          throw new Error('Bu email adresi zaten kayıtlı');
        }
        
        // Yeni kullanıcı oluştur
        const newUser: User = {
          id: `mock_${Date.now()}`,
          email: userData.email,
          username: userData.username,
          full_name: userData.full_name || userData.username,
          role: 'user',
          is_active: true,
          created_at: new Date().toISOString()
        };
        
        // Mock users store'a ekle
        MockUsersStore.add(newUser);
        
        // Response oluştur
        const mockResponse: RegisterResponse = {
          success: true,
          message: 'Kayıt başarılı',
          user: newUser,
          token: {
            access_token: `mock_token_${Date.now()}`,
            token_type: 'bearer',
            expires_in: 86400
          }
        };
        
        return mockResponse;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Kayıt başarısız');
      }

      return data as RegisterResponse;
    } catch (error: any) {
      // Backend ulaşılamıyorsa mock kullan
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        console.warn('Backend unreachable, using mock auth');
        
        // Email zaten kayıtlı mı kontrol et
        const existingUser = MockUsersStore.findByEmail(userData.email);
        if (existingUser) {
          throw new Error('Bu email adresi zaten kayıtlı');
        }
        
        // Yeni kullanıcı oluştur
        const newUser: User = {
          id: `mock_${Date.now()}`,
          email: userData.email,
          username: userData.username,
          full_name: userData.full_name || userData.username,
          role: 'user',
          is_active: true,
          created_at: new Date().toISOString()
        };
        
        // Mock users store'a ekle
        MockUsersStore.add(newUser);
        
        const mockResponse: RegisterResponse = {
          success: true,
          message: 'Kayıt başarılı',
          user: newUser,
          token: {
            access_token: `mock_token_${Date.now()}`,
            token_type: 'bearer',
            expires_in: 86400
          }
        };
        
        return mockResponse;
      }
      
      throw new Error(error?.message || 'Kayıt sırasında bir hata oluştu');
    }
  }

  /**
   * Get Current User - Mevcut kullanıcı bilgileri
   */
  static async getCurrentUser(token: string): Promise<User> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.ME}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        throw new Error('Kullanıcı bilgileri alınamadı');
      }

      const data = await response.json();
      return data as User;
    } catch (error: any) {
      throw new Error(error?.message || 'Kullanıcı bilgileri alınamadı');
    }
  }

  /**
   * Update Profile - Profil güncelleme
   */
  static async updateProfile(token: string, updates: ProfileUpdateRequest): Promise<User> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.ME}`;
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(updates),
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        throw new Error('Profil güncellenemedi');
      }

      const data = await response.json();
      return data as User;
    } catch (error: any) {
      throw new Error(error?.message || 'Profil güncellenemedi');
    }
  }

  /**
   * Change Password - Şifre değiştirme
   */
  static async changePassword(token: string, passwords: ChangePasswordRequest): Promise<ApiResponse<void>> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.CHANGE_PASSWORD}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(passwords),
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Şifre değiştirilemedi');
      }

      return await response.json();
    } catch (error: any) {
      throw new Error(error?.message || 'Şifre değiştirilemedi');
    }
  }

  /**
   * Logout - Çıkış
   */
  static async logout(token: string): Promise<ApiResponse<void>> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.LOGOUT}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      if (!response.ok) {
        throw new Error('Çıkış yapılamadı');
      }

      return await response.json();
    } catch (error: any) {
      // Logout always succeeds locally
      return { success: true, message: 'Çıkış yapıldı' };
    }
  }

  /**
   * Check Email - Email kontrolü
   */
  static async checkEmail(email: string): Promise<boolean> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.CHECK_EMAIL}/${encodeURIComponent(email)}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      const data = await response.json();
      return data.available === true;
    } catch (error) {
      // Mock mode - check local storage
      const existingUser = MockUsersStore.findByEmail(email);
      return existingUser === null; // Available if not found
    }
  }

  /**
   * Check Username - Username kontrolü
   */
  static async checkUsername(username: string): Promise<boolean> {
    try {
      const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.CHECK_USERNAME}/${encodeURIComponent(username)}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT)
      });

      const data = await response.json();
      return data.available === true;
    } catch (error) {
      // Mock mode - check local storage
      const users = MockUsersStore.getAll();
      return !users.some(u => u.username === username); // Available if not found
    }
  }
}
