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
import { apiRequest } from './auth-utils';

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
  data: AppearanceSettingsUpdate,
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
  data: NotificationSettingsUpdate,
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
  data: PrivacySettingsUpdate,
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
  data: AIPreferencesUpdate,
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
  format: 'json' | 'csv' = 'json',
): Promise<DataExportResponse> {
  return apiRequest<DataExportResponse>('/api/settings/data/export', {
    method: 'POST',
    body: JSON.stringify({ format }),
  });
}
