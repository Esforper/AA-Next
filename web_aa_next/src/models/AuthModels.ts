// Auth Models - API Contract Interfaces
import { ApiResponse } from './CommonModels';

/**
 * User Model - Kullanıcı bilgileri
 */
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: 'user' | 'admin';
  bio?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

/**
 * Token Response
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Login Request
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Login Response
 */
export interface LoginResponse {
  success: boolean;
  message: string;
  user: User;
  token: TokenResponse;
}

/**
 * Register Request
 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

/**
 * Register Response
 */
export interface RegisterResponse {
  success: boolean;
  message: string;
  user: User;
  token: TokenResponse;
}

/**
 * Profile Update Request
 */
export interface ProfileUpdateRequest {
  full_name?: string;
  bio?: string;
  avatar_url?: string;
}

/**
 * Change Password Request
 */
export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

/**
 * Auth State
 */
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
