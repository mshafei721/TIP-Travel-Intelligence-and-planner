/**
 * Visa Intelligence Types
 * Based on backend VisaAgent output (Session 13)
 */

export type ConfidenceLevel = 'official' | 'third-party' | 'uncertain';
export type VisaCategory = 'visa-free' | 'visa-on-arrival' | 'evisa' | 'visa-required' | 'eta';
export type TripPurpose = 'tourism' | 'business' | 'transit';

export interface SourceReference {
  name: string;
  url: string;
  type: 'government' | 'embassy' | 'third-party';
  lastVerified: string; // ISO date string
}

export interface VisaRequirement {
  visaRequired: boolean;
  visaType: string; // e.g., "Tourist Visa", "eVisa", "Visa-Free", "B1/B2"
  visaCategory?: VisaCategory;
  maxStayDays?: number;
  maxStayDuration?: string; // e.g., "90 days", "6 months"
  multipleEntry?: boolean;
  confidenceLevel: ConfidenceLevel;
}

export interface ApplicationProcess {
  applicationMethod: string; // e.g., "online", "embassy", "not_required"
  applicationUrl?: string;
  processingTime?: string; // e.g., "10-15 business days"
  processingTimeDays?: number;
  costUsd?: number;
  costLocal?: {
    amount: number;
    currency: string;
  };
  requiredDocuments?: string[];
  steps?: string[];
}

export interface EntryRequirement {
  passportValidity: string; // e.g., "6 months beyond stay"
  passportValidityMonths?: number;
  blankPagesRequired?: number;
  vaccinations?: string[];
  returnTicket?: boolean;
  proofOfAccommodation?: boolean;
  proofOfFunds?: boolean;
  otherRequirements?: string[];
}

export interface TransitRequirements {
  required: boolean;
  details?: string;
  maxTransitHours?: number;
  sources?: SourceReference[];
  confidenceLevel?: ConfidenceLevel;
}

export interface ProcessingTimes {
  standard?: string;
  expedited?: string;
  rush?: string;
  notes?: string[];
}

export interface VisaIntelligence {
  tripId: string;
  generatedAt: string; // ISO datetime
  userNationality: string; // ISO Alpha-2
  destinationCountry: string; // ISO Alpha-2
  destinationCity?: string;
  tripPurpose: TripPurpose;
  durationDays: number;

  // Core visa information
  visaRequirement: VisaRequirement;
  applicationProcess: ApplicationProcess;
  entryRequirements: EntryRequirement;
  transitRequirements?: TransitRequirements;
  processingTimes?: ProcessingTimes;

  // Intelligence
  tips: string[];
  warnings: string[];

  // Confidence and provenance
  confidenceScore: number; // 0.0 - 1.0
  sources: SourceReference[];
  lastVerified: string; // ISO datetime

  // Metadata
  isPartialData?: boolean;
  missingFields?: string[];
}

export interface VisaReportProps {
  visaData: VisaIntelligence | null;
  isLoading?: boolean;
  error?: string | null;
  onContactEmbassy?: () => void;
  onRefresh?: () => void;
}
