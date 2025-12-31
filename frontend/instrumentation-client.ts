import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Adds request headers and IP for users
  sendDefaultPii: true,

  // Performance monitoring
  // Capture 100% in dev, 10% in production
  tracesSampleRate: process.env.NODE_ENV === 'development' ? 1.0 : 0.1,

  // Session Replay
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      maskAllInputs: true,
      blockAllMedia: true,
    }),
    Sentry.feedbackIntegration({
      colorScheme: 'system',
      // Enable for production, can be toggled via env var
      autoInject: process.env.NEXT_PUBLIC_SENTRY_FEEDBACK_ENABLED === 'true',
    }),
  ],

  // Session Replay sample rates
  // Capture Replay for 10% of all sessions,
  // plus for 100% of sessions with an error
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  // Enable logs
  enableLogs: true,

  // Environment
  environment: process.env.NODE_ENV || 'development',

  // Release version for source maps
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE || process.env.VERCEL_GIT_COMMIT_SHA,

  // Don't send events in development unless explicitly enabled
  enabled: process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_SENTRY_DEBUG === 'true',

  // Filter out sensitive data
  beforeSend(event) {
    // Remove any PII from the event
    if (event.user) {
      // Keep only non-PII user data
      event.user = {
        id: event.user.id,
      };
    }
    return event;
  },
});

// Export for router transition tracking
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
