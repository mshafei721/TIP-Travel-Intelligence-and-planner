'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { validatePassword, passwordsMatch } from '@/lib/auth/validation';
import type { PasswordStrength } from '@/types/auth';

export interface PasswordResetFormProps {
  onResetPassword: (password: string) => Promise<void>;
  isLoading?: boolean;
  success?: boolean;
  error?: string;
}

export function PasswordResetForm({
  onResetPassword,
  isLoading = false,
  success = false,
  error,
}: PasswordResetFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: '',
  });

  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [touched, setTouched] = useState({
    newPassword: false,
    confirmPassword: false,
  });

  // Redirect to login after success
  useEffect(() => {
    if (success) {
      const timeout = setTimeout(() => {
        router.push('/login');
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [success, router]);

  // Validation
  const passwordValidation = validatePassword(formData.newPassword);
  const confirmPasswordValid = passwordsMatch(formData.newPassword, formData.confirmPassword);

  const formValid = passwordValidation.isValid && confirmPasswordValid;

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
      newPassword: true,
      confirmPassword: true,
    });

    if (!formValid) return;

    await onResetPassword(formData.newPassword);
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

  if (success) {
    return (
      <div className="w-full max-w-md space-y-6">
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>Password Updated Successfully</AlertTitle>
          <AlertDescription>
            Your password has been reset. You can now log in with your new password.
          </AlertDescription>
        </Alert>

        <p className="text-sm text-slate-600 text-center">
          Redirecting to login page in 3 seconds...
        </p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Set New Password</h1>
        <p className="text-sm text-slate-600">Enter a strong password for your account.</p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* New Password Field */}
        <div className="space-y-2">
          <Label htmlFor="newPassword">New Password</Label>
          <div className="relative">
            <Input
              id="newPassword"
              name="newPassword"
              type={showNewPassword ? 'text' : 'password'}
              placeholder="Create a secure password"
              value={formData.newPassword}
              onChange={handleChange('newPassword')}
              onBlur={handleBlur('newPassword')}
              aria-invalid={touched.newPassword && !passwordValidation.isValid}
              disabled={isLoading}
              autoFocus
              required
            />
            <button
              type="button"
              onClick={() => setShowNewPassword(!showNewPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showNewPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {/* Password Strength Indicator */}
          {formData.newPassword && (
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
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
    </div>
  );
}
