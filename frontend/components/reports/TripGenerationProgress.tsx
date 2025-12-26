'use client';

import { useEffect, useState } from 'react';
import { getTripGenerationStatus, type TripGenerationStatus } from '@/lib/api/reports';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  Sparkles,
  Globe,
  Cloud,
  DollarSign,
  Users,
  Utensils,
  MapPin,
  Calendar,
  Plane,
} from 'lucide-react';

interface TripGenerationProgressProps {
  tripId: string;
  onComplete?: () => void;
  onError?: (error: string) => void;
  pollingInterval?: number; // milliseconds, default 3000
}

// Agent metadata with icons and display names
const AGENT_METADATA: Record<
  string,
  {
    name: string;
    icon: typeof Sparkles;
    color: string;
  }
> = {
  visa: {
    name: 'Visa Requirements',
    icon: Globe,
    color: 'text-blue-500 dark:text-blue-400',
  },
  country: {
    name: 'Country Intelligence',
    icon: MapPin,
    color: 'text-green-500 dark:text-green-400',
  },
  weather: {
    name: 'Weather Forecast',
    icon: Cloud,
    color: 'text-sky-500 dark:text-sky-400',
  },
  currency: {
    name: 'Currency & Costs',
    icon: DollarSign,
    color: 'text-amber-500 dark:text-amber-400',
  },
  culture: {
    name: 'Cultural Insights',
    icon: Users,
    color: 'text-purple-500 dark:text-purple-400',
  },
  food: {
    name: 'Culinary Guide',
    icon: Utensils,
    color: 'text-orange-500 dark:text-orange-400',
  },
  attractions: {
    name: 'Top Attractions',
    icon: MapPin,
    color: 'text-pink-500 dark:text-pink-400',
  },
  itinerary: {
    name: 'Itinerary Planning',
    icon: Calendar,
    color: 'text-indigo-500 dark:text-indigo-400',
  },
  flight: {
    name: 'Flight Options',
    icon: Plane,
    color: 'text-red-500 dark:text-red-400',
  },
};

export function TripGenerationProgress({
  tripId,
  onComplete,
  onError,
  pollingInterval = 3000,
}: TripGenerationProgressProps) {
  const [status, setStatus] = useState<TripGenerationStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for status updates using interval
  useEffect(() => {
    let isMounted = true;

    // Fetch status function (defined inside effect to avoid setState-in-effect error)
    const fetchStatus = async () => {
      const result = await getTripGenerationStatus(tripId);

      if (!isMounted) return;

      if (result.success && result.status) {
        setStatus(result.status);
        setError(null);

        // Handle completion
        if (result.status.status === 'completed') {
          onComplete?.();
        }

        // Handle failure
        if (result.status.status === 'failed') {
          const errorMsg = result.status.error || 'Report generation failed';
          setError(errorMsg);
          onError?.(errorMsg);
        }
      } else {
        setError(result.error || 'Failed to fetch status');
        onError?.(result.error || 'Failed to fetch status');
      }
    };

    // Initial fetch on mount
    fetchStatus();

    // Only poll if not completed or failed
    const intervalId = setInterval(() => {
      // Check current status before fetching
      if (status?.status !== 'completed' && status?.status !== 'failed') {
        fetchStatus();
      }
    }, pollingInterval);

    // Cleanup on unmount
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [tripId, pollingInterval, status?.status, onComplete, onError]);

  // Error state
  if (error && !status) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-950">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <div>
            <h3 className="font-semibold text-red-900 dark:text-red-100">Status Check Failed</h3>
            <p className="mt-1 text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Loading initial state
  if (!status) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-slate-600 dark:text-slate-400" />
          <p className="text-slate-700 dark:text-slate-300">Loading generation status...</p>
        </div>
      </div>
    );
  }

  // Main progress UI
  return (
    <div className="space-y-6">
      {/* Progress Header */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
            Report Generation Progress
          </h3>
          <span className="text-sm text-slate-600 dark:text-slate-400">
            {status.progress}% Complete
          </span>
        </div>

        {/* Progress Bar */}
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
            style={{ width: `${status.progress}%` }}
          />
        </div>

        {/* Time info */}
        {status.started_at && (
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <Clock className="h-4 w-4" />
            <span>
              Started {new Date(status.started_at).toLocaleTimeString()}
              {status.completed_at &&
                ` · Completed ${new Date(status.completed_at).toLocaleTimeString()}`}
            </span>
          </div>
        )}
      </div>

      {/* Agent Status List */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">Agent Status</h4>
        <div className="space-y-1">
          {Object.entries(AGENT_METADATA).map(([agentKey, metadata]) => {
            const IconComponent = metadata.icon;
            const isCompleted = status.agents_completed.includes(agentKey);
            const isFailed = status.agents_failed.includes(agentKey);
            const isProcessing = status.current_agent === agentKey;
            const isPending = !isCompleted && !isFailed && !isProcessing;

            return (
              <div
                key={agentKey}
                className={`flex items-center justify-between rounded-lg border p-3 transition-colors ${
                  isProcessing
                    ? 'border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-950'
                    : isCompleted
                      ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950'
                      : isFailed
                        ? 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950'
                        : 'border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <IconComponent className={`h-4 w-4 ${metadata.color}`} />
                  <span
                    className={`text-sm font-medium ${
                      isCompleted
                        ? 'text-green-900 dark:text-green-100'
                        : isFailed
                          ? 'text-red-900 dark:text-red-100'
                          : isProcessing
                            ? 'text-blue-900 dark:text-blue-100'
                            : 'text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    {metadata.name}
                  </span>
                </div>

                {/* Status Icon */}
                {isCompleted && (
                  <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                )}
                {isFailed && <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />}
                {isProcessing && (
                  <Loader2 className="h-5 w-5 animate-spin text-blue-600 dark:text-blue-400" />
                )}
                {isPending && (
                  <div className="h-2 w-2 rounded-full bg-slate-300 dark:bg-slate-700" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Failed Status Message */}
      {status.status === 'failed' && status.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <div>
              <h4 className="font-semibold text-red-900 dark:text-red-100">Generation Failed</h4>
              <p className="mt-1 text-sm text-red-700 dark:text-red-300">{status.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Completed Status Message */}
      {status.status === 'completed' && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-950">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
            <div>
              <h4 className="font-semibold text-green-900 dark:text-green-100">
                Report Generation Complete!
              </h4>
              <p className="mt-1 text-sm text-green-700 dark:text-green-300">
                Your comprehensive travel intelligence report is ready to view.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
