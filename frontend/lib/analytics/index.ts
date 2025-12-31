/**
 * Analytics Module
 *
 * Centralized analytics utilities for PostHog integration.
 * Use this module for all analytics tracking to ensure:
 * - Consistent event naming
 * - Property sanitization
 * - Type safety
 * - Easy mocking in tests
 */

import posthog from 'posthog-js';
import {
  ANALYTICS_EVENTS,
  sanitizeProperties,
  type TripCreatedProperties,
  type ReportGeneratedProperties,
  type FeedbackSubmittedProperties,
  type WizardStepProperties,
  type ApiErrorProperties,
} from './events';

// Re-export event constants and types
export { ANALYTICS_EVENTS } from './events';
export type {
  TripCreatedProperties,
  ReportGeneratedProperties,
  FeedbackSubmittedProperties,
  WizardStepProperties,
  ApiErrorProperties,
} from './events';

/**
 * Check if analytics is enabled and initialized
 */
function isAnalyticsEnabled(): boolean {
  if (typeof window === 'undefined') return false;
  if (!process.env.NEXT_PUBLIC_POSTHOG_KEY) return false;
  if (!process.env.NEXT_PUBLIC_POSTHOG_HOST) return false;

  try {
    // Check if posthog is initialized and not opted out
    return posthog.has_opted_out_capturing?.() === false;
  } catch {
    return false;
  }
}

/**
 * Generic event capture with sanitization
 */
export function captureEvent(eventName: string, properties?: Record<string, unknown>): void {
  if (!isAnalyticsEnabled()) return;

  try {
    const sanitizedProps = properties ? sanitizeProperties(properties) : undefined;
    posthog.capture(eventName, sanitizedProps);
  } catch (error) {
    // Silently fail analytics - never break the app for analytics
    console.warn('Analytics capture failed:', error);
  }
}

/**
 * Identify user for analytics (call after login)
 */
export function identifyUser(userId: string, properties?: { email?: string; name?: string }): void {
  if (!isAnalyticsEnabled()) return;

  try {
    posthog.identify(userId, properties);
  } catch (error) {
    console.warn('Analytics identify failed:', error);
  }
}

/**
 * Reset user identity (call after logout)
 */
export function resetUser(): void {
  if (!isAnalyticsEnabled()) return;

  try {
    posthog.reset();
  } catch (error) {
    console.warn('Analytics reset failed:', error);
  }
}

// Type-safe event capture functions

/**
 * Track trip creation
 */
export function trackTripCreated(properties: TripCreatedProperties): void {
  captureEvent(ANALYTICS_EVENTS.TRIP_CREATED, properties);
}

/**
 * Track report generation completion
 */
export function trackReportGenerated(properties: ReportGeneratedProperties): void {
  captureEvent(ANALYTICS_EVENTS.REPORT_GENERATED, properties);
}

/**
 * Track report generation start
 */
export function trackReportGenerationStarted(tripId: string): void {
  captureEvent(ANALYTICS_EVENTS.REPORT_GENERATION_STARTED, { trip_id: tripId });
}

/**
 * Track report generation failure
 */
export function trackReportGenerationFailed(
  tripId: string,
  errorCode: string,
  durationMs: number,
): void {
  captureEvent(ANALYTICS_EVENTS.REPORT_GENERATION_FAILED, {
    trip_id: tripId,
    error_code: errorCode,
    duration_ms: durationMs,
  });
}

/**
 * Track feedback submission
 */
export function trackFeedbackSubmitted(properties: FeedbackSubmittedProperties): void {
  captureEvent(ANALYTICS_EVENTS.FEEDBACK_SUBMITTED, properties);
}

/**
 * Track wizard step completion
 */
export function trackWizardStepCompleted(properties: WizardStepProperties): void {
  captureEvent(ANALYTICS_EVENTS.WIZARD_STEP_COMPLETED, properties);
}

/**
 * Track wizard abandonment
 */
export function trackWizardAbandoned(
  stepNumber: number,
  stepName: string,
  totalSteps: number,
): void {
  captureEvent(ANALYTICS_EVENTS.WIZARD_ABANDONED, {
    step_number: stepNumber,
    step_name: stepName,
    total_steps: totalSteps,
  });
}

/**
 * Track API errors for debugging
 */
export function trackApiError(properties: ApiErrorProperties): void {
  captureEvent(ANALYTICS_EVENTS.API_ERROR, properties);
}

/**
 * Track client-side errors
 */
export function trackClientError(error: Error, context?: string): void {
  captureEvent(ANALYTICS_EVENTS.CLIENT_ERROR, {
    error_name: error.name,
    error_message: error.message.substring(0, 200),
    context: context || 'unknown',
    url: typeof window !== 'undefined' ? window.location.pathname : undefined,
  });
}
