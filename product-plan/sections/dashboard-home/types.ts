/**
 * Dashboard & Home - Type Definitions
 *
 * TypeScript interfaces for dashboard data structures
 */

import type { Trip, TripListItem } from '../../../contracts/types'

// ============================================================================
// Dashboard Data Aggregation
// ============================================================================

/**
 * Complete dashboard data payload
 * Combines all data needed to render the dashboard
 */
export interface DashboardData {
  /** Most recent 5 trips (any status) */
  recentTrips: TripListItem[]

  /** Future trips with active statuses (draft, pending, processing) */
  upcomingTrips: TripListItem[]

  /** User travel statistics aggregated from trip history */
  statistics: Statistics

  /** AI/algorithm-generated destination recommendations */
  recommendations: Recommendation[]

  /** User profile info for personalization */
  userProfile: {
    name: string
    email: string
  }
}

// ============================================================================
// Statistics
// ============================================================================

/**
 * Aggregated travel statistics for user
 * Displayed in StatisticsSummaryCard
 */
export interface Statistics {
  /** Total number of trips created (all statuses) */
  totalTrips: number

  /** Unique countries visited (from completed trips) */
  countriesVisited: number

  /** Unique cities/destinations explored (from completed trips) */
  destinationsExplored: number

  /** Active trips (draft, pending, processing statuses) */
  activeTrips: number
}

// ============================================================================
// Recommendations
// ============================================================================

/**
 * AI-generated or algorithm-based destination recommendation
 * Displayed in RecommendationsCard
 */
export interface Recommendation {
  /** Destination name (e.g., "Barcelona, Spain") */
  destination: string

  /** Country (for grouping/filtering) */
  country: string

  /** Reason for recommendation (personalized message) */
  reason: string

  /** Image URL for destination card */
  imageUrl: string

  /** Confidence score (0-1) for recommendation quality */
  confidence?: number

  /** Tags for categorization (e.g., ["adventure", "beach", "culture"]) */
  tags?: string[]
}

// ============================================================================
// Component Props
// ============================================================================

/**
 * Props for TripCard component
 */
export interface TripCardProps {
  /** Trip data to display */
  trip: TripListItem

  /** Click handler */
  onClick?: (tripId: string) => void

  /** Show countdown timer for upcoming trips */
  showCountdown?: boolean

  /** Analytics tracking function */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for RecentTripsCard
 */
export interface RecentTripsCardProps {
  /** Recent trips to display (max 5) */
  trips?: TripListItem[]

  /** Loading state */
  isLoading?: boolean

  /** Error state */
  error?: Error | null

  /** Click handler for trip cards */
  onTripClick?: (tripId: string) => void

  /** Click handler for "View All" link */
  onViewAll?: () => void

  /** Analytics tracking */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for UpcomingTripsCard
 */
export interface UpcomingTripsCardProps {
  /** Upcoming trips to display */
  trips?: TripListItem[]

  /** Loading state */
  isLoading?: boolean

  /** Error state */
  error?: Error | null

  /** Click handler for trip cards */
  onTripClick?: (tripId: string) => void

  /** Analytics tracking */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for QuickActionsCard
 */
export interface QuickActionsCardProps {
  /** Handler for Create New Trip */
  onCreateTrip?: () => void

  /** Handler for View All Trips */
  onViewAllTrips?: () => void

  /** Handler for Use Template */
  onUseTemplate?: () => void

  /** Analytics tracking */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for StatisticsSummaryCard
 */
export interface StatisticsSummaryCardProps {
  /** Statistics data */
  statistics?: Statistics

  /** Loading state */
  isLoading?: boolean

  /** Error state */
  error?: Error | null
}

/**
 * Props for RecommendationsCard
 */
export interface RecommendationsCardProps {
  /** Recommendations to display (max 3) */
  recommendations?: Recommendation[]

  /** Loading state */
  isLoading?: boolean

  /** Click handler for recommendation */
  onRecommendationClick?: (destination: string) => void

  /** Analytics tracking */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for EmptyState component
 */
export interface EmptyStateProps {
  /** Handler for "Create Your First Trip" CTA */
  onCreateTrip?: () => void

  /** Analytics tracking */
  trackEvent?: (event: string, data: Record<string, unknown>) => void
}

/**
 * Props for DashboardLayout
 */
export interface DashboardLayoutProps {
  /** Child components (cards) */
  children: React.ReactNode
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Response from /profile/statistics endpoint
 */
export interface StatisticsResponse {
  statistics: Statistics
}

/**
 * Response from recommendations algorithm
 */
export interface RecommendationsResponse {
  recommendations: Recommendation[]
}

// ============================================================================
// Feature Flag Configuration
// ============================================================================

/**
 * Feature flags for dashboard
 */
export interface DashboardFeatureFlags {
  /** Enable/disable dashboard home section */
  dashboardHome: boolean

  /** Enable/disable recommendations feature */
  recommendations: boolean

  /** Enable/disable analytics tracking */
  analytics: boolean
}

// ============================================================================
// Helper Types
// ============================================================================

/**
 * Countdown calculation result
 */
export interface CountdownData {
  days: number
  hours: number
  minutes: number
  seconds: number
  formatted: string // e.g., "45 days until departure"
}
