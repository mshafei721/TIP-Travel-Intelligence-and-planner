'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, MapPin, DollarSign, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { createTripFromTemplate } from '@/lib/api/templates';
import type { PublicTemplate } from '@/types/profile';

export interface UseTemplateDialogProps {
  template: PublicTemplate | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * UseTemplateDialog - Dialog for creating a trip from a template
 */
export function UseTemplateDialog({ template, open, onOpenChange }: UseTemplateDialogProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [tripTitle, setTripTitle] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Reset form when dialog opens
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setTripTitle('');
      setStartDate('');
      setEndDate('');
      setError(null);
    }
    onOpenChange(newOpen);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!template) return;

    setLoading(true);
    setError(null);

    try {
      const result = await createTripFromTemplate(template.id, {
        title: tripTitle || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });

      // Navigate to the new trip
      if (result && typeof result === 'object' && 'id' in result) {
        router.push(`/trips/${result.id}`);
      } else {
        router.push('/trips');
      }

      handleOpenChange(false);
    } catch (err) {
      console.error('Error creating trip from template:', err);
      setError('Failed to create trip. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!template) return null;

  const formatBudget = (budget: number | null | undefined, currency: string) => {
    if (!budget) return null;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0,
    }).format(budget);
  };

  const destinations = template.destinations
    .map((d) => (d.city ? `${d.city}, ${d.country}` : d.country))
    .join(' → ');

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Use Template: {template.name}</DialogTitle>
          <DialogDescription>
            Create a new trip based on this template. You can customize the dates and title.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6 py-4">
            {/* Template Preview */}
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
              <div className="mb-2 flex items-start gap-2">
                <MapPin className="mt-0.5 h-4 w-4 text-blue-600" />
                <span className="text-sm text-slate-700 dark:text-slate-300">{destinations}</span>
              </div>

              <div className="flex gap-4 text-sm text-slate-500 dark:text-slate-400">
                {template.typical_duration && (
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{template.typical_duration} days</span>
                  </div>
                )}
                {template.estimated_budget && (
                  <div className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4" />
                    <span>~{formatBudget(template.estimated_budget, template.currency)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tripTitle">Trip Title (Optional)</Label>
                <Input
                  id="tripTitle"
                  placeholder={`Trip to ${template.destinations[0]?.city || template.destinations[0]?.country || 'destination'}`}
                  value={tripTitle}
                  onChange={(e) => setTripTitle(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startDate">Start Date</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endDate">End Date</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    min={startDate || new Date().toISOString().split('T')[0]}
                  />
                </div>
              </div>
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
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Trip'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
