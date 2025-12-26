'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Calendar, MapPin, Star, Archive, ArchiveRestore, MoreVertical, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { formatDateRange, formatDuration } from '@/lib/api/history';
import type { TravelHistoryEntry } from '@/types/profile';

export interface TripHistoryCardProps {
  trip: TravelHistoryEntry;
  onArchive: (tripId: string) => Promise<void>;
  onUnarchive: (tripId: string) => Promise<void>;
  onRate: (trip: TravelHistoryEntry) => void;
}

/**
 * TripHistoryCard - Display a single trip history entry
 */
export function TripHistoryCard({ trip, onArchive, onUnarchive, onRate }: TripHistoryCardProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleArchiveToggle = async () => {
    setLoading(true);
    try {
      if (trip.is_archived) {
        await onUnarchive(trip.trip_id);
      } else {
        await onArchive(trip.trip_id);
      }
    } finally {
      setLoading(false);
    }
  };

  const startDate = new Date(trip.start_date);
  const endDate = new Date(trip.end_date);
  const durationDays = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

  const statusColors = {
    completed: 'bg-green-100 text-green-700 dark:bg-green-950/30 dark:text-green-400',
    cancelled: 'bg-red-100 text-red-700 dark:bg-red-950/30 dark:text-red-400',
  };

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border bg-white shadow-sm transition-all hover:shadow-md dark:bg-slate-900 ${
        trip.is_archived
          ? 'border-slate-300 opacity-75 dark:border-slate-700'
          : 'border-slate-200 dark:border-slate-800'
      }`}
    >
      {/* Cover Image or Gradient */}
      <div className="relative h-32 overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600">
        {trip.cover_image && (
          <Image
            src={trip.cover_image}
            alt={trip.destination}
            fill
            className="object-cover"
            unoptimized
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />

        {/* Status Badge */}
        <div className="absolute right-3 top-3">
          <Badge className={statusColors[trip.status]}>{trip.status}</Badge>
        </div>

        {/* Archived Badge */}
        {trip.is_archived && (
          <div className="absolute left-3 top-3">
            <Badge variant="secondary" className="gap-1">
              <Archive className="h-3 w-3" />
              Archived
            </Badge>
          </div>
        )}

        {/* Destination overlay */}
        <div className="absolute bottom-3 left-3 right-3">
          <h3 className="text-lg font-semibold text-white">{trip.destination}</h3>
          <p className="flex items-center gap-1 text-sm text-white/80">
            <MapPin className="h-3 w-3" />
            {trip.country}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Date and Duration */}
        <div className="mb-3 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>{formatDateRange(trip.start_date, trip.end_date)}</span>
          </div>
          <span>{formatDuration(durationDays)}</span>
        </div>

        {/* Rating */}
        {trip.user_rating ? (
          <div className="mb-3 flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`h-4 w-4 ${
                  star <= trip.user_rating!
                    ? 'fill-amber-400 text-amber-400'
                    : 'text-slate-300 dark:text-slate-600'
                }`}
              />
            ))}
            {trip.user_notes && (
              <span className="ml-2 text-xs text-slate-500 dark:text-slate-400">(with notes)</span>
            )}
          </div>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            className="mb-3 h-auto p-0 text-blue-600 hover:text-blue-700 dark:text-blue-400"
            onClick={() => onRate(trip)}
          >
            <Star className="mr-1 h-4 w-4" />
            Rate this trip
          </Button>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          <Button variant="outline" size="sm" onClick={() => router.push(`/trips/${trip.trip_id}`)}>
            <Eye className="mr-1 h-4 w-4" />
            View Details
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onRate(trip)}>
                <Star className="mr-2 h-4 w-4" />
                {trip.user_rating ? 'Update Rating' : 'Rate Trip'}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleArchiveToggle} disabled={loading}>
                {trip.is_archived ? (
                  <>
                    <ArchiveRestore className="mr-2 h-4 w-4" />
                    Unarchive
                  </>
                ) : (
                  <>
                    <Archive className="mr-2 h-4 w-4" />
                    Archive
                  </>
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
}
