'use client';

export default function LoadingState() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header skeleton */}
      <div className="mb-8 animate-pulse">
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-lg w-2/3 mb-3" />
        <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded-lg w-1/2" />
      </div>

      {/* Cards grid skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Large card skeleton (Country Overview) */}
        <div className="xl:col-span-2 animate-pulse">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-slate-200 dark:bg-slate-800 rounded-lg" />
              <div className="flex-1">
                <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-1/3 mb-2" />
                <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4" />
              </div>
            </div>
            <div className="space-y-3">
              <div className="h-20 bg-slate-200 dark:bg-slate-800 rounded-lg" />
              <div className="h-20 bg-slate-200 dark:bg-slate-800 rounded-lg" />
            </div>
          </div>
        </div>

        {/* Standard card skeletons */}
        {[...Array(6)].map((_, idx) => (
          <div key={idx} className="animate-pulse">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-slate-200 dark:bg-slate-800 rounded-lg" />
                <div className="flex-1">
                  <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-2/3" />
                </div>
              </div>
              <div className="space-y-3">
                <div className="h-16 bg-slate-200 dark:bg-slate-800 rounded-lg" />
                <div className="h-16 bg-slate-200 dark:bg-slate-800 rounded-lg" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
