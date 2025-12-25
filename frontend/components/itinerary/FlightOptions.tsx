'use client';

import React from 'react';
import type { FlightOption } from '@/types/itinerary';
import { Plane, Clock, Calendar, DollarSign, Info } from 'lucide-react';

interface FlightOptionsProps {
  flights: FlightOption[];
  onSelectFlight?: (flightId: string) => void;
  readOnly?: boolean;
}

// Format datetime
function formatFlightTime(datetime: string): string {
  const date = new Date(datetime);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

function formatFlightDate(datetime: string): string {
  const date = new Date(datetime);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// Format duration
function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

// Flight status badge colors
const statusColors = {
  searching: 'bg-gray-100 text-gray-700 dark:bg-gray-950 dark:text-gray-400',
  available: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
  selected: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
  booked: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400',
};

// Fare class colors
const fareColors = {
  economy: 'text-green-600 dark:text-green-400',
  'premium-economy': 'text-blue-600 dark:text-blue-400',
  business: 'text-purple-600 dark:text-purple-400',
  first: 'text-amber-600 dark:text-amber-400',
};

export function FlightOptions({
  flights,
  onSelectFlight,
  readOnly = false,
}: FlightOptionsProps) {
  const [expandedFlights, setExpandedFlights] = React.useState<Set<string>>(new Set());

  const toggleExpanded = (flightId: string) => {
    setExpandedFlights((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(flightId)) {
        newSet.delete(flightId);
      } else {
        newSet.add(flightId);
      }
      return newSet;
    });
  };

  if (flights.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center dark:border-slate-700 dark:bg-slate-800/50">
        <Plane className="mx-auto mb-3 h-12 w-12 text-slate-400" />
        <p className="text-slate-600 dark:text-slate-400">
          No flights added yet. Add flight details to complete your itinerary.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {flights.map((flight, index) => {
        const isExpanded = expandedFlights.has(flight.id);
        const fareClass = flight.price.fareClass.replace('-', ' ');

        return (
          <div
            key={flight.id}
            className="group overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm transition-all duration-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
            style={{
              animation: `fade-in 0.3s ease-out ${index * 0.1}s both`,
            }}
          >
            {/* Flight type badge */}
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-2 dark:border-slate-800 dark:bg-slate-800/50">
              <div className="flex items-center gap-2">
                <Plane
                  className={`h-4 w-4 ${
                    flight.type === 'outbound'
                      ? 'text-blue-600 dark:text-blue-400'
                      : flight.type === 'return'
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-purple-600 dark:text-purple-400'
                  }`}
                />
                <span className="text-sm font-semibold capitalize text-slate-700 dark:text-slate-300">
                  {flight.type} Flight
                </span>
              </div>
              {flight.bookingStatus && (
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${statusColors[flight.bookingStatus]}`}
                >
                  {flight.bookingStatus === 'booked' ? '✓ ' : ''}
                  {flight.bookingStatus.charAt(0).toUpperCase() + flight.bookingStatus.slice(1)}
                </span>
              )}
            </div>

            {/* Main flight info */}
            <div className="p-6">
              {/* Flight arc visualization */}
              <div className="relative mb-6">
                {/* Departure */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-3xl font-bold text-slate-900 dark:text-slate-50">
                      {flight.departure.airportCode}
                    </div>
                    <div className="mt-1 text-sm font-medium text-slate-600 dark:text-slate-400">
                      {flight.departure.city}
                    </div>
                    <div className="mt-2 text-xl font-semibold text-blue-600 dark:text-blue-400">
                      {formatFlightTime(flight.departure.datetime)}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-500">
                      {formatFlightDate(flight.departure.datetime)}
                    </div>
                  </div>

                  {/* Arc connector */}
                  <div className="relative mx-8 flex flex-1 flex-col items-center justify-center">
                    {/* Animated dotted line */}
                    <div className="relative w-full">
                      <svg
                        viewBox="0 0 200 60"
                        className="w-full"
                        preserveAspectRatio="none"
                      >
                        <defs>
                          <linearGradient id={`grad-${flight.id}`} x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
                            <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.8" />
                          </linearGradient>
                        </defs>
                        <path
                          d="M 10 50 Q 100 10, 190 50"
                          fill="none"
                          stroke={`url(#grad-${flight.id})`}
                          strokeWidth="3"
                          strokeDasharray="5,5"
                          className="animate-dash"
                        />
                      </svg>
                      {/* Airplane icon */}
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white p-2 shadow-md dark:bg-slate-800">
                        <Plane className="h-4 w-4 rotate-90 text-blue-600 dark:text-blue-400" />
                      </div>
                    </div>

                    {/* Duration */}
                    <div className="mt-2 text-center">
                      <div className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        {formatDuration(flight.duration)}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-500">
                        {flight.stops === 0 ? 'Direct' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                      </div>
                    </div>
                  </div>

                  {/* Arrival */}
                  <div className="flex-1 text-right">
                    <div className="text-3xl font-bold text-slate-900 dark:text-slate-50">
                      {flight.arrival.airportCode}
                    </div>
                    <div className="mt-1 text-sm font-medium text-slate-600 dark:text-slate-400">
                      {flight.arrival.city}
                    </div>
                    <div className="mt-2 text-xl font-semibold text-amber-600 dark:text-amber-400">
                      {formatFlightTime(flight.arrival.datetime)}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-500">
                      {formatFlightDate(flight.arrival.datetime)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Flight details grid */}
              <div className="grid grid-cols-2 gap-4 rounded-lg bg-slate-50 p-4 dark:bg-slate-800/50 md:grid-cols-4">
                {/* Airline */}
                <div className="text-center">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-500">
                    Airline
                  </div>
                  <div className="mt-1 font-semibold text-slate-900 dark:text-slate-50">
                    {flight.airline}
                  </div>
                  {flight.flightNumber && (
                    <div className="mt-0.5 text-xs font-mono text-slate-600 dark:text-slate-400">
                      {flight.flightNumber}
                    </div>
                  )}
                </div>

                {/* Class */}
                <div className="text-center">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-500">
                    Class
                  </div>
                  <div className={`mt-1 font-semibold capitalize ${fareColors[flight.price.fareClass]}`}>
                    {fareClass}
                  </div>
                </div>

                {/* Price */}
                <div className="text-center">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-500">
                    Price
                  </div>
                  <div className="mt-1 text-lg font-bold text-green-600 dark:text-green-400">
                    ${flight.price.amount.toLocaleString()}
                  </div>
                </div>

                {/* Stops */}
                <div className="text-center">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-500">
                    Stops
                  </div>
                  <div className="mt-1 font-semibold text-slate-900 dark:text-slate-50">
                    {flight.stops === 0 ? 'Direct' : flight.stops}
                  </div>
                </div>
              </div>

              {/* Expandable layover details */}
              {flight.layovers && flight.layovers.length > 0 && (
                <div className="mt-3">
                  <button
                    onClick={() => toggleExpanded(flight.id)}
                    className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    <Info className="h-4 w-4" />
                    {isExpanded ? 'Hide' : 'Show'} layover details
                  </button>

                  {isExpanded && (
                    <div className="mt-3 space-y-2 rounded-lg bg-amber-50 p-3 dark:bg-amber-950/20">
                      <div className="text-xs font-semibold uppercase tracking-wide text-amber-900 dark:text-amber-400">
                        Layovers
                      </div>
                      {flight.layovers.map((layover, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between text-sm"
                        >
                          <div>
                            <span className="font-semibold text-slate-900 dark:text-slate-50">
                              {layover.airportCode}
                            </span>
                            <span className="ml-2 text-slate-600 dark:text-slate-400">
                              {layover.airportName}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-slate-600 dark:text-slate-400">
                            <Clock className="h-3.5 w-3.5" />
                            {formatDuration(layover.duration)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Action button */}
              {!readOnly && onSelectFlight && flight.bookingStatus !== 'booked' && (
                <button
                  onClick={() => onSelectFlight(flight.id)}
                  className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white transition-colors hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-500"
                >
                  {flight.bookingStatus === 'selected' ? 'Book This Flight' : 'Select Flight'}
                </button>
              )}
            </div>
          </div>
        );
      })}

      {/* Animations */}
      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes dash {
          to {
            stroke-dashoffset: -10;
          }
        }

        :global(.animate-dash) {
          animation: dash 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
