import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Performance monitoring
  tracesSampleRate: process.env.NODE_ENV === 'development' ? 1.0 : 0.1,

  // Enable logs
  enableLogs: true,

  // Environment
  environment: process.env.NODE_ENV || 'development',

  // Release version
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE || process.env.VERCEL_GIT_COMMIT_SHA,

  // Only enable in production unless debug mode is on
  enabled: process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_SENTRY_DEBUG === 'true',
});
