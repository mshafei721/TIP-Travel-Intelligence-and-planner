/**
 * Analytics Types
 * Aligned with backend API models
 */

// ============================================
// Enums and Constants
// ============================================

export type DateRange = 'week' | 'month' | 'quarter' | 'year' | 'all_time';

export const DATE_RANGE_OPTIONS: { value: DateRange; label: string }[] = [
  { value: 'week', label: 'Last 7 days' },
  { value: 'month', label: 'Last 30 days' },
  { value: 'quarter', label: 'Last 90 days' },
  { value: 'year', label: 'Last 12 months' },
  { value: 'all_time', label: 'All time' },
];

// ============================================
// Usage Analytics Types
// ============================================

export interface UsageStats {
  period: DateRange;
  total_trips: number;
  trips_created: number;
  trips_completed: number;
  reports_generated: number;
  agents_invoked: Record<string, number>;
  avg_generation_time_seconds: number | null;
}

export interface UsageTrend {
  date: string;
  trips_created: number;
  reports_generated: number;
  agents_used: number;
}

export interface AgentUsageStats {
  agent_type: string;
  display_name: string;
  total_invocations: number;
  successful_invocations: number;
  failed_invocations: number;
  avg_response_time_seconds: number | null;
  success_rate: number;
}

// ============================================
// Trip Analytics Types
// ============================================

export interface DestinationCount {
  country: string;
  country_code: string;
  city: string | null;
  count: number;
  percentage: number;
}

export interface BudgetRange {
  range_label: string;
  min_value: number;
  max_value: number;
  count: number;
  percentage: number;
}

export interface SeasonalCount {
  season: 'spring' | 'summer' | 'fall' | 'winter';
  count: number;
  percentage: number;
}

export interface PurposeCount {
  purpose: string;
  count: number;
  percentage: number;
}

export interface TripAnalytics {
  period: DateRange;
  unique_countries: number;
  unique_cities: number;
  top_destinations: DestinationCount[];
  budget_analysis: {
    average_budget: number | null;
    min_budget: number | null;
    max_budget: number | null;
    budget_ranges: BudgetRange[];
  };
  seasonal_trends: SeasonalCount[];
  purpose_breakdown: PurposeCount[];
  avg_trip_duration_days: number | null;
}

// ============================================
// API Response Types
// ============================================

export interface UsageStatsResponse {
  success: boolean;
  data: UsageStats;
}

export interface UsageTrendsResponse {
  success: boolean;
  data: UsageTrend[];
}

export interface AgentUsageResponse {
  success: boolean;
  total_invocations: number;
  data: AgentUsageStats[];
}

export interface TripAnalyticsResponse {
  success: boolean;
  data: TripAnalytics;
}

export interface DestinationAnalyticsResponse {
  success: boolean;
  data: DestinationCount[];
}

export interface BudgetAnalyticsResponse {
  success: boolean;
  data: {
    average_budget: number | null;
    min_budget: number | null;
    max_budget: number | null;
    budget_ranges: BudgetRange[];
    currency: string;
  };
}
