/**
 * Analytics Event Taxonomy
 *
 * Standardized event names and property contracts for PostHog analytics.
 * All custom events should be captured using these constants and helper functions.
 *
 * Event naming convention:
 * - Use snake_case for event names
 * - Use past tense verbs (created, submitted, generated)
 * - Be specific and descriptive
 */

// Event name constants - prevents typos and enables autocomplete
export const ANALYTICS_EVENTS = {
  // Trip lifecycle events
  TRIP_CREATED: 'trip_created',
  TRIP_UPDATED: 'trip_updated',
  TRIP_DELETED: 'trip_deleted',
  TRIP_VIEWED: 'trip_viewed',

  // Report generation events
  REPORT_GENERATION_STARTED: 'report_generation_started',
  REPORT_GENERATED: 'report_generated',
  REPORT_GENERATION_FAILED: 'report_generation_failed',
  REPORT_SECTION_VIEWED: 'report_section_viewed',

  // User engagement events
  FEEDBACK_SUBMITTED: 'feedback_submitted',
  SHARE_LINK_CREATED: 'share_link_created',
  TEMPLATE_SAVED: 'template_saved',
  TEMPLATE_USED: 'template_used',

  // Navigation events
  WIZARD_STEP_COMPLETED: 'wizard_step_completed',
  WIZARD_ABANDONED: 'wizard_abandoned',

  // Error events
  API_ERROR: 'api_error',
  CLIENT_ERROR: 'client_error',
} as const;

// Base type for analytics properties - allows index signature
type AnalyticsProperties = Record<string, unknown>;

// Type-safe event property interfaces
export interface TripCreatedProperties extends AnalyticsProperties {
  destination_city: string;
  destination_country: string;
  trip_duration_days: number;
  travelers_count: number;
  trip_purposes: string[];
  has_return_flight: boolean;
}

export interface ReportGeneratedProperties extends AnalyticsProperties {
  trip_id: string;
  duration_ms: number;
  success: boolean;
  sections_count: number;
  error_code?: string;
}

export interface FeedbackSubmittedProperties extends AnalyticsProperties {
  type: 'bug' | 'feature';
  has_attachment: boolean;
  route: string;
}

export interface WizardStepProperties extends AnalyticsProperties {
  step_number: number;
  step_name: string;
  total_steps: number;
}

export interface ApiErrorProperties extends AnalyticsProperties {
  endpoint: string;
  status_code: number;
  error_code: string;
  request_id?: string;
}

// Property sanitization - removes PII and sensitive data
export function sanitizeProperties<T extends Record<string, unknown>>(properties: T): T {
  const sensitiveKeys = [
    'email',
    'password',
    'token',
    'api_key',
    'phone',
    'address',
    'credit_card',
    'ssn',
  ];

  const sanitized = { ...properties };

  for (const key of Object.keys(sanitized)) {
    const lowerKey = key.toLowerCase();

    // Remove sensitive fields
    if (sensitiveKeys.some((sensitive) => lowerKey.includes(sensitive))) {
      delete sanitized[key];
      continue;
    }

    // Truncate long string values
    const value = sanitized[key];
    if (typeof value === 'string' && value.length > 500) {
      (sanitized as Record<string, unknown>)[key] = value.substring(0, 500) + '...';
    }
  }

  return sanitized;
}
