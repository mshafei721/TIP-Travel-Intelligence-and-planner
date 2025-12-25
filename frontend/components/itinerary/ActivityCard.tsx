'use client';

import React from 'react';
import type { Activity, ActivityCategory } from '@/types/itinerary';
import { Clock, MapPin, DollarSign, Star, ExternalLink, Edit, Trash2, Map } from 'lucide-react';

interface ActivityCardProps {
  activity: Activity;
  onEdit?: (activity: Activity) => void;
  onRemove?: (activityId: string) => void;
  onViewOnMap?: (activity: Activity) => void;
  readOnly?: boolean;
}

// Category colors and icons
const categoryStyles: Record<
  ActivityCategory,
  { color: string; bgColor: string; borderColor: string; icon: string }
> = {
  culture: {
    color: 'text-purple-700 dark:text-purple-400',
    bgColor: 'bg-purple-50 dark:bg-purple-950/30',
    borderColor: 'border-l-purple-500',
    icon: '🎭',
  },
  food: {
    color: 'text-orange-700 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-950/30',
    borderColor: 'border-l-orange-500',
    icon: '🍽️',
  },
  nature: {
    color: 'text-green-700 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-950/30',
    borderColor: 'border-l-green-500',
    icon: '🏞️',
  },
  shopping: {
    color: 'text-pink-700 dark:text-pink-400',
    bgColor: 'bg-pink-50 dark:bg-pink-950/30',
    borderColor: 'border-l-pink-500',
    icon: '🛍️',
  },
  accommodation: {
    color: 'text-blue-700 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-950/30',
    borderColor: 'border-l-blue-500',
    icon: '🏨',
  },
  transport: {
    color: 'text-slate-700 dark:text-slate-400',
    bgColor: 'bg-slate-50 dark:bg-slate-950/30',
    borderColor: 'border-l-slate-500',
    icon: '🚇',
  },
  entertainment: {
    color: 'text-indigo-700 dark:text-indigo-400',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/30',
    borderColor: 'border-l-indigo-500',
    icon: '🎪',
  },
  relaxation: {
    color: 'text-teal-700 dark:text-teal-400',
    bgColor: 'bg-teal-50 dark:bg-teal-950/30',
    borderColor: 'border-l-teal-500',
    icon: '🧘',
  },
  adventure: {
    color: 'text-red-700 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-950/30',
    borderColor: 'border-l-red-500',
    icon: '⛰️',
  },
  other: {
    color: 'text-gray-700 dark:text-gray-400',
    bgColor: 'bg-gray-50 dark:bg-gray-950/30',
    borderColor: 'border-l-gray-500',
    icon: '📍',
  },
};

// Format time (HH:mm to 12-hour format)
function formatTime(time: string): string {
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

// Calculate duration display
function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export function ActivityCard({
  activity,
  onEdit,
  onRemove,
  onViewOnMap,
  readOnly = false,
}: ActivityCardProps) {
  const style = categoryStyles[activity.category];
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <div
      className={`
        group relative overflow-hidden rounded-lg border border-slate-200 dark:border-slate-800
        bg-white dark:bg-slate-900 shadow-sm transition-all duration-200
        hover:shadow-md hover:-translate-y-0.5
        ${style.borderColor} border-l-4
      `}
    >
      {/* Priority badge */}
      {activity.priority === 'must-see' && (
        <div className="absolute top-2 right-2 z-10">
          <div className="flex items-center gap-1 rounded-full bg-amber-500 px-2 py-0.5 text-xs font-semibold text-white shadow-sm">
            <Star className="h-3 w-3 fill-current" />
            Must See
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="p-4">
        {/* Header */}
        <div className="mb-3 flex items-start gap-3">
          <div
            className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${style.bgColor} text-2xl`}
          >
            {style.icon}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
              {activity.name}
            </h3>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-slate-600 dark:text-slate-400">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span className="font-mono">
                  {formatTime(activity.startTime)} - {formatTime(activity.endTime)}
                </span>
              </div>
              <span className="text-slate-400 dark:text-slate-600">•</span>
              <span>{formatDuration(activity.duration)}</span>
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="mb-3 flex items-start gap-2 text-sm">
          <MapPin className="mt-0.5 h-4 w-4 flex-shrink-0 text-slate-500 dark:text-slate-400" />
          <div>
            <div className="font-medium text-slate-900 dark:text-slate-50">
              {activity.location.name}
            </div>
            {activity.location.neighborhood && (
              <div className="text-slate-600 dark:text-slate-400">
                {activity.location.neighborhood}
              </div>
            )}
            {activity.location.transportInfo && (
              <div className="mt-1 text-xs text-slate-500 dark:text-slate-500">
                🚇 {activity.location.transportInfo}
              </div>
            )}
          </div>
        </div>

        {/* Cost */}
        {activity.cost && (
          <div className="mb-3 flex items-center gap-2 text-sm">
            <DollarSign className="h-4 w-4 text-green-600 dark:text-green-400" />
            <span className="font-semibold text-green-700 dark:text-green-400">
              {activity.cost.amount === 0 ? 'Free' : `¥${activity.cost.amount.toLocaleString()}`}
              {activity.cost.perPerson && activity.cost.amount > 0 && ' per person'}
            </span>
            {activity.cost.notes && (
              <span className="text-slate-500 dark:text-slate-400">• {activity.cost.notes}</span>
            )}
          </div>
        )}

        {/* Description */}
        {activity.description && (
          <p className="mb-3 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
            {activity.description}
          </p>
        )}

        {/* Expandable details */}
        {(activity.bookingInfo || activity.notes || activity.accessibility) && (
          <>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mb-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              {isExpanded ? '− Show less' : '+ Show more details'}
            </button>

            {isExpanded && (
              <div className="space-y-2 rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800/50">
                {/* Booking info */}
                {activity.bookingInfo && (
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-slate-50">
                      Booking Information
                    </div>
                    <div className="mt-1 space-y-1 text-slate-600 dark:text-slate-400">
                      {activity.bookingInfo.required && <div>⚠️ Booking required in advance</div>}
                      {activity.bookingInfo.website && (
                        <div className="flex items-center gap-1">
                          <ExternalLink className="h-3 w-3" />
                          <a
                            href={activity.bookingInfo.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline dark:text-blue-400"
                          >
                            Book online
                          </a>
                        </div>
                      )}
                      {activity.bookingInfo.bookingStatus && (
                        <div className="flex items-center gap-2">
                          <span>Status:</span>
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                              activity.bookingInfo.bookingStatus === 'confirmed'
                                ? 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400'
                                : activity.bookingInfo.bookingStatus === 'pending'
                                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400'
                                  : 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400'
                            }`}
                          >
                            {activity.bookingInfo.bookingStatus}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Notes */}
                {activity.notes && (
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-slate-50">Notes</div>
                    <div className="mt-1 text-slate-600 dark:text-slate-400">{activity.notes}</div>
                  </div>
                )}

                {/* Accessibility */}
                {activity.accessibility && (
                  <div>
                    <div className="font-semibold text-slate-900 dark:text-slate-50">
                      Accessibility
                    </div>
                    <div className="mt-1 text-slate-600 dark:text-slate-400">
                      {activity.accessibility.wheelchairAccessible
                        ? '♿ Wheelchair accessible'
                        : '⚠️ Limited wheelchair access'}
                      {activity.accessibility.notes && (
                        <div className="mt-1">{activity.accessibility.notes}</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Actions */}
        {!readOnly && (
          <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3 dark:border-slate-800">
            {onEdit && (
              <button
                onClick={() => onEdit(activity)}
                className="flex items-center gap-1.5 rounded-md bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                <Edit className="h-3.5 w-3.5" />
                Edit
              </button>
            )}
            {onViewOnMap && activity.location.coordinates && (
              <button
                onClick={() => onViewOnMap(activity)}
                className="flex items-center gap-1.5 rounded-md bg-blue-100 px-3 py-1.5 text-sm font-medium text-blue-700 transition-colors hover:bg-blue-200 dark:bg-blue-950/50 dark:text-blue-400 dark:hover:bg-blue-950"
              >
                <Map className="h-3.5 w-3.5" />
                View on Map
              </button>
            )}
            {onRemove && (
              <button
                onClick={() => onRemove(activity.id)}
                className="flex items-center gap-1.5 rounded-md bg-red-100 px-3 py-1.5 text-sm font-medium text-red-700 transition-colors hover:bg-red-200 dark:bg-red-950/50 dark:text-red-400 dark:hover:bg-red-950"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Remove
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
