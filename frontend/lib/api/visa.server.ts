/**
 * Server-side Visa Report API Client
 * For use in Server Components only
 */

import type { ConfidenceLevel, TripPurpose, VisaIntelligence } from '@/types/visa';
import { getServerAuthToken } from './auth-utils.server';

/**
 * Fetch visa report for a specific trip (SERVER-SIDE)
 */
export async function fetchVisaReportServer(tripId: string): Promise<VisaIntelligence> {
  const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const url = `${apiUrl}/api/trips/${tripId}/report/visa`;
  const token = await getServerAuthToken();

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: 'no-store',
  });

  if (response.status === 404) {
    throw new Error('REPORT_NOT_FOUND');
  }

  if (response.status === 401 || response.status === 403) {
    throw new Error('UNAUTHORIZED');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to fetch visa report: ${response.statusText}`);
  }

  const data = await response.json();
  return transformVisaReport(data, tripId);
}

// Type definitions for API response
type VisaSourceApi = {
  name?: string;
  title?: string; // Backend uses 'title' instead of 'name'
  url?: string;
  source_type?: string;
  type?: 'government' | 'embassy' | 'third-party';
  reliability?: string;
  last_verified?: string;
  accessed_at?: string;
  verified_at?: string;
};

type VisaReportApi = {
  generated_at?: string;
  // Top-level trip context fields (new backend structure)
  user_nationality?: string;
  destination_country?: string;
  destination_city?: string;
  trip_purpose?: string;
  duration_days?: number;
  confidence_level?: 'official' | 'verified' | 'uncertain';
  // Nested visa requirement (agent output)
  visa_requirement?: {
    // Legacy: some fields may still be here from old data
    user_nationality?: string;
    destination_country?: string;
    destination_city?: string;
    trip_purpose?: string;
    duration_days?: number;
    // Core visa fields
    visa_required?: boolean;
    visa_type?: string;
    visa_category?: string;
    max_stay_days?: number;
    max_stay_duration?: string;
    validity_period?: string;
    multiple_entry?: boolean;
    urgency_level?: string;
    confidence_level?: 'official' | 'verified' | 'uncertain';
  } | null;
  application_process?: {
    application_method?: string;
    application_url?: string;
    processing_time?: string;
    processing_time_days?: number;
    cost_usd?: number;
    cost_local?: string | { amount?: number; currency?: string };
    required_documents?: string[];
    steps?: string[];
  } | null;
  entry_requirements?: {
    passport_validity?: string;
    passport_validity_months?: number;
    blank_pages_required?: number;
    vaccinations?: string[];
    health_declaration?: boolean;
    travel_insurance?: boolean;
    return_ticket?: boolean;
    proof_of_accommodation?: boolean;
    proof_of_funds?: boolean;
    other_requirements?: string[];
  } | null;
  tips?: string[];
  warnings?: string[];
  confidence_score?: number;
  sources?: VisaSourceApi[];
  last_verified?: string;
  is_partial_data?: boolean;
  missing_fields?: string[];
};

function transformVisaReport(apiData: VisaReportApi, tripId: string): VisaIntelligence {
  // Handle cost_local which can be string or object
  const costLocal = apiData.application_process?.cost_local;
  let normalizedCostLocal: { amount: number; currency: string } | undefined;
  if (costLocal && typeof costLocal === 'object' && 'amount' in costLocal) {
    if (typeof costLocal.amount === 'number' && typeof costLocal.currency === 'string') {
      normalizedCostLocal = { amount: costLocal.amount, currency: costLocal.currency };
    }
  }

  // Get trip context - prefer top-level fields (new structure) over nested (legacy)
  const userNationality =
    apiData.user_nationality || apiData.visa_requirement?.user_nationality || 'Unknown';
  const destinationCountry =
    apiData.destination_country || apiData.visa_requirement?.destination_country || 'Unknown';
  const destinationCity = apiData.destination_city || apiData.visa_requirement?.destination_city;
  const tripPurpose = apiData.trip_purpose || apiData.visa_requirement?.trip_purpose || 'tourism';
  const durationDays = apiData.duration_days ?? apiData.visa_requirement?.duration_days ?? 0;
  const confidenceLevel =
    apiData.confidence_level || apiData.visa_requirement?.confidence_level || 'uncertain';

  return {
    tripId,
    generatedAt: apiData.generated_at || new Date().toISOString(),
    userNationality,
    destinationCountry,
    destinationCity,
    tripPurpose: tripPurpose as TripPurpose,
    durationDays,
    visaRequirement: {
      visaRequired: apiData.visa_requirement?.visa_required ?? true,
      visaType: apiData.visa_requirement?.visa_type || 'Unknown',
      visaCategory: apiData.visa_requirement
        ?.visa_category as VisaIntelligence['visaRequirement']['visaCategory'],
      maxStayDays: apiData.visa_requirement?.max_stay_days,
      maxStayDuration:
        apiData.visa_requirement?.max_stay_duration || apiData.visa_requirement?.validity_period,
      multipleEntry: apiData.visa_requirement?.multiple_entry,
      confidenceLevel: confidenceLevel as ConfidenceLevel,
    },
    applicationProcess: {
      applicationMethod: apiData.application_process?.application_method || 'unknown',
      applicationUrl: apiData.application_process?.application_url,
      processingTime: apiData.application_process?.processing_time,
      processingTimeDays: apiData.application_process?.processing_time_days,
      costUsd: apiData.application_process?.cost_usd,
      costLocal: normalizedCostLocal,
      requiredDocuments: apiData.application_process?.required_documents || [],
      steps: apiData.application_process?.steps || [],
    },
    entryRequirements: {
      passportValidity: apiData.entry_requirements?.passport_validity || 'Not specified',
      passportValidityMonths: apiData.entry_requirements?.passport_validity_months,
      blankPagesRequired: apiData.entry_requirements?.blank_pages_required,
      vaccinations: apiData.entry_requirements?.vaccinations || [],
      returnTicket: apiData.entry_requirements?.return_ticket,
      proofOfAccommodation: apiData.entry_requirements?.proof_of_accommodation,
      proofOfFunds: apiData.entry_requirements?.proof_of_funds,
      otherRequirements: apiData.entry_requirements?.other_requirements || [],
    },
    tips: apiData.tips || [],
    warnings: apiData.warnings || [],
    confidenceScore: apiData.confidence_score || 0.0,
    sources: (apiData.sources || []).map((source) => ({
      name: source.name || source.title || 'Unknown Source',
      url: source.url || '',
      type: source.type || 'third-party',
      lastVerified: source.last_verified || new Date().toISOString(),
    })),
    lastVerified: apiData.last_verified || new Date().toISOString(),
    isPartialData: apiData.is_partial_data || false,
    missingFields: apiData.missing_fields || [],
  };
}
