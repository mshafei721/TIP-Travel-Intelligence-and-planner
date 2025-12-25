/**
 * Profile API Client
 *
 * API functions for user profile, traveler profile, and preferences management
 */

import type {
  UserProfile,
  UserProfileUpdate,
  TravelerProfile,
  TravelerProfileUpdate,
  UserPreferences,
  AccountDeletionRequest,
  ProfileResponse,
  TravelStatistics,
} from '@/types/profile';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Get authentication token from Supabase session
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  try {
    // Dynamically import Supabase client (browser-only)
    const { createClient } = await import('@/lib/supabase/client');
    const supabase = createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      console.warn('Failed to get Supabase session:', error);
      return null;
    }

    return session.access_token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

/**
 * Generic API request helper
 */
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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

// ============================================
// Profile API Functions
// ============================================

/**
 * Get complete user profile including traveler profile and notification settings
 */
export async function getProfile(): Promise<ProfileResponse> {
  return apiRequest<ProfileResponse>('/api/profile');
}

/**
 * Update user profile (display name and/or avatar URL)
 */
export async function updateProfile(data: UserProfileUpdate): Promise<UserProfile> {
  return apiRequest<UserProfile>('/api/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Get user travel statistics
 */
export async function getStatistics(): Promise<TravelStatistics> {
  const response = await apiRequest<{ statistics: TravelStatistics }>('/api/profile/statistics');
  return response.statistics;
}

// ============================================
// Traveler Profile API Functions
// ============================================

/**
 * Get traveler profile
 */
export async function getTravelerProfile(): Promise<TravelerProfile | null> {
  return apiRequest<TravelerProfile | null>('/api/profile/traveler');
}

/**
 * Create or update traveler profile
 */
export async function updateTravelerProfile(data: TravelerProfileUpdate): Promise<TravelerProfile> {
  return apiRequest<TravelerProfile>('/api/profile/traveler', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Preferences API Functions
// ============================================

/**
 * Update user preferences (notifications, language, currency, units)
 */
export async function updatePreferences(data: UserPreferences): Promise<UserProfile> {
  return apiRequest<UserProfile>('/api/profile/preferences', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Account Deletion
// ============================================

/**
 * Delete user account permanently
 * Requires confirmation text: "DELETE MY ACCOUNT"
 */
export async function deleteAccount(
  data: AccountDeletionRequest,
): Promise<{ message: string; user_id: string }> {
  return apiRequest<{ message: string; user_id: string }>('/api/profile', {
    method: 'DELETE',
    body: JSON.stringify(data),
  });
}

// ============================================
// Validation Helpers
// ============================================

/**
 * Validate country code (ISO Alpha-2)
 */
export function isValidCountryCode(code: string): boolean {
  return /^[A-Z]{2}$/.test(code);
}

/**
 * Validate currency code (ISO 4217)
 */
export function isValidCurrencyCode(code: string): boolean {
  return /^[A-Z]{3}$/.test(code);
}

/**
 * Validate language code (ISO 639-1)
 */
export function isValidLanguageCode(code: string): boolean {
  return /^[a-z]{2}(-[A-Z]{2})?$/.test(code);
}

/**
 * Validate date of birth (must be in the past)
 */
export function isValidDateOfBirth(dateString: string): boolean {
  try {
    const date = new Date(dateString);
    const now = new Date();
    return date < now && date.getFullYear() > 1900;
  } catch {
    return false;
  }
}
