'use client';

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

const stepLabels = ['Traveler', 'Destination', 'Trip Details', 'Preferences'];

export default function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  return (
    <div className="relative">
      {/* Desktop: Horizontal route map */}
      <div className="hidden md:flex items-center justify-between max-w-2xl mx-auto">
        {Array.from({ length: totalSteps }, (_, index) => {
          const step = index + 1;
          const isCompleted = step < currentStep;
          const isCurrent = step === currentStep;

          return (
            <div key={step} className="flex-1 relative">
              {/* Connecting line */}
              {step < totalSteps && (
                <div className="absolute top-5 left-1/2 w-full h-0.5 -z-10">
                  <div className="h-full bg-slate-200 dark:bg-slate-800">
                    <div
                      className="h-full bg-blue-600 transition-all duration-700 ease-out"
                      style={{
                        width: isCompleted ? '100%' : '0%',
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Step node */}
              <div className="flex flex-col items-center">
                <div
                  className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ease-out ${isCompleted ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : isCurrent ? 'bg-amber-500 text-white shadow-xl shadow-amber-500/40 scale-110' : 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600'}`}
                >
                  {isCompleted ? (
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      strokeWidth="2.5"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="font-mono text-sm font-semibold">{step}</span>
                  )}

                  {/* Pulse animation for current step */}
                  {isCurrent && (
                    <span className="absolute inset-0 rounded-full bg-amber-500 animate-ping opacity-20" />
                  )}
                </div>

                {/* Step label */}
                <div
                  className={`mt-3 text-xs font-medium tracking-wide transition-colors ${isCompleted || isCurrent ? 'text-slate-900 dark:text-slate-100' : 'text-slate-500 dark:text-slate-600'}`}
                >
                  {stepLabels[index]}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Mobile: Compact version */}
      <div className="md:hidden flex items-center justify-center space-x-2">
        {Array.from({ length: totalSteps }, (_, index) => {
          const step = index + 1;
          const isCompleted = step < currentStep;
          const isCurrent = step === currentStep;

          return (
            <div
              key={step}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-semibold transition-all duration-500 ${isCompleted ? 'bg-blue-600 text-white' : isCurrent ? 'bg-amber-500 text-white scale-125' : 'bg-slate-200 dark:bg-slate-800 text-slate-400'}`}
            >
              {isCompleted ? (
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeWidth="2.5"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                step
              )}
            </div>
          );
        })}
        <div className="ml-3 text-sm font-medium text-slate-600 dark:text-slate-400">
          {stepLabels[currentStep - 1]}
        </div>
      </div>
    </div>
  );
}
