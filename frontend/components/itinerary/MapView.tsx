'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  Map,
  Marker,
  Popup,
  Source,
  Layer,
  NavigationControl,
  GeolocateControl,
} from 'react-map-gl/mapbox';
import type { Activity, DayItinerary, ActivityCategory } from '@/types/itinerary';
import { MapPin, X, Clock, DollarSign } from 'lucide-react';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapViewProps {
  days: DayItinerary[];
  selectedDayNumber?: number | null; // null = show all days
  onActivityClick?: (activity: Activity) => void;
  className?: string;
}

// Category colors matching ActivityCard
const categoryColors: Record<ActivityCategory, { bg: string; border: string; text: string }> = {
  culture: { bg: '#9333ea', border: '#a855f7', text: '#ffffff' },
  food: { bg: '#f97316', border: '#fb923c', text: '#ffffff' },
  nature: { bg: '#10b981', border: '#34d399', text: '#ffffff' },
  shopping: { bg: '#ec4899', border: '#f472b6', text: '#ffffff' },
  accommodation: { bg: '#3b82f6', border: '#60a5fa', text: '#ffffff' },
  transport: { bg: '#6366f1', border: '#818cf8', text: '#ffffff' },
  entertainment: { bg: '#8b5cf6', border: '#a78bfa', text: '#ffffff' },
  relaxation: { bg: '#14b8a6', border: '#2dd4bf', text: '#ffffff' },
  adventure: { bg: '#f59e0b', border: '#fbbf24', text: '#ffffff' },
  other: { bg: '#64748b', border: '#94a3b8', text: '#ffffff' },
};

// Get emoji for category
const getCategoryEmoji = (category: ActivityCategory): string => {
  const emojiMap: Record<ActivityCategory, string> = {
    culture: '🎭',
    food: '🍽️',
    nature: '🏞️',
    shopping: '🛍️',
    accommodation: '🏨',
    transport: '🚇',
    entertainment: '🎪',
    relaxation: '🧘',
    adventure: '⛰️',
    other: '📍',
  };
  return emojiMap[category];
};

export function MapView({
  days,
  selectedDayNumber,
  onActivityClick,
  className = '',
}: MapViewProps) {
  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [hoveredActivity, setHoveredActivity] = useState<string | null>(null);

  // Filter activities based on selected day
  const visibleActivities = useMemo(() => {
    const filteredDays =
      selectedDayNumber !== null && selectedDayNumber !== undefined
        ? days.filter((d) => d.dayNumber === selectedDayNumber)
        : days;

    return filteredDays.flatMap((day) =>
      day.timeBlocks.flatMap((block) =>
        block.activities.map((activity) => ({
          ...activity,
          dayNumber: day.dayNumber,
        })),
      ),
    );
  }, [days, selectedDayNumber]);

  // Calculate initial viewport to fit all markers
  const initialViewState = useMemo(() => {
    if (visibleActivities.length === 0) {
      // Default to Tokyo if no activities
      return {
        longitude: 139.6917,
        latitude: 35.6895,
        zoom: 11,
      };
    }

    // For now, center on Tokyo (in production, calculate bounds from activity coordinates)
    // TODO: Add coordinates to ActivityLocation type and calculate proper bounds
    return {
      longitude: 139.6917,
      latitude: 35.6895,
      zoom: 11,
    };
  }, [visibleActivities]);

  // Route line data (GeoJSON LineString)
  const routeLineData = useMemo(() => {
    if (visibleActivities.length < 2) return null;

    // In production, use actual coordinates from activities
    // For now, creating a simple demo route
    const coordinates = visibleActivities.map((_, index) => {
      // Demo: Create a simple path around Tokyo
      const baseLng = 139.6917 + index * 0.02;
      const baseLat = 35.6895 + Math.sin(index) * 0.01;
      return [baseLng, baseLat];
    });

    return {
      type: 'Feature' as const,
      geometry: {
        type: 'LineString' as const,
        coordinates,
      },
      properties: {},
    };
  }, [visibleActivities]);

  const handleMarkerClick = useCallback(
    (activity: Activity) => {
      setSelectedActivity(activity);
      onActivityClick?.(activity);
    },
    [onActivityClick],
  );

  // Show warning if no API key
  if (!mapboxToken) {
    return (
      <div
        className={`flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-lg p-8 ${className}`}
      >
        <MapPin className="h-16 w-16 text-slate-400 dark:text-slate-600 mb-4" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-2">
          Mapbox API Key Required
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 text-center max-w-md mb-4">
          To view the interactive map, please add your Mapbox access token to the{' '}
          <code className="bg-slate-200 dark:bg-slate-700 px-1 rounded">
            NEXT_PUBLIC_MAPBOX_TOKEN
          </code>{' '}
          environment variable.
        </p>
        <a
          href="https://account.mapbox.com/access-tokens/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Get a free Mapbox token →
        </a>
      </div>
    );
  }

  return (
    <div
      className={`relative rounded-lg overflow-hidden border border-slate-200 dark:border-slate-800 ${className}`}
    >
      <Map
        {...initialViewState}
        mapStyle="mapbox://styles/mapbox/streets-v12"
        mapboxAccessToken={mapboxToken}
        style={{ width: '100%', height: '100%' }}
        attributionControl={true}
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" />
        <GeolocateControl position="top-right" />

        {/* Route Line */}
        {routeLineData && (
          <Source id="route" type="geojson" data={routeLineData}>
            <Layer
              id="route-line"
              type="line"
              paint={{
                'line-color': '#3b82f6',
                'line-width': 3,
                'line-opacity': 0.6,
                'line-dasharray': [2, 1],
              }}
            />
          </Source>
        )}

        {/* Activity Markers */}
        {visibleActivities.map((activity, index) => {
          const colors = categoryColors[activity.category];
          // Demo coordinates - in production, use activity.location.coordinates
          const lng = 139.6917 + index * 0.02;
          const lat = 35.6895 + Math.sin(index) * 0.01;

          return (
            <Marker
              key={activity.id}
              longitude={lng}
              latitude={lat}
              anchor="bottom"
              onClick={() => handleMarkerClick(activity)}
            >
              <div
                className="relative cursor-pointer transition-transform hover:scale-110"
                onMouseEnter={() => setHoveredActivity(activity.id)}
                onMouseLeave={() => setHoveredActivity(null)}
              >
                {/* Marker Pin */}
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-full border-2 shadow-lg"
                  style={{
                    backgroundColor: colors.bg,
                    borderColor: colors.border,
                    transform: hoveredActivity === activity.id ? 'scale(1.2)' : 'scale(1)',
                    transition: 'transform 0.2s ease-out',
                  }}
                >
                  <span className="text-lg">{getCategoryEmoji(activity.category)}</span>
                </div>

                {/* Marker Number Badge */}
                <div className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-xs font-bold text-slate-700 dark:text-slate-300">
                  {index + 1}
                </div>

                {/* Pointer Triangle */}
                <div
                  className="absolute left-1/2 bottom-0 -translate-x-1/2 translate-y-full"
                  style={{
                    width: 0,
                    height: 0,
                    borderLeft: '6px solid transparent',
                    borderRight: '6px solid transparent',
                    borderTop: `8px solid ${colors.border}`,
                  }}
                />
              </div>
            </Marker>
          );
        })}

        {/* Popup for Selected Activity */}
        {selectedActivity &&
          (() => {
            const activityIndex = visibleActivities.findIndex((a) => a.id === selectedActivity.id);
            const lng = 139.6917 + activityIndex * 0.02;
            const lat = 35.6895 + Math.sin(activityIndex) * 0.01;

            return (
              <Popup
                longitude={lng}
                latitude={lat}
                anchor="top"
                onClose={() => setSelectedActivity(null)}
                closeButton={false}
                className="activity-popup"
              >
                <div className="w-72 p-4">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-lg">
                          {getCategoryEmoji(selectedActivity.category)}
                        </span>
                        <span className="text-xs font-medium text-slate-600 dark:text-slate-400 capitalize">
                          {selectedActivity.category}
                        </span>
                      </div>
                      <h3 className="font-bold text-slate-900 dark:text-slate-50 leading-tight">
                        {selectedActivity.name}
                      </h3>
                    </div>
                    <button
                      onClick={() => setSelectedActivity(null)}
                      className="rounded-lg p-1 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Location */}
                  <div className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400 mb-3">
                    <MapPin className="h-4 w-4 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-slate-900 dark:text-slate-50">
                        {selectedActivity.location.name}
                      </p>
                      {selectedActivity.location.neighborhood && (
                        <p>{selectedActivity.location.neighborhood}</p>
                      )}
                    </div>
                  </div>

                  {/* Time */}
                  <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mb-2">
                    <Clock className="h-4 w-4" />
                    <span>
                      {selectedActivity.startTime} - {selectedActivity.endTime} (
                      {selectedActivity.duration} min)
                    </span>
                  </div>

                  {/* Cost */}
                  {selectedActivity.cost && selectedActivity.cost.amount > 0 && (
                    <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mb-3">
                      <DollarSign className="h-4 w-4" />
                      <span>
                        {selectedActivity.cost.currency}
                        {selectedActivity.cost.amount.toLocaleString()}
                        {selectedActivity.cost.perPerson && ' per person'}
                      </span>
                    </div>
                  )}

                  {/* Description */}
                  {selectedActivity.description && (
                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-3 border-t border-slate-200 dark:border-slate-700 pt-3">
                      {selectedActivity.description}
                    </p>
                  )}

                  {/* Priority Badge */}
                  {selectedActivity.priority && (
                    <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-700 pt-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          selectedActivity.priority === 'must-see'
                            ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/30 dark:text-amber-400'
                            : selectedActivity.priority === 'recommended'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-950/30 dark:text-blue-400'
                              : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400'
                        }`}
                      >
                        {selectedActivity.priority === 'must-see' && '⭐ '}
                        {selectedActivity.priority.charAt(0).toUpperCase() +
                          selectedActivity.priority.slice(1)}
                      </span>
                    </div>
                  )}
                </div>
              </Popup>
            );
          })()}
      </Map>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm rounded-lg border border-slate-200 dark:border-slate-800 p-3 shadow-lg max-w-[200px]">
        <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
          {selectedDayNumber ? `Day ${selectedDayNumber}` : 'All Days'}
        </h4>
        <p className="text-xs text-slate-600 dark:text-slate-400">
          {visibleActivities.length} {visibleActivities.length === 1 ? 'activity' : 'activities'}
        </p>
      </div>
    </div>
  );
}
