/**
 * Analytics API Client
 * API functions for usage analytics and trip analytics
 */

import type {
  DateRange,
  UsageStatsResponse,
  UsageTrendsResponse,
  AgentUsageResponse,
  TripAnalyticsResponse,
  DestinationAnalyticsResponse,
  BudgetAnalyticsResponse,
} from '@/types/analytics';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Get authentication token from Supabase session
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  try {
    const { createClient } = await import('@/lib/supabase/client');
    const supabase = createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      console.warn('Failed to get Supabase session:', error);
      return null;
    }

    return session.access_token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

/**
 * Generic API request helper
 */
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An unexpected error occurred',
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================
// Usage Analytics API Functions
// ============================================

/**
 * Get usage statistics for a given period
 */
export async function getUsageStats(period: DateRange = 'month'): Promise<UsageStatsResponse> {
  return apiRequest<UsageStatsResponse>(`/api/analytics/usage?period=${period}`);
}

/**
 * Get usage trends over time
 */
export async function getUsageTrends(period: DateRange = 'month'): Promise<UsageTrendsResponse> {
  return apiRequest<UsageTrendsResponse>(`/api/analytics/usage/trends?period=${period}`);
}

/**
 * Get agent usage statistics
 */
export async function getAgentUsageStats(period: DateRange = 'month'): Promise<AgentUsageResponse> {
  return apiRequest<AgentUsageResponse>(`/api/analytics/usage/agents?period=${period}`);
}

// ============================================
// Trip Analytics API Functions
// ============================================

/**
 * Get comprehensive trip analytics
 */
export async function getTripAnalytics(
  period: DateRange = 'year',
  limitDestinations: number = 10
): Promise<TripAnalyticsResponse> {
  return apiRequest<TripAnalyticsResponse>(
    `/api/analytics/trips?period=${period}&limit_destinations=${limitDestinations}`
  );
}

/**
 * Get destination analytics
 */
export async function getDestinationAnalytics(
  period: DateRange = 'year',
  limit: number = 20
): Promise<DestinationAnalyticsResponse> {
  return apiRequest<DestinationAnalyticsResponse>(
    `/api/analytics/trips/destinations?period=${period}&limit=${limit}`
  );
}

/**
 * Get budget analytics
 */
export async function getBudgetAnalytics(period: DateRange = 'year'): Promise<BudgetAnalyticsResponse> {
  return apiRequest<BudgetAnalyticsResponse>(`/api/analytics/trips/budgets?period=${period}`);
}
