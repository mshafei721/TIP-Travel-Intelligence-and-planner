/**
 * Generic card skeleton with shimmer animation
 * Use for loading states across dashboard cards
 */
export function CardSkeleton() {
  return (
    <div
      data-testid="card-skeleton"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="animate-pulse space-y-4">
        {/* Header */}
        <div className="h-6 w-32 rounded bg-slate-200 dark:bg-slate-700" />

        {/* Content */}
        <div className="space-y-3">
          <div className="h-4 w-full rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-5/6 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-4/6 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
      </div>
    </div>
  );
}
