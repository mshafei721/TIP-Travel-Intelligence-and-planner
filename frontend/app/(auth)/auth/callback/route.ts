/**
 * OAuth Callback Handler
 *
 * This route redirects to a client-side page that handles the PKCE
 * code exchange. The browser client has access to the code verifier
 * stored in cookies during OAuth initiation.
 */

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

  // Redirect to client-side page to handle PKCE code exchange
  // The browser client has access to the code verifier in cookies
  const confirmUrl = new URL('/auth/confirm', origin);
  confirmUrl.searchParams.set('code', code);
  confirmUrl.searchParams.set('redirectTo', redirectTo);

  return NextResponse.redirect(confirmUrl);
}
