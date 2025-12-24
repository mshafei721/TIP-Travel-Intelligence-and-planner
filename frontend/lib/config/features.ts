/**
 * Feature Flag Configuration
 *
 * Controls which features are enabled/disabled in the application
 * Flags can be overridden via environment variables
 */

export const features = {
  /**
   * Dashboard & Home section
   * When disabled, /dashboard returns 404
   */
  dashboardHome: process.env.NEXT_PUBLIC_FEATURE_DASHBOARD_HOME !== 'false',

  /**
   * AI-powered recommendations
   * When disabled, RecommendationsCard is hidden
   */
  recommendations: process.env.NEXT_PUBLIC_FEATURE_RECOMMENDATIONS !== 'false',

  /**
   * Analytics tracking
   * When disabled, no analytics events are sent
   */
  analytics: process.env.NEXT_PUBLIC_FEATURE_ANALYTICS !== 'false',
} as const

export type FeatureFlags = typeof features
