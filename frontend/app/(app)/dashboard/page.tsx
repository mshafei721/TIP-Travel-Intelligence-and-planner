import { notFound } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { features } from '@/lib/config/features'
import { ApiClient } from '@/lib/api/client'
import { DashboardGrid, DashboardSection } from '@/components/dashboard/DashboardLayout'
import { QuickActionsCard } from '@/components/dashboard/QuickActionsCard'
import { StatisticsSummaryCard } from '@/components/dashboard/StatisticsSummaryCard'
import { RecentTripsCard } from '@/components/dashboard/RecentTripsCard'
import { UpcomingTripsCard } from '@/components/dashboard/UpcomingTripsCard'
import { RecommendationsCard } from '@/components/dashboard/RecommendationsCard'
import { EmptyState } from '@/components/dashboard/EmptyState'

interface TripListItem {
  id: string
  destination: string
  startDate: string
  endDate: string
  status: 'upcoming' | 'in-progress' | 'completed'
}

interface Statistics {
  totalTrips: number
  countriesVisited: number
  destinationsExplored: number
  activeTrips: number
}

interface Recommendation {
  destination: string
  country: string
  reason: string
  imageUrl: string
  confidence?: number
  tags?: string[]
}

export default async function DashboardPage() {
  // Feature flag check
  if (!features.dashboardHome) {
    notFound()
  }

  // Get authenticated user session
  const supabase = await createClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  // This should be handled by middleware, but double-check
  if (!session) {
    notFound()
  }

  // Create API client with access token getter
  const apiClient = new ApiClient(async () => session.access_token)

  // Fetch all data in parallel
  const today = new Date().toISOString().split('T')[0]

  const [recentTripsResult, upcomingTripsResult, statisticsResult, recommendationsResult] =
    await Promise.allSettled([
      apiClient.get<{ items: TripListItem[] }>('/trips?limit=5&sort=createdAt:desc'),
      apiClient.get<{ items: TripListItem[] }>(`/trips?filter=departureDate>=${today}`),
      apiClient.get<{ statistics: Statistics }>('/profile/statistics'),
      features.recommendations
        ? apiClient.get<{ recommendations: Recommendation[] }>('/recommendations?limit=3')
        : Promise.resolve({ recommendations: [] }),
    ])

  // Extract data or handle errors gracefully
  const recentTrips =
    recentTripsResult.status === 'fulfilled' ? recentTripsResult.value.items : []
  const upcomingTrips =
    upcomingTripsResult.status === 'fulfilled' ? upcomingTripsResult.value.items : []
  const statistics =
    statisticsResult.status === 'fulfilled'
      ? statisticsResult.value.statistics
      : { totalTrips: 0, countriesVisited: 0, destinationsExplored: 0, activeTrips: 0 }
  const recommendations =
    recommendationsResult.status === 'fulfilled'
      ? recommendationsResult.value.recommendations
      : []

  // Check if user has any trips
  const hasTrips = recentTrips.length > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Dashboard</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Welcome back! Here&apos;s an overview of your travel plans.
        </p>
      </div>

      {/* Empty State - Show when user has no trips */}
      {!hasTrips ? (
        <EmptyState />
      ) : (
        <>
          {/* Dashboard Grid - 2 columns on desktop, 1 on mobile */}
          <DashboardGrid>
            {/* Row 1: Quick Actions | Statistics Summary */}
            <QuickActionsCard />
            <StatisticsSummaryCard statistics={statistics} />

            {/* Row 2: Recent Trips | Upcoming Trips */}
            <RecentTripsCard trips={recentTrips} />
            <UpcomingTripsCard trips={upcomingTrips} />
          </DashboardGrid>

          {/* Row 3: Recommendations (full width) */}
          <DashboardSection>
            <RecommendationsCard recommendations={recommendations} />
          </DashboardSection>
        </>
      )}
    </div>
  )
}
