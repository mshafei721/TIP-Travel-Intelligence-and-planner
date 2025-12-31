import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Performance monitoring
  tracesSampleRate: process.env.NODE_ENV === 'development' ? 1.0 : 0.1,

  // Enable logs
  enableLogs: true,

  // Environment
  environment: process.env.NODE_ENV || 'development',

  // Release version for source maps
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE || process.env.VERCEL_GIT_COMMIT_SHA,

  // Only enable in production unless debug mode is on
  enabled: process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_SENTRY_DEBUG === 'true',

  // Filter out certain exceptions
  beforeSend(event) {
    // Filter out 404 and authentication errors
    if (event.exception?.values) {
      const exception = event.exception.values[0];
      if (exception?.type === 'NotFoundError' || exception?.value?.includes('404')) {
        return null;
      }
    }
    return event;
  },
});
