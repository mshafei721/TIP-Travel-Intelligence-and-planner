'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { TripCard } from './TripCard';

interface TripListItem {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  status: 'upcoming' | 'in-progress' | 'completed';
}

interface RecentTripsCardProps {
  trips?: TripListItem[];
  isLoading?: boolean;
  error?: Error | null;
  onTripClick?: (tripId: string) => void;
  onViewAll?: () => void;
}

export function RecentTripsCard({
  trips = [],
  isLoading = false,
  error = null,
  onTripClick,
  onViewAll,
}: RecentTripsCardProps) {
  const router = useRouter();

  const handleTripClick = (tripId: string) => {
    if (onTripClick) {
      onTripClick(tripId);
    } else {
      router.push(`/trips/${tripId}`);
    }
  };

  const handleViewAll = () => {
    if (onViewAll) {
      onViewAll();
    } else {
      router.push('/trips');
    }
  };

  if (error) {
    return (
      <div
        data-testid="recent-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Trips</h2>
        </div>
        <div className="text-center text-sm text-red-600 dark:text-red-400">
          Failed to load recent trips
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        data-testid="recent-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Trips</h2>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="animate-pulse rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="space-y-2">
                <div className="h-5 w-32 rounded bg-slate-200 dark:bg-slate-700" />
                <div className="h-4 w-48 rounded bg-slate-200 dark:bg-slate-700" />
                <div className="h-6 w-20 rounded bg-slate-200 dark:bg-slate-700" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (trips.length === 0) {
    return (
      <div
        data-testid="recent-trips-card"
        className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Trips</h2>
        </div>
        <div className="py-8 text-center text-sm text-slate-600 dark:text-slate-400">
          No trips yet. Start planning your first adventure!
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="recent-trips-card"
      className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Trips</h2>
        <Link
          href="/trips"
          onClick={(e) => {
            e.preventDefault();
            handleViewAll();
          }}
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          View All →
        </Link>
      </div>

      <div className="space-y-3">
        {trips.slice(0, 5).map((trip) => (
          <TripCard key={trip.id} trip={trip} onClick={handleTripClick} location="recent_trips" />
        ))}
      </div>
    </div>
  );
}
