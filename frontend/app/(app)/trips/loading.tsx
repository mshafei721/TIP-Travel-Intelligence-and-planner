/**
 * Trips Page Loading State
 */
export default function TripsLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-56 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>
        <div className="h-10 w-36 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Filters/tabs skeleton */}
      <div className="flex gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-9 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        ))}
      </div>

      {/* Trips list skeleton */}
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4"
          >
            <div className="flex gap-4">
              {/* Trip image placeholder */}
              <div className="w-24 h-24 bg-slate-200 dark:bg-slate-800 rounded-lg animate-pulse flex-shrink-0" />

              {/* Trip details */}
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  <div className="h-6 w-20 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
                </div>
                <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                <div className="h-4 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                <div className="flex gap-2 pt-2">
                  {[1, 2, 3].map((j) => (
                    <div
                      key={j}
                      className="h-8 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse"
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
