'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

/**
 * Travel History Error Boundary
 * Catches and displays errors that occur during history page loading
 */
export default function HistoryError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('History Error:', error);
  }, [error]);

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border-2 border-dashed border-red-300 bg-red-50 p-12 dark:border-red-900 dark:bg-red-950">
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
          <svg
            className="h-8 w-8 text-red-600 dark:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        <h2 className="mb-2 text-2xl font-bold text-slate-900 dark:text-slate-100">
          Unable to load travel history
        </h2>
        <p className="mb-6 max-w-md text-slate-600 dark:text-slate-400">
          We encountered an error while loading your travel history. Please try again.
        </p>

        {process.env.NODE_ENV === 'development' && (
          <div className="mb-6 rounded-lg bg-slate-100 p-4 text-left dark:bg-slate-800">
            <p className="font-mono text-xs text-red-600 dark:text-red-400">{error.message}</p>
            {error.digest && (
              <p className="mt-1 font-mono text-xs text-slate-500">Digest: {error.digest}</p>
            )}
          </div>
        )}

        <div className="flex gap-4">
          <Button
            onClick={reset}
            className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            Try Again
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/dashboard')}
            className="dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
