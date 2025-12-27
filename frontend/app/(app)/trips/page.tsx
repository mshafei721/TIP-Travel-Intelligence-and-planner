'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { TripCard } from '@/components/dashboard/TripCard';
import { Loader2, Plus, Search, FileEdit, Trash2 } from 'lucide-react';
import Link from 'next/link';

interface TripDraft {
  formData: {
    destinations?: Array<{ country?: string; city?: string }>;
    tripDetails?: { departureDate?: string; returnDate?: string };
  };
  currentStep: number;
  savedAt: string;
}

interface Trip {
  id: string;
  destination_city: string;
  destination_country: string;
  departure_date: string;
  return_date: string;
  status: 'upcoming' | 'in-progress' | 'completed';
  created_at: string;
}

interface TripFromDB {
  id: string;
  destination_city: string;
  destination_country: string;
  departure_date: string;
  return_date: string;
  created_at: string;
  [key: string]: unknown;
}

const DRAFT_KEY = 'trip-wizard-draft';

export default function TripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [draft, setDraft] = useState<TripDraft | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<
    'all' | 'upcoming' | 'in-progress' | 'completed'
  >('all');

  useEffect(() => {
    loadTrips();
    loadDraft();
  }, []);

  const loadDraft = () => {
    try {
      const savedDraft = localStorage.getItem(DRAFT_KEY);
      if (savedDraft) {
        const parsed = JSON.parse(savedDraft) as TripDraft;
        setDraft(parsed);
      }
    } catch {
      console.error('Failed to load draft');
    }
  };

  const deleteDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setDraft(null);
  };

  const loadTrips = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const supabase = createClient();
      const { data, error } = await supabase
        .from('trips')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      // Transform data to match TripCard interface
      const transformedTrips: Trip[] = ((data || []) as TripFromDB[]).map((trip) => {
        const today = new Date();
        const departure = new Date(trip.departure_date);
        const returnDate = new Date(trip.return_date);

        let status: 'upcoming' | 'in-progress' | 'completed' = 'upcoming';
        if (today >= departure && today <= returnDate) {
          status = 'in-progress';
        } else if (today > returnDate) {
          status = 'completed';
        }

        return {
          ...trip,
          status,
        };
      });

      setTrips(transformedTrips);
    } catch (err) {
      console.error('Error loading trips:', err);
      setError('Failed to load trips');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTripClick = (tripId: string) => {
    router.push(`/trips/${tripId}`);
  };

  const filteredTrips = trips.filter((trip) => {
    const matchesSearch =
      searchQuery === '' ||
      trip.destination_city.toLowerCase().includes(searchQuery.toLowerCase()) ||
      trip.destination_country.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter = filterStatus === 'all' || trip.status === filterStatus;

    return matchesSearch && matchesFilter;
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">My Trips</h1>
            <p className="mt-2 text-slate-600 dark:text-slate-400">
              View and manage all your travel plans
            </p>
          </div>
        </div>

        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">My Trips</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            View and manage all your travel plans
          </p>
        </div>

        <div className="rounded-lg border-2 border-red-200 bg-red-50 p-8 text-center dark:border-red-800 dark:bg-red-950/30">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={loadTrips}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">My Trips</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            View and manage all your travel plans
          </p>
        </div>

        <Link
          href="/trips/create"
          className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-amber-600 transition-colors"
        >
          <Plus size={18} />
          Create Trip
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Search destinations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 pl-10 pr-4 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2">
          {(['all', 'upcoming', 'in-progress', 'completed'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'
              }`}
            >
              {status === 'all'
                ? 'All'
                : status === 'in-progress'
                  ? 'In Progress'
                  : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Draft Section */}
      {draft && (
        <div className="rounded-xl border-2 border-dashed border-amber-400 dark:border-amber-600 bg-amber-50/50 dark:bg-amber-950/20 p-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-amber-100 dark:bg-amber-900/50 p-2">
                <FileEdit className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                  Unsaved Trip Draft
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {draft.formData.destinations?.[0]?.city
                    ? `${draft.formData.destinations[0].city}, ${draft.formData.destinations[0].country || 'Unknown'}`
                    : 'Destination not set yet'}
                  {' • '}
                  Step {draft.currentStep} of 5{' • '}
                  Saved {new Date(draft.savedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={deleteDraft}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <Trash2 size={16} />
                Discard
              </button>
              <Link
                href="/trips/create"
                className="inline-flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 transition-colors"
              >
                Continue Editing
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Trip Count */}
      {filteredTrips.length > 0 && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Showing {filteredTrips.length} {filteredTrips.length === 1 ? 'trip' : 'trips'}
        </p>
      )}

      {/* Trips Grid */}
      {filteredTrips.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 p-12 text-center">
          <div className="mx-auto max-w-md space-y-4">
            <div className="text-4xl">✈️</div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {searchQuery || filterStatus !== 'all' ? 'No trips found' : 'No trips yet'}
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {searchQuery || filterStatus !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Start planning your first adventure!'}
            </p>
            {!searchQuery && filterStatus === 'all' && (
              <Link
                href="/trips/create"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
              >
                <Plus size={18} />
                Create Your First Trip
              </Link>
            )}
          </div>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredTrips.map((trip) => (
            <TripCard
              key={trip.id}
              trip={{
                id: trip.id,
                destination: `${trip.destination_city}, ${trip.destination_country}`,
                startDate: trip.departure_date,
                endDate: trip.return_date,
                status: trip.status,
              }}
              onClick={handleTripClick}
              showCountdown={trip.status === 'upcoming'}
              location="trips_list"
            />
          ))}
        </div>
      )}
    </div>
  );
}
