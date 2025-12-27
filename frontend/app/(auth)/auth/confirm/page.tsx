'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';

/**
 * OAuth Confirmation Content
 *
 * Handles the PKCE code exchange on the client side.
 * The browser client has access to the code verifier stored
 * in cookies during OAuth initiation.
 */
function AuthConfirmContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const redirectTo = searchParams.get('redirectTo') || '/dashboard';

    if (!code) {
      router.push('/login?error=No authorization code provided');
      return;
    }

    const exchangeCode = async () => {
      try {
        const supabase = createClient();

        const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

        if (exchangeError) {
          console.error('Code exchange error:', exchangeError.message);
          setError(exchangeError.message);
          // Redirect to login with error after a short delay
          setTimeout(() => {
            router.push(`/login?error=${encodeURIComponent(exchangeError.message)}`);
          }, 2000);
          return;
        }

        // Success - redirect to intended destination
        router.push(redirectTo);
      } catch (err) {
        console.error('Unexpected error during code exchange:', err);
        setError('An unexpected error occurred');
        setTimeout(() => {
          router.push('/login?error=Authentication failed');
        }, 2000);
      }
    };

    exchangeCode();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <svg
              className="mx-auto h-12 w-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Authentication Error</h2>
          <p className="text-slate-600">{error}</p>
          <p className="text-sm text-slate-500 mt-2">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Completing sign in...</h2>
        <p className="text-slate-600">Please wait while we verify your credentials.</p>
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Loading...</h2>
      </div>
    </div>
  );
}

export default function AuthConfirmPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <AuthConfirmContent />
    </Suspense>
  );
}
