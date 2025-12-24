'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

/**
 * Dashboard Error Boundary
 * Catches and displays errors that occur during dashboard data fetching
 */
export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to error reporting service
    console.error('Dashboard Error:', error)
  }, [error])

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center space-y-4 rounded-lg border-2 border-dashed border-red-300 bg-red-50 p-12 dark:border-red-900 dark:bg-red-950">
      <div className="text-center">
        {/* Error Icon */}
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

        {/* Error Message */}
        <h2 className="mb-2 text-2xl font-bold text-slate-900 dark:text-slate-100">
          Oops! Something went wrong
        </h2>
        <p className="mb-6 max-w-md text-slate-600 dark:text-slate-400">
          We encountered an error while loading your dashboard. This could be due to a network
          issue or a temporary server problem.
        </p>

        {/* Error Details (Development Only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-6 rounded-lg bg-slate-100 p-4 text-left dark:bg-slate-800">
            <p className="font-mono text-xs text-red-600 dark:text-red-400">
              {error.message}
            </p>
            {error.digest && (
              <p className="mt-1 font-mono text-xs text-slate-500">Digest: {error.digest}</p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            onClick={reset}
            className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            <svg
              className="mr-2 h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Try Again
          </Button>

          <Button
            variant="outline"
            onClick={() => (window.location.href = '/')}
            className="dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Go to Home
          </Button>
        </div>

        {/* Help Text */}
        <p className="mt-6 text-xs text-slate-500 dark:text-slate-400">
          If this problem persists, please contact support or try again later.
        </p>
      </div>
    </div>
  )
}
