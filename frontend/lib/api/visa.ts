/**
 * Visa Report API Client
 *
 * Functions for fetching visa intelligence reports from the backend
 */

import type { ConfidenceLevel, TripPurpose, VisaCategory, VisaIntelligence } from '@/types/visa';

type VisaSourceApi = {
  name?: string;
  url?: string;
  type?: 'government' | 'embassy' | 'third-party';
  last_verified?: string;
};

type VisaRequirementApi = {
  user_nationality?: string;
  destination_country?: string;
  destination_city?: string;
  trip_purpose?: TripPurpose;
  duration_days?: number;
  visa_required?: boolean;
  visa_type?: string;
  visa_category?: VisaCategory;
  max_stay_days?: number;
  max_stay_duration?: string;
  multiple_entry?: boolean;
  confidence_level?: ConfidenceLevel;
};

type ApplicationProcessApi = {
  application_method?: string;
  application_url?: string;
  processing_time?: string;
  processing_time_days?: number;
  cost_usd?: number;
  cost_local?: {
    amount?: number;
    currency?: string;
  };
  required_documents?: string[];
  steps?: string[];
};

type EntryRequirementsApi = {
  passport_validity?: string;
  passport_validity_months?: number;
  blank_pages_required?: number;
  vaccinations?: string[];
  return_ticket?: boolean;
  proof_of_accommodation?: boolean;
  proof_of_funds?: boolean;
  other_requirements?: string[];
};

type VisaReportApi = {
  generated_at?: string;
  visa_requirement?: VisaRequirementApi | null;
  application_process?: ApplicationProcessApi | null;
  entry_requirements?: EntryRequirementsApi | null;
  tips?: string[];
  warnings?: string[];
  confidence_score?: number;
  sources?: VisaSourceApi[];
  last_verified?: string;
  is_partial_data?: boolean;
  missing_fields?: string[];
};

/**
 * Fetch visa report for a specific trip
 *
 * @param tripId - UUID of the trip
 * @returns Visa intelligence data
 * @throws Error if report not found or API call fails
 */
export async function fetchVisaReport(tripId: string): Promise<VisaIntelligence> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${apiUrl}/api/trips/${tripId}/report/visa`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // TODO: Add authentication token from Supabase session
      // 'Authorization': `Bearer ${token}`,
    },
    cache: 'no-store', // Don't cache visa reports (they should be up-to-date)
  });

  if (response.status === 404) {
    throw new Error('REPORT_NOT_FOUND');
  }

  if (response.status === 403) {
    throw new Error('UNAUTHORIZED');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to fetch visa report: ${response.statusText}`);
  }

  const data = (await response.json()) as VisaReportApi;

  // Transform API response to match frontend types
  return transformVisaReport(data, tripId);
}

/**
 * Transform backend API response to frontend VisaIntelligence type
 *
 * @param apiData - Data from GET /trips/{id}/report/visa
 * @param tripId - Trip ID
 * @returns Transformed visa intelligence data
 */
function transformVisaReport(apiData: VisaReportApi, tripId: string): VisaIntelligence {
  const costLocal = apiData.application_process?.cost_local
  const normalizedCostLocal =
    costLocal
    && typeof costLocal.amount === 'number'
    && typeof costLocal.currency === 'string'
      ? { amount: costLocal.amount, currency: costLocal.currency }
      : undefined

  return {
    tripId,
    generatedAt: apiData.generated_at || new Date().toISOString(),
    userNationality: apiData.visa_requirement?.user_nationality || 'Unknown',
    destinationCountry: apiData.visa_requirement?.destination_country || 'Unknown',
    destinationCity: apiData.visa_requirement?.destination_city,
    tripPurpose: apiData.visa_requirement?.trip_purpose || 'tourism',
    durationDays: apiData.visa_requirement?.duration_days || 0,

    // Visa requirement
    visaRequirement: {
      visaRequired: apiData.visa_requirement?.visa_required ?? true,
      visaType: apiData.visa_requirement?.visa_type || 'Unknown',
      visaCategory: apiData.visa_requirement?.visa_category,
      maxStayDays: apiData.visa_requirement?.max_stay_days,
      maxStayDuration: apiData.visa_requirement?.max_stay_duration,
      multipleEntry: apiData.visa_requirement?.multiple_entry,
      confidenceLevel: apiData.visa_requirement?.confidence_level || 'uncertain',
    },

    // Application process
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

    // Entry requirements
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

    // Tips and warnings
    tips: apiData.tips || [],
    warnings: apiData.warnings || [],

    // Confidence and sources
    confidenceScore: apiData.confidence_score || 0.0,
      sources: (apiData.sources || []).map((source) => ({
        name: source.name || 'Unknown Source',
        url: source.url || '',
        type: source.type || 'third-party',
        lastVerified: source.last_verified || new Date().toISOString(),
      })),
    lastVerified: apiData.last_verified || new Date().toISOString(),

    // Metadata
    isPartialData: apiData.is_partial_data || false,
    missingFields: apiData.missing_fields || [],
  };
}

/**
 * Trigger visa report generation for a trip
 *
 * @param tripId - UUID of the trip
 * @returns Task ID for tracking generation status
 */
export async function generateVisaReport(tripId: string): Promise<{ taskId: string; status: string }> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${apiUrl}/api/trips/${tripId}/generate`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // TODO: Add authentication token from Supabase session
      // 'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to generate visa report: ${response.statusText}`);
  }

  const data = await response.json();

  return {
    taskId: data.task_id,
    status: data.status,
  };
}

/**
 * Check generation status for a trip report
 *
 * @param tripId - UUID of the trip
 * @returns Generation status with progress
 */
export async function checkGenerationStatus(tripId: string): Promise<{
  status: string;
  progress: number;
  currentAgent: string | null;
  agentsCompleted: string[];
  agentsFailed: string[];
  error: string | null;
}> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${apiUrl}/api/trips/${tripId}/status`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // TODO: Add authentication token from Supabase session
      // 'Authorization': `Bearer ${token}`,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to check generation status: ${response.statusText}`);
  }

  const data = await response.json();

  return {
    status: data.status,
    progress: data.progress,
    currentAgent: data.current_agent,
    agentsCompleted: data.agents_completed || [],
    agentsFailed: data.agents_failed || [],
    error: data.error,
  };
}
