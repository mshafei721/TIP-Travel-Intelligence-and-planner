/**
 * Settings API Client
 * API functions for user settings management
 */

import type {
  UserSettingsResponse,
  AppearanceSettingsResponse,
  NotificationSettingsResponse,
  PrivacySettingsResponse,
  AIPreferencesResponse,
  DataExportResponse,
  AppearanceSettingsUpdate,
  NotificationSettingsUpdate,
  PrivacySettingsUpdate,
  AIPreferencesUpdate,
} from '@/types/settings';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Get authentication token from Supabase session
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  try {
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
// Settings API Functions
// ============================================

/**
 * Get all user settings
 */
export async function getAllSettings(): Promise<UserSettingsResponse> {
  return apiRequest<UserSettingsResponse>('/api/settings');
}

/**
 * Update all user settings
 */
export async function updateAllSettings(data: {
  appearance?: AppearanceSettingsUpdate;
  notifications?: NotificationSettingsUpdate;
  privacy?: PrivacySettingsUpdate;
  ai_preferences?: AIPreferencesUpdate;
}): Promise<UserSettingsResponse> {
  return apiRequest<UserSettingsResponse>('/api/settings', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Appearance Settings
// ============================================

/**
 * Get appearance settings
 */
export async function getAppearanceSettings(): Promise<AppearanceSettingsResponse> {
  return apiRequest<AppearanceSettingsResponse>('/api/settings/appearance');
}

/**
 * Update appearance settings
 */
export async function updateAppearanceSettings(
  data: AppearanceSettingsUpdate
): Promise<AppearanceSettingsResponse> {
  return apiRequest<AppearanceSettingsResponse>('/api/settings/appearance', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Notification Settings
// ============================================

/**
 * Get notification settings
 */
export async function getNotificationSettings(): Promise<NotificationSettingsResponse> {
  return apiRequest<NotificationSettingsResponse>('/api/settings/notifications');
}

/**
 * Update notification settings
 */
export async function updateNotificationSettings(
  data: NotificationSettingsUpdate
): Promise<NotificationSettingsResponse> {
  return apiRequest<NotificationSettingsResponse>('/api/settings/notifications', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Privacy Settings
// ============================================

/**
 * Get privacy settings
 */
export async function getPrivacySettings(): Promise<PrivacySettingsResponse> {
  return apiRequest<PrivacySettingsResponse>('/api/settings/privacy');
}

/**
 * Update privacy settings
 */
export async function updatePrivacySettings(
  data: PrivacySettingsUpdate
): Promise<PrivacySettingsResponse> {
  return apiRequest<PrivacySettingsResponse>('/api/settings/privacy', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// AI Preferences
// ============================================

/**
 * Get AI preferences
 */
export async function getAIPreferences(): Promise<AIPreferencesResponse> {
  return apiRequest<AIPreferencesResponse>('/api/settings/ai');
}

/**
 * Update AI preferences
 */
export async function updateAIPreferences(
  data: AIPreferencesUpdate
): Promise<AIPreferencesResponse> {
  return apiRequest<AIPreferencesResponse>('/api/settings/ai', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ============================================
// Data Export
// ============================================

/**
 * Request data export (GDPR)
 */
export async function requestDataExport(
  format: 'json' | 'csv' = 'json'
): Promise<DataExportResponse> {
  return apiRequest<DataExportResponse>('/api/settings/data/export', {
    method: 'POST',
    body: JSON.stringify({ format }),
  });
}
