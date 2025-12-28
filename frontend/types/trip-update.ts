/**
 * Trip Update Types
 * Types for trip editing, version history, and change tracking
 */

// ============================================
// Trip Data Types
// ============================================

export interface TripData {
  id: string;
  user_id: string;
  title: string;
  destination_city: string;
  destination_country: string;
  origin_city: string;
  departure_date: string;
  return_date: string;
  budget: number;
  currency: string;
  trip_purpose: string;
  party_size: number;
  travel_style: string;
  interests: string[];
  dietary_restrictions: string[];
  accessibility_needs: string | null;
  status: 'draft' | 'pending' | 'processing' | 'completed' | 'failed';
  generation_status: string | null;
  created_at: string;
  updated_at: string;
  cover_image_url: string | null;
}

export interface TripUpdateData {
  title?: string;
  destination_city?: string;
  destination_country?: string;
  origin_city?: string;
  departure_date?: string;
  return_date?: string;
  budget?: number;
  currency?: string;
  trip_purpose?: string;
  party_size?: number;
  travel_style?: string;
  interests?: string[];
  dietary_restrictions?: string[];
  accessibility_needs?: string | null;
  cover_image_url?: string | null;
}

// ============================================
// Change Tracking Types
// ============================================

export interface FieldChange {
  field: string;
  fieldLabel: string;
  oldValue: unknown;
  newValue: unknown;
  impactLevel: 'low' | 'medium' | 'high';
}

export interface ChangeImpact {
  affectedSections: string[];
  requiresRecalculation: boolean;
  estimatedRecalcTime: number; // in seconds
  impactSummary: string;
}

export interface ChangePreviewData {
  changes: FieldChange[];
  impact: ChangeImpact;
  canApply: boolean;
  warnings: string[];
}

// ============================================
// Version History Types
// ============================================

export interface TripVersion {
  id: string;
  trip_id: string;
  version_number: number;
  snapshot: TripData;
  change_summary: string;
  changed_fields: string[];
  created_by: 'user' | 'system' | 'ai';
  created_at: string;
  is_current: boolean;
}

export interface VersionDiff {
  version_a: number;
  version_b: number;
  differences: FieldChange[];
  sections_affected: string[];
}

// ============================================
// Recalculation Types
// ============================================

export type RecalculationStatus =
  | 'idle'
  | 'queued'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface RecalculationProgress {
  status: RecalculationStatus;
  currentAgent: string | null;
  completedAgents: string[];
  failedAgents: string[];
  progress: number; // 0-100
  startedAt: string | null;
  completedAt: string | null;
  estimatedTimeRemaining: number | null; // in seconds
  error: string | null;
}

export interface RecalculationRequest {
  trip_id: string;
  sections: string[];
  priority: 'normal' | 'high';
}

// ============================================
// Report Section Types
// ============================================

export const REPORT_SECTIONS = [
  { id: 'visa', label: 'Visa Intelligence', icon: 'passport' },
  { id: 'destination', label: 'Destination Guide', icon: 'map-pin' },
  { id: 'itinerary', label: 'Itinerary', icon: 'calendar' },
  { id: 'budget', label: 'Budget Breakdown', icon: 'wallet' },
  { id: 'safety', label: 'Safety & Health', icon: 'shield' },
  { id: 'culture', label: 'Cultural Tips', icon: 'globe' },
  { id: 'packing', label: 'Packing List', icon: 'briefcase' },
  { id: 'transportation', label: 'Transportation', icon: 'plane' },
] as const;

export type ReportSectionId = (typeof REPORT_SECTIONS)[number]['id'];

// ============================================
// API Response Types
// ============================================

export interface TripUpdateResponse {
  success: boolean;
  trip: TripData;
  version: TripVersion;
  recalculation: RecalculationProgress | null;
}

export interface VersionHistoryResponse {
  versions: TripVersion[];
  total_count: number;
  current_version: number;
}

export interface RestoreVersionResponse {
  success: boolean;
  trip: TripData;
  restored_version: number;
  new_version: number;
  message: string;
}

export interface VersionCompareResponse {
  trip_id: string;
  version_a: number;
  version_b: number;
  changes: BackendFieldChange[];
  summary: string;
}

/**
 * Backend-compatible field change type (snake_case)
 * Used for API responses that haven't been transformed
 */
export interface BackendFieldChange {
  field: string;
  old_value: unknown;
  new_value: unknown;
}

export interface RecalculationCancelResponse {
  task_id: string;
  cancelled: boolean;
  message: string;
  completed_agents: string[];
}

// ============================================
// UI State Types
// ============================================

export type EditFormState = 'viewing' | 'editing' | 'previewing' | 'saving';

export interface EditFormErrors {
  [field: string]: string | undefined;
}

// ============================================
// Field Impact Mapping
// ============================================

export const FIELD_IMPACT_MAP: Record<
  string,
  {
    label: string;
    impactLevel: 'low' | 'medium' | 'high';
    affectedSections: ReportSectionId[];
  }
> = {
  title: {
    label: 'Trip Title',
    impactLevel: 'low',
    affectedSections: [],
  },
  destination_city: {
    label: 'Destination City',
    impactLevel: 'high',
    affectedSections: ['visa', 'destination', 'itinerary', 'safety', 'culture', 'transportation'],
  },
  destination_country: {
    label: 'Destination Country',
    impactLevel: 'high',
    affectedSections: ['visa', 'destination', 'itinerary', 'safety', 'culture', 'transportation'],
  },
  origin_city: {
    label: 'Origin City',
    impactLevel: 'medium',
    affectedSections: ['visa', 'transportation'],
  },
  departure_date: {
    label: 'Departure Date',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget', 'packing'],
  },
  return_date: {
    label: 'Return Date',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget', 'packing'],
  },
  budget: {
    label: 'Budget',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget'],
  },
  currency: {
    label: 'Currency',
    impactLevel: 'low',
    affectedSections: ['budget'],
  },
  trip_purpose: {
    label: 'Trip Purpose',
    impactLevel: 'high',
    affectedSections: ['visa', 'itinerary', 'packing'],
  },
  party_size: {
    label: 'Party Size',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget', 'transportation'],
  },
  travel_style: {
    label: 'Travel Style',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget'],
  },
  interests: {
    label: 'Interests',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'destination'],
  },
  dietary_restrictions: {
    label: 'Dietary Restrictions',
    impactLevel: 'low',
    affectedSections: ['itinerary'],
  },
  accessibility_needs: {
    label: 'Accessibility Needs',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'transportation'],
  },
};
