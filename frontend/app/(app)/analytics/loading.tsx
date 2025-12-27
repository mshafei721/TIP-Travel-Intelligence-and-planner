/**
 * Analytics Page Loading State
 */
export default function AnalyticsLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-8 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        <div className="h-4 w-72 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Stats overview cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4"
          >
            <div className="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-2" />
            <div className="h-8 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-1" />
            <div className="h-3 w-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          </div>
        ))}
      </div>

      {/* Charts row skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Usage trends chart */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Agent usage chart */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>
      </div>

      {/* Bottom row skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Destinations chart */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Budget chart */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-36 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
