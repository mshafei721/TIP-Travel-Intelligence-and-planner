'use client';

import { analytics } from '@/lib/analytics';

interface TripCardProps {
  trip: {
    id: string;
    destination: string;
    startDate: string;
    endDate: string;
    status: 'upcoming' | 'in-progress' | 'completed';
  };
  showCountdown?: boolean;
  onClick?: (tripId: string) => void;
  location?: string;
}

export function TripCard({
  trip,
  showCountdown = false,
  onClick,
  location = 'dashboard',
}: TripCardProps) {
  const handleClick = () => {
    if (onClick) {
      analytics.tripCardClick(trip.id, location);
      onClick(trip.id);
    }
  };

  // Calculate days until departure
  const getDaysUntilDeparture = () => {
    if (!showCountdown) return null;
    const today = new Date();
    const departure = new Date(trip.startDate);
    const diffTime = departure.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const daysUntil = getDaysUntilDeparture();

  // Format dates
  const formatDateRange = () => {
    const start = new Date(trip.startDate);
    const end = new Date(trip.endDate);
    const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' };
    return `${start.toLocaleDateString('en-US', options)} - ${end.toLocaleDateString('en-US', options)}`;
  };

  // Status badge styling
  const statusStyles = {
    upcoming: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    'in-progress': 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
    completed: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  };

  return (
    <div
      data-testid="trip-card"
      onClick={handleClick}
      className={`
        rounded-lg border border-slate-200 bg-white p-4 transition-all
        dark:border-slate-800 dark:bg-slate-900
        ${onClick ? 'cursor-pointer hover:border-blue-300 hover:shadow-md dark:hover:border-blue-700' : ''}
      `}
    >
      <div className="space-y-2">
        {/* Destination */}
        <h3 className="font-semibold text-slate-900 dark:text-slate-100">{trip.destination}</h3>

        {/* Dates */}
        <p className="text-sm text-slate-600 dark:text-slate-400">{formatDateRange()}</p>

        {/* Status Badge & Countdown */}
        <div className="flex items-center justify-between">
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
              statusStyles[trip.status]
            }`}
          >
            {trip.status === 'upcoming'
              ? 'Upcoming'
              : trip.status === 'in-progress'
                ? 'In Progress'
                : 'Completed'}
          </span>

          {showCountdown && daysUntil !== null && daysUntil > 0 && (
            <span className="text-xs text-slate-600 dark:text-slate-400">
              {daysUntil} days until departure
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
