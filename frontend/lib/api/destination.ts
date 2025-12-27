/**
 * Destination/Country Intelligence API Client
 *
 * Handles fetching destination intelligence reports from the backend API.
 */

import { createClient } from '@/lib/supabase/client';
import type { CountryOverview } from '@/types/destination';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Error types for destination report API
 */
export type DestinationReportError =
  | 'REPORT_NOT_FOUND'
  | 'UNAUTHORIZED'
  | 'FETCH_ERROR'
  | 'PARSE_ERROR';

export interface DestinationReportErrorResponse {
  type: DestinationReportError;
  message: string;
  suggestion?: string;
}

/**
 * Backend API response for destination/country report
 */
interface CountryReportAPIResponse {
  report_id: string;
  trip_id: string;
  generated_at: string;
  confidence_score: number;

  // Basic Information
  country_name: string;
  country_code: string;
  capital: string;
  region: string;
  subregion?: string;

  // Demographics
  population: number;
  area_km2?: number;
  population_density?: number;

  // Languages
  official_languages: string[];
  common_languages?: string[];

  // Time and Geography
  time_zones: string[];
  coordinates?: { lat: number; lng: number };
  borders?: string[];

  // Practical Information
  emergency_numbers: Array<{
    service: string;
    number: string;
    notes?: string;
  }>;
  power_outlet: {
    plug_types: string[];
    voltage: string;
    frequency: string;
  };
  driving_side: string;

  // Currency
  currencies: string[];
  currency_codes: string[];

  // Safety
  safety_rating: number;
  travel_advisories?: Array<{
    level: string;
    title: string;
    summary: string;
    updated_at?: string;
    source: string;
  }>;

  // Additional
  notable_facts?: string[];
  best_time_to_visit?: string;

  // Metadata
  sources?: Array<{
    url: string;
    source_type: string;
    title?: string;
    reliability?: string;
    accessed_at?: string;
  }>;
  warnings?: string[];
}

/**
 * Fetch country/destination intelligence report for a trip
 *
 * @param tripId - The trip ID
 * @returns Country overview data or error
 */
export async function fetchDestinationReport(
  tripId: string,
): Promise<{ data: CountryOverview } | { error: DestinationReportErrorResponse }> {
  try {
    // Get Supabase session for auth token
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      return {
        error: {
          type: 'UNAUTHORIZED',
          message: 'You must be logged in to view destination reports',
        },
      };
    }

    // Fetch report from backend
    const response = await fetch(`${API_BASE_URL}/api/trips/${tripId}/report/destination`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Handle error responses
      if (response.status === 404) {
        const errorData = await response.json();
        return {
          error: {
            type: 'REPORT_NOT_FOUND',
            message: errorData.detail || 'Destination report not found',
            suggestion:
              'The destination report has not been generated yet. Generate it using the trip generation feature.',
          },
        };
      }

      if (response.status === 403) {
        return {
          error: {
            type: 'UNAUTHORIZED',
            message: 'You do not have permission to access this report',
          },
        };
      }

      throw new Error(`API returned ${response.status}: ${response.statusText}`);
    }

    // Parse response
    const apiData: CountryReportAPIResponse = await response.json();

    // Transform API response to frontend CountryOverview format
    const countryOverview: CountryOverview = {
      name: apiData.country_name,
      code: apiData.country_code,
      capital: apiData.capital,
      region: apiData.region,
      subregion: apiData.subregion || '',
      population: apiData.population,
      area: apiData.area_km2 || 0,
      languages: apiData.official_languages,
      timezones: apiData.time_zones,
      coordinates: apiData.coordinates || { lat: 0, lng: 0 },
      borderingCountries: apiData.borders || [],
      drivingSide: apiData.driving_side as 'left' | 'right',
      politicalSystem: undefined, // Not provided by Country Agent yet
      currency: {
        code: apiData.currency_codes[0] || '',
        name: apiData.currencies[0] || '',
        symbol: '', // Would need currency symbols mapping
      },
      flag: undefined, // Not provided by Country Agent - frontend can use emoji based on country code
      officialWebsite: undefined,
      tourismWebsite: undefined,
    };

    return { data: countryOverview };
  } catch (error) {
    console.error('Error fetching destination report:', error);
    return {
      error: {
        type: 'FETCH_ERROR',
        message: error instanceof Error ? error.message : 'Failed to fetch destination report',
      },
    };
  }
}

/**
 * Check if a destination report exists for a trip
 *
 * @param tripId - The trip ID
 * @returns true if report exists, false otherwise
 */
export async function checkDestinationReportExists(tripId: string): Promise<boolean> {
  const result = await fetchDestinationReport(tripId);
  return 'data' in result;
}
