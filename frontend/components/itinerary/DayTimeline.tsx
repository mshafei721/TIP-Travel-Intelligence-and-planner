'use client';

import React from 'react';
import type { DayItinerary, TimeOfDay, Activity } from '@/types/itinerary';
import { ActivityCard } from './ActivityCard';
import { ChevronDown, ChevronUp, Plus, Sunrise, Sun, Sunset, Moon } from 'lucide-react';

interface DayTimelineProps {
  day: DayItinerary;
  onEditActivity?: (activity: Activity) => void;
  onRemoveActivity?: (activityId: string) => void;
  onViewOnMap?: (activity: Activity) => void;
  onAddActivity?: (dayNumber: number, timeOfDay: TimeOfDay) => void;
  readOnly?: boolean;
}

// Time of day configurations
const timeOfDayConfig = {
  morning: {
    label: 'Morning',
    timeRange: '6:00 AM - 12:00 PM',
    icon: Sunrise,
    gradient: 'from-amber-50 to-yellow-100 dark:from-amber-950/20 dark:to-yellow-950/20',
    borderColor: 'border-amber-300 dark:border-amber-800',
    dotColor: 'bg-amber-500',
  },
  afternoon: {
    label: 'Afternoon',
    timeRange: '12:00 PM - 6:00 PM',
    icon: Sun,
    gradient: 'from-orange-50 to-amber-100 dark:from-orange-950/20 dark:to-amber-950/20',
    borderColor: 'border-orange-300 dark:border-orange-800',
    dotColor: 'bg-orange-500',
  },
  evening: {
    label: 'Evening',
    timeRange: '6:00 PM - 10:00 PM',
    icon: Sunset,
    gradient: 'from-purple-50 to-blue-100 dark:from-purple-950/20 dark:to-blue-950/20',
    borderColor: 'border-purple-300 dark:border-purple-800',
    dotColor: 'bg-purple-500',
  },
  night: {
    label: 'Night',
    timeRange: '10:00 PM - 6:00 AM',
    icon: Moon,
    gradient: 'from-indigo-50 to-slate-100 dark:from-indigo-950/20 dark:to-slate-950/20',
    borderColor: 'border-indigo-300 dark:border-indigo-800',
    dotColor: 'bg-indigo-500',
  },
};

// Format date
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

export function DayTimeline({
  day,
  onEditActivity,
  onRemoveActivity,
  onViewOnMap,
  onAddActivity,
  readOnly = false,
}: DayTimelineProps) {
  const [expandedBlocks, setExpandedBlocks] = React.useState<Set<string>>(
    new Set(day.timeBlocks.map((b) => b.id))
  );

  const toggleBlock = (blockId: string) => {
    setExpandedBlocks((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(blockId)) {
        newSet.delete(blockId);
      } else {
        newSet.add(blockId);
      }
      return newSet;
    });
  };

  return (
    <div className="relative">
      {/* Day header */}
      <div className="sticky top-0 z-20 mb-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-amber-500 text-lg font-bold text-white shadow-md">
                {day.dayNumber}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  Day {day.dayNumber} - {day.location}
                </h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {formatDate(day.date)}
                </p>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
              {day.timeBlocks.reduce((acc, b) => acc + b.activities.length, 0)} activities
            </div>
          </div>
        </div>
        {day.notes && (
          <div className="mt-4 rounded-md bg-blue-50 p-3 text-sm text-blue-900 dark:bg-blue-950/30 dark:text-blue-300">
            📝 {day.notes}
          </div>
        )}
      </div>

      {/* Timeline */}
      <div className="relative pl-8">
        {/* Vertical connector line */}
        <div
          className="absolute left-[15px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-amber-500 to-blue-500"
          style={{
            backgroundSize: '100% 200%',
            animation: 'gradient-flow 3s ease infinite',
          }}
        />

        {/* Timeline blocks */}
        <div className="space-y-6">
          {day.timeBlocks.map((block, blockIndex) => {
            const config = timeOfDayConfig[block.timeOfDay];
            const Icon = config.icon;
            const isExpanded = expandedBlocks.has(block.id);
            const activityCount = block.activities.length;

            return (
              <div key={block.id} className="relative">
                {/* Timeline dot */}
                <div
                  className={`absolute -left-[27px] top-6 h-6 w-6 rounded-full ${config.dotColor} shadow-md ring-4 ring-white dark:ring-slate-900`}
                  style={{
                    animation: `dot-appear 0.3s ease-out ${blockIndex * 0.1}s both`,
                  }}
                />

                {/* Time block container */}
                <div
                  className={`rounded-lg border ${config.borderColor} bg-gradient-to-br ${config.gradient} p-4 shadow-sm transition-all duration-200`}
                  style={{
                    animation: `slide-in-left 0.4s ease-out ${blockIndex * 0.1 + 0.2}s both`,
                  }}
                >
                  {/* Time block header */}
                  <button
                    onClick={() => toggleBlock(block.id)}
                    className="mb-3 flex w-full items-center justify-between text-left transition-opacity hover:opacity-80"
                  >
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-white p-2 shadow-sm dark:bg-slate-800">
                        <Icon className="h-5 w-5 text-slate-700 dark:text-slate-300" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                          {config.label}
                        </h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          {config.timeRange} • {activityCount}{' '}
                          {activityCount === 1 ? 'activity' : 'activities'}
                        </p>
                      </div>
                    </div>
                    <div className="text-slate-500 dark:text-slate-400">
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </div>
                  </button>

                  {/* Activities */}
                  {isExpanded && (
                    <div className="space-y-3">
                      {block.activities.length > 0 ? (
                        block.activities.map((activity, actIndex) => (
                          <div
                            key={activity.id}
                            style={{
                              animation: `fade-in 0.3s ease-out ${actIndex * 0.08}s both`,
                            }}
                          >
                            <ActivityCard
                              activity={activity}
                              onEdit={onEditActivity}
                              onRemove={onRemoveActivity}
                              onViewOnMap={onViewOnMap}
                              readOnly={readOnly}
                            />
                          </div>
                        ))
                      ) : (
                        <div className="rounded-lg border-2 border-dashed border-slate-300 bg-white/50 p-6 text-center dark:border-slate-700 dark:bg-slate-800/50">
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            No activities planned for {config.label.toLowerCase()}
                          </p>
                        </div>
                      )}

                      {/* Add activity button */}
                      {!readOnly && onAddActivity && (
                        <button
                          onClick={() => onAddActivity(day.dayNumber, block.timeOfDay)}
                          className="flex w-full items-center justify-center gap-2 rounded-lg border-2 border-dashed border-slate-300 bg-white/50 p-3 text-sm font-medium text-slate-700 transition-all hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-blue-600 dark:hover:bg-blue-950/30 dark:hover:text-blue-400"
                        >
                          <Plus className="h-4 w-4" />
                          Add Activity
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Animations */}
      <style jsx>{`
        @keyframes dot-appear {
          from {
            opacity: 0;
            transform: scale(0);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes slide-in-left {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes gradient-flow {
          0%,
          100% {
            background-position: 0% 0%;
          }
          50% {
            background-position: 0% 100%;
          }
        }
      `}</style>
    </div>
  );
}
