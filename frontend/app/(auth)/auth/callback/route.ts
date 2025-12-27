/**
 * OAuth Callback Handler
 * Handles the OAuth redirect from Google and establishes the session
 */

import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import type { Database } from '@/types/database';

/**
 * Sanitize the redirect URL to remove any OAuth codes that might have leaked into it
 */
function sanitizeRedirectUrl(redirectTo: string): string {
  try {
    // Remove any code= parameters from the redirect URL
    const url = new URL(redirectTo, 'http://localhost');
    url.searchParams.delete('code');
    url.searchParams.delete('error');
    url.searchParams.delete('error_description');

    // Return just the pathname + remaining search params
    const cleanPath = url.pathname + (url.search || '');

    // If it's just "/" or empty, go to dashboard
    if (cleanPath === '/' || cleanPath === '' || cleanPath === '/?') {
      return '/dashboard';
    }

    return cleanPath;
  } catch {
    return '/dashboard';
  }
}

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const error = requestUrl.searchParams.get('error');
  const errorDescription = requestUrl.searchParams.get('error_description');
  const rawRedirectTo = requestUrl.searchParams.get('redirectTo') || '/dashboard';
  const redirectTo = sanitizeRedirectUrl(rawRedirectTo);
  const origin = requestUrl.origin;

  // Handle OAuth errors from provider
  if (error) {
    console.error('OAuth error:', error, errorDescription);
    const loginUrl = new URL('/login', origin);
    loginUrl.searchParams.set('error', errorDescription || error);
    return NextResponse.redirect(loginUrl);
  }

  // No code provided
  if (!code) {
    console.error('No code provided in OAuth callback');
    const loginUrl = new URL('/login', origin);
    loginUrl.searchParams.set('error', 'Authentication failed. Please try again.');
    return NextResponse.redirect(loginUrl);
  }

  const cookieStore = await cookies();

  const supabase = createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        },
      },
    },
  );

  try {
    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

    if (exchangeError) {
      console.error('Session exchange error:', exchangeError.message);
      const loginUrl = new URL('/login', origin);
      loginUrl.searchParams.set('error', exchangeError.message);
      return NextResponse.redirect(loginUrl);
    }

    // Success - redirect to intended destination
    return NextResponse.redirect(new URL(redirectTo, origin));
  } catch (err) {
    console.error('Unexpected error in OAuth callback:', err);
    const loginUrl = new URL('/login', origin);
    loginUrl.searchParams.set('error', 'An unexpected error occurred. Please try again.');
    return NextResponse.redirect(loginUrl);
  }
}
