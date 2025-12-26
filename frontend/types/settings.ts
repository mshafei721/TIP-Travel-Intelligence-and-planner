/**
 * Settings Types
 * Aligned with backend API models
 */

// ============================================
// Enums and Constants
// ============================================

export type Theme = 'light' | 'dark' | 'system';
export type ProfileVisibility = 'public' | 'private' | 'friends_only';
export type DetailLevel = 'minimal' | 'standard' | 'detailed';
export type DateFormat = 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
export type Units = 'metric' | 'imperial';

export const THEME_OPTIONS: { value: Theme; label: string; description: string }[] = [
  { value: 'light', label: 'Light', description: 'Always use light mode' },
  { value: 'dark', label: 'Dark', description: 'Always use dark mode' },
  { value: 'system', label: 'System', description: 'Match your device settings' },
];

export const VISIBILITY_OPTIONS: { value: ProfileVisibility; label: string; description: string }[] = [
  { value: 'public', label: 'Public', description: 'Anyone can see your profile' },
  { value: 'friends_only', label: 'Friends Only', description: 'Only friends can see your profile' },
  { value: 'private', label: 'Private', description: 'Only you can see your profile' },
];

export const DETAIL_LEVEL_OPTIONS: { value: DetailLevel; label: string; description: string }[] = [
  { value: 'minimal', label: 'Minimal', description: 'Basic recommendations' },
  { value: 'standard', label: 'Standard', description: 'Balanced detail level' },
  { value: 'detailed', label: 'Detailed', description: 'Comprehensive recommendations' },
];

export const DATE_FORMAT_OPTIONS: { value: DateFormat; label: string; example: string }[] = [
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY', example: '12/26/2025' },
  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY', example: '26/12/2025' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD', example: '2025-12-26' },
];

// ============================================
// Settings Types
// ============================================

export interface AppearanceSettings {
  theme: Theme;
  compact_mode: boolean;
  show_animations: boolean;
  font_size: 'small' | 'medium' | 'large';
}

export interface NotificationSettings {
  email_trip_updates: boolean;
  email_report_ready: boolean;
  email_weekly_digest: boolean;
  email_marketing: boolean;
  push_trip_reminders: boolean;
  push_agent_completion: boolean;
  push_system_alerts: boolean;
}

export interface PrivacySettings {
  profile_visibility: ProfileVisibility;
  show_travel_history: boolean;
  allow_recommendations_sharing: boolean;
  data_collection_consent: boolean;
  analytics_enabled: boolean;
}

export interface AIPreferences {
  detail_level: DetailLevel;
  include_budget_suggestions: boolean;
  include_local_tips: boolean;
  preferred_activity_types: string[];
  excluded_categories: string[];
  language_preference: string;
}

export interface UserSettings {
  appearance: AppearanceSettings;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  ai_preferences: AIPreferences;
}

// ============================================
// Update Types (partial updates)
// ============================================

export interface AppearanceSettingsUpdate {
  theme?: Theme;
  compact_mode?: boolean;
  show_animations?: boolean;
  font_size?: 'small' | 'medium' | 'large';
}

export interface NotificationSettingsUpdate {
  email_trip_updates?: boolean;
  email_report_ready?: boolean;
  email_weekly_digest?: boolean;
  email_marketing?: boolean;
  push_trip_reminders?: boolean;
  push_agent_completion?: boolean;
  push_system_alerts?: boolean;
}

export interface PrivacySettingsUpdate {
  profile_visibility?: ProfileVisibility;
  show_travel_history?: boolean;
  allow_recommendations_sharing?: boolean;
  data_collection_consent?: boolean;
  analytics_enabled?: boolean;
}

export interface AIPreferencesUpdate {
  detail_level?: DetailLevel;
  include_budget_suggestions?: boolean;
  include_local_tips?: boolean;
  preferred_activity_types?: string[];
  excluded_categories?: string[];
  language_preference?: string;
}

// ============================================
// API Response Types
// ============================================

export interface UserSettingsResponse {
  success: boolean;
  data: UserSettings;
}

export interface AppearanceSettingsResponse {
  success: boolean;
  data: AppearanceSettings;
}

export interface NotificationSettingsResponse {
  success: boolean;
  data: NotificationSettings;
}

export interface PrivacySettingsResponse {
  success: boolean;
  data: PrivacySettings;
}

export interface AIPreferencesResponse {
  success: boolean;
  data: AIPreferences;
}

export interface DataExportResponse {
  success: boolean;
  message: string;
  data: {
    export_id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    download_url: string | null;
    expires_at: string | null;
  };
}

// ============================================
// Activity Types Options
// ============================================

export const ACTIVITY_TYPES = [
  'Adventure',
  'Beach',
  'Cultural',
  'Culinary',
  'Historical',
  'Nature',
  'Nightlife',
  'Relaxation',
  'Shopping',
  'Sports',
  'Wildlife',
] as const;

export const EXCLUDED_CATEGORIES = [
  'Extreme Sports',
  'Gambling',
  'Adult Entertainment',
  'Religious Sites',
  'Political Sites',
  'High Altitude',
  'Water Activities',
] as const;
