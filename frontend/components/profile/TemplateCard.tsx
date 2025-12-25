'use client';

import { MapPin, Calendar, Pencil, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { TripTemplate } from '@/types/profile';

export interface TemplateCardProps {
  template: TripTemplate;
  onEdit: (template: TripTemplate) => void;
  onDelete: (id: string) => void;
}

/**
 * TemplateCard - Display individual trip template
 *
 * Shows:
 * - Template name
 * - Destinations
 * - Date pattern
 * - Travel style
 * - Edit/Delete actions
 */
export function TemplateCard({ template, onEdit, onDelete }: TemplateCardProps) {
  const destinations = template.destinations.length > 0
    ? template.destinations
        .map((destination) =>
          destination.city ? `${destination.city}, ${destination.country}` : destination.country,
        )
        .join(', ')
    : 'No destinations';
  const datePattern = template.description || 'Custom trip';
  const travelStyle = template.preferences?.travel_style || 'balanced';
  const travelStyleLabel = travelStyle
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  const handleDelete = () => {
    if (confirm(`Delete template "${template.name}"? This action cannot be undone.`)) {
      onDelete(template.id);
    }
  };

  return (
    <div className="group rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-all hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
      {/* Header */}
      <div className="mb-3 flex items-start justify-between">
        <h3 className="font-semibold text-slate-900 dark:text-slate-50">{template.name}</h3>
        <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <Button
            size="icon"
            variant="ghost"
            onClick={() => onEdit(template)}
            aria-label={`Edit ${template.name}`}
            className="h-8 w-8"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            onClick={handleDelete}
            aria-label={`Delete ${template.name}`}
            className="h-8 w-8 text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/20"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Destinations */}
      <div className="mb-2 flex items-start gap-2">
        <MapPin
          className="mt-0.5 h-4 w-4 shrink-0 text-blue-600 dark:text-blue-400"
          aria-hidden="true"
        />
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {destinations}
        </p>
      </div>

      {/* Date Pattern */}
      <div className="mb-2 flex items-center gap-2">
        <Calendar
          className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400"
          aria-hidden="true"
        />
        <p className="text-sm text-slate-600 dark:text-slate-400">{datePattern}</p>
      </div>

      {/* Travel Style */}
      <div className="mt-3 inline-block rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
        {travelStyleLabel}
      </div>
    </div>
  );
}
