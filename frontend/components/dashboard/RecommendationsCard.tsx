'use client'

import { useRouter } from 'next/navigation'
import { analytics } from '@/lib/analytics'
import { features } from '@/lib/config/features'

interface Recommendation {
  destination: string
  country: string
  reason: string
  imageUrl: string
  confidence?: number
  tags?: string[]
}

interface RecommendationsCardProps {
  recommendations?: Recommendation[]
  isLoading?: boolean
  onRecommendationClick?: (destination: string) => void
}

export function RecommendationsCard({
  recommendations = [],
  isLoading = false,
  onRecommendationClick,
}: RecommendationsCardProps) {
  const router = useRouter()

  // Don't render if feature is disabled or no recommendations
  if (!features.recommendations || (!isLoading && recommendations.length === 0)) {
    return null
  }

  const handleClick = (destination: string) => {
    analytics.recommendationClick(destination, 'dashboard_recommendations')

    if (onRecommendationClick) {
      onRecommendationClick(destination)
    } else {
      // Navigate to trip creation with pre-filled destination
      const params = new URLSearchParams({ destination })
      router.push(`/trips/create?${params.toString()}`)
    }
  }

  if (isLoading) {
    return (
      <div
        data-testid="recommendations-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Recommended Destinations
        </h2>
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
    )
  }

  return (
    <div
      data-testid="recommendations-card"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Recommended Destinations
        </h2>
        <div className="text-xs text-slate-500 dark:text-slate-400">
          Based on your travel history
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {recommendations.slice(0, 3).map((recommendation) => (
          <div
            key={recommendation.destination}
            onClick={() => handleClick(recommendation.destination)}
            className="group cursor-pointer overflow-hidden rounded-lg border border-slate-200 transition-all hover:border-blue-300 hover:shadow-lg dark:border-slate-700 dark:hover:border-blue-600"
          >
            {/* Image */}
            <div className="relative h-40 overflow-hidden bg-slate-100 dark:bg-slate-800">
              {recommendation.imageUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={recommendation.imageUrl}
                  alt={recommendation.destination}
                  className="h-full w-full object-cover transition-transform group-hover:scale-110"
                />
              ) : (
                <div className="flex h-full items-center justify-center">
                  <svg
                    className="h-12 w-12 text-slate-300 dark:text-slate-600"
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
                </div>
              )}

              {/* Confidence Badge */}
              {recommendation.confidence && (
                <div className="absolute right-2 top-2 rounded-full bg-blue-600 px-2 py-1 text-xs font-medium text-white">
                  {Math.round(recommendation.confidence * 100)}% match
                </div>
              )}
            </div>

            {/* Content */}
            <div className="p-4">
              <h3 className="mb-1 font-semibold text-slate-900 dark:text-slate-100">
                {recommendation.destination}
              </h3>
              <p className="mb-2 text-sm text-slate-600 dark:text-slate-400">
                {recommendation.reason}
              </p>

              {/* Tags */}
              {recommendation.tags && recommendation.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {recommendation.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
