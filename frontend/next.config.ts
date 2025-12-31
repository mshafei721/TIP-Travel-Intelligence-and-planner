import type { NextConfig } from 'next';
import { withSentryConfig } from '@sentry/nextjs';
import path from 'path';

const nextConfig: NextConfig = {
  /* config options here */

  // Prevent these packages from being bundled in server components (they're client-only)
  serverExternalPackages: ['react-map-gl', 'mapbox-gl'],

  // Turbopack configuration for Next.js 16+
  turbopack: {
    root: path.resolve(__dirname),
    resolveAlias: {
      // Ensure mapbox-gl uses the dist version
      'mapbox-gl': 'mapbox-gl/dist/mapbox-gl.js',
      // Ensure react-map-gl resolves to the mapbox export
      'react-map-gl': 'react-map-gl/mapbox',
    },
  },
};

export default withSentryConfig(nextConfig, {
  // Sentry organization slug
  org: process.env.SENTRY_ORG,

  // Sentry project name
  project: process.env.SENTRY_PROJECT,

  // Auth token for uploading source maps
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // Only print logs for uploading source maps in CI
  silent: !process.env.CI,

  // Upload a larger set of source maps for prettier stack traces
  widenClientFileUpload: true,

  // Use tunneling to prevent ad blockers from blocking Sentry events
  tunnelRoute: '/monitoring',

  // Source maps configuration
  sourcemaps: {
    // Delete source maps after uploading to hide them from client bundles
    deleteSourcemapsAfterUpload: true,
  },

  // Bundle size optimizations
  bundleSizeOptimizations: {
    // Tree-shake Sentry debug statements
    excludeDebugStatements: true,
  },
});
