'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { analytics } from '@/lib/analytics';

interface EmptyStateProps {
  onCreateTrip?: () => void;
}

export function EmptyState({ onCreateTrip }: EmptyStateProps) {
  const router = useRouter();

  const handleClick = () => {
    analytics.createTripStart('empty_state');
    if (onCreateTrip) {
      onCreateTrip();
    } else {
      router.push('/trips/create');
    }
  };

  return (
    <div className="flex min-h-[400px] items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-12 dark:border-slate-700 dark:bg-slate-900/50">
      <div className="text-center">
        {/* Icon */}
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
          <svg
            className="h-8 w-8 text-blue-600 dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        {/* Heading */}
        <h2 className="mb-2 text-2xl font-bold text-slate-900 dark:text-slate-100">
          Welcome to TIP!
        </h2>

        {/* Description */}
        <p className="mx-auto mb-6 max-w-md text-slate-600 dark:text-slate-400">
          Start planning your next adventure with AI-powered travel intelligence. Get accurate visa
          requirements, destination insights, weather forecasts, and personalized itineraries—all in
          one comprehensive report.
        </p>

        {/* CTA Button */}
        <Button
          onClick={handleClick}
          size="lg"
          className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700"
        >
          Create Your First Trip
        </Button>

        {/* Features List */}
        <div className="mt-8 grid gap-4 text-left sm:grid-cols-2">
          <FeatureItem
            icon="📋"
            title="Accurate Visa Info"
            description="Official government sources, >95% accuracy"
          />
          <FeatureItem
            icon="🌍"
            title="Destination Intelligence"
            description="Weather, culture, budget, and more"
          />
          <FeatureItem
            icon="✈️"
            title="Smart Itineraries"
            description="AI-powered day-by-day planning"
          />
          <FeatureItem
            icon="🔒"
            title="GDPR Compliant"
            description="Auto-deletion after trip completion"
          />
        </div>
      </div>
    </div>
  );
}

function FeatureItem({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex items-start space-x-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <h4 className="font-medium text-slate-900 dark:text-slate-100">{title}</h4>
        <p className="text-sm text-slate-600 dark:text-slate-400">{description}</p>
      </div>
    </div>
  );
}
