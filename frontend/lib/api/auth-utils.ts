/**
 * Shared Authentication Utilities
 * Centralized auth token management with caching for performance
 */

// Token cache with expiration
let cachedToken: string | null = null;
let tokenExpiry: number = 0;
const TOKEN_CACHE_BUFFER_MS = 60 * 1000; // Refresh 1 minute before expiry

/**
 * Get authentication token from Supabase session with caching
 * Caches the token to avoid repeated Supabase calls
 */
export async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  // Check if cached token is still valid
  const now = Date.now();
  if (cachedToken && tokenExpiry > now + TOKEN_CACHE_BUFFER_MS) {
    return cachedToken;
  }

  try {
    const { createClient } = await import('@/lib/supabase/client');
    const supabase = createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      cachedToken = null;
      tokenExpiry = 0;
      return null;
    }

    // Cache the token
    cachedToken = session.access_token;
    // Calculate expiry from JWT (expires_at is in seconds)
    tokenExpiry = session.expires_at ? session.expires_at * 1000 : now + 3600 * 1000;

    return cachedToken;
  } catch (error) {
    console.error('Error getting auth token:', error);
    cachedToken = null;
    tokenExpiry = 0;
    return null;
  }
}

/**
 * Clear the cached token (call on logout)
 */
export function clearAuthCache(): void {
  cachedToken = null;
  tokenExpiry = 0;
}

/**
 * Check if user is authenticated (without network call if cached)
 */
export function isAuthenticated(): boolean {
  return cachedToken !== null && tokenExpiry > Date.now() + TOKEN_CACHE_BUFFER_MS;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Generic API request helper with authentication
 */
export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An unexpected error occurred',
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
