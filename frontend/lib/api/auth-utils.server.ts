/**
 * Server-side Authentication Utilities
 * For use in Server Components, Server Actions, and Route Handlers only
 */

import { createClient } from '@/lib/supabase/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Get authentication token on the server side
 */
export async function getServerAuthToken(): Promise<string | null> {
  try {
    const supabase = await createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      return null;
    }

    return session.access_token;
  } catch (error) {
    console.error('Error getting server auth token:', error);
    return null;
  }
}

/**
 * Server-side API request helper with authentication
 * For use in Server Components, Server Actions, and Route Handlers only
 */
export async function serverApiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = await getServerAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    cache: 'no-store', // Disable caching for server components
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An unexpected error occurred',
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}
