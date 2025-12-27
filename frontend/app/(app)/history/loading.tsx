/**
 * History Page Loading State
 */
export default function HistoryLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        <div className="h-4 w-80 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Stats cards skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4"
          >
            <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-2" />
            <div className="h-8 w-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          </div>
        ))}
      </div>

      {/* World map skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
        <div className="h-6 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Timeline skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
        <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4">
              <div className="w-2 h-2 rounded-full bg-slate-200 dark:bg-slate-800 animate-pulse mt-2" />
              <div className="flex-1 space-y-2">
                <div className="h-5 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
