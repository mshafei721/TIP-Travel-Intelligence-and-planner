'use client'

import { useEffect } from 'react'
import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Profile Error Boundary
 */
export default function ProfileError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Profile page error:', error)
  }, [error])

  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-red-200 dark:border-red-900 p-8">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0 mt-1" />
          <div className="flex-1 space-y-4">
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
                Failed to Load Profile
              </h2>
              <p className="mt-2 text-slate-600 dark:text-slate-400">
                We encountered an error while loading your profile settings. This might be a
                temporary issue.
              </p>
            </div>

            {process.env.NODE_ENV === 'development' && (
              <div className="bg-slate-50 dark:bg-slate-950 rounded p-4 text-sm font-mono text-red-600 dark:text-red-400">
                {error.message}
              </div>
            )}

            <div className="flex gap-3">
              <Button onClick={reset}>Try Again</Button>
              <Button variant="outline" onClick={() => (window.location.href = '/dashboard')}>
                Go to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
