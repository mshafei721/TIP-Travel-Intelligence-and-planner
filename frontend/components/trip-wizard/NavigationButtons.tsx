'use client'

interface NavigationButtonsProps {
  currentStep: number
  totalSteps: number
  onBack: () => void
  onNext: () => void
  canGoBack: boolean
  canGoNext: boolean
  isSubmitting?: boolean
  nextLabel?: string
}

export default function NavigationButtons({
  currentStep,
  totalSteps,
  onBack,
  onNext,
  canGoBack,
  canGoNext,
  isSubmitting = false,
  nextLabel,
}: NavigationButtonsProps) {
  const isLastStep = currentStep === totalSteps
  const isSummaryPage = currentStep === totalSteps + 1

  const getNextLabel = () => {
    if (nextLabel) return nextLabel
    if (isSummaryPage) return 'Confirm & Generate Report'
    if (isLastStep) return 'Review Trip'
    return 'Next Step'
  }

  return (
    <div className="flex items-center justify-between gap-4 mt-8">
      {/* Back button */}
      {canGoBack ? (
        <button
          type="button"
          onClick={onBack}
          disabled={isSubmitting}
          className="px-6 py-3 rounded-lg border-2 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-medium hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
      ) : (
        <div></div> // Spacer
      )}

      {/* Next/Submit button */}
      <button
        type="button"
        onClick={onNext}
        disabled={!canGoNext || isSubmitting}
        className={`px-8 py-3 rounded-lg font-semibold text-white transition-all duration-200 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${isSummaryPage ? 'bg-amber-500 hover:bg-amber-600 shadow-lg shadow-amber-500/30 hover:shadow-xl hover:shadow-amber-500/40 hover:scale-105' : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30'}`}
      >
        {isSubmitting ? (
          <>
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Processing...
          </>
        ) : (
          <>
            {getNextLabel()}
            <svg className="w-5 h-5" fill="none" strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </>
        )}
      </button>
    </div>
  )
}
