'use client';

import { useEffect, useState, useCallback } from 'react';
import { Archive, ArchiveRestore, Loader2, History, Map } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  TravelStats,
  CountryBadges,
  TripHistoryCard,
  TripRatingDialog,
  WorldMapViz,
} from '@/components/history';
import {
  getTravelHistory,
  getTravelStats,
  getCountriesVisited,
  archiveTrip,
  unarchiveTrip,
  rateTrip,
} from '@/lib/api/history';
import type {
  TravelHistoryEntry,
  TravelStats as TravelStatsType,
  CountryVisit,
} from '@/types/profile';

type FilterMode = 'all' | 'active' | 'archived';

export default function TravelHistoryPage() {
  // Data state
  const [history, setHistory] = useState<TravelHistoryEntry[]>([]);
  const [stats, setStats] = useState<TravelStatsType | null>(null);
  const [countries, setCountries] = useState<CountryVisit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI state
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [showMap, setShowMap] = useState(true);

  // Rating dialog state
  const [ratingTrip, setRatingTrip] = useState<TravelHistoryEntry | null>(null);
  const [ratingDialogOpen, setRatingDialogOpen] = useState(false);

  // Fetch data
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [historyResult, statsResult, countriesResult] = await Promise.allSettled([
        getTravelHistory({ includeArchived: true }),
        getTravelStats(),
        getCountriesVisited(),
      ]);

      if (historyResult.status === 'fulfilled') {
        setHistory(historyResult.value.entries);
      }
      if (statsResult.status === 'fulfilled') {
        setStats(statsResult.value.stats);
        if (!countriesResult || countriesResult.status !== 'fulfilled') {
          setCountries(statsResult.value.countries);
        }
      }
      if (countriesResult.status === 'fulfilled') {
        setCountries(countriesResult.value);
      }
    } catch (err) {
      setError('Failed to load travel history. Please try again.');
      console.error('Error fetching travel history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter history based on filterMode
  const filteredHistory = history.filter((trip) => {
    if (filterMode === 'active') return !trip.isArchived;
    if (filterMode === 'archived') return trip.isArchived;
    return true;
  });

  // Count for badges
  const activeCount = history.filter((t) => !t.isArchived).length;
  const archivedCount = history.filter((t) => t.isArchived).length;

  // Handlers
  const handleArchive = async (tripId: string) => {
    try {
      await archiveTrip(tripId);
      setHistory((prev) =>
        prev.map((t) =>
          t.tripId === tripId
            ? { ...t, isArchived: true, archivedAt: new Date().toISOString() }
            : t,
        ),
      );
    } catch (err) {
      console.error('Error archiving trip:', err);
      alert('Failed to archive trip. Please try again.');
    }
  };

  const handleUnarchive = async (tripId: string) => {
    try {
      await unarchiveTrip(tripId);
      setHistory((prev) =>
        prev.map((t) => (t.tripId === tripId ? { ...t, isArchived: false, archivedAt: null } : t)),
      );
    } catch (err) {
      console.error('Error unarchiving trip:', err);
      alert('Failed to unarchive trip. Please try again.');
    }
  };

  const handleRateTrip = (trip: TravelHistoryEntry) => {
    setRatingTrip(trip);
    setRatingDialogOpen(true);
  };

  const handleRateSubmit = async (tripId: string, rating: number, notes?: string) => {
    await rateTrip(tripId, { rating, notes });
    setHistory((prev) =>
      prev.map((t) =>
        t.tripId === tripId ? { ...t, userRating: rating, userNotes: notes || null } : t,
      ),
    );
  };

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-2 text-sm text-slate-500">Loading travel history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Travel History</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Your travel memories and statistics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={showMap ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowMap(!showMap)}
          >
            <Map className="mr-1 h-4 w-4" />
            {showMap ? 'Hide Map' : 'Show Map'}
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-400">
          {error}
          <Button
            variant="link"
            className="ml-2 text-red-700 dark:text-red-400"
            onClick={fetchData}
          >
            Retry
          </Button>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <section>
          <h2 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
            Your Stats
          </h2>
          <TravelStats stats={stats} />
        </section>
      )}

      {/* World Map */}
      {showMap && countries.length >= 0 && (
        <section>
          <WorldMapViz countries={countries} />
        </section>
      )}

      {/* Countries Visited */}
      {countries.length > 0 && (
        <section>
          <h2 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">
            Countries You&apos;ve Visited
          </h2>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <CountryBadges countries={countries} maxDisplay={20} />
          </div>
        </section>
      )}

      {/* Trip History */}
      <section>
        <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Past Trips</h2>

          {/* Filter Tabs */}
          <div className="flex items-center gap-2">
            <Badge
              variant={filterMode === 'all' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setFilterMode('all')}
            >
              All ({history.length})
            </Badge>
            <Badge
              variant={filterMode === 'active' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setFilterMode('active')}
            >
              <History className="mr-1 h-3 w-3" />
              Active ({activeCount})
            </Badge>
            <Badge
              variant={filterMode === 'archived' ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setFilterMode('archived')}
            >
              <Archive className="mr-1 h-3 w-3" />
              Archived ({archivedCount})
            </Badge>
          </div>
        </div>

        {/* Trip Grid */}
        {filteredHistory.length > 0 ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredHistory.map((trip) => (
              <TripHistoryCard
                key={trip.tripId}
                trip={trip}
                onArchive={handleArchive}
                onUnarchive={handleUnarchive}
                onRate={handleRateTrip}
              />
            ))}
          </div>
        ) : (
          <div className="flex min-h-[200px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
            <div className="text-center">
              {filterMode === 'archived' ? (
                <>
                  <ArchiveRestore className="mx-auto mb-2 h-8 w-8 text-slate-400" />
                  <p className="text-slate-500 dark:text-slate-400">No archived trips</p>
                  <p className="text-sm text-slate-400 dark:text-slate-500">
                    Archive completed trips to keep your history organized
                  </p>
                </>
              ) : filterMode === 'active' ? (
                <>
                  <History className="mx-auto mb-2 h-8 w-8 text-slate-400" />
                  <p className="text-slate-500 dark:text-slate-400">No active trips in history</p>
                  <p className="text-sm text-slate-400 dark:text-slate-500">
                    Complete a trip to see it here
                  </p>
                </>
              ) : (
                <>
                  <History className="mx-auto mb-2 h-8 w-8 text-slate-400" />
                  <p className="text-slate-500 dark:text-slate-400">No travel history yet</p>
                  <p className="text-sm text-slate-400 dark:text-slate-500">
                    Complete your first trip to start building your travel history
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </section>

      {/* Rating Dialog */}
      <TripRatingDialog
        trip={ratingTrip}
        open={ratingDialogOpen}
        onOpenChange={setRatingDialogOpen}
        onSubmit={handleRateSubmit}
      />
    </div>
  );
}
