/**
 * User Profile & Settings Types
 * Aligned with backend API and database schema
 * Using camelCase to match API contract (backend uses Pydantic aliases)
 */

// ============================================
// Core Profile Types (from database schema)
// ============================================

export interface UserProfile {
  id: string;
  displayName: string | null;
  avatarUrl: string | null;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
}

export interface UserProfileUpdate {
  displayName?: string | null;
  avatarUrl?: string | null;
}

export type TravelStyle = 'budget' | 'balanced' | 'luxury';

export interface TravelerProfile {
  id: string;
  userId: string;
  nationality: string; // ISO Alpha-2 country code (e.g., "US")
  residencyCountry: string; // ISO Alpha-2 country code
  residencyStatus: string;
  dateOfBirth: string | null; // ISO date format (YYYY-MM-DD)
  travelStyle: TravelStyle;
  dietaryRestrictions: string[]; // JSONB array
  accessibilityNeeds: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface TravelerProfileUpdate {
  nationality?: string;
  residencyCountry?: string;
  residencyStatus?: string;
  dateOfBirth?: string | null;
  travelStyle?: TravelStyle;
  dietaryRestrictions?: string[];
  accessibilityNeeds?: string | null;
}

export type Units = 'metric' | 'imperial';

export interface UserPreferences {
  emailNotifications: boolean;
  pushNotifications: boolean;
  marketingEmails: boolean;
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
  displayName?: string;
  avatarUrl?: string;
}

export interface TravelerProfileFormErrors {
  nationality?: string;
  residencyCountry?: string;
  residencyStatus?: string;
  dateOfBirth?: string;
  travelStyle?: string;
  dietaryRestrictions?: string;
  accessibilityNeeds?: string;
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
  travelStyle?: TravelStyle;
  dietaryRestrictions?: string[];
  accessibilityNeeds?: string | null;
}

export interface TemplateDestination {
  country: string;
  city?: string;
  suggestedDays?: number;
  highlights?: string[];
}

export interface TripTemplate {
  id: string;
  userId: string;
  name: string;
  description: string | null;
  coverImage?: string | null;
  isPublic: boolean;
  tags: string[];
  travelerDetails: Record<string, unknown> | null;
  destinations: TemplateDestination[];
  preferences: TripTemplatePreferences | null;
  typicalDuration?: number | null;
  estimatedBudget?: number | null;
  currency: string;
  useCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface PublicTemplate {
  id: string;
  name: string;
  description: string | null;
  coverImage?: string | null;
  tags: string[];
  destinations: TemplateDestination[];
  typicalDuration?: number | null;
  estimatedBudget?: number | null;
  currency: string;
  useCount: number;
  createdAt: string;
}

export interface TripTemplateCreate {
  name: string;
  description?: string | null;
  coverImage?: string | null;
  isPublic?: boolean;
  tags?: string[];
  travelerDetails?: Record<string, unknown> | null;
  destinations: TemplateDestination[];
  preferences?: TripTemplatePreferences | null;
  typicalDuration?: number;
  estimatedBudget?: number;
  currency?: string;
}

export interface TripTemplateUpdate {
  name?: string;
  description?: string | null;
  coverImage?: string | null;
  isPublic?: boolean;
  tags?: string[];
  travelerDetails?: Record<string, unknown> | null;
  destinations?: TemplateDestination[];
  preferences?: TripTemplatePreferences | null;
  typicalDuration?: number;
  estimatedBudget?: number;
  currency?: string;
}

export interface CreateTripFromTemplateRequest {
  title?: string;
  startDate?: string;
  endDate?: string;
  overrideTravelerDetails?: Record<string, unknown>;
  overridePreferences?: Record<string, unknown>;
}

// ============================================
// Travel History Types
// ============================================

export interface TravelHistoryEntry {
  tripId: string;
  destination: string;
  country: string;
  startDate: string;
  endDate: string;
  status: 'completed' | 'cancelled';
  userRating?: number | null;
  userNotes?: string | null;
  isArchived: boolean;
  archivedAt?: string | null;
  coverImage?: string | null;
}

export interface TravelStats {
  totalTrips: number;
  countriesVisited: number;
  citiesVisited: number;
  totalDaysTraveled: number;
  favoriteDestination?: string | null;
  mostVisitedCountry?: string | null;
  travelStreak: number;
}

export interface CountryVisit {
  countryCode: string;
  countryName: string;
  visitCount: number;
  lastVisited?: string | null;
  cities: string[];
}

export interface TravelHistoryResponse {
  entries: TravelHistoryEntry[];
  totalCount: number;
}

export interface TravelStatsResponse {
  stats: TravelStats;
  countries: CountryVisit[];
}

export interface TravelTimelineEntry {
  tripId: string;
  title: string;
  destination: string;
  startDate: string;
  endDate: string;
  durationDays: number;
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
  tripId: string;
  isArchived: boolean;
  archivedAt?: string | null;
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
