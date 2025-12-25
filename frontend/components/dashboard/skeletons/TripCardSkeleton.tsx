/**
 * Trip card skeleton
 * Matches TripCard component structure
 */
export function TripCardSkeleton() {
  return (
    <div
      data-testid="trip-card-skeleton"
      className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="animate-pulse space-y-2">
        {/* Destination */}
        <div className="h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />

        {/* Dates */}
        <div className="h-4 w-48 rounded bg-slate-200 dark:bg-slate-700" />

        {/* Status Badge & Countdown */}
        <div className="flex items-center justify-between">
          <div className="h-6 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700" />
        </div>
      </div>
    </div>
  );
}
