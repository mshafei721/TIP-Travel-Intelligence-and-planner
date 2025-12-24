import { Suspense } from 'react'
import TripCreationWizard from '@/components/trip-wizard/TripCreationWizard'

export const metadata = {
  title: 'Create New Trip | TIP',
  description: 'Plan your journey with personalized travel intelligence',
}

export default function NewTripPage() {
  return (
    <Suspense fallback={<TripWizardLoading />}>
      <TripCreationWizard />
    </Suspense>
  )
}

function TripWizardLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-amber-50/20 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900
                  flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-600 dark:text-slate-400">Loading trip wizard...</p>
      </div>
    </div>
  )
}
