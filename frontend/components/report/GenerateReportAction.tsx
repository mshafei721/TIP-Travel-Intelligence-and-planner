'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AlertTriangle, Info, Loader2, RefreshCw } from 'lucide-react';
import { generateTripReport, getTripGenerationStatus } from '@/lib/api/reports';
import { TripGenerationProgress } from '@/components/reports/TripGenerationProgress';

interface GenerateReportActionProps {
  tripId: string;
  variant?: 'not-found' | 'error';
}

/**
 * Client component that handles AI report generation
 * Displays appropriate banner and handles async generation process
 */
export function GenerateReportAction({ tripId, variant = 'not-found' }: GenerateReportActionProps) {
  const router = useRouter();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<string | null>(null);
  const [showProgressTracker, setShowProgressTracker] = useState(false);

  // Check if generation is already in progress on mount
  useEffect(() => {
    const checkExistingGeneration = async () => {
      try {
        const statusResult = await getTripGenerationStatus(tripId);
        if (statusResult.success && statusResult.status) {
          const status = statusResult.status.status;
          // Only show progress tracker if actively processing
          // 'pending' means ready to start, not in progress
          if (status === 'processing') {
            setShowProgressTracker(true);
            setIsGenerating(true);
          }
        }
      } catch {
        // Ignore errors - just means no existing generation
      }
    };
    checkExistingGeneration();
  }, [tripId]);

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    setError(null);
    setProgress('Starting report generation...');

    try {
      const result = await generateTripReport(tripId);

      if (!result.success) {
        // Check if generation is already in progress
        if (result.error?.includes('already in progress')) {
          // Show the progress tracker instead of an error
          setShowProgressTracker(true);
          setError(null);
          return;
        }
        setError(result.error || 'Failed to start report generation');
        setIsGenerating(false);
        return;
      }

      setProgress('AI agents are analyzing your trip...');

      // Poll for completion (max 2 minutes with 3-second intervals)
      const maxAttempts = 40;
      for (let i = 0; i < maxAttempts; i++) {
        await new Promise((resolve) => setTimeout(resolve, 3000));

        const statusResult = await getTripGenerationStatus(tripId);

        if (!statusResult.success) {
          continue; // Keep trying on status fetch errors
        }

        const status = statusResult.status;
        if (!status) continue;

        if (status.current_agent) {
          setProgress(`Processing: ${status.current_agent} (${status.progress}%)`);
        }

        if (status.status === 'completed') {
          setProgress('Report generated successfully!');
          // Refresh the page to show the new report
          setTimeout(() => {
            router.refresh();
          }, 1000);
          return;
        }

        if (status.status === 'failed') {
          setError(status.error || 'Report generation failed. Please try again.');
          setIsGenerating(false);
          return;
        }
      }

      // Timeout - but report might still be processing
      setProgress('Generation is taking longer than expected. The page will refresh shortly...');
      setTimeout(() => {
        router.refresh();
      }, 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setIsGenerating(false);
    }
  };

  const handleRetry = () => {
    router.refresh();
  };

  // Config based on variant
  const config = {
    'not-found': {
      icon: Info,
      title: 'Visa Report Not Generated Yet',
      message:
        "The visa intelligence report for this trip hasn't been generated. Click below to start the AI analysis.",
      buttonLabel: 'Generate Report',
      colors: {
        bg: 'bg-blue-50 dark:bg-blue-950/30',
        border: 'border-blue-200 dark:border-blue-800',
        text: 'text-blue-900 dark:text-blue-100',
        icon: 'text-blue-600 dark:text-blue-400',
        button: 'bg-blue-600 hover:bg-blue-700 text-white',
      },
    },
    error: {
      icon: AlertTriangle,
      title: 'Error Loading Visa Report',
      message:
        'We encountered an error loading the visa report. You can try refreshing or regenerating.',
      buttonLabel: 'Retry',
      colors: {
        bg: 'bg-red-50 dark:bg-red-950/30',
        border: 'border-red-200 dark:border-red-800',
        text: 'text-red-900 dark:text-red-100',
        icon: 'text-red-600 dark:text-red-400',
        button: 'bg-red-600 hover:bg-red-700 text-white',
      },
    },
  };

  const currentConfig = config[variant];
  const Icon = currentConfig.icon;

  // Show full progress tracker when generation is in progress
  if (showProgressTracker) {
    return (
      <div className="rounded-lg border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/30 p-6">
        <TripGenerationProgress
          tripId={tripId}
          onComplete={() => {
            router.refresh();
          }}
          onError={(errorMsg) => {
            setShowProgressTracker(false);
            setError(errorMsg);
            setIsGenerating(false);
          }}
        />
      </div>
    );
  }

  return (
    <div
      className={`
        rounded-lg border-2 p-4
        ${currentConfig.colors.bg} ${currentConfig.colors.border}
        animate-in fade-in slide-in-from-top-2 duration-300
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0">
          {isGenerating ? (
            <Loader2
              className={`${currentConfig.colors.icon} animate-spin`}
              size={24}
              strokeWidth={2}
            />
          ) : (
            <Icon className={currentConfig.colors.icon} size={24} strokeWidth={2} />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className={`font-bold text-base ${currentConfig.colors.text} mb-1`}>
            {isGenerating ? 'Generating Report...' : currentConfig.title}
          </h3>
          <p className={`text-sm ${currentConfig.colors.text} opacity-90 leading-relaxed`}>
            {isGenerating ? progress : error || currentConfig.message}
          </p>

          {/* Error state with retry */}
          {error && !isGenerating && (
            <div className="mt-3 flex gap-2">
              <button
                onClick={handleGenerateReport}
                className={`
                  px-4 py-2 rounded-lg text-sm font-semibold
                  ${currentConfig.colors.button}
                  transition-all duration-200
                  hover:shadow-md
                  focus:outline-none focus:ring-2 focus:ring-offset-2
                `}
              >
                Try Again
              </button>
              <button
                onClick={handleRetry}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 transition-all duration-200"
              >
                <RefreshCw size={16} className="inline mr-1" />
                Refresh Page
              </button>
            </div>
          )}

          {/* Normal action button */}
          {!error && !isGenerating && (
            <button
              onClick={variant === 'error' ? handleRetry : handleGenerateReport}
              className={`
                mt-3 px-4 py-2 rounded-lg text-sm font-semibold
                ${currentConfig.colors.button}
                transition-all duration-200
                hover:shadow-md
                focus:outline-none focus:ring-2 focus:ring-offset-2
              `}
            >
              {currentConfig.buttonLabel}
            </button>
          )}

          {/* Progress indicator while generating */}
          {isGenerating && (
            <div className="mt-3">
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500 animate-pulse"
                  style={{ width: '60%' }}
                />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                This may take 1-2 minutes...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
