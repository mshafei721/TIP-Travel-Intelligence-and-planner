/**
 * Settings Types
 * Aligned with backend API models
 * Using camelCase to match API contract (backend uses Pydantic aliases)
 */

// ============================================
// Enums and Constants
// ============================================

export type Theme = 'light' | 'dark' | 'system';
export type ProfileVisibility = 'public' | 'private' | 'friends';
export type DetailLevel = 'brief' | 'balanced' | 'detailed';
export type DateFormat = 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
export type Units = 'metric' | 'imperial';

export const THEME_OPTIONS: { value: Theme; label: string; description: string }[] = [
  { value: 'light', label: 'Light', description: 'Always use light mode' },
  { value: 'dark', label: 'Dark', description: 'Always use dark mode' },
  { value: 'system', label: 'System', description: 'Match your device settings' },
];

export const VISIBILITY_OPTIONS: {
  value: ProfileVisibility;
  label: string;
  description: string;
}[] = [
  { value: 'public', label: 'Public', description: 'Anyone can see your profile' },
  {
    value: 'friends',
    label: 'Friends Only',
    description: 'Only friends can see your profile',
  },
  { value: 'private', label: 'Private', description: 'Only you can see your profile' },
];

export const DETAIL_LEVEL_OPTIONS: { value: DetailLevel; label: string; description: string }[] = [
  { value: 'brief', label: 'Brief', description: 'Basic recommendations' },
  { value: 'balanced', label: 'Balanced', description: 'Balanced detail level' },
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
  language: string;
  timezone: string;
  dateFormat: DateFormat;
  currency: string;
  units: Units;
}

export interface NotificationSettings {
  emailNotifications: boolean;
  emailTripUpdates: boolean;
  emailReportCompletion: boolean;
  emailRecommendations: boolean;
  emailMarketing: boolean;
  emailWeeklyDigest: boolean;
  pushNotifications: boolean;
  pushTripReminders: boolean;
  pushTravelAlerts: boolean;
}

export interface PrivacySettings {
  profileVisibility: ProfileVisibility;
  showTravelHistory: boolean;
  allowTemplateSharing: boolean;
  analyticsOptIn: boolean;
  personalizationOptIn: boolean;
  shareUsageData: boolean;
}

export interface AIPreferences {
  aiTemperature: number;
  preferredDetailLevel: DetailLevel;
  includeBudgetEstimates: boolean;
  includeLocalTips: boolean;
  includeSafetyWarnings: boolean;
  preferredPace: string;
}

export interface UserSettings {
  appearance: AppearanceSettings;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  aiPreferences: AIPreferences;
}

// ============================================
// Update Types (partial updates)
// ============================================

export interface AppearanceSettingsUpdate {
  theme?: Theme;
  language?: string;
  timezone?: string;
  dateFormat?: DateFormat;
  currency?: string;
  units?: Units;
}

export interface NotificationSettingsUpdate {
  emailNotifications?: boolean;
  emailTripUpdates?: boolean;
  emailReportCompletion?: boolean;
  emailRecommendations?: boolean;
  emailMarketing?: boolean;
  emailWeeklyDigest?: boolean;
  pushNotifications?: boolean;
  pushTripReminders?: boolean;
  pushTravelAlerts?: boolean;
}

export interface PrivacySettingsUpdate {
  profileVisibility?: ProfileVisibility;
  showTravelHistory?: boolean;
  allowTemplateSharing?: boolean;
  analyticsOptIn?: boolean;
  personalizationOptIn?: boolean;
  shareUsageData?: boolean;
}

export interface AIPreferencesUpdate {
  aiTemperature?: number;
  preferredDetailLevel?: DetailLevel;
  includeBudgetEstimates?: boolean;
  includeLocalTips?: boolean;
  includeSafetyWarnings?: boolean;
  preferredPace?: string;
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
    exportId: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    downloadUrl: string | null;
    expiresAt: string | null;
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
