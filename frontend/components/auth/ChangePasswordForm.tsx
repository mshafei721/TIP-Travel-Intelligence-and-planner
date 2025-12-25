'use client';

import { useState } from 'react';
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { validatePassword, passwordsMatch } from '@/lib/auth/validation';
import type { ChangePasswordData, PasswordStrength } from '@/types/auth';

export interface ChangePasswordFormProps {
  onChangePassword: (data: ChangePasswordData) => Promise<void>;
  isLoading?: boolean;
  success?: boolean;
  error?: string;
}

export function ChangePasswordForm({
  onChangePassword,
  isLoading = false,
  success = false,
  error,
}: ChangePasswordFormProps) {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [touched, setTouched] = useState({
    currentPassword: false,
    newPassword: false,
    confirmPassword: false,
  });

  // Validation
  const currentPasswordValid = formData.currentPassword.length > 0;
  const passwordValidation = validatePassword(formData.newPassword);
  const confirmPasswordValid = passwordsMatch(formData.newPassword, formData.confirmPassword);

  const formValid = currentPasswordValid && passwordValidation.isValid && confirmPasswordValid;

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
      currentPassword: true,
      newPassword: true,
      confirmPassword: true,
    });

    if (!formValid) return;

    await onChangePassword(formData);

    // Clear form on success
    if (success) {
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setTouched({
        currentPassword: false,
        newPassword: false,
        confirmPassword: false,
      });
    }
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
      {/* Success Alert */}
      {success && (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>Password updated successfully</AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Current Password Field */}
        <div className="space-y-2">
          <Label htmlFor="currentPassword">Current Password</Label>
          <div className="relative">
            <Input
              id="currentPassword"
              name="currentPassword"
              type={showCurrentPassword ? 'text' : 'password'}
              placeholder="Enter current password"
              value={formData.currentPassword}
              onChange={handleChange('currentPassword')}
              onBlur={handleBlur('currentPassword')}
              aria-invalid={touched.currentPassword && !currentPasswordValid}
              disabled={isLoading}
              required
            />
            <button
              type="button"
              onClick={() => setShowCurrentPassword(!showCurrentPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* New Password Field */}
        <div className="space-y-2">
          <Label htmlFor="newPassword">New Password</Label>
          <div className="relative">
            <Input
              id="newPassword"
              name="newPassword"
              type={showNewPassword ? 'text' : 'password'}
              placeholder="Enter new password"
              value={formData.newPassword}
              onChange={handleChange('newPassword')}
              onBlur={handleBlur('newPassword')}
              aria-invalid={touched.newPassword && !passwordValidation.isValid}
              disabled={isLoading}
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

        {/* Confirm New Password Field */}
        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm New Password</Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter new password"
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
        <Button type="submit" className="w-full" disabled={!formValid || isLoading}>
          {isLoading ? 'Updating...' : 'Update Password'}
        </Button>
      </form>
    </div>
  );
}
