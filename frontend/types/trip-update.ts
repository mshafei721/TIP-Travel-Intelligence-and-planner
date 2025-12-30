/**
 * Trip Update Types
 * Types for trip editing, version history, and change tracking
 * Using camelCase to match API contract (backend uses Pydantic aliases)
 */

// ============================================
// Trip Data Types
// ============================================

export interface TripData {
  id: string;
  userId: string;
  title: string;
  destinationCity: string;
  destinationCountry: string;
  originCity: string;
  departureDate: string;
  returnDate: string;
  budget: number;
  currency: string;
  tripPurpose: string;
  partySize: number;
  travelStyle: string;
  interests: string[];
  dietaryRestrictions: string[];
  accessibilityNeeds: string | null;
  status: 'draft' | 'pending' | 'processing' | 'completed' | 'failed';
  generationStatus: string | null;
  createdAt: string;
  updatedAt: string;
  coverImageUrl: string | null;
}

export interface TripUpdateData {
  title?: string;
  destinationCity?: string;
  destinationCountry?: string;
  originCity?: string;
  departureDate?: string;
  returnDate?: string;
  budget?: number;
  currency?: string;
  tripPurpose?: string;
  partySize?: number;
  travelStyle?: string;
  interests?: string[];
  dietaryRestrictions?: string[];
  accessibilityNeeds?: string | null;
  coverImageUrl?: string | null;
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
  tripId: string;
  versionNumber: number;
  snapshot: TripData;
  changeSummary: string;
  changedFields: string[];
  createdBy: 'user' | 'system' | 'ai';
  createdAt: string;
  isCurrent: boolean;
}

export interface VersionDiff {
  versionA: number;
  versionB: number;
  differences: FieldChange[];
  sectionsAffected: string[];
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
  tripId: string;
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
  totalCount: number;
  currentVersion: number;
}

export interface RestoreVersionResponse {
  success: boolean;
  trip: TripData;
  restoredVersion: number;
  newVersion: number;
  message: string;
}

export interface VersionCompareResponse {
  tripId: string;
  versionA: number;
  versionB: number;
  changes: BackendFieldChange[];
  summary: string;
}

/**
 * Backend-compatible field change type (camelCase from API)
 * Used for API responses
 */
export interface BackendFieldChange {
  field: string;
  oldValue: unknown;
  newValue: unknown;
}

export interface RecalculationCancelResponse {
  taskId: string;
  cancelled: boolean;
  message: string;
  completedAgents: string[];
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
  destinationCity: {
    label: 'Destination City',
    impactLevel: 'high',
    affectedSections: ['visa', 'destination', 'itinerary', 'safety', 'culture', 'transportation'],
  },
  destinationCountry: {
    label: 'Destination Country',
    impactLevel: 'high',
    affectedSections: ['visa', 'destination', 'itinerary', 'safety', 'culture', 'transportation'],
  },
  originCity: {
    label: 'Origin City',
    impactLevel: 'medium',
    affectedSections: ['visa', 'transportation'],
  },
  departureDate: {
    label: 'Departure Date',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget', 'packing'],
  },
  returnDate: {
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
  tripPurpose: {
    label: 'Trip Purpose',
    impactLevel: 'high',
    affectedSections: ['visa', 'itinerary', 'packing'],
  },
  partySize: {
    label: 'Party Size',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget', 'transportation'],
  },
  travelStyle: {
    label: 'Travel Style',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'budget'],
  },
  interests: {
    label: 'Interests',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'destination'],
  },
  dietaryRestrictions: {
    label: 'Dietary Restrictions',
    impactLevel: 'low',
    affectedSections: ['itinerary'],
  },
  accessibilityNeeds: {
    label: 'Accessibility Needs',
    impactLevel: 'medium',
    affectedSections: ['itinerary', 'transportation'],
  },
};
