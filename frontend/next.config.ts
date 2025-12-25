import type { NextConfig } from 'next';
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

export default nextConfig;
