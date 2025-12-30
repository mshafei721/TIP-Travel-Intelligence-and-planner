'use client';

import { MapPin, Calendar, Pencil, Trash2, Globe, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { TripTemplate } from '@/types/profile';

export interface TemplateGridProps {
  templates: TripTemplate[];
  onEdit: (template: TripTemplate) => void;
  onDelete: (id: string) => void;
  variant?: 'user' | 'public';
}

/**
 * TemplateGrid - Grid layout for displaying user templates
 */
export function TemplateGrid({ templates, onEdit, onDelete, variant = 'user' }: TemplateGridProps) {
  const formatBudget = (budget: number | null | undefined, currency: string) => {
    if (!budget) return null;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0,
    }).format(budget);
  };

  const handleDelete = (template: TripTemplate) => {
    if (confirm(`Delete template "${template.name}"? This action cannot be undone.`)) {
      onDelete(template.id);
    }
  };

  if (templates.length === 0) {
    return (
      <div className="flex min-h-[150px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
        <p className="text-slate-500 dark:text-slate-400">
          No templates yet. Create your first template!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {templates.map((template) => {
        const destinations = template.destinations
          .slice(0, 2)
          .map((d) => d.city || d.country)
          .join(', ');
        const additionalCount =
          template.destinations.length > 2 ? `+${template.destinations.length - 2}` : null;

        return (
          <div
            key={template.id}
            className="group relative rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
          >
            {/* Header */}
            <div className="mb-3 flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-slate-900 dark:text-slate-50">
                    {template.name}
                  </h3>
                  {template.isPublic ? (
                    <span title="Public template">
                      <Globe className="h-4 w-4 text-blue-500" />
                    </span>
                  ) : (
                    <span title="Private template">
                      <Lock className="h-4 w-4 text-slate-400" />
                    </span>
                  )}
                </div>
                {template.description && (
                  <p className="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">
                    {template.description}
                  </p>
                )}
              </div>

              {/* Actions */}
              {variant === 'user' && (
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
                    onClick={() => handleDelete(template)}
                    aria-label={`Delete ${template.name}`}
                    className="h-8 w-8 text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950/20"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Destinations */}
            <div className="mb-2 flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-blue-600 dark:text-blue-400" />
              <div className="flex flex-wrap items-center gap-1">
                <span className="text-sm text-slate-600 dark:text-slate-400">{destinations}</span>
                {additionalCount && (
                  <Badge variant="secondary" className="text-xs">
                    {additionalCount}
                  </Badge>
                )}
              </div>
            </div>

            {/* Duration & Budget */}
            <div className="mb-3 flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
              {template.typicalDuration && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>{template.typicalDuration} days</span>
                </div>
              )}
              {template.estimatedBudget && (
                <span>~{formatBudget(template.estimatedBudget, template.currency)}</span>
              )}
            </div>

            {/* Tags */}
            {template.tags && template.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {template.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {template.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{template.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}

            {/* Use count (for public templates) */}
            {template.isPublic && template.useCount > 0 && (
              <div className="mt-3 text-xs text-slate-400 dark:text-slate-500">
                Used {template.useCount} time{template.useCount !== 1 ? 's' : ''}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
