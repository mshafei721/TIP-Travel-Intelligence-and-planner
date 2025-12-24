'use client'

interface Statistics {
  totalTrips: number
  countriesVisited: number
  destinationsExplored: number
  activeTrips: number
}

interface StatisticsSummaryCardProps {
  statistics?: Statistics
  isLoading?: boolean
  error?: Error | null
}

export function StatisticsSummaryCard({
  statistics,
  isLoading = false,
  error = null,
}: StatisticsSummaryCardProps) {
  if (error) {
    return (
      <div
        data-testid="statistics-summary-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Travel Statistics
        </h2>
        <div className="text-center text-sm text-red-600 dark:text-red-400">
          Failed to load statistics
        </div>
      </div>
    )
  }

  if (isLoading || !statistics) {
    return (
      <div
        data-testid="statistics-summary-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Travel Statistics
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse space-y-2">
              <div className="h-4 w-4 rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-8 w-16 rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-700" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  const metrics = [
    {
      id: 'total-trips',
      label: 'Total Trips',
      value: statistics.totalTrips,
      icon: (
        <svg
          data-testid="icon-total-trips"
          className="h-5 w-5 text-blue-600 dark:text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
      ),
    },
    {
      id: 'countries',
      label: 'Countries Visited',
      value: statistics.countriesVisited,
      icon: (
        <svg
          data-testid="icon-countries"
          className="h-5 w-5 text-green-600 dark:text-green-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
    },
    {
      id: 'destinations',
      label: 'Destinations Explored',
      value: statistics.destinationsExplored,
      icon: (
        <svg
          data-testid="icon-destinations"
          className="h-5 w-5 text-purple-600 dark:text-purple-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      ),
    },
    {
      id: 'active',
      label: 'Active Trips',
      value: statistics.activeTrips,
      icon: (
        <svg
          data-testid="icon-active"
          className="h-5 w-5 text-amber-600 dark:text-amber-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      ),
    },
  ]

  return (
    <div
      data-testid="statistics-summary-card"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Travel Statistics
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric) => (
          <div
            key={metric.id}
            className="flex flex-col space-y-1 rounded-lg bg-slate-50 p-3 dark:bg-slate-800/50"
          >
            {metric.icon}
            <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {metric.value}
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-400">
              {metric.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
