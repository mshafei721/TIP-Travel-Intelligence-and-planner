'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Eye, EyeOff, AlertCircle, CheckCircle2, Chrome } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  validateEmail,
  validatePassword,
  validateName,
  passwordsMatch,
} from '@/lib/auth/validation';
import type { SignupCredentials, PasswordStrength } from '@/types/auth';

export interface SignupFormProps {
  onSignup: (credentials: SignupCredentials) => Promise<void>;
  onGoogleAuth: () => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

export function SignupForm({ onSignup, onGoogleAuth, isLoading = false, error }: SignupFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [touched, setTouched] = useState({
    name: false,
    email: false,
    password: false,
    confirmPassword: false,
  });

  // Validation
  const nameValid = validateName(formData.name);
  const emailValid = validateEmail(formData.email);
  const passwordValidation = validatePassword(formData.password);
  const confirmPasswordValid = passwordsMatch(formData.password, formData.confirmPassword);

  const formValid =
    nameValid &&
    emailValid &&
    passwordValidation.isValid &&
    confirmPasswordValid &&
    formData.name.trim() !== '' &&
    formData.email.trim() !== '' &&
    formData.password !== '' &&
    formData.confirmPassword !== '';

  const handleChange =
    (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const handleBlur = (field: keyof typeof touched) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({
      name: true,
      email: true,
      password: true,
      confirmPassword: true,
    });

    if (!formValid) return;

    await onSignup({
      name: formData.name.trim(),
      email: formData.email.trim(),
      password: formData.password,
    });
  };

  const getStrengthColor = (strength: PasswordStrength) => {
    switch (strength) {
      case 'weak':
        return 'text-red-600';
      case 'medium':
        return 'text-amber-600';
      case 'strong':
        return 'text-green-600';
    }
  };

  return (
    <div className="w-full max-w-md space-y-6">
      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Google OAuth Button */}
      <Button
        type="button"
        variant="outline"
        className="w-full h-11 text-base"
        onClick={onGoogleAuth}
        disabled={isLoading}
      >
        <Chrome className="h-5 w-5" />
        Continue with Google
      </Button>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-slate-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-slate-500">Or</span>
        </div>
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name Field */}
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            name="name"
            type="text"
            placeholder="Enter your full name"
            value={formData.name}
            onChange={handleChange('name')}
            onBlur={handleBlur('name')}
            aria-invalid={touched.name && !nameValid}
            disabled={isLoading}
            autoFocus
            required
          />
          {touched.name && !nameValid && formData.name.trim() !== '' && (
            <p className="text-sm text-red-600">Name must be 2-100 characters</p>
          )}
        </div>

        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange('email')}
            onBlur={handleBlur('email')}
            aria-invalid={touched.email && !emailValid}
            disabled={isLoading}
            required
          />
          {touched.email && !emailValid && formData.email.trim() !== '' && (
            <p className="text-sm text-red-600">Invalid email address</p>
          )}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a secure password"
              value={formData.password}
              onChange={handleChange('password')}
              onBlur={handleBlur('password')}
              aria-invalid={touched.password && !passwordValidation.isValid}
              disabled={isLoading}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {/* Password Strength Indicator */}
          {formData.password && (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-600">Strength:</span>
                <span
                  className={`text-sm font-medium ${getStrengthColor(passwordValidation.strength)}`}
                >
                  {passwordValidation.strength.charAt(0).toUpperCase() +
                    passwordValidation.strength.slice(1)}
                </span>
              </div>
              {passwordValidation.feedback.length > 0 && (
                <ul className="text-sm text-slate-600 space-y-1">
                  {passwordValidation.feedback.map((item, index) => (
                    <li key={index} className="flex items-center gap-1">
                      <AlertCircle className="h-3 w-3 text-red-500" />
                      {item}
                    </li>
                  ))}
                </ul>
              )}
              {passwordValidation.isValid && (
                <div className="flex items-center gap-1 text-sm text-green-600">
                  <CheckCircle2 className="h-3 w-3" />
                  All requirements met
                </div>
              )}
            </div>
          )}
        </div>

        {/* Confirm Password Field */}
        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter your password"
              value={formData.confirmPassword}
              onChange={handleChange('confirmPassword')}
              onBlur={handleBlur('confirmPassword')}
              aria-invalid={touched.confirmPassword && !confirmPasswordValid}
              disabled={isLoading}
              required
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {touched.confirmPassword && !confirmPasswordValid && formData.confirmPassword !== '' && (
            <p className="text-sm text-red-600">Passwords do not match</p>
          )}
        </div>

        {/* Submit Button */}
        <Button type="submit" className="w-full h-11 text-base" disabled={!formValid || isLoading}>
          {isLoading ? 'Signing up...' : 'Sign Up'}
        </Button>
      </form>

      {/* Login Link */}
      <p className="text-center text-sm text-slate-600">
        Already have an account?{' '}
        <Link href="/login" className="font-medium text-blue-600 hover:text-blue-700">
          Log in
        </Link>
      </p>
    </div>
  );
}
