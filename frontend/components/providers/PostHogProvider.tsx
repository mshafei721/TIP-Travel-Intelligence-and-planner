'use client';

import posthog from 'posthog-js';
import { PostHogProvider as PHProvider, usePostHog } from 'posthog-js/react';
import { usePathname, useSearchParams } from 'next/navigation';
import { useEffect, Suspense } from 'react';
import type { ReactNode } from 'react';

// Initialize PostHog only on client-side
if (typeof window !== 'undefined') {
  const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  const posthogHost = process.env.NEXT_PUBLIC_POSTHOG_HOST;

  if (posthogKey && posthogHost) {
    posthog.init(posthogKey, {
      api_host: posthogHost,
      person_profiles: 'identified_only',
      capture_pageview: false, // We'll capture manually for better SPA support
      capture_pageleave: true,
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') {
          // Disable in development unless explicitly enabled
          if (process.env.NEXT_PUBLIC_POSTHOG_DEBUG !== 'true') {
            posthog.opt_out_capturing();
          }
        }
      },
    });
  }
}

// PageView tracker component - must be wrapped in Suspense due to useSearchParams
function PostHogPageViewTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const posthogClient = usePostHog();

  useEffect(() => {
    if (pathname && posthogClient) {
      let url = window.origin + pathname;
      const search = searchParams?.toString();
      if (search) {
        url = url + '?' + search;
      }
      posthogClient.capture('$pageview', {
        $current_url: url,
      });
    }
  }, [pathname, searchParams, posthogClient]);

  return null;
}

interface PostHogProviderProps {
  children: ReactNode;
}

export function PostHogProvider({ children }: PostHogProviderProps) {
  // Don't render PostHog if not configured
  const isConfigured =
    typeof window !== 'undefined' &&
    process.env.NEXT_PUBLIC_POSTHOG_KEY &&
    process.env.NEXT_PUBLIC_POSTHOG_HOST;

  if (!isConfigured) {
    return <>{children}</>;
  }

  return (
    <PHProvider client={posthog}>
      <Suspense fallback={null}>
        <PostHogPageViewTracker />
      </Suspense>
      {children}
    </PHProvider>
  );
}

export { posthog };
