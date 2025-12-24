export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-amber-50/20 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900">
      <div className="max-w-4xl mx-auto px-4 py-8 md:py-12">
        {/* Header skeleton */}
        <div className="text-center mb-8 md:mb-12 animate-pulse">
          <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg w-64 mx-auto mb-3"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-48 mx-auto"></div>
        </div>

        {/* Progress bar skeleton */}
        <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full mb-4 animate-pulse"></div>
        <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-24 ml-auto mb-8 animate-pulse"></div>

        {/* Step indicator skeleton */}
        <div className="flex items-center justify-between max-w-2xl mx-auto mb-12">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex flex-col items-center animate-pulse">
              <div className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-800 mb-3"></div>
              <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
            </div>
          ))}
        </div>

        {/* Form skeleton */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-6 md:p-10">
          <div className="space-y-6 animate-pulse">
            <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-48"></div>
            <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-32"></div>
            <div className="space-y-4 mt-8">
              {[1, 2, 3, 4].map((i) => (
                <div key={i}>
                  <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-24 mb-2"></div>
                  <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg"></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Navigation buttons skeleton */}
        <div className="flex items-center justify-between mt-8 animate-pulse">
          <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg w-24"></div>
          <div className="h-12 bg-slate-200 dark:bg-slate-800 rounded-lg w-32"></div>
        </div>
      </div>
    </div>
  )
}
