/**
 * Itinerary Loading State
 */
export default function ItineraryLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Day tabs skeleton */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="h-10 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse flex-shrink-0"
          />
        ))}
      </div>

      {/* Timeline skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
        <div className="space-y-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex gap-4">
              {/* Time column */}
              <div className="w-20 flex-shrink-0">
                <div className="h-5 w-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              </div>

              {/* Timeline line */}
              <div className="flex flex-col items-center">
                <div className="w-3 h-3 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
                <div className="w-0.5 h-full bg-slate-200 dark:bg-slate-800 animate-pulse" />
              </div>

              {/* Activity content */}
              <div className="flex-1 pb-6">
                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                    <div className="h-5 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  </div>
                  <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  <div className="flex gap-2">
                    <div className="h-6 w-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                    <div className="h-6 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
