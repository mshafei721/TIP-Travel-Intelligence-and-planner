'use client';

import { useRouter } from 'next/navigation';
import { Minimize2, X, ExternalLink } from 'lucide-react';
import { useGenerationProgress } from '@/contexts/GenerationProgressContext';
import { TripGenerationProgress } from './TripGenerationProgress';
import { Button } from '@/components/ui/button';

export function GenerationProgressModal() {
  const router = useRouter();
  const { isGenerating, tripId, isMinimized, isComplete, minimize, setComplete, setError, reset } =
    useGenerationProgress();

  // Don't render if not generating or minimized
  if (!isGenerating || isMinimized || !tripId) {
    return null;
  }

  const handleComplete = () => {
    setComplete();
  };

  const handleError = (error: string) => {
    setError(error);
  };

  const handleViewReport = () => {
    reset();
    router.push(`/trips/${tripId}`);
  };

  const handleMinimize = () => {
    minimize();
  };

  const handleClose = () => {
    reset();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={handleMinimize} />

      {/* Modal */}
      <div className="relative z-10 mx-4 w-full max-w-lg animate-in fade-in zoom-in-95 duration-200">
        <div className="rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Generating Your Report
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={handleMinimize}
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                title="Minimize"
              >
                <Minimize2 className="h-4 w-4" />
              </button>
              {isComplete && (
                <button
                  onClick={handleClose}
                  className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            <TripGenerationProgress
              tripId={tripId}
              onComplete={handleComplete}
              onError={handleError}
            />

            {/* View Report Button */}
            {isComplete && (
              <div className="mt-6">
                <Button onClick={handleViewReport} className="w-full bg-blue-600 hover:bg-blue-700">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View Report
                </Button>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-slate-200 px-6 py-3 dark:border-slate-700">
            <p className="text-center text-sm text-slate-500 dark:text-slate-400">
              {isComplete ? 'Your report is ready!' : 'You can minimize this and continue browsing'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
