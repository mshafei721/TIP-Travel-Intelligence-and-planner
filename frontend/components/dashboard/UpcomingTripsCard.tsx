'use client';

import { useRouter } from 'next/navigation';
import { TripCard } from './TripCard';

interface TripListItem {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  status: 'upcoming' | 'in-progress' | 'completed';
}

interface UpcomingTripsCardProps {
  trips?: TripListItem[];
  isLoading?: boolean;
  error?: Error | null;
  onTripClick?: (tripId: string) => void;
}

export function UpcomingTripsCard({
  trips = [],
  isLoading = false,
  error = null,
  onTripClick,
}: UpcomingTripsCardProps) {
  const router = useRouter();

  const handleTripClick = (tripId: string) => {
    if (onTripClick) {
      onTripClick(tripId);
    } else {
      router.push(`/trips/${tripId}`);
    }
  };

  // Filter for upcoming trips only (future dates with active statuses)
  const upcomingTrips = trips.filter((trip) => {
    const today = new Date();
    const startDate = new Date(trip.startDate);
    // Show trips that haven't started yet and are in active status
    return startDate > today && trip.status === 'upcoming';
  });

  if (error) {
    return (
      <div
        data-testid="upcoming-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Upcoming Trips
        </h2>
        <div className="text-center text-sm text-red-600 dark:text-red-400">
          Failed to load upcoming trips
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        data-testid="upcoming-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Upcoming Trips
        </h2>
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="animate-pulse rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="space-y-2">
                <div className="h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />
                <div className="h-4 w-48 rounded bg-slate-200 dark:bg-slate-700" />
                <div className="flex justify-between">
                  <div className="h-6 w-20 rounded bg-slate-200 dark:bg-slate-700" />
                  <div className="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (upcomingTrips.length === 0) {
    return (
      <div
        data-testid="upcoming-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Upcoming Trips
        </h2>
        <div className="py-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
            <svg
              className="h-6 w-6 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400">No upcoming trips planned</p>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="upcoming-trips-card"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Upcoming Trips
      </h2>

      <div className="space-y-3">
        {upcomingTrips.map((trip) => (
          <TripCard
            key={trip.id}
            trip={trip}
            showCountdown={true}
            onClick={handleTripClick}
            location="upcoming_trips"
          />
        ))}
      </div>
    </div>
  );
}
