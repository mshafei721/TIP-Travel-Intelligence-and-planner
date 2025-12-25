'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import dynamic from 'next/dynamic';
import { DayTimeline } from '@/components/itinerary/DayTimeline';
import { FlightOptions } from '@/components/itinerary/FlightOptions';
import { ActivityModal } from '@/components/itinerary/ActivityModal';
import { ConfirmDialog } from '@/components/itinerary/ConfirmDialog';
import { sampleItinerary } from '@/lib/mock-data/itinerary-sample';
import type { Activity, TimeOfDay, TripItinerary } from '@/types/itinerary';
import { Calendar, MapPin, Plane, ChevronRight, Map as MapIcon, List } from 'lucide-react';

// Dynamically import MapView with no SSR to avoid mapbox-gl issues
const MapView = dynamic(
  () => import('@/components/itinerary/MapView').then((mod) => ({ default: mod.MapView })),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[600px] items-center justify-center rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">Loading map...</p>
        </div>
      </div>
    ),
  },
);

interface ItineraryPageProps {
  params: {
    id: string;
  };
}

export default function ItineraryPage({ params }: ItineraryPageProps) {
  // State for itinerary data (using sample data, in production this would come from API)
  const [itinerary, setItinerary] = useState<TripItinerary>(sampleItinerary);

  // View mode state
  const [viewMode, setViewMode] = useState<'timeline' | 'map'>('timeline');
  const [mapSelectedDay, setMapSelectedDay] = useState<number | null>(null);

  // Modal state
  const [isActivityModalOpen, setIsActivityModalOpen] = useState(false);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [editingActivity, setEditingActivity] = useState<Activity | undefined>(undefined);
  const [activityToDelete, setActivityToDelete] = useState<string | null>(null);
  const [selectedDayNumber, setSelectedDayNumber] = useState<number>(1);
  const [selectedTimeOfDay, setSelectedTimeOfDay] = useState<TimeOfDay>('morning');

  if (!itinerary) {
    notFound();
  }

  // Calculate trip stats
  const totalDays = itinerary.days.length;
  const totalActivities = itinerary.days.reduce(
    (acc, day) => acc + day.timeBlocks.reduce((a, b) => a + b.activities.length, 0),
    0,
  );

  // Get activities for time conflict detection
  const getActivitiesForDay = (dayNumber: number): Activity[] => {
    const day = itinerary.days.find((d) => d.dayNumber === dayNumber);
    if (!day) return [];
    return day.timeBlocks.flatMap((block) => block.activities);
  };

  // Handler: Open add activity modal
  const handleAddActivity = (dayNumber: number, timeOfDay: TimeOfDay) => {
    setSelectedDayNumber(dayNumber);
    setSelectedTimeOfDay(timeOfDay);
    setEditingActivity(undefined);
    setIsActivityModalOpen(true);
  };

  // Handler: Open edit activity modal
  const handleEditActivity = (activity: Activity) => {
    // Find which day this activity belongs to
    for (const day of itinerary.days) {
      for (const block of day.timeBlocks) {
        if (block.activities.some((a) => a.id === activity.id)) {
          setSelectedDayNumber(day.dayNumber);
          setSelectedTimeOfDay(block.timeOfDay);
          break;
        }
      }
    }
    setEditingActivity(activity);
    setIsActivityModalOpen(true);
  };

  // Handler: Save activity (add or edit)
  const handleSaveActivity = (activityData: Partial<Activity>) => {
    setItinerary((prev) => {
      const newItinerary = { ...prev };
      const dayIndex = newItinerary.days.findIndex((d) => d.dayNumber === selectedDayNumber);

      if (dayIndex === -1) return prev;

      const day = { ...newItinerary.days[dayIndex] };
      const blockIndex = day.timeBlocks.findIndex((b) => b.timeOfDay === selectedTimeOfDay);

      if (blockIndex === -1) return prev;

      const block = { ...day.timeBlocks[blockIndex] };

      if (editingActivity) {
        // Update existing activity
        const activityIndex = block.activities.findIndex((a) => a.id === editingActivity.id);
        if (activityIndex !== -1) {
          block.activities = [...block.activities];
          block.activities[activityIndex] = { ...block.activities[activityIndex], ...activityData };
        }
      } else {
        // Add new activity
        const newActivity = activityData as Activity;
        block.activities = [...block.activities, newActivity];
      }

      day.timeBlocks = [...day.timeBlocks];
      day.timeBlocks[blockIndex] = block;
      newItinerary.days = [...newItinerary.days];
      newItinerary.days[dayIndex] = day;

      return newItinerary;
    });
  };

  // Handler: Open remove confirmation dialog
  const handleRemoveActivity = (activityId: string) => {
    setActivityToDelete(activityId);
    setIsConfirmDialogOpen(true);
  };

  // Handler: Confirm remove activity
  const handleConfirmRemove = () => {
    if (!activityToDelete) return;

    setItinerary((prev) => {
      const newItinerary = { ...prev };

      // Find and remove the activity
      for (let i = 0; i < newItinerary.days.length; i++) {
        const day = { ...newItinerary.days[i] };
        let activityFound = false;

        for (let j = 0; j < day.timeBlocks.length; j++) {
          const block = { ...day.timeBlocks[j] };
          const activityIndex = block.activities.findIndex((a) => a.id === activityToDelete);

          if (activityIndex !== -1) {
            block.activities = block.activities.filter((a) => a.id !== activityToDelete);
            day.timeBlocks = [...day.timeBlocks];
            day.timeBlocks[j] = block;
            activityFound = true;
            break;
          }
        }

        if (activityFound) {
          newItinerary.days = [...newItinerary.days];
          newItinerary.days[i] = day;
          break;
        }
      }

      return newItinerary;
    });

    setActivityToDelete(null);
  };

  // Handler: View on map (placeholder for I7-FE-04 MapView)
  const handleViewOnMap = (activity: Activity) => {
    console.log('View on map:', activity);
    // TODO: Implement in I7-FE-04 when Mapbox is integrated
    alert(`Map view for "${activity.name}" will be available when Mapbox is integrated (I7-FE-04)`);
  };

  // Handler: Select flight
  const handleSelectFlight = (flightId: string) => {
    setItinerary((prev) => ({
      ...prev,
      flights: prev.flights.map((flight) =>
        flight.id === flightId ? { ...flight, bookingStatus: 'selected' as const } : flight,
      ),
    }));
  };

  // Get activity by ID (for confirm dialog)
  const getActivityById = (activityId: string): Activity | undefined => {
    for (const day of itinerary.days) {
      for (const block of day.timeBlocks) {
        const activity = block.activities.find((a) => a.id === activityId);
        if (activity) return activity;
      }
    }
    return undefined;
  };

  const activityToDeleteData = activityToDelete ? getActivityById(activityToDelete) : undefined;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white/80 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/80">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <div className="mb-4 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <Link href="/trips" className="hover:text-blue-600 dark:hover:text-blue-400">
              My Trips
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link
              href={`/trips/${params.id}`}
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              {itinerary.tripName}
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="font-medium text-slate-900 dark:text-slate-50">Itinerary</span>
          </div>

          {/* Title */}
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50 md:text-4xl">
                {itinerary.tripName}
              </h1>
              <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-4 w-4" />
                  <span>{itinerary.destination}</span>
                </div>
                <span className="text-slate-400 dark:text-slate-600">•</span>
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {new Date(itinerary.startDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}{' '}
                    -{' '}
                    {new Date(itinerary.endDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
                <span className="text-slate-400 dark:text-slate-600">•</span>
                <span>
                  {totalDays} days, {totalActivities} activities
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              {/* View Mode Toggle */}
              <div className="flex rounded-lg border border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-800 p-1">
                <button
                  onClick={() => setViewMode('timeline')}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all ${
                    viewMode === 'timeline'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700'
                  }`}
                >
                  <List className="h-4 w-4" />
                  Timeline
                </button>
                <button
                  onClick={() => setViewMode('map')}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all ${
                    viewMode === 'map'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700'
                  }`}
                >
                  <MapIcon className="h-4 w-4" />
                  Map
                </button>
              </div>

              <button className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">
                Export PDF
              </button>
              <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700">
                <Plane className="h-4 w-4" />
                View Flights
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-12">
          {/* Sidebar - Quick navigation */}
          <aside className="lg:col-span-3">
            <div className="sticky top-6 space-y-4">
              {/* Day navigation */}
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">
                  Quick Navigation
                </h3>
                <nav className="space-y-1">
                  {itinerary.days.map((day) => (
                    <a
                      key={day.dayNumber}
                      href={`#day-${day.dayNumber}`}
                      className="block rounded-md px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-blue-50 hover:text-blue-700 dark:text-slate-300 dark:hover:bg-blue-950/30 dark:hover:text-blue-400"
                    >
                      <div className="flex items-center gap-2">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-200 text-xs font-bold dark:bg-slate-700">
                          {day.dayNumber}
                        </div>
                        <span>{day.location}</span>
                      </div>
                    </a>
                  ))}
                  {itinerary.flights.length > 0 && (
                    <>
                      <div className="my-2 border-t border-slate-200 dark:border-slate-800" />
                      <a
                        href="#flights"
                        className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-blue-50 hover:text-blue-700 dark:text-slate-300 dark:hover:bg-blue-950/30 dark:hover:text-blue-400"
                      >
                        <Plane className="h-4 w-4" />
                        <span>Flights</span>
                      </a>
                    </>
                  )}
                </nav>
              </div>

              {/* Trip stats */}
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700 dark:text-slate-300">
                  Trip Summary
                </h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-slate-600 dark:text-slate-400">Days</dt>
                    <dd className="font-semibold text-slate-900 dark:text-slate-50">{totalDays}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-slate-600 dark:text-slate-400">Activities</dt>
                    <dd className="font-semibold text-slate-900 dark:text-slate-50">
                      {totalActivities}
                    </dd>
                  </div>
                  {itinerary.totalBudget && (
                    <div className="flex justify-between border-t border-slate-200 pt-2 dark:border-slate-800">
                      <dt className="text-slate-600 dark:text-slate-400">Budget</dt>
                      <dd className="font-semibold text-green-600 dark:text-green-400">
                        ¥{itinerary.totalBudget.toLocaleString()}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>
          </aside>

          {/* Main itinerary */}
          <main className="lg:col-span-9">
            <div className="space-y-8">
              {/* Timeline View */}
              {viewMode === 'timeline' && (
                <>
                  {/* Days */}
                  {itinerary.days.map((day) => (
                    <div key={day.dayNumber} id={`day-${day.dayNumber}`}>
                      <DayTimeline
                        day={day}
                        onEditActivity={handleEditActivity}
                        onRemoveActivity={handleRemoveActivity}
                        onViewOnMap={handleViewOnMap}
                        onAddActivity={handleAddActivity}
                        readOnly={false}
                      />
                    </div>
                  ))}
                </>
              )}

              {/* Map View */}
              {viewMode === 'map' && (
                <div className="space-y-4">
                  {/* Day Filter for Map */}
                  <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        Filter by day:
                      </span>
                      <button
                        onClick={() => setMapSelectedDay(null)}
                        className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                          mapSelectedDay === null
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                        }`}
                      >
                        All Days
                      </button>
                      {itinerary.days.map((day) => (
                        <button
                          key={day.dayNumber}
                          onClick={() => setMapSelectedDay(day.dayNumber)}
                          className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                            mapSelectedDay === day.dayNumber
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
                          }`}
                        >
                          Day {day.dayNumber}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Map Container */}
                  <MapView
                    days={itinerary.days}
                    selectedDayNumber={mapSelectedDay}
                    onActivityClick={handleEditActivity}
                    className="h-[600px]"
                  />
                </div>
              )}

              {/* Flights section */}
              {itinerary.flights.length > 0 && (
                <div id="flights" className="scroll-mt-6">
                  <div className="mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-950/50">
                        <Plane className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                          Flights
                        </h2>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                          Your flight details and options
                        </p>
                      </div>
                    </div>
                  </div>
                  <FlightOptions
                    flights={itinerary.flights}
                    onSelectFlight={handleSelectFlight}
                    readOnly={false}
                  />
                </div>
              )}
            </div>
          </main>
        </div>
      </div>

      {/* Activity Modal */}
      <ActivityModal
        isOpen={isActivityModalOpen}
        onClose={() => {
          setIsActivityModalOpen(false);
          setEditingActivity(undefined);
        }}
        onSave={handleSaveActivity}
        activity={editingActivity}
        dayNumber={selectedDayNumber}
        timeOfDay={selectedTimeOfDay}
        existingActivities={getActivitiesForDay(selectedDayNumber)}
      />

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={isConfirmDialogOpen}
        onClose={() => {
          setIsConfirmDialogOpen(false);
          setActivityToDelete(null);
        }}
        onConfirm={handleConfirmRemove}
        title="Remove Activity?"
        message={
          activityToDeleteData
            ? `Are you sure you want to remove "${activityToDeleteData.name}" from your itinerary? This action cannot be undone.`
            : 'Are you sure you want to remove this activity?'
        }
        confirmText="Remove Activity"
        cancelText="Keep Activity"
        variant="danger"
      />
    </div>
  );
}
