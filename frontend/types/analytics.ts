/**
 * Analytics Types
 * Aligned with backend API models
 * Using camelCase to match API contract (backend uses Pydantic aliases)
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
  totalTrips: number;
  tripsCreated: number;
  tripsCompleted: number;
  reportsGenerated: number;
  agentsInvoked: Record<string, number>;
  avgGenerationTimeSeconds: number | null;
}

export interface UsageTrend {
  date: string;
  tripsCreated: number;
  reportsGenerated: number;
  countriesVisited: number;
}

export interface AgentUsageStats {
  agentType: string;
  invocations: number;
  avgDurationSeconds: number | null;
  successRate: number;
}

// ============================================
// Trip Analytics Types
// ============================================

export interface DestinationCount {
  country: string;
  countryCode: string;
  city: string | null;
  count: number;
  percentage: number;
}

export interface BudgetRange {
  rangeLabel: string;
  minValue: number;
  maxValue: number;
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
  uniqueCountries: number;
  uniqueCities: number;
  topDestinations: DestinationCount[];
  budgetAnalysis: {
    averageBudget: number | null;
    minBudget: number | null;
    maxBudget: number | null;
    budgetRanges: BudgetRange[];
  };
  seasonalTrends: SeasonalCount[];
  purposeBreakdown: PurposeCount[];
  avgTripDurationDays: number | null;
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
  totalInvocations: number;
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
    averageBudget: number | null;
    minBudget: number | null;
    maxBudget: number | null;
    budgetRanges: BudgetRange[];
    currency: string;
  };
}
