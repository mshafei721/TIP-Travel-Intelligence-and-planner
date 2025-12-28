'use client';

import Image from 'next/image';
import { analytics } from '@/lib/analytics';

interface TripCardProps {
  trip: {
    id: string;
    destination: string;
    startDate: string;
    endDate: string;
    status: 'upcoming' | 'in-progress' | 'completed';
    coverImageUrl?: string | null;
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
    if (!trip.startDate || !trip.endDate) {
      return 'Dates not set';
    }
    const start = new Date(trip.startDate);
    const end = new Date(trip.endDate);
    // Check for invalid dates
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return 'Dates not set';
    }
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
        rounded-lg border border-slate-200 bg-white overflow-hidden transition-all
        dark:border-slate-800 dark:bg-slate-900
        ${onClick ? 'cursor-pointer hover:border-blue-300 hover:shadow-md dark:hover:border-blue-700' : ''}
      `}
    >
      {/* Cover Image */}
      <div className="relative h-32 w-full">
        {trip.coverImageUrl ? (
          <Image
            src={trip.coverImageUrl}
            alt={`${trip.destination} cover`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 300px"
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500" />
        )}
        {/* Status Badge Overlay */}
        <div className="absolute bottom-2 left-2">
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium backdrop-blur-sm ${
              statusStyles[trip.status]
            }`}
          >
            {trip.status === 'upcoming'
              ? 'Upcoming'
              : trip.status === 'in-progress'
                ? 'In Progress'
                : 'Completed'}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-2">
        {/* Destination */}
        <h3 className="font-semibold text-slate-900 dark:text-slate-100">{trip.destination}</h3>

        {/* Dates */}
        <p className="text-sm text-slate-600 dark:text-slate-400">{formatDateRange()}</p>

        {/* Countdown */}
        {showCountdown && daysUntil !== null && daysUntil > 0 && (
          <p className="text-xs text-slate-500 dark:text-slate-500">
            {daysUntil} days until departure
          </p>
        )}
      </div>
    </div>
  );
}
