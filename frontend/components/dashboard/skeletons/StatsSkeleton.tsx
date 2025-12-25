/**
 * Statistics summary skeleton
 * Matches StatisticsSummaryCard layout
 */
export function StatsSkeleton() {
  return (
    <div
      data-testid="stats-skeleton"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="mb-4">
        <div className="h-6 w-32 rounded bg-slate-200 dark:bg-slate-700" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="animate-pulse space-y-1 rounded-lg bg-slate-50 p-3 dark:bg-slate-800/50"
          >
            {/* Icon */}
            <div className="h-5 w-5 rounded bg-slate-200 dark:bg-slate-700" />
            {/* Value */}
            <div className="h-8 w-16 rounded bg-slate-200 dark:bg-slate-700" />
            {/* Label */}
            <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
        ))}
      </div>
    </div>
  );
}
