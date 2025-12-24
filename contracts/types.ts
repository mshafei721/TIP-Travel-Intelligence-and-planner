export type TripStatus = 'draft' | 'pending' | 'processing' | 'completed' | 'failed'

export type AgentType =
  | 'visa'
  | 'country'
  | 'weather'
  | 'currency'
  | 'culture'
  | 'food'
  | 'attractions'
  | 'itinerary'
  | 'flight'

export type AgentJobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'skipped' | 'retrying'

export type ReportSectionType = 'visa' | 'destination' | 'itinerary' | 'flight' | 'summary'

export type ConfidenceLevel = 'high' | 'medium' | 'low'

export interface Destination {
  id: string
  country: string
  city: string
  order: number
}

export interface TravelerDetails {
  name: string
  email: string
  age?: number
  nationality: string
  residencyCountry: string
  residencyStatus: string
  originCity: string
  partySize: number
  companionAges?: number[]
}

export interface TripDetails {
  departureDate: string
  returnDate: string
  budget: number
  budgetCurrency: string
  purpose: 'tourism' | 'business' | 'visiting_family' | 'education' | 'other'
}

export interface TripPreferences {
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget'
  interests: string[]
  dietaryRestrictions: string[]
  accessibilityNeeds?: string
}

export interface Trip {
  id: string
  userId: string
  title: string
  status: TripStatus
  travelerDetails: TravelerDetails
  destinations: Destination[]
  tripDetails: TripDetails
  preferences: TripPreferences
  autoDeleteAt?: string
  createdAt: string
  updatedAt: string
}

export interface TripCreateRequest {
  title: string
  travelerDetails: TravelerDetails
  destinations: Destination[]
  tripDetails: TripDetails
  preferences: TripPreferences
  submit?: boolean
}

export type TripUpdateRequest = Partial<TripCreateRequest> & {
  status?: TripStatus
}

export interface TripListItem {
  id: string
  destination: string
  startDate: string
  endDate: string
  status: 'upcoming' | 'in-progress' | 'completed'
  createdAt: string
  deletionDate: string
}

export interface TripListResponse {
  items: TripListItem[]
  nextCursor?: string
}

export interface AgentJob {
  id: string
  tripId: string
  agentType: AgentType
  status: AgentJobStatus
  startedAt?: string
  completedAt?: string
  retryCount: number
  confidenceScore?: number
  errorMessage?: string
  result?: Record<string, unknown>
}

export interface AgentJobListResponse {
  items: AgentJob[]
}

export interface SourceReference {
  id: string
  url: string
  title: string
  sourceType: 'government' | 'embassy' | 'official' | 'third_party'
  lastVerified: string
}

export interface ReportSection {
  id: string
  tripId: string
  sectionType: ReportSectionType
  title: string
  content: Record<string, unknown>
  confidenceLevel: ConfidenceLevel
  sources: SourceReference[]
  generatedAt: string
}

export interface ReportSummary {
  destination: string
  dates: string
  visaStatus: string
  weatherSummary: string
  totalBudget: {
    amount: number
    currency: string
  }
}

export interface TravelReport {
  id: string
  tripId: string
  title: string
  summary: ReportSummary
  sections: ReportSection[]
  generatedAt: string
  expiresAt: string
}

export interface ProgressStage {
  name: string
  status: 'pending' | 'in-progress' | 'completed' | 'failed'
  message: string
}

export interface ProgressState {
  percentage: number
  currentStage: string
  stages: ProgressStage[]
  estimatedTimeRemaining?: number
}

export interface TripStatusResponse {
  status: TripStatus
  progress?: ProgressState
}

export interface ReportPdfResponse {
  url: string
  expiresAt: string
}

export interface UserProfile {
  id: string
  email: string
  name: string
  avatarUrl?: string
  authProvider: 'email' | 'google'
  emailVerified: boolean
  createdAt: string
  updatedAt: string
}

export interface TravelerProfile {
  id: string
  userId: string
  nationality: string
  residencyCountry: string
  residencyStatus: string
  dateOfBirth?: string
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget'
  dietaryRestrictions: string[]
  accessibilityNeeds?: string
  createdAt: string
  updatedAt: string
}

export interface NotificationSettings {
  deletionReminders: boolean
  reportCompletion: boolean
  productUpdates: boolean
}

export interface ProfileResponse {
  user: UserProfile
  travelerProfile: TravelerProfile
  notificationSettings: NotificationSettings
}

export interface ProfileUpdateRequest {
  user?: Partial<UserProfile>
  travelerProfile?: Partial<TravelerProfile>
  notificationSettings?: Partial<NotificationSettings>
}

export interface TripTemplate {
  id: string
  userId: string
  name: string
  description?: string
  travelerDetails?: TravelerDetails
  destinations?: Destination[]
  preferences?: TripPreferences
  createdAt: string
  updatedAt: string
}

export interface TemplateCreateRequest {
  name: string
  description?: string
  travelerDetails?: TravelerDetails
  destinations?: Destination[]
  preferences?: TripPreferences
}

export type TemplateUpdateRequest = Partial<TemplateCreateRequest>

export interface TemplateListResponse {
  items: TripTemplate[]
}

export interface Notification {
  id: string
  userId: string
  type: 'report_completed' | 'deletion_reminder' | 'deletion_warning' | 'system_update'
  title: string
  message: string
  read: boolean
  tripId?: string
  createdAt: string
}

export interface NotificationListResponse {
  items: Notification[]
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

export interface ApiErrorResponse {
  requestId: string
  error: ApiError
}
