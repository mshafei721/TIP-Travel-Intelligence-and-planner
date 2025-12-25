// Itinerary and Travel Planning Types
// For I7: Travel Planning and Itinerary section

export interface TripItinerary {
  tripId: string;
  tripName: string;
  destination: string;
  startDate: string; // ISO date
  endDate: string; // ISO date
  days: DayItinerary[];
  flights: FlightOption[];
  totalBudget?: number;
  currency: string;
}

export interface DayItinerary {
  dayNumber: number;
  date: string; // ISO date
  location: string; // City/area for this day
  timeBlocks: TimeBlock[];
  notes?: string;
}

export interface TimeBlock {
  id: string;
  timeOfDay: TimeOfDay;
  activities: Activity[];
}

export type TimeOfDay = 'morning' | 'afternoon' | 'evening' | 'night';

export interface Activity {
  id: string;
  name: string;
  category: ActivityCategory;
  startTime: string; // HH:mm format (24-hour)
  endTime: string; // HH:mm format (24-hour)
  duration: number; // in minutes
  location: ActivityLocation;
  description?: string;
  cost?: ActivityCost;
  bookingInfo?: BookingInfo;
  notes?: string;
  imageUrl?: string;
  priority?: 'must-see' | 'recommended' | 'optional';
  accessibility?: AccessibilityInfo;
}

export type ActivityCategory =
  | 'culture' // Museums, theaters, cultural sites
  | 'food' // Restaurants, cafes, food tours
  | 'nature' // Parks, beaches, hiking
  | 'shopping' // Markets, malls, boutiques
  | 'accommodation' // Hotels, check-in/out
  | 'transport' // Trains, buses, transfers
  | 'entertainment' // Shows, concerts, nightlife
  | 'relaxation' // Spa, leisure
  | 'adventure' // Sports, activities
  | 'other';

export interface ActivityLocation {
  name: string;
  address?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  neighborhood?: string;
  transportInfo?: string; // How to get there
}

export interface ActivityCost {
  amount: number;
  currency: string;
  perPerson: boolean;
  notes?: string; // e.g., "Entrance fee included"
}

export interface BookingInfo {
  required: boolean;
  website?: string;
  phone?: string;
  confirmationNumber?: string;
  bookingStatus?: 'pending' | 'confirmed' | 'cancelled';
}

export interface AccessibilityInfo {
  wheelchairAccessible: boolean;
  notes?: string;
}

export interface FlightOption {
  id: string;
  type: 'outbound' | 'return' | 'internal';
  departure: FlightLeg;
  arrival: FlightLeg;
  duration: number; // in minutes
  price: {
    amount: number;
    currency: string;
    fareClass: 'economy' | 'premium-economy' | 'business' | 'first';
  };
  airline: string;
  flightNumber?: string;
  stops: number; // 0 for direct
  layovers?: FlightLayover[];
  bookingStatus?: 'searching' | 'available' | 'selected' | 'booked';
}

export interface FlightLeg {
  airportCode: string; // IATA code (e.g., LAX, NRT)
  airportName: string;
  city: string;
  country: string;
  datetime: string; // ISO datetime
  terminal?: string;
  gate?: string;
}

export interface FlightLayover {
  airportCode: string;
  airportName: string;
  duration: number; // in minutes
}

// Map-related types
export interface MapMarker {
  id: string;
  activityId: string;
  position: {
    lat: number;
    lng: number;
  };
  category: ActivityCategory;
  name: string;
  dayNumber: number;
}

export interface MapRoute {
  id: string;
  dayNumber: number;
  coordinates: Array<{ lat: number; lng: number }>;
  color: string;
}

// Time conflict detection
export interface TimeConflict {
  activity1: Activity;
  activity2: Activity;
  overlapMinutes: number;
}

// Itinerary statistics
export interface ItineraryStats {
  totalDays: number;
  totalActivities: number;
  totalCost: number;
  currency: string;
  activitiesByCategory: Record<ActivityCategory, number>;
  busyDays: number[]; // Day numbers with most activities
}

// Activity suggestions (for editing mode)
export interface ActivitySuggestion {
  name: string;
  category: ActivityCategory;
  estimatedDuration: number; // in minutes
  estimatedCost?: number;
  popularTimes?: string[];
  rating?: number;
  reviewCount?: number;
}
