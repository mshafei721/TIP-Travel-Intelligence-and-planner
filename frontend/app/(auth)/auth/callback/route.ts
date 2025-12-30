/**
 * OAuth Callback Handler
 *
 * Handles the OAuth code exchange server-side using cookies to store
 * the PKCE code verifier.
 */

import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const error = requestUrl.searchParams.get('error');
  const errorDescription = requestUrl.searchParams.get('error_description');
  const redirectTo = requestUrl.searchParams.get('redirectTo') || '/dashboard';
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

  // Exchange the code for a session server-side
  const cookieStore = await cookies();

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // Ignore errors in Server Components
          }
        },
      },
    },
  );

  const { data: sessionData, error: exchangeError } =
    await supabase.auth.exchangeCodeForSession(code);

  if (exchangeError) {
    console.error('Code exchange error:', exchangeError.message);
    const loginUrl = new URL('/login', origin);
    loginUrl.searchParams.set('error', exchangeError.message);
    return NextResponse.redirect(loginUrl);
  }

  // Check if user has a traveler profile
  // New users should be redirected to onboarding
  if (sessionData?.user) {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/profile/traveler`, {
        headers: {
          Authorization: `Bearer ${sessionData.session?.access_token}`,
        },
      });

      if (response.ok) {
        const travelerProfile = await response.json();
        // If no traveler profile exists, redirect to onboarding
        if (!travelerProfile || !travelerProfile.nationality) {
          const onboardingUrl = new URL('/onboarding', origin);
          return NextResponse.redirect(onboardingUrl);
        }
      } else if (response.status === 404) {
        // No profile found, redirect to onboarding
        const onboardingUrl = new URL('/onboarding', origin);
        return NextResponse.redirect(onboardingUrl);
      }
    } catch (error) {
      console.warn('Could not check traveler profile:', error);
      // Continue to default redirect on error
    }
  }

  // Success - redirect to intended destination
  const successUrl = new URL(redirectTo, origin);
  return NextResponse.redirect(successUrl);
}
