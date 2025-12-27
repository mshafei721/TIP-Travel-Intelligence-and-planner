/**
 * Travel History API Client
 *
 * API functions for travel history management
 */

import type {
  ArchiveResponse,
  CountryVisit,
  TravelHistoryResponse,
  TravelStatsResponse,
  TravelTimelineResponse,
  TripRatingRequest,
} from '@/types/profile';
import { apiRequest } from './auth-utils';

// ============================================
// Travel History API Functions
// ============================================

/**
 * Get travel history for the authenticated user
 */
export async function getTravelHistory(options?: {
  includeArchived?: boolean;
  limit?: number;
  offset?: number;
}): Promise<TravelHistoryResponse> {
  const params = new URLSearchParams();
  if (options?.includeArchived) params.append('include_archived', 'true');
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());

  const queryString = params.toString();
  const endpoint = queryString ? `/api/history?${queryString}` : '/api/history';

  return apiRequest<TravelHistoryResponse>(endpoint);
}

/**
 * Get travel statistics
 */
export async function getTravelStats(): Promise<TravelStatsResponse> {
  return apiRequest<TravelStatsResponse>('/api/history/stats');
}

/**
 * Get countries visited for world map
 */
export async function getCountriesVisited(): Promise<CountryVisit[]> {
  return apiRequest<CountryVisit[]>('/api/history/countries');
}

/**
 * Get travel timeline
 */
export async function getTravelTimeline(year?: number): Promise<TravelTimelineResponse> {
  const endpoint = year ? `/api/history/timeline?year=${year}` : '/api/history/timeline';
  return apiRequest<TravelTimelineResponse>(endpoint);
}

/**
 * Archive a trip
 */
export async function archiveTrip(tripId: string): Promise<ArchiveResponse> {
  return apiRequest<ArchiveResponse>(`/api/history/trips/${tripId}/archive`, {
    method: 'POST',
  });
}

/**
 * Unarchive a trip
 */
export async function unarchiveTrip(tripId: string): Promise<ArchiveResponse> {
  return apiRequest<ArchiveResponse>(`/api/history/trips/${tripId}/unarchive`, {
    method: 'POST',
  });
}

/**
 * Rate a completed trip
 */
export async function rateTrip(
  tripId: string,
  data: TripRatingRequest,
): Promise<{ trip_id: string; rating: number; notes?: string; message: string }> {
  return apiRequest(`/api/history/trips/${tripId}/rate`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ============================================
// Utility Functions
// ============================================

/**
 * Format duration for display
 */
export function formatDuration(days: number): string {
  if (days === 1) return '1 day';
  if (days < 7) return `${days} days`;
  const weeks = Math.floor(days / 7);
  const remainingDays = days % 7;
  if (remainingDays === 0) {
    return weeks === 1 ? '1 week' : `${weeks} weeks`;
  }
  return `${weeks}w ${remainingDays}d`;
}

/**
 * Format date range for display
 */
export function formatDateRange(startDate: string, endDate: string): string {
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };

    if (start.getFullYear() !== end.getFullYear()) {
      return `${start.toLocaleDateString('en-US', { ...options, year: 'numeric' })} - ${end.toLocaleDateString('en-US', { ...options, year: 'numeric' })}`;
    }

    if (start.getMonth() === end.getMonth()) {
      return `${start.toLocaleDateString('en-US', { month: 'short' })} ${start.getDate()}-${end.getDate()}, ${start.getFullYear()}`;
    }

    return `${start.toLocaleDateString('en-US', options)} - ${end.toLocaleDateString('en-US', options)}, ${start.getFullYear()}`;
  } catch {
    return `${startDate} - ${endDate}`;
  }
}
