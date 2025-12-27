/**
 * Trip Overview Loading State
 */
export default function TripOverviewLoading() {
  return (
    <div className="space-y-6">
      {/* Trip header skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
        <div className="flex items-start gap-6">
          <div className="w-32 h-32 bg-slate-200 dark:bg-slate-800 rounded-lg animate-pulse flex-shrink-0" />
          <div className="flex-1 space-y-3">
            <div className="h-8 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            <div className="h-4 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            <div className="flex gap-2 pt-2">
              <div className="h-6 w-20 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
              <div className="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick stats skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4"
          >
            <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-2" />
            <div className="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          </div>
        ))}
      </div>

      {/* Report sections skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6"
          >
            <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
            <div className="space-y-3">
              <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-5/6 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
