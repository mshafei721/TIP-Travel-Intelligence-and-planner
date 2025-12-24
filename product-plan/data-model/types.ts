// TIP - Travel Intelligence & Planner
// Core Data Model Types

// ============================================
// User & Authentication
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  authProvider: 'email' | 'google';
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TravelerProfile {
  id: string;
  userId: string;
  nationality: string;
  residencyCountry: string;
  residencyStatus: 'citizen' | 'permanent_resident' | 'work_visa' | 'student_visa' | 'tourist' | 'other';
  dateOfBirth?: string;
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget';
  dietaryRestrictions: string[];
  accessibilityNeeds?: string;
  createdAt: string;
  updatedAt: string;
}

// ============================================
// Trip & Destinations
// ============================================

export type TripStatus = 'draft' | 'pending' | 'processing' | 'completed' | 'failed';

export interface Trip {
  id: string;
  userId: string;
  title: string;
  status: TripStatus;

  // Traveler Details
  travelerDetails: {
    name: string;
    email: string;
    age?: number;
    nationality: string;
    residencyCountry: string;
    residencyStatus: string;
    originCity: string;
    partySize: number;
    companionAges?: number[];
  };

  // Destinations
  destinations: Destination[];

  // Trip Details
  tripDetails: {
    departureDate: string;
    returnDate: string;
    budget: number;
    budgetCurrency: string;
    purpose: 'tourism' | 'business' | 'visiting_family' | 'education' | 'other';
  };

  // Preferences
  preferences: {
    travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget';
    interests: string[];
    dietaryRestrictions: string[];
    accessibilityNeeds?: string;
  };

  createdAt: string;
  updatedAt: string;
  autoDeleteAt?: string;
}

export interface Destination {
  id: string;
  country: string;
  city: string;
  order: number;
}

// ============================================
// AI Agent Jobs
// ============================================

export type AgentType =
  | 'visa'
  | 'country'
  | 'weather'
  | 'currency'
  | 'culture'
  | 'food'
  | 'attractions'
  | 'itinerary'
  | 'flight';

export type AgentJobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'skipped';

export interface AgentJob {
  id: string;
  tripId: string;
  agentType: AgentType;
  status: AgentJobStatus;
  startedAt?: string;
  completedAt?: string;
  retryCount: number;
  confidenceScore?: number;
  errorMessage?: string;
  result?: Record<string, unknown>;
}

// ============================================
// Report Sections
// ============================================

export type ReportSectionType =
  | 'visa'
  | 'country'
  | 'weather'
  | 'currency'
  | 'culture'
  | 'food'
  | 'attractions'
  | 'itinerary'
  | 'flight'
  | 'summary';

export type ConfidenceLevel = 'high' | 'medium' | 'low';

export interface ReportSection {
  id: string;
  tripId: string;
  sectionType: ReportSectionType;
  title: string;
  content: Record<string, unknown>;
  confidenceLevel: ConfidenceLevel;
  sources: SourceReference[];
  generatedAt: string;
}

export interface SourceReference {
  id: string;
  url: string;
  title: string;
  sourceType: 'government' | 'embassy' | 'official' | 'third_party';
  lastVerified: string;
}

// ============================================
// Visa & Entry
// ============================================

export interface VisaRequirement {
  visaType: 'visa_free' | 'visa_on_arrival' | 'evisa' | 'visa_required';
  visaName?: string;
  maxStayDays?: number;
  processingTime?: string;
  cost?: {
    amount: number;
    currency: string;
  };
  requiredDocuments: string[];
  entryConditions: string[];
  transitRequirements?: {
    required: boolean;
    details?: string;
  };
  passportValidity: string;
  confidenceLevel: ConfidenceLevel;
  disclaimer: string;
  sources: SourceReference[];
}

// ============================================
// Itinerary
// ============================================

export type ItineraryItemType = 'attraction' | 'restaurant' | 'activity' | 'transport' | 'accommodation';

export interface ItineraryItem {
  id: string;
  type: ItineraryItemType;
  name: string;
  description?: string;
  location: {
    address?: string;
    latitude?: number;
    longitude?: number;
  };
  startTime?: string;
  duration?: number; // minutes
  cost?: {
    amount: number;
    currency: string;
  };
  category?: string;
  rating?: number;
  mapLink?: string;
  bookingUrl?: string;
}

export interface ItineraryDay {
  dayNumber: number;
  date: string;
  city: string;
  weather?: {
    condition: string;
    tempHigh: number;
    tempLow: number;
    precipitation: number;
  };
  items: ItineraryItem[];
}

export interface Itinerary {
  tripId: string;
  style: 'relaxed' | 'balanced' | 'packed' | 'budget';
  days: ItineraryDay[];
  totalEstimatedCost: {
    amount: number;
    currency: string;
  };
  generatedAt: string;
}

// ============================================
// Flights
// ============================================

export interface FlightOption {
  id: string;
  airline: string;
  flightNumber?: string;
  route: {
    departure: {
      airport: string;
      city: string;
      time: string;
    };
    arrival: {
      airport: string;
      city: string;
      time: string;
    };
  };
  duration: number; // minutes
  stops: number;
  price: {
    amount: number;
    currency: string;
  };
  bookingUrl: string;
  source: string;
}

// ============================================
// Travel Report
// ============================================

export interface TravelReport {
  id: string;
  tripId: string;
  title: string;
  summary: {
    destination: string;
    dates: string;
    visaStatus: string;
    weatherSummary: string;
    totalBudget: {
      amount: number;
      currency: string;
    };
  };
  sections: ReportSection[];
  generatedAt: string;
  expiresAt: string;
}

// ============================================
// Notifications
// ============================================

export type NotificationType =
  | 'report_completed'
  | 'deletion_reminder'
  | 'deletion_warning'
  | 'system_update';

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  tripId?: string;
  createdAt: string;
}

// ============================================
// Deletion Schedule
// ============================================

export type DeletionStatus = 'pending' | 'executing' | 'completed' | 'failed';

export interface DeletionSchedule {
  id: string;
  tripId: string;
  userId: string;
  scheduledAt: string;
  status: DeletionStatus;
  executedAt?: string;
}

// ============================================
// Templates
// ============================================

export interface TripTemplate {
  id: string;
  userId: string;
  name: string;
  description?: string;
  travelerDetails?: Partial<Trip['travelerDetails']>;
  destinations?: Destination[];
  preferences?: Partial<Trip['preferences']>;
  createdAt: string;
  updatedAt: string;
}

// ============================================
// Dashboard Statistics
// ============================================

export interface UserStatistics {
  totalTrips: number;
  countriesVisited: number;
  destinationsExplored: number;
  activeTrips: number;
}

export interface RecommendedDestination {
  id: string;
  country: string;
  cities: string[];
  imageUrl: string;
  reason: string;
  estimatedDays: string;
  estimatedBudget: {
    amount: number;
    currency: string;
  };
}
