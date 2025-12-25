import React from 'react';
import { notFound } from 'next/navigation';
import { DayTimeline } from '@/components/itinerary/DayTimeline';
import { FlightOptions } from '@/components/itinerary/FlightOptions';
import { sampleItinerary } from '@/lib/mock-data/itinerary-sample';
import type { Activity, TimeOfDay } from '@/types/itinerary';
import { Calendar, MapPin, Plane, ChevronRight } from 'lucide-react';

interface ItineraryPageProps {
  params: {
    id: string;
  };
}

export default function ItineraryPage({ params }: ItineraryPageProps) {
  // In production, fetch itinerary data from API based on params.id
  // For now, using sample data
  const itinerary = sampleItinerary;

  if (!itinerary) {
    notFound();
  }

  // Calculate trip stats
  const totalDays = itinerary.days.length;
  const totalActivities = itinerary.days.reduce(
    (acc, day) => acc + day.timeBlocks.reduce((a, b) => a + b.activities.length, 0),
    0
  );

  // Handlers (will be implemented in I7-FE-06 editing feature)
  const handleEditActivity = (activity: Activity) => {
    console.log('Edit activity:', activity);
    // TODO: Open edit modal
  };

  const handleRemoveActivity = (activityId: string) => {
    console.log('Remove activity:', activityId);
    // TODO: Confirm and remove activity
  };

  const handleViewOnMap = (activity: Activity) => {
    console.log('View on map:', activity);
    // TODO: Open map view and center on activity location
  };

  const handleAddActivity = (dayNumber: number, timeOfDay: TimeOfDay) => {
    console.log('Add activity:', { dayNumber, timeOfDay });
    // TODO: Open add activity modal
  };

  const handleSelectFlight = (flightId: string) => {
    console.log('Select flight:', flightId);
    // TODO: Update flight selection
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white/80 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-900/80">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <div className="mb-4 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <a
              href="/trips"
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              My Trips
            </a>
            <ChevronRight className="h-4 w-4" />
            <a
              href={`/trips/${params.id}`}
              className="hover:text-blue-600 dark:hover:text-blue-400"
            >
              {itinerary.tripName}
            </a>
            <ChevronRight className="h-4 w-4" />
            <span className="font-medium text-slate-900 dark:text-slate-50">
              Itinerary
            </span>
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
                    <dd className="font-semibold text-slate-900 dark:text-slate-50">
                      {totalDays}
                    </dd>
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
    </div>
  );
}
