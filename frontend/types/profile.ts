/**
 * User Profile & Settings Types
 * Aligned with backend API and database schema
 */

// ============================================
// Core Profile Types (from database schema)
// ============================================

export interface UserProfile {
  id: string;
  display_name: string | null;
  avatar_url: string | null;
  preferences: UserPreferences;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  display_name?: string | null;
  avatar_url?: string | null;
}

export type TravelStyle = 'budget' | 'balanced' | 'luxury';

export interface TravelerProfile {
  id: string;
  user_id: string;
  nationality: string; // ISO Alpha-2 country code (e.g., "US")
  residency_country: string; // ISO Alpha-2 country code
  residency_status: string;
  date_of_birth: string | null; // ISO date format (YYYY-MM-DD)
  travel_style: TravelStyle;
  dietary_restrictions: string[]; // JSONB array
  accessibility_needs: string | null;
  created_at: string;
  updated_at: string;
}

export interface TravelerProfileUpdate {
  nationality?: string;
  residency_country?: string;
  residency_status?: string;
  date_of_birth?: string | null;
  travel_style?: TravelStyle;
  dietary_restrictions?: string[];
  accessibility_needs?: string | null;
}

export type Units = 'metric' | 'imperial';

export interface UserPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  marketing_emails: boolean;
  language: string; // ISO 639-1 language code (e.g., "en")
  currency: string; // ISO 4217 currency code (e.g., "USD")
  units: Units;
}

export interface AccountDeletionRequest {
  confirmation: string; // Must be "DELETE MY ACCOUNT"
}

// ============================================
// API Response Types
// ============================================

export interface ProfileResponse {
  user: UserProfile;
  travelerProfile: TravelerProfile | null;
  notificationSettings: {
    deletionReminders: boolean;
    reportCompletion: boolean;
    productUpdates: boolean;
  };
}

export interface TravelStatistics {
  totalTrips: number;
  countriesVisited: number;
  destinationsExplored: number;
  activeTrips: number;
}

// ============================================
// Form Validation Types
// ============================================

export interface ProfileFormErrors {
  display_name?: string;
  avatar_url?: string;
}

export interface TravelerProfileFormErrors {
  nationality?: string;
  residency_country?: string;
  residency_status?: string;
  date_of_birth?: string;
  travel_style?: string;
  dietary_restrictions?: string;
  accessibility_needs?: string;
}

export interface PreferencesFormErrors {
  language?: string;
  currency?: string;
  units?: string;
}

export type SaveState = 'idle' | 'saving' | 'saved' | 'error';

// ============================================
// Constants and Options
// ============================================

export const DIETARY_RESTRICTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Dairy-Free',
  'Nut-Free',
  'Halal',
  'Kosher',
  'Pescatarian',
  'Low-Carb',
  'Other',
] as const;

export const TRAVEL_STYLES: { value: TravelStyle; label: string; description: string }[] = [
  {
    value: 'budget',
    label: 'Budget',
    description: 'Cost-effective options, hostels, local transport',
  },
  {
    value: 'balanced',
    label: 'Balanced',
    description: 'Mix of comfort and value, mid-range hotels',
  },
  {
    value: 'luxury',
    label: 'Luxury',
    description: 'Premium experiences, 4-5 star hotels, private transport',
  },
] as const;

export const CURRENCY_OPTIONS = [
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
] as const;

export const LANGUAGE_OPTIONS = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' },
  { code: 'it', name: 'Italiano' },
  { code: 'pt', name: 'Português' },
  { code: 'ja', name: '日本語' },
  { code: 'ko', name: '한국어' },
  { code: 'zh', name: '中文' },
  { code: 'ar', name: 'العربية' },
  { code: 'hi', name: 'हिन्दी' },
  { code: 'ru', name: 'Русский' },
] as const;

// ============================================
// Legacy Types (keeping for compatibility)
// ============================================

/**
 * Legacy UserProfile interface for component compatibility.
 * Uses camelCase field names instead of snake_case database names.
 * Used by ProfileSection and other UI components.
 */
export interface LegacyUserProfile {
  id: string;
  name: string;
  email: string;
  photoUrl?: string;
  authProvider: 'email' | 'google';
  createdAt: string;
  updatedAt: string;
}

/** @deprecated Use UserProfile instead */
export interface TravelerDetails {
  nationality: string;
  residenceCountry: string;
  residencyStatus: 'citizen' | 'permanent_resident' | 'temporary_resident' | 'visitor';
  dateOfBirth: string;
}

/** @deprecated Use TravelerProfile instead */
export interface TravelPreferences {
  travelStyle: TravelStyle;
  dietaryRestrictions: string[];
  accessibilityNeeds?: string;
}

// ============================================
// Trip Template Types (aligned with backend)
// ============================================

export interface TripTemplatePreferences {
  travel_style?: TravelStyle;
  dietary_restrictions?: string[];
  accessibility_needs?: string | null;
}

export interface TemplateDestination {
  country: string;
  city?: string;
  suggested_days?: number;
  highlights?: string[];
}

export interface TripTemplate {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  cover_image?: string | null;
  is_public: boolean;
  tags: string[];
  traveler_details: Record<string, unknown> | null;
  destinations: TemplateDestination[];
  preferences: TripTemplatePreferences | null;
  typical_duration?: number | null;
  estimated_budget?: number | null;
  currency: string;
  use_count: number;
  created_at: string;
  updated_at: string;
}

export interface PublicTemplate {
  id: string;
  name: string;
  description: string | null;
  cover_image?: string | null;
  tags: string[];
  destinations: TemplateDestination[];
  typical_duration?: number | null;
  estimated_budget?: number | null;
  currency: string;
  use_count: number;
  created_at: string;
}

export interface TripTemplateCreate {
  name: string;
  description?: string | null;
  cover_image?: string | null;
  is_public?: boolean;
  tags?: string[];
  traveler_details?: Record<string, unknown> | null;
  destinations: TemplateDestination[];
  preferences?: TripTemplatePreferences | null;
  typical_duration?: number;
  estimated_budget?: number;
  currency?: string;
}

export interface TripTemplateUpdate {
  name?: string;
  description?: string | null;
  cover_image?: string | null;
  is_public?: boolean;
  tags?: string[];
  traveler_details?: Record<string, unknown> | null;
  destinations?: TemplateDestination[];
  preferences?: TripTemplatePreferences | null;
  typical_duration?: number;
  estimated_budget?: number;
  currency?: string;
}

export interface CreateTripFromTemplateRequest {
  title?: string;
  start_date?: string;
  end_date?: string;
  override_traveler_details?: Record<string, unknown>;
  override_preferences?: Record<string, unknown>;
}

// ============================================
// Travel History Types
// ============================================

export interface TravelHistoryEntry {
  trip_id: string;
  destination: string;
  country: string;
  start_date: string;
  end_date: string;
  status: 'completed' | 'cancelled';
  user_rating?: number | null;
  user_notes?: string | null;
  is_archived: boolean;
  archived_at?: string | null;
  cover_image?: string | null;
}

export interface TravelStats {
  total_trips: number;
  countries_visited: number;
  cities_visited: number;
  total_days_traveled: number;
  favorite_destination?: string | null;
  most_visited_country?: string | null;
  travel_streak: number;
}

export interface CountryVisit {
  country_code: string;
  country_name: string;
  visit_count: number;
  last_visited?: string | null;
  cities: string[];
}

export interface TravelHistoryResponse {
  entries: TravelHistoryEntry[];
  total_count: number;
}

export interface TravelStatsResponse {
  stats: TravelStats;
  countries: CountryVisit[];
}

export interface TravelTimelineEntry {
  trip_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  status: string;
  thumbnail?: string | null;
}

export interface TravelTimelineResponse {
  entries: TravelTimelineEntry[];
  years: number[];
}

export interface TripRatingRequest {
  rating: number; // 1-5
  notes?: string;
}

export interface ArchiveResponse {
  trip_id: string;
  is_archived: boolean;
  archived_at?: string | null;
  message: string;
}

// ============================================
// Legacy Types (for backwards compatibility)
// ============================================

/** @deprecated Use TripTemplate instead */
export interface LegacyTripTemplate {
  id: string;
  name: string;
  destinations: string[];
  datePattern: string;
  preferences: TravelPreferences;
  createdAt: string;
  updatedAt: string;
}

/** @deprecated Use UserPreferences instead */
export interface NotificationSettings {
  deletionReminders: boolean;
  reportCompletion: boolean;
  productUpdates: boolean;
}

/** @deprecated Use UserPreferences instead */
export interface PrivacySettings {
  dataRetentionAcknowledged: boolean;
  allowAnalytics: boolean;
}

/** @deprecated Use ProfileResponse with adapters */
export interface ProfileSettings {
  profile: LegacyUserProfile;
  travelerDetails: TravelerDetails;
  travelPreferences: TravelPreferences;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  templates: TripTemplate[];
}

/** @deprecated */
export interface ValidationErrors {
  [key: string]: string | undefined;
}
