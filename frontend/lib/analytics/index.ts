/**
 * Analytics Tracking Utility
 *
 * Centralized analytics event tracking
 * Currently logs to console, can be extended to send to analytics service
 */

import { features } from '../config/features';

type EventData = Record<string, unknown>;

export function trackEvent(eventName: string, data?: EventData) {
  if (!features.analytics) {
    return; // Analytics disabled
  }

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics]', eventName, data);
  }

  // TODO: Send to analytics service (Google Analytics, Mixpanel, etc.)
  // Example:
  // window.gtag?.('event', eventName, data)
  // window.mixpanel?.track(eventName, data)
}

// Predefined event types for type safety
export const AnalyticsEvents = {
  PAGE_VIEW: 'page_view',
  CTA_CLICK: 'cta_click',
  TRIP_CARD_CLICK: 'trip_card_click',
  RECOMMENDATION_CLICK: 'recommendation_click',
  CREATE_TRIP_START: 'create_trip_start',
  TEMPLATE_MODAL_OPEN: 'template_modal_open',
} as const;

// Helper functions for common events
export const analytics = {
  pageView: (page: string, section?: string) => {
    trackEvent(AnalyticsEvents.PAGE_VIEW, { page, section });
  },

  ctaClick: (cta: string, location: string) => {
    trackEvent(AnalyticsEvents.CTA_CLICK, { cta, location });
  },

  tripCardClick: (tripId: string, location: string) => {
    trackEvent(AnalyticsEvents.TRIP_CARD_CLICK, { tripId, location });
  },

  recommendationClick: (destination: string, location: string) => {
    trackEvent(AnalyticsEvents.RECOMMENDATION_CLICK, { destination, location });
  },

  createTripStart: (source: string) => {
    trackEvent(AnalyticsEvents.CREATE_TRIP_START, { source });
  },

  templateModalOpen: () => {
    trackEvent(AnalyticsEvents.TEMPLATE_MODAL_OPEN, {});
  },
};
