/**
 * Settings Page Loading State
 */
export default function SettingsLoading() {
  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <div className="space-y-6">
        {/* Header skeleton */}
        <div className="space-y-2">
          <div className="h-8 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
          <div className="h-4 w-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        </div>

        {/* Settings sections skeleton */}
        {[1, 2, 3, 4].map((section) => (
          <div
            key={section}
            className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6"
          >
            {/* Section header */}
            <div className="flex items-center gap-3 mb-6">
              <div className="h-5 w-5 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
              <div className="h-6 w-40 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            </div>

            {/* Setting items */}
            <div className="space-y-4">
              {[1, 2, 3].map((item) => (
                <div
                  key={item}
                  className="flex items-center justify-between py-3 border-b border-slate-100 dark:border-slate-800 last:border-0"
                >
                  <div className="space-y-1">
                    <div className="h-5 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                    <div className="h-4 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
                  </div>
                  <div className="h-6 w-12 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
