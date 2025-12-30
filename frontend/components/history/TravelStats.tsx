'use client';

import { Globe, Building2, Plane, Calendar, MapPin, TrendingUp } from 'lucide-react';
import type { TravelStats as TravelStatsType } from '@/types/profile';

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ElementType;
  color: 'blue' | 'amber' | 'green' | 'purple' | 'rose' | 'slate';
}

function StatCard({ label, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-950/30 dark:text-green-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950/30 dark:text-purple-400',
    rose: 'bg-rose-50 text-rose-600 dark:bg-rose-950/30 dark:text-rose-400',
    slate: 'bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg p-2 ${colorClasses[color]}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">{value}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
        </div>
      </div>
    </div>
  );
}

export interface TravelStatsProps {
  stats: TravelStatsType;
  loading?: boolean;
}

/**
 * TravelStats - Display aggregated travel statistics
 *
 * Shows:
 * - Countries visited
 * - Cities explored
 * - Total trips
 * - Days traveled
 * - Favorite destination (if available)
 * - Travel streak (if available)
 */
export function TravelStats({ stats, loading }: TravelStatsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-xl border border-slate-200 bg-slate-100 dark:border-slate-800 dark:bg-slate-800"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Main stats grid */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          label="Countries Visited"
          value={stats.countriesVisited}
          icon={Globe}
          color="blue"
        />
        <StatCard
          label="Cities Explored"
          value={stats.citiesVisited}
          icon={Building2}
          color="amber"
        />
        <StatCard label="Total Trips" value={stats.totalTrips} icon={Plane} color="green" />
        <StatCard
          label="Days Traveled"
          value={stats.totalDaysTraveled}
          icon={Calendar}
          color="purple"
        />
      </div>

      {/* Additional stats (if available) */}
      {(stats.favoriteDestination || stats.travelStreak > 0) && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {stats.favoriteDestination && (
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
              <div className="rounded-lg bg-rose-50 p-2 text-rose-600 dark:bg-rose-950/30 dark:text-rose-400">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Favorite Destination</p>
                <p className="font-semibold text-slate-900 dark:text-slate-50">
                  {stats.favoriteDestination}
                </p>
              </div>
            </div>
          )}
          {stats.travelStreak > 0 && (
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
              <div className="rounded-lg bg-green-50 p-2 text-green-600 dark:bg-green-950/30 dark:text-green-400">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Travel Streak</p>
                <p className="font-semibold text-slate-900 dark:text-slate-50">
                  {stats.travelStreak} month{stats.travelStreak !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
