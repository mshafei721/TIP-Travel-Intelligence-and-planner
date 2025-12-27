'use client';

import { useState, useEffect } from 'react';
import { Loader2, CheckCircle, XCircle, Clock, Pause, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type {
  RecalculationProgress,
  RecalculationStatus as RecalcStatus,
} from '@/types/trip-update';

interface RecalculationStatusProps {
  progress: RecalculationProgress;
  onCancel?: () => void;
  onRetry?: () => void;
}

const AI_AGENTS = [
  { id: 'visa_intelligence', label: 'Visa Intelligence', icon: '🛂' },
  { id: 'destination_guide', label: 'Destination Guide', icon: '📍' },
  { id: 'itinerary_builder', label: 'Itinerary Builder', icon: '📅' },
  { id: 'budget_optimizer', label: 'Budget Optimizer', icon: '💰' },
  { id: 'safety_advisor', label: 'Safety Advisor', icon: '🛡️' },
  { id: 'culture_expert', label: 'Culture Expert', icon: '🌍' },
  { id: 'packing_assistant', label: 'Packing Assistant', icon: '🧳' },
  { id: 'transport_planner', label: 'Transport Planner', icon: '✈️' },
];

const STATUS_CONFIG: Record<
  RecalcStatus,
  {
    icon: React.ElementType;
    label: string;
    color: string;
    bgColor: string;
  }
> = {
  idle: {
    icon: Clock,
    label: 'Idle',
    color: 'text-slate-500',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
  },
  queued: {
    icon: Clock,
    label: 'Queued',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
  },
  processing: {
    icon: Loader2,
    label: 'Processing',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
  },
  completed: {
    icon: CheckCircle,
    label: 'Completed',
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/30',
  },
  failed: {
    icon: XCircle,
    label: 'Failed',
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/30',
  },
  cancelled: {
    icon: Pause,
    label: 'Cancelled',
    color: 'text-amber-600',
    bgColor: 'bg-amber-50 dark:bg-amber-950/30',
  },
};

/**
 * RecalculationStatus - Shows the progress of AI recalculation
 */
export function RecalculationStatus({ progress, onCancel, onRetry }: RecalculationStatusProps) {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update elapsed time while processing
  useEffect(() => {
    if (progress.status !== 'processing' || !progress.startedAt) {
      return;
    }

    const startTime = new Date(progress.startedAt).getTime();
    const updateElapsed = () => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 1000);

    return () => clearInterval(interval);
  }, [progress.status, progress.startedAt]);

  const statusConfig = STATUS_CONFIG[progress.status];
  const StatusIcon = statusConfig.icon;

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getAgentStatus = (agentId: string): 'completed' | 'failed' | 'current' | 'pending' => {
    if (progress.completedAgents.includes(agentId)) return 'completed';
    if (progress.failedAgents.includes(agentId)) return 'failed';
    if (progress.currentAgent === agentId) return 'current';
    return 'pending';
  };

  if (progress.status === 'idle') {
    return null;
  }

  return (
    <div
      className={`rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden ${statusConfig.bgColor}`}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon
            className={`h-5 w-5 ${statusConfig.color} ${
              progress.status === 'processing' ? 'animate-spin' : ''
            }`}
          />
          <div>
            <h3 className="font-medium text-slate-900 dark:text-slate-100">
              AI Recalculation {statusConfig.label}
            </h3>
            {progress.status === 'processing' && (
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Updating your travel report...
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {progress.status === 'processing' && onCancel && (
            <Button variant="outline" size="sm" onClick={onCancel}>
              Cancel
            </Button>
          )}
          {(progress.status === 'failed' || progress.status === 'cancelled') && onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {(progress.status === 'processing' || progress.status === 'queued') && (
        <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-400 mb-2">
            <span>{progress.progress}% complete</span>
            <div className="flex items-center gap-4">
              {elapsedTime > 0 && <span>Elapsed: {formatTime(elapsedTime)}</span>}
              {progress.estimatedTimeRemaining && (
                <span>~{formatTime(progress.estimatedTimeRemaining)} remaining</span>
              )}
            </div>
          </div>
          <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Agent Progress */}
      <div className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {AI_AGENTS.map((agent) => {
            const agentStatus = getAgentStatus(agent.id);

            return (
              <div
                key={agent.id}
                className={`flex items-center gap-2 p-2 rounded-lg border transition-all ${
                  agentStatus === 'current'
                    ? 'bg-blue-50 dark:bg-blue-950/50 border-blue-200 dark:border-blue-800'
                    : agentStatus === 'completed'
                      ? 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900'
                      : agentStatus === 'failed'
                        ? 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900'
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 opacity-50'
                }`}
              >
                <span className="text-lg">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                  <span className="text-xs font-medium text-slate-700 dark:text-slate-300 truncate block">
                    {agent.label}
                  </span>
                </div>
                <div className="flex-shrink-0">
                  {agentStatus === 'current' && (
                    <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                  )}
                  {agentStatus === 'completed' && (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  )}
                  {agentStatus === 'failed' && <XCircle className="h-4 w-4 text-red-600" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Error Message */}
      {progress.status === 'failed' && progress.error && (
        <div className="px-4 pb-4">
          <div className="bg-red-100 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <p className="text-sm text-red-700 dark:text-red-300">{progress.error}</p>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {progress.status === 'completed' && (
        <div className="px-4 pb-4">
          <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-300">
            <CheckCircle className="h-4 w-4" />
            <span>
              All sections have been updated successfully.
              {progress.completedAt && (
                <span className="text-slate-500 ml-1">
                  Completed at {new Date(progress.completedAt).toLocaleTimeString()}
                </span>
              )}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecalculationStatus;
