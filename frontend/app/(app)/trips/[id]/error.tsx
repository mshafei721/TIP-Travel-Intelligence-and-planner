'use client';

import { useEffect } from 'react';
import { VisaErrorState } from '@/components/report/VisaLoadingState';

export default function TripReportError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Trip report error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        <VisaErrorState
          error={error.message || 'Failed to load trip report'}
          onRetry={reset}
        />
      </div>
    </div>
  );
}
