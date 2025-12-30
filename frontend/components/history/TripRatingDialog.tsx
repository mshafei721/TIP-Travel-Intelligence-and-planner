'use client';

import { useState, useEffect } from 'react';
import { Star, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { TravelHistoryEntry } from '@/types/profile';

export interface TripRatingDialogProps {
  trip: TravelHistoryEntry | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (tripId: string, rating: number, notes?: string) => Promise<void>;
}

/**
 * TripRatingDialog - Dialog for rating a completed trip
 */
export function TripRatingDialog({ trip, open, onOpenChange, onSubmit }: TripRatingDialogProps) {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when dialog opens with a trip
  useEffect(() => {
    if (trip && open) {
      setRating(trip.userRating || 0);
      setNotes(trip.userNotes || '');
      setError(null);
    }
  }, [trip, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!trip || rating === 0) {
      setError('Please select a rating');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onSubmit(trip.tripId, rating, notes || undefined);
      onOpenChange(false);
    } catch (err) {
      console.error('Error rating trip:', err);
      setError('Failed to save rating. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!trip) return null;

  const ratingLabels = ['', 'Poor', 'Fair', 'Good', 'Great', 'Amazing'];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Rate Your Trip</DialogTitle>
          <DialogDescription>How was your trip to {trip.destination}?</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6 py-4">
            {/* Star Rating */}
            <div className="space-y-2">
              <Label>Rating</Label>
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      className="rounded p-1 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
                      onMouseEnter={() => setHoveredRating(star)}
                      onMouseLeave={() => setHoveredRating(0)}
                      onClick={() => setRating(star)}
                    >
                      <Star
                        className={`h-8 w-8 transition-colors ${
                          star <= (hoveredRating || rating)
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-slate-300 dark:text-slate-600'
                        }`}
                      />
                    </button>
                  ))}
                </div>
                {(hoveredRating || rating) > 0 && (
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    {ratingLabels[hoveredRating || rating]}
                  </span>
                )}
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Trip Notes (Optional)</Label>
              <Textarea
                id="notes"
                placeholder="Share your thoughts about this trip..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                maxLength={1000}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {notes.length}/1000 characters
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-400">
                {error}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading || rating === 0}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Rating'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
