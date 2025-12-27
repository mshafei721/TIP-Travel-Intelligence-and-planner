/**
 * Trips API Client
 * API functions for trip management, updates, and version control
 */

import type {
  TripData,
  TripUpdateData,
  TripUpdateResponse,
  VersionHistoryResponse,
  RestoreVersionResponse,
  ChangePreviewData,
  RecalculationProgress,
  RecalculationCancelResponse,
  FieldChange,
  VersionCompareResponse,
  FIELD_IMPACT_MAP,
} from '@/types/trip-update';
import { apiRequest } from './auth-utils';

// ============================================
// Trip CRUD Operations
// ============================================

/**
 * Get trip by ID
 */
export async function getTrip(tripId: string): Promise<TripData> {
  return apiRequest<TripData>(`/api/trips/${tripId}`);
}

/**
 * Update trip details
 */
export async function updateTrip(
  tripId: string,
  updates: TripUpdateData,
): Promise<TripUpdateResponse> {
  return apiRequest<TripUpdateResponse>(`/api/trips/${tripId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

/**
 * Delete a trip
 */
export async function deleteTrip(tripId: string): Promise<{ success: boolean; message: string }> {
  return apiRequest(`/api/trips/${tripId}`, {
    method: 'DELETE',
  });
}

// ============================================
// Change Preview
// ============================================

/**
 * Preview changes before applying
 */
export async function previewChanges(
  tripId: string,
  updates: TripUpdateData,
): Promise<ChangePreviewData> {
  return apiRequest<ChangePreviewData>(`/api/trips/${tripId}/changes/preview`, {
    method: 'POST',
    body: JSON.stringify(updates),
  });
}

/**
 * Calculate changes locally (for immediate feedback)
 */
export function calculateLocalChanges(
  original: TripData,
  updates: TripUpdateData,
  fieldImpactMap: typeof FIELD_IMPACT_MAP,
): FieldChange[] {
  const changes: FieldChange[] = [];

  for (const [field, newValue] of Object.entries(updates)) {
    const oldValue = original[field as keyof TripData];

    // Skip if values are equal
    if (JSON.stringify(oldValue) === JSON.stringify(newValue)) continue;

    const fieldInfo = fieldImpactMap[field];
    if (!fieldInfo) continue;

    changes.push({
      field,
      fieldLabel: fieldInfo.label,
      oldValue,
      newValue,
      impactLevel: fieldInfo.impactLevel,
    });
  }

  return changes;
}

// ============================================
// Version History
// ============================================

/**
 * Get version history for a trip
 */
export async function getVersionHistory(
  tripId: string,
  limit?: number,
  offset?: number,
): Promise<VersionHistoryResponse> {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit.toString());
  if (offset) params.append('offset', offset.toString());

  const queryString = params.toString();
  const endpoint = queryString
    ? `/api/trips/${tripId}/versions?${queryString}`
    : `/api/trips/${tripId}/versions`;

  return apiRequest<VersionHistoryResponse>(endpoint);
}

/**
 * Get a specific version
 */
export async function getVersion(tripId: string, versionNumber: number): Promise<TripData> {
  return apiRequest<TripData>(`/api/trips/${tripId}/versions/${versionNumber}`);
}

/**
 * Restore a previous version
 */
export async function restoreVersion(
  tripId: string,
  versionNumber: number,
): Promise<RestoreVersionResponse> {
  return apiRequest<RestoreVersionResponse>(
    `/api/trips/${tripId}/versions/${versionNumber}/restore`,
    {
      method: 'POST',
    },
  );
}

/**
 * Compare two versions
 */
export async function compareVersions(
  tripId: string,
  versionA: number,
  versionB: number,
): Promise<VersionCompareResponse> {
  return apiRequest<VersionCompareResponse>(
    `/api/trips/${tripId}/versions/compare?version_a=${versionA}&version_b=${versionB}`,
  );
}

// ============================================
// Recalculation
// ============================================

/**
 * Get recalculation status
 */
export async function getRecalculationStatus(tripId: string): Promise<RecalculationProgress> {
  return apiRequest<RecalculationProgress>(`/api/trips/${tripId}/recalculation/status`);
}

/**
 * Start recalculation for specific sections
 */
export async function startRecalculation(
  tripId: string,
  sections?: string[],
): Promise<RecalculationProgress> {
  return apiRequest<RecalculationProgress>(`/api/trips/${tripId}/recalculation`, {
    method: 'POST',
    body: JSON.stringify({ sections }),
  });
}

/**
 * Cancel ongoing recalculation
 */
export async function cancelRecalculation(tripId: string): Promise<RecalculationCancelResponse> {
  return apiRequest<RecalculationCancelResponse>(`/api/trips/${tripId}/recalculation/cancel`, {
    method: 'POST',
  });
}

// ============================================
// Utility Functions
// ============================================

/**
 * Format date for display
 */
export function formatTripDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateString;
  }
}

/**
 * Calculate trip duration in days
 */
export function calculateTripDuration(departureDate: string, returnDate: string): number {
  const departure = new Date(departureDate);
  const returnD = new Date(returnDate);
  const diffTime = Math.abs(returnD.getTime() - departure.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Format budget with currency symbol
 */
export function formatBudget(amount: number, currency: string): string {
  const symbols: Record<string, string> = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    AUD: 'A$',
    CAD: 'C$',
  };
  const symbol = symbols[currency] || currency;
  return `${symbol}${amount.toLocaleString()}`;
}
