/**
 * Authentication Types
 * Aligned with product spec and Supabase Auth
 */

export interface SignupCredentials {
  email: string;
  password: string;
  name: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export type PasswordStrength = 'weak' | 'medium' | 'strong';

export interface PasswordValidation {
  isValid: boolean;
  strength: PasswordStrength;
  feedback: string[];
  requirements: {
    minLength: boolean;
    hasUppercase: boolean;
    hasLowercase: boolean;
    hasNumber: boolean;
    hasSpecialChar: boolean;
  };
}

export interface AuthError {
  code: string;
  message: string;
  field?: string;
}

export interface RateLimitState {
  attempts: number;
  lockedUntil: Date | null;
  isLocked: boolean;
}

export interface SessionState {
  user: {
    id: string;
    email: string;
    name: string;
    emailVerified: boolean;
  } | null;
  expiresAt: Date | null;
  isAuthenticated: boolean;
}
