'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { analytics } from '@/lib/analytics'

interface QuickActionsCardProps {
  onCreateTrip?: () => void
  onViewAllTrips?: () => void
  onUseTemplate?: () => void
}

export function QuickActionsCard({
  onCreateTrip,
  onViewAllTrips,
  onUseTemplate,
}: QuickActionsCardProps) {
  const router = useRouter()
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false)

  const handleCreateTrip = () => {
    analytics.ctaClick('create_trip', 'dashboard_quick_actions')
    if (onCreateTrip) {
      onCreateTrip()
    } else {
      router.push('/trips/create')
    }
  }

  const handleViewAllTrips = () => {
    analytics.ctaClick('view_all_trips', 'dashboard_quick_actions')
    if (onViewAllTrips) {
      onViewAllTrips()
    } else {
      router.push('/trips')
    }
  }

  const handleUseTemplate = () => {
    analytics.ctaClick('use_template', 'dashboard_quick_actions')
    analytics.templateModalOpen()
    if (onUseTemplate) {
      onUseTemplate()
    } else {
      setIsTemplateModalOpen(true)
    }
  }

  return (
    <div
      data-testid="quick-actions-card"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Quick Actions
      </h2>

      <div className="flex flex-col space-y-3">
        {/* Create New Trip - Primary Blue Button */}
        <Button
          onClick={handleCreateTrip}
          className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
          size="lg"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Create New Trip
        </Button>

        {/* View All Trips - Secondary Button */}
        <Button
          onClick={handleViewAllTrips}
          variant="outline"
          size="lg"
          className="dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
          View All Trips
        </Button>

        {/* Use Template - Secondary Button */}
        <Button
          onClick={handleUseTemplate}
          variant="outline"
          size="lg"
          className="dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Use Template
        </Button>
      </div>

      {/* Template Modal will be handled separately */}
      {isTemplateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="rounded-lg bg-white p-6 dark:bg-slate-900">
            <h3 className="mb-4 text-lg font-semibold">Select Template</h3>
            <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
              Template selection coming soon...
            </p>
            <Button onClick={() => setIsTemplateModalOpen(false)}>Close</Button>
          </div>
        </div>
      )}
    </div>
  )
}
