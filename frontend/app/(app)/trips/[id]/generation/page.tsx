'use client';

import { use, useState } from 'react';
import Link from 'next/link';
import { TripGenerationProgress } from '@/components/reports';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';

export default function TripGenerationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id: tripId } = use(params);
  const [isComplete, setIsComplete] = useState(false);

  const handleComplete = () => {
    setIsComplete(true);
  };

  const handleError = (error: string) => {
    console.error('Generation error:', error);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="container mx-auto max-w-4xl px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/trips/${tripId}`}
            className="inline-flex items-center gap-2 text-sm text-slate-600 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Trip
          </Link>
          <h1 className="mt-4 text-3xl font-bold text-slate-900 dark:text-slate-50">
            Generating Your Travel Intelligence Report
          </h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Our AI agents are researching and compiling comprehensive travel information for your
            trip. This usually takes 2-3 minutes.
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-lg dark:border-slate-800 dark:bg-slate-900">
          <TripGenerationProgress
            tripId={tripId}
            onComplete={handleComplete}
            onError={handleError}
          />
        </div>

        {/* Action Buttons */}
        {isComplete && (
          <div className="mt-8 flex gap-4">
            <Link
              href={`/trips/${tripId}`}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
            >
              <CheckCircle2 className="h-5 w-5" />
              View Report
            </Link>
            <Link
              href="/trips"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              All Trips
            </Link>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-8 rounded-lg border border-blue-200 bg-blue-50 p-6 dark:border-blue-800 dark:bg-blue-950">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100">What&apos;s happening?</h3>
          <ul className="mt-2 space-y-1 text-sm text-blue-800 dark:text-blue-200">
            <li>✓ Analyzing visa requirements and entry conditions</li>
            <li>✓ Gathering country intelligence and cultural insights</li>
            <li>✓ Fetching weather forecasts and climate data</li>
            <li>✓ Researching currency, costs, and budget estimates</li>
            <li>✓ Compiling food recommendations and dining tips</li>
            <li>✓ Discovering top attractions and hidden gems</li>
            <li>✓ Planning optimized daily itineraries</li>
            <li>✓ Finding flight options and travel routes</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
