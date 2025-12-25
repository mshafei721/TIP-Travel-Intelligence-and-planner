/**
 * Profile Loading State
 */
export default function ProfileLoading() {
  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="space-y-2">
          <div className="h-8 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-96 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Profile section skeleton */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <div className="flex items-start gap-6">
            {/* Avatar skeleton */}
            <div className="w-24 h-24 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />

            {/* Fields skeleton */}
            <div className="flex-1 space-y-4">
              <div className="space-y-2">
                <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              </div>
            </div>
          </div>
        </div>

        {/* Additional sections skeleton */}
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6"
          >
            <div className="space-y-4">
              <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-full bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
