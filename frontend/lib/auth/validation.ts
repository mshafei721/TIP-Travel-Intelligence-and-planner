/**
 * Authentication Validation Utilities
 * Password strength, email validation, etc.
 */

import type { PasswordValidation, PasswordStrength } from '@/types/auth';

/**
 * Validates email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 255;
}

/**
 * Validates password and returns strength + feedback
 */
export function validatePassword(password: string): PasswordValidation {
  const requirements = {
    minLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecialChar: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
  };

  const feedback: string[] = [];

  if (!requirements.minLength) {
    feedback.push('Password must be at least 8 characters');
  }
  if (!requirements.hasUppercase) {
    feedback.push('Include at least one uppercase letter');
  }
  if (!requirements.hasLowercase) {
    feedback.push('Include at least one lowercase letter');
  }
  if (!requirements.hasNumber) {
    feedback.push('Include at least one number');
  }
  if (!requirements.hasSpecialChar) {
    feedback.push('Include at least one special character');
  }

  const isValid = Object.values(requirements).every(Boolean);
  const strength = calculatePasswordStrength(password, requirements);

  return {
    isValid,
    strength,
    feedback,
    requirements,
  };
}

/**
 * Calculate password strength
 */
function calculatePasswordStrength(
  password: string,
  requirements: Record<string, boolean>,
): PasswordStrength {
  const reqsMet = Object.values(requirements).filter(Boolean).length;

  // Weak: minimum requirements only
  if (reqsMet < 5 || password.length < 8) {
    return 'weak';
  }

  // Strong: 12+ characters with all requirements
  if (password.length >= 12 && reqsMet === 5) {
    return 'strong';
  }

  // Medium: 10+ characters with variety
  if (password.length >= 10) {
    return 'medium';
  }

  return 'weak';
}

/**
 * Validates name format
 */
export function validateName(name: string): boolean {
  return name.trim().length >= 2 && name.trim().length <= 100;
}

/**
 * Check if passwords match
 */
export function passwordsMatch(password: string, confirmPassword: string): boolean {
  return password === confirmPassword && password.length > 0;
}
