/**
 * Trip Generation Loading State
 */
export default function GenerationLoading() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="max-w-md w-full mx-auto p-8 text-center space-y-6">
        {/* Animated icon placeholder */}
        <div className="w-24 h-24 mx-auto bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />

        {/* Title skeleton */}
        <div className="space-y-2">
          <div className="h-7 w-56 mx-auto bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-72 mx-auto bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Progress bar skeleton */}
        <div className="space-y-2">
          <div className="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
          <div className="h-4 w-24 mx-auto bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Agent status list skeleton */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-4">
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  <div className="h-4 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                </div>
                <div className="h-4 w-16 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
