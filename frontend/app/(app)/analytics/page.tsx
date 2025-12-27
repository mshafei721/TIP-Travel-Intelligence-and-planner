'use client';

import { useState, useEffect, useCallback } from 'react';
import { MapPin, Plane, Clock, Bot, TrendingUp, DollarSign } from 'lucide-react';
import {
  StatCard,
  UsageChart,
  DestinationChart,
  BudgetChart,
  AgentUsageChart,
} from '@/components/analytics';
import { PageHeader } from '@/components/ui/PageHeader';
import {
  getUsageStats,
  getUsageTrends,
  getAgentUsageStats,
  getTripAnalytics,
} from '@/lib/api/analytics';
import type {
  DateRange,
  UsageStats,
  UsageTrend,
  AgentUsageStats,
  TripAnalytics,
} from '@/types/analytics';
import { DATE_RANGE_OPTIONS } from '@/types/analytics';

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<DateRange>('month');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [usageTrends, setUsageTrends] = useState<UsageTrend[]>([]);
  const [agentStats, setAgentStats] = useState<AgentUsageStats[]>([]);
  const [tripAnalytics, setTripAnalytics] = useState<TripAnalytics | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [usageRes, trendsRes, agentsRes, tripsRes] = await Promise.allSettled([
        getUsageStats(period),
        getUsageTrends(period),
        getAgentUsageStats(period),
        getTripAnalytics(period),
      ]);

      if (usageRes.status === 'fulfilled') {
        setUsageStats(usageRes.value.data);
      }
      if (trendsRes.status === 'fulfilled') {
        setUsageTrends(trendsRes.value.data);
      }
      if (agentsRes.status === 'fulfilled') {
        setAgentStats(agentsRes.value.data);
      }
      if (tripsRes.status === 'fulfilled') {
        setTripAnalytics(tripsRes.value.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const totalAgentInvocations = agentStats.reduce((sum, a) => sum + a.invocations, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Analytics"
        description="Track your travel planning activity and insights"
        backHref="/dashboard"
        backLabel="Back to Dashboard"
        actions={
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as DateRange)}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            {DATE_RANGE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        }
      />

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
          <p className="text-red-700 dark:text-red-400">{error}</p>
          <button
            onClick={fetchData}
            className="mt-2 text-sm font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
          >
            Try again
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-32 animate-pulse rounded-xl border border-slate-200 bg-slate-100 dark:border-slate-800 dark:bg-slate-800"
            />
          ))}
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Trips"
              value={usageStats?.total_trips ?? 0}
              description={`${usageStats?.trips_completed ?? 0} completed`}
              icon={Plane}
            />
            <StatCard
              title="Countries Visited"
              value={tripAnalytics?.unique_countries ?? 0}
              description={`${tripAnalytics?.unique_cities ?? 0} cities explored`}
              icon={MapPin}
            />
            <StatCard
              title="AI Agents Used"
              value={totalAgentInvocations}
              description={`${agentStats.length} different agents`}
              icon={Bot}
            />
            <StatCard
              title="Avg Trip Duration"
              value={
                tripAnalytics?.avg_trip_duration_days
                  ? `${tripAnalytics.avg_trip_duration_days.toFixed(1)} days`
                  : 'N/A'
              }
              description="Average trip length"
              icon={Clock}
            />
          </div>

          {/* Charts Row 1 */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
              <UsageChart data={usageTrends} />
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
              <DestinationChart data={tripAnalytics?.top_destinations ?? []} />
            </div>
          </div>

          {/* Charts Row 2 */}
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
              <BudgetChart
                data={tripAnalytics?.budget_analysis.budget_ranges ?? []}
                averageBudget={tripAnalytics?.budget_analysis.average_budget ?? null}
              />
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
              <AgentUsageChart data={agentStats} />
            </div>
          </div>

          {/* Additional Stats */}
          {tripAnalytics && (
            <div className="grid gap-4 md:grid-cols-3">
              {/* Seasonal Trends */}
              <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
                  <TrendingUp className="h-5 w-5" />
                  Seasonal Trends
                </h3>
                <div className="space-y-3">
                  {tripAnalytics.seasonal_trends.length > 0 ? (
                    tripAnalytics.seasonal_trends.map((trend) => (
                      <div key={trend.season} className="flex items-center justify-between">
                        <span className="capitalize text-slate-600 dark:text-slate-400">
                          {trend.season}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${trend.percentage}%` }}
                            />
                          </div>
                          <span className="w-12 text-right text-sm font-medium text-slate-900 dark:text-slate-100">
                            {trend.percentage.toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500">No seasonal data available</p>
                  )}
                </div>
              </div>

              {/* Trip Purpose */}
              <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
                  <Plane className="h-5 w-5" />
                  Trip Purpose
                </h3>
                <div className="space-y-3">
                  {tripAnalytics.purpose_breakdown.length > 0 ? (
                    tripAnalytics.purpose_breakdown.map((purpose) => (
                      <div key={purpose.purpose} className="flex items-center justify-between">
                        <span className="capitalize text-slate-600 dark:text-slate-400">
                          {purpose.purpose}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                            <div
                              className="h-full bg-green-500"
                              style={{ width: `${purpose.percentage}%` }}
                            />
                          </div>
                          <span className="w-12 text-right text-sm font-medium text-slate-900 dark:text-slate-100">
                            {purpose.percentage.toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500">No purpose data available</p>
                  )}
                </div>
              </div>

              {/* Budget Summary */}
              <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
                <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
                  <DollarSign className="h-5 w-5" />
                  Budget Summary
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600 dark:text-slate-400">Average</span>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">
                      {tripAnalytics.budget_analysis.average_budget
                        ? `$${tripAnalytics.budget_analysis.average_budget.toLocaleString()}`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600 dark:text-slate-400">Minimum</span>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">
                      {tripAnalytics.budget_analysis.min_budget
                        ? `$${tripAnalytics.budget_analysis.min_budget.toLocaleString()}`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600 dark:text-slate-400">Maximum</span>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">
                      {tripAnalytics.budget_analysis.max_budget
                        ? `$${tripAnalytics.budget_analysis.max_budget.toLocaleString()}`
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
