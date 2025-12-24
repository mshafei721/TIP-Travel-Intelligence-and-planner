import { DashboardGrid, DashboardSection } from '@/components/dashboard/DashboardLayout'
import { CardSkeleton } from '@/components/dashboard/skeletons/CardSkeleton'
import { TripCardSkeleton } from '@/components/dashboard/skeletons/TripCardSkeleton'
import { StatsSkeleton } from '@/components/dashboard/skeletons/StatsSkeleton'

/**
 * Dashboard Loading State
 * Displays skeleton screens while data is being fetched
 */
export default function DashboardLoading() {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="animate-pulse space-y-2">
        <div className="h-9 w-48 rounded bg-slate-200 dark:bg-slate-700" />
        <div className="h-6 w-96 rounded bg-slate-200 dark:bg-slate-700" />
      </div>

      {/* Dashboard Grid */}
      <DashboardGrid>
        {/* Quick Actions Skeleton */}
        <CardSkeleton />

        {/* Statistics Skeleton */}
        <StatsSkeleton />

        {/* Recent Trips Skeleton */}
        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex items-center justify-between">
            <div className="h-6 w-32 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-4 w-20 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
          <div className="space-y-3">
            <TripCardSkeleton />
            <TripCardSkeleton />
            <TripCardSkeleton />
          </div>
        </div>

        {/* Upcoming Trips Skeleton */}
        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4">
            <div className="h-6 w-32 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
          <div className="space-y-3">
            <TripCardSkeleton />
            <TripCardSkeleton />
          </div>
        </div>
      </DashboardGrid>

      {/* Recommendations Skeleton (full width) */}
      <DashboardSection>
        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4">
            <div className="h-6 w-48 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="animate-pulse overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700"
              >
                <div className="h-40 bg-slate-200 dark:bg-slate-700" />
                <div className="p-4">
                  <div className="mb-2 h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />
                  <div className="h-4 w-full rounded bg-slate-200 dark:bg-slate-700" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </DashboardSection>
    </div>
  )
}
