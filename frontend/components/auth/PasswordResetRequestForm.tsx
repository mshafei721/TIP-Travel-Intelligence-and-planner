'use client';

import { useState } from 'react';
import Link from 'next/link';
import { CheckCircle2, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { validateEmail } from '@/lib/auth/validation';

export interface PasswordResetRequestFormProps {
  onRequestReset: (email: string) => Promise<void>;
  isLoading?: boolean;
  emailSent?: boolean;
}

export function PasswordResetRequestForm({
  onRequestReset,
  isLoading = false,
  emailSent = false,
}: PasswordResetRequestFormProps) {
  const [email, setEmail] = useState('');
  const [touched, setTouched] = useState(false);

  const emailValid = validateEmail(email);
  const formValid = emailValid;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);

    if (!formValid) return;

    await onRequestReset(email.trim());
  };

  if (emailSent) {
    return (
      <div className="w-full max-w-md space-y-6">
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>Check your email</AlertTitle>
          <AlertDescription>
            We&apos;ve sent a password reset link to <strong>{email}</strong>. Click the link in the
            email to reset your password.
          </AlertDescription>
        </Alert>

        <div className="space-y-4">
          <p className="text-sm text-slate-600 text-center">
            Didn&apos;t receive the email? Check your spam folder or request another reset link.
          </p>

          <Button type="button" variant="outline" className="w-full" onClick={() => setEmail('')}>
            <Mail className="h-4 w-4" />
            Send another email
          </Button>

          <Link href="/login">
            <Button type="button" variant="ghost" className="w-full">
              Back to Login
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Reset Password</h1>
        <p className="text-sm text-slate-600">
          Enter your email address and we&apos;ll send you a link to reset your password.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => setTouched(true)}
            aria-invalid={touched && !emailValid}
            disabled={isLoading}
            autoFocus
            required
          />
          {touched && !emailValid && email.trim() !== '' && (
            <p className="text-sm text-red-600">Invalid email address</p>
          )}
        </div>

        {/* Submit Button */}
        <Button type="submit" className="w-full h-11 text-base" disabled={!formValid || isLoading}>
          {isLoading ? 'Sending...' : 'Send Reset Link'}
        </Button>
      </form>

      {/* Back to Login Link */}
      <p className="text-center text-sm text-slate-600">
        <Link href="/login" className="font-medium text-blue-600 hover:text-blue-700">
          Back to Login
        </Link>
      </p>
    </div>
  );
}
