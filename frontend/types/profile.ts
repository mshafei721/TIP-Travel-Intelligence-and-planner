/**
 * User Profile & Settings Types
 * Used for profile management, traveler details, preferences, and templates
 */

export interface UserProfile {
  id: string
  name: string
  email: string
  photoUrl?: string
  authProvider: 'email' | 'google'
  createdAt: string
  updatedAt: string
}

export interface TravelerDetails {
  nationality: string // ISO Alpha-2 code (e.g., "US")
  residenceCountry: string // ISO Alpha-2 code
  residencyStatus: 'citizen' | 'permanent_resident' | 'temporary_resident' | 'visitor'
  dateOfBirth: string // ISO date format (YYYY-MM-DD)
}

export type TravelStyle = 'relaxed' | 'balanced' | 'packed' | 'budget-focused'

export interface TravelPreferences {
  travelStyle: TravelStyle
  dietaryRestrictions: string[] // e.g., ["vegetarian", "gluten-free"]
  accessibilityNeeds?: string
}

export interface TripTemplate {
  id: string
  name: string
  destinations: string[] // Country/city names
  datePattern: string // e.g., "Weekend getaway", "1 week", "2 weeks"
  preferences: TravelPreferences
  createdAt: string
  updatedAt: string
}

export interface NotificationSettings {
  deletionReminders: boolean // Email before trip auto-deletion
  reportCompletion: boolean // Email when travel report is ready
  productUpdates: boolean // Product news and feature updates
}

export interface PrivacySettings {
  dataRetentionAcknowledged: boolean // User acknowledged 7-day deletion policy
  allowAnalytics: boolean // Allow anonymous usage analytics
}

/**
 * Combined profile settings data
 */
export interface ProfileSettings {
  profile: UserProfile
  travelerDetails: TravelerDetails
  travelPreferences: TravelPreferences
  notifications: NotificationSettings
  privacy: PrivacySettings
  templates: TripTemplate[]
}

/**
 * Auto-save state for UI feedback
 */
export type SaveState = 'idle' | 'saving' | 'saved' | 'error'

/**
 * Form validation errors
 */
export interface ValidationErrors {
  [key: string]: string | undefined
}
