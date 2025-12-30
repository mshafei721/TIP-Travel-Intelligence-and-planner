/**
 * Itinerary and Flight Report API Client
 * Fetches AI-generated itinerary and flight data from the backend
 */

import { createClient } from '@/lib/supabase/client';
import type {
  TripItinerary,
  DayItinerary,
  Activity,
  FlightOption,
  TimeOfDay,
} from '@/types/itinerary';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

interface ItineraryReportApiResponse {
  report_id: string;
  trip_id: string;
  generated_at: string;
  confidence_score: number;
  content: {
    daily_plans?: DayPlanApi[];
    total_estimated_cost?: string;
    cost_breakdown?: Record<string, string>;
    transportation_plan?: string;
    getting_around_tips?: string[];
    accommodation_suggestions?: AccommodationApi[];
    optimization_notes?: string[];
    packing_checklist?: string[];
    pro_tips?: string[];
    flexible_alternatives?: Record<string, string[]>;
  };
  sources: Array<{ name: string; url: string; type: string }>;
  warnings: string[];
}

interface FlightReportApiResponse {
  report_id: string;
  trip_id: string;
  generated_at: string;
  confidence_score: number;
  content: {
    recommended_flights?: FlightOptionApi[];
    price_range?: { min: number; max: number; average: number };
    best_time_to_book?: string;
    booking_tips?: string[];
    airport_info?: AirportInfoApi;
    layover_suggestions?: string[];
    alternative_routes?: string[];
    seasonal_notes?: string[];
    baggage_tips?: string[];
  };
  sources: Array<{ name: string; url: string; type: string }>;
  warnings: string[];
}

interface DayPlanApi {
  day_number: number;
  date: string;
  theme?: string;
  location?: string;
  activities: ActivityApi[];
  meals?: MealApi[];
  notes?: string;
  weather_note?: string;
}

interface ActivityApi {
  id?: string;
  name: string;
  time_slot: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location?: string;
  address?: string;
  coordinates?: { lat: number; lng: number };
  description?: string;
  category?: string;
  estimated_cost?: string;
  cost_currency?: string;
  booking_required?: boolean;
  booking_url?: string;
  tips?: string[];
  priority?: string;
}

interface MealApi {
  type: string;
  restaurant?: string;
  cuisine?: string;
  price_range?: string;
  notes?: string;
}

interface AccommodationApi {
  name: string;
  type?: string;
  area?: string;
  price_range?: string;
  booking_url?: string;
  notes?: string;
}

interface FlightOptionApi {
  id?: string;
  flight_type?: string;
  airline: string;
  flight_number?: string;
  departure_airport: string;
  departure_city: string;
  departure_datetime: string;
  arrival_airport: string;
  arrival_city: string;
  arrival_datetime: string;
  duration_minutes: number;
  stops: number;
  layovers?: LayoverApi[];
  price_usd?: number;
  fare_class?: string;
  booking_url?: string;
}

interface LayoverApi {
  airport_code: string;
  airport_name?: string;
  duration_minutes: number;
}

interface AirportInfoApi {
  departure_airport?: {
    code: string;
    name: string;
    city: string;
    tips?: string[];
  };
  arrival_airport?: {
    code: string;
    name: string;
    city: string;
    tips?: string[];
  };
}

/**
 * Fetch itinerary report for a trip
 */
export async function fetchItineraryReport(tripId: string): Promise<ApiResponse<TripItinerary>> {
  try {
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      return { success: false, error: 'Not authenticated' };
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/report/itinerary`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      },
    );

    if (response.status === 404) {
      return { success: false, error: 'REPORT_NOT_FOUND' };
    }

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: 'Failed to fetch itinerary' }));
      return { success: false, error: errorData.detail || `HTTP ${response.status}` };
    }

    const apiData: ItineraryReportApiResponse = await response.json();

    // Also fetch trip info for context
    const tripResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    let tripInfo = {
      title: 'Trip',
      destinations: [{ city: 'Destination', country: '' }],
      trip_details: { departure_date: '', return_date: '', currency: 'USD' },
    };
    if (tripResponse.ok) {
      tripInfo = await tripResponse.json();
    }

    const itinerary = transformItineraryReport(apiData, tripInfo);
    return { success: true, data: itinerary };
  } catch (error) {
    console.error('Error fetching itinerary report:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch itinerary',
    };
  }
}

/**
 * Fetch flight report for a trip
 */
export async function fetchFlightReport(tripId: string): Promise<ApiResponse<FlightOption[]>> {
  try {
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      return { success: false, error: 'Not authenticated' };
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/report/flight`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      },
    );

    if (response.status === 404) {
      return { success: false, error: 'REPORT_NOT_FOUND' };
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch flights' }));
      return { success: false, error: errorData.detail || `HTTP ${response.status}` };
    }

    const apiData: FlightReportApiResponse = await response.json();
    const flights = transformFlightReport(apiData);
    return { success: true, data: flights };
  } catch (error) {
    console.error('Error fetching flight report:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch flights',
    };
  }
}

/**
 * Fetch both itinerary and flight data combined
 */
export async function fetchFullItinerary(tripId: string): Promise<ApiResponse<TripItinerary>> {
  const [itineraryResult, flightResult] = await Promise.all([
    fetchItineraryReport(tripId),
    fetchFlightReport(tripId),
  ]);

  if (!itineraryResult.success || !itineraryResult.data) {
    return itineraryResult;
  }

  // Merge flight data into itinerary
  const itinerary = { ...itineraryResult.data };
  if (flightResult.success && flightResult.data) {
    itinerary.flights = flightResult.data;
  }

  return { success: true, data: itinerary };
}

// Transform API response to frontend TripItinerary type
function transformItineraryReport(
  apiData: ItineraryReportApiResponse,
  tripInfo: {
    title: string;
    destinations: Array<{ city: string; country: string }>;
    trip_details: { departure_date: string; return_date: string; currency: string };
  },
): TripItinerary {
  const content = apiData.content;
  const destination = tripInfo.destinations[0]
    ? `${tripInfo.destinations[0].city}, ${tripInfo.destinations[0].country}`
    : 'Destination';

  const days: DayItinerary[] = (content.daily_plans || []).map((day) => ({
    dayNumber: day.day_number,
    date: day.date,
    location: day.location || day.theme || destination,
    timeBlocks: groupActivitiesByTimeOfDay(day.activities || []),
    notes: day.notes || day.weather_note,
  }));

  return {
    tripId: apiData.trip_id,
    tripName: tripInfo.title,
    destination,
    startDate: tripInfo.trip_details?.departure_date || '',
    endDate: tripInfo.trip_details?.return_date || '',
    days,
    flights: [], // Will be populated by fetchFullItinerary
    totalBudget: content.total_estimated_cost
      ? parseFloat(content.total_estimated_cost.replace(/[^0-9.]/g, ''))
      : undefined,
    currency: tripInfo.trip_details?.currency || 'USD',
  };
}

// Group activities by time of day
function groupActivitiesByTimeOfDay(
  activities: ActivityApi[],
): Array<{ id: string; timeOfDay: TimeOfDay; activities: Activity[] }> {
  const blocks: Record<TimeOfDay, Activity[]> = {
    morning: [],
    afternoon: [],
    evening: [],
    night: [],
  };

  for (const activity of activities) {
    const transformed = transformActivity(activity);
    const timeOfDay = determineTimeOfDay(activity.time_slot || activity.start_time || '12:00');
    blocks[timeOfDay].push(transformed);
  }

  return Object.entries(blocks)
    .filter(([, activities]) => activities.length > 0)
    .map(([timeOfDay, activities]) => ({
      id: `block-${timeOfDay}`,
      timeOfDay: timeOfDay as TimeOfDay,
      activities,
    }));
}

// Transform API activity to frontend Activity type
function transformActivity(api: ActivityApi): Activity {
  const startTime = api.start_time || parseTimeFromSlot(api.time_slot || '09:00');
  const duration = api.duration_minutes || 60;
  const endTime = api.end_time || calculateEndTime(startTime, duration);

  return {
    id: api.id || crypto.randomUUID(),
    name: api.name,
    category: mapCategory(api.category),
    startTime,
    endTime,
    duration,
    location: {
      name: api.location || api.name,
      address: api.address,
      coordinates: api.coordinates,
    },
    description: api.description,
    cost: api.estimated_cost
      ? {
          amount: parseFloat(api.estimated_cost.replace(/[^0-9.]/g, '')) || 0,
          currency: api.cost_currency || 'USD',
          perPerson: true,
        }
      : undefined,
    bookingInfo: api.booking_required
      ? {
          required: true,
          website: api.booking_url,
        }
      : undefined,
    notes: api.tips?.join('. '),
    priority: api.priority as Activity['priority'],
  };
}

// Determine time of day from time string
function determineTimeOfDay(time: string): TimeOfDay {
  const hour = parseInt(time.split(':')[0], 10);
  if (hour >= 5 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 17) return 'afternoon';
  if (hour >= 17 && hour < 21) return 'evening';
  return 'night';
}

// Parse time from slot description (e.g., "Morning" -> "09:00")
function parseTimeFromSlot(slot: string): string {
  const lower = slot.toLowerCase();
  if (lower.includes('morning') || lower.includes('breakfast')) return '09:00';
  if (lower.includes('afternoon') || lower.includes('lunch')) return '13:00';
  if (lower.includes('evening') || lower.includes('dinner')) return '18:00';
  if (lower.includes('night')) return '21:00';
  // If it looks like a time, return as-is
  if (/^\d{1,2}:\d{2}/.test(slot)) return slot;
  return '12:00';
}

// Calculate end time from start time and duration
function calculateEndTime(startTime: string, durationMinutes: number): string {
  const [hours, minutes] = startTime.split(':').map(Number);
  const totalMinutes = hours * 60 + minutes + durationMinutes;
  const endHours = Math.floor(totalMinutes / 60) % 24;
  const endMinutes = totalMinutes % 60;
  return `${endHours.toString().padStart(2, '0')}:${endMinutes.toString().padStart(2, '0')}`;
}

// Map API category to frontend category
function mapCategory(apiCategory?: string): Activity['category'] {
  if (!apiCategory) return 'other';
  const lower = apiCategory.toLowerCase();
  if (
    lower.includes('museum') ||
    lower.includes('culture') ||
    lower.includes('temple') ||
    lower.includes('shrine')
  )
    return 'culture';
  if (
    lower.includes('food') ||
    lower.includes('restaurant') ||
    lower.includes('dining') ||
    lower.includes('eat')
  )
    return 'food';
  if (
    lower.includes('nature') ||
    lower.includes('park') ||
    lower.includes('garden') ||
    lower.includes('beach')
  )
    return 'nature';
  if (lower.includes('shop') || lower.includes('market')) return 'shopping';
  if (lower.includes('hotel') || lower.includes('accommodation') || lower.includes('check'))
    return 'accommodation';
  if (
    lower.includes('transport') ||
    lower.includes('train') ||
    lower.includes('bus') ||
    lower.includes('transfer')
  )
    return 'transport';
  if (lower.includes('entertainment') || lower.includes('show') || lower.includes('concert'))
    return 'entertainment';
  if (lower.includes('spa') || lower.includes('relax') || lower.includes('onsen'))
    return 'relaxation';
  if (lower.includes('adventure') || lower.includes('sport') || lower.includes('hike'))
    return 'adventure';
  return 'other';
}

// Transform flight API response
function transformFlightReport(apiData: FlightReportApiResponse): FlightOption[] {
  const content = apiData.content;

  return (content.recommended_flights || []).map((flight) => ({
    id: flight.id || crypto.randomUUID(),
    type: mapFlightType(flight.flight_type),
    departure: {
      airportCode: flight.departure_airport,
      airportName: flight.departure_airport, // Could be enhanced with airport lookup
      city: flight.departure_city,
      country: '', // Would need airport data
      datetime: flight.departure_datetime,
    },
    arrival: {
      airportCode: flight.arrival_airport,
      airportName: flight.arrival_airport,
      city: flight.arrival_city,
      country: '',
      datetime: flight.arrival_datetime,
    },
    duration: flight.duration_minutes,
    price: {
      amount: flight.price_usd || 0,
      currency: 'USD',
      fareClass: mapFareClass(flight.fare_class),
    },
    airline: flight.airline,
    flightNumber: flight.flight_number,
    stops: flight.stops,
    layovers: (flight.layovers || []).map((l) => ({
      airportCode: l.airport_code,
      airportName: l.airport_name || l.airport_code,
      duration: l.duration_minutes,
    })),
    bookingStatus: 'available' as const,
  }));
}

function mapFlightType(type?: string): FlightOption['type'] {
  if (!type) return 'outbound';
  const lower = type.toLowerCase();
  if (lower.includes('return') || lower.includes('inbound')) return 'return';
  if (lower.includes('internal') || lower.includes('domestic')) return 'internal';
  return 'outbound';
}

function mapFareClass(fareClass?: string): FlightOption['price']['fareClass'] {
  if (!fareClass) return 'economy';
  const lower = fareClass.toLowerCase();
  if (lower.includes('first')) return 'first';
  if (lower.includes('business')) return 'business';
  if (lower.includes('premium')) return 'premium-economy';
  return 'economy';
}
