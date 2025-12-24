'use client';

/**
 * Loading states for visa report components
 */

export function VisaSectionSkeleton({ className = '' }: { className?: string }) {
  return (
    <div
      className={`
        bg-white dark:bg-slate-900
        rounded-xl border-2 border-slate-200 dark:border-slate-800
        p-6 space-y-6
        ${className}
        animate-pulse
      `}
    >
      {/* Header skeleton */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-lg bg-slate-200 dark:bg-slate-800" />
          <div className="space-y-2">
            <div className="h-5 w-32 bg-slate-200 dark:bg-slate-800 rounded" />
            <div className="h-3 w-48 bg-slate-200 dark:bg-slate-800 rounded" />
          </div>
        </div>
        <div className="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded-full" />
      </div>

      {/* Hero section skeleton */}
      <div className="p-6 rounded-lg bg-slate-100 dark:bg-slate-800 space-y-3">
        <div className="h-6 w-40 bg-slate-200 dark:bg-slate-700 rounded" />
        <div className="h-4 w-64 bg-slate-200 dark:bg-slate-700 rounded" />
      </div>

      {/* Content skeleton */}
      <div className="space-y-4">
        <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded" />
        <div className="h-4 w-5/6 bg-slate-200 dark:bg-slate-800 rounded" />
        <div className="h-4 w-4/6 bg-slate-200 dark:bg-slate-800 rounded" />
      </div>

      {/* Grid skeleton */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg" />
        <div className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg" />
      </div>
    </div>
  );
}

export function VisaReportLoadingSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      {/* Page header skeleton */}
      <div className="space-y-3 animate-pulse">
        <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded" />
        <div className="h-5 w-64 bg-slate-200 dark:bg-slate-800 rounded" />
      </div>

      {/* Sections */}
      <VisaSectionSkeleton />
      <VisaSectionSkeleton />
      <VisaSectionSkeleton />
    </div>
  );
}

/**
 * Shimmer loading state with travel-themed animation
 */
export function VisaLoadingAnimation() {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-6">
      {/* Animated plane icon */}
      <div className="relative">
        <svg
          className="w-16 h-16 text-blue-600 dark:text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            className="animate-bounce"
          />
        </svg>
        <div className="absolute inset-0 bg-blue-400 dark:bg-blue-600 rounded-full blur-xl opacity-20 animate-pulse" />
      </div>

      {/* Loading text */}
      <div className="text-center space-y-2">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Analyzing Visa Requirements
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 animate-pulse">
          Processing your travel intelligence...
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-64 h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full animate-[shimmer_2s_ease-in-out_infinite]" />
      </div>
    </div>
  );
}

/**
 * Error state for visa report
 */
interface VisaErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export function VisaErrorState({ error, onRetry }: VisaErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-6">
      {/* Error icon */}
      <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-950/30 flex items-center justify-center">
        <svg
          className="w-8 h-8 text-red-600 dark:text-red-400"
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

      {/* Error message */}
      <div className="text-center space-y-2 max-w-md">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Failed to Load Visa Information
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {error || 'An unexpected error occurred while fetching visa requirements.'}
        </p>
      </div>

      {/* Retry button */}
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
