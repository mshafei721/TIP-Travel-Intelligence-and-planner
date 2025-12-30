'use client';

import { Loader2, CheckCircle, AlertCircle, Maximize2 } from 'lucide-react';
import { useGenerationProgress } from '@/contexts/GenerationProgressContext';

export function GenerationProgressBadge() {
  const { isGenerating, isMinimized, isComplete, progress, error, maximize } =
    useGenerationProgress();

  // Only show when generating and minimized
  if (!isGenerating || !isMinimized) {
    return null;
  }

  return (
    <button
      onClick={maximize}
      className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-3 shadow-lg transition-all hover:scale-105 hover:shadow-xl dark:border-slate-700 dark:bg-slate-900"
    >
      {/* Status Icon */}
      {error ? (
        <AlertCircle className="h-5 w-5 text-red-500" />
      ) : isComplete ? (
        <CheckCircle className="h-5 w-5 text-green-500" />
      ) : (
        <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
      )}

      {/* Progress Text */}
      <div className="flex flex-col items-start">
        <span className="text-sm font-medium text-slate-900 dark:text-white">
          {error ? 'Generation Failed' : isComplete ? 'Report Ready!' : 'Generating Report'}
        </span>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {error ? 'Click to view details' : isComplete ? 'Click to view' : `${progress}% complete`}
        </span>
      </div>

      {/* Expand Icon */}
      <Maximize2 className="h-4 w-4 text-slate-400" />
    </button>
  );
}
