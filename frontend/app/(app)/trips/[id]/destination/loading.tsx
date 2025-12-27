/**
 * Destination Report Loading State
 */
export default function DestinationLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        <div className="h-8 w-56 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>

      {/* Hero section skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="h-48 bg-slate-200 dark:bg-slate-800 animate-pulse" />
        <div className="p-6 space-y-4">
          <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>
      </div>

      {/* Weather & best time skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
            <div className="space-y-2">
              <div className="h-8 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
          <div className="space-y-3">
            <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            <div className="h-4 w-2/3 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          </div>
        </div>
      </div>

      {/* Attractions skeleton */}
      <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
        <div className="h-6 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-4" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="space-y-3">
              <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-5 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
