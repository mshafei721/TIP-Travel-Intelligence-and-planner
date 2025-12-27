'use client';

import { useState, Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { LoginForm } from '@/components/auth';
import { signIn } from '@/lib/auth/actions';
import { createClient } from '@/lib/supabase/client';
import { getRateLimitState, recordFailedAttempt, clearRateLimit } from '@/lib/auth/rate-limit';
import type { LoginCredentials } from '@/types/auth';

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirectTo') || '/dashboard';
  const urlError = searchParams.get('error');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>(urlError || undefined);
  const [rateLimitState, setRateLimitState] = useState({
    isLocked: false,
    lockedUntil: undefined as string | undefined,
  });

  // Clear URL error param after displaying it
  useEffect(() => {
    if (urlError) {
      // Remove error from URL without reload
      const url = new URL(window.location.href);
      url.searchParams.delete('error');
      window.history.replaceState({}, '', url.toString());
    }
  }, [urlError]);

  const handleLogin = async (credentials: LoginCredentials) => {
    setError(undefined);
    setIsLoading(true);

    // Check rate limit
    const rateLimitCheck = getRateLimitState(credentials.email);
    if (rateLimitCheck.isLocked) {
      setRateLimitState({
        isLocked: true,
        lockedUntil: rateLimitCheck.lockedUntil?.toISOString(),
      });
      setIsLoading(false);
      return;
    }

    try {
      const result = await signIn(credentials);

      if (result.error) {
        // Record failed attempt
        const newState = recordFailedAttempt(credentials.email);
        if (newState.isLocked) {
          setRateLimitState({
            isLocked: true,
            lockedUntil: newState.lockedUntil?.toISOString(),
          });
        }
        setError(result.error);
      } else {
        // Clear rate limit on success
        clearRateLimit(credentials.email);
        router.push(redirectTo);
      }
    } catch {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setError(undefined);
    setIsLoading(true);

    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?redirectTo=${encodeURIComponent(redirectTo)}`,
        },
      });

      if (error) {
        setError(error.message);
        setIsLoading(false);
      }
    } catch {
      setError('An unexpected error occurred. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900">Welcome Back</h1>
          <p className="mt-2 text-sm text-slate-600">Sign in to access your travel intelligence</p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <LoginForm
            onLogin={handleLogin}
            onGoogleAuth={handleGoogleAuth}
            isLoading={isLoading}
            error={error}
            rateLimited={rateLimitState.isLocked}
            lockoutEndsAt={rateLimitState.lockedUntil}
          />
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginContent />
    </Suspense>
  );
}
