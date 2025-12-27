/**
 * Templates Page Loading State
 */
export default function TemplatesLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>
        <div className="h-10 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Tabs skeleton */}
      <div className="flex gap-4 border-b border-slate-200 dark:border-slate-800 pb-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-8 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        ))}
      </div>

      {/* Template cards grid skeleton */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden"
          >
            {/* Image placeholder */}
            <div className="h-40 bg-slate-200 dark:bg-slate-800 animate-pulse" />
            {/* Content */}
            <div className="p-4 space-y-3">
              <div className="h-5 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-2/3 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              {/* Tags */}
              <div className="flex gap-2">
                {[1, 2].map((j) => (
                  <div
                    key={j}
                    className="h-6 w-16 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse"
                  />
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
