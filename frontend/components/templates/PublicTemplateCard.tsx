'use client';

import Image from 'next/image';
import { MapPin, Calendar, DollarSign, Users, Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { PublicTemplate } from '@/types/profile';

export interface PublicTemplateCardProps {
  template: PublicTemplate;
  onUseTemplate: (template: PublicTemplate) => void;
  onClone?: (template: PublicTemplate) => void;
  showCloneButton?: boolean;
}

/**
 * PublicTemplateCard - Display public template in library
 *
 * Features:
 * - Cover image
 * - Template name and description
 * - Destinations with tags
 * - Duration and budget info
 * - Use count indicator
 * - Use Template and Clone actions
 */
export function PublicTemplateCard({
  template,
  onUseTemplate,
  onClone,
  showCloneButton = true,
}: PublicTemplateCardProps) {
  const destinationsList = template.destinations
    .slice(0, 3)
    .map((d) => d.city || d.country)
    .join(', ');

  const additionalDestinations =
    template.destinations.length > 3 ? `+${template.destinations.length - 3}` : null;

  const formatBudget = (budget: number | null | undefined, currency: string) => {
    if (!budget) return null;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0,
    }).format(budget);
  };

  const formatDuration = (days: number | null | undefined) => {
    if (!days) return null;
    if (days === 1) return '1 day';
    if (days < 7) return `${days} days`;
    if (days === 7) return '1 week';
    const weeks = Math.floor(days / 7);
    const remainingDays = days % 7;
    if (remainingDays === 0) return `${weeks} weeks`;
    return `${weeks}w ${remainingDays}d`;
  };

  return (
    <div className="group flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition-all hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
      {/* Cover Image */}
      <div className="relative aspect-video overflow-hidden bg-gradient-to-br from-blue-500 to-blue-700">
        {template.coverImage ? (
          <Image
            src={template.coverImage}
            alt={template.name}
            fill
            className="object-cover transition-transform group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <MapPin className="h-12 w-12 text-white/50" />
          </div>
        )}
        {/* Use count badge */}
        {template.useCount > 0 && (
          <div className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-black/50 px-2 py-1 text-xs text-white">
            <Users className="h-3 w-3" />
            <span>{template.useCount}</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col p-4">
        <h3 className="mb-1 font-semibold text-slate-900 dark:text-slate-50">{template.name}</h3>

        {template.description && (
          <p className="mb-3 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">
            {template.description}
          </p>
        )}

        {/* Destinations */}
        <div className="mb-3 flex items-start gap-2">
          <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-blue-600 dark:text-blue-400" />
          <div className="flex flex-wrap gap-1">
            <span className="text-sm text-slate-600 dark:text-slate-400">{destinationsList}</span>
            {additionalDestinations && (
              <Badge variant="secondary" className="text-xs">
                {additionalDestinations}
              </Badge>
            )}
          </div>
        </div>

        {/* Tags */}
        {template.tags && template.tags.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-1">
            {template.tags.slice(0, 4).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}

        {/* Meta info */}
        <div className="mt-auto flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
          {template.typicalDuration && (
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>{formatDuration(template.typicalDuration)}</span>
            </div>
          )}
          {template.estimatedBudget && (
            <div className="flex items-center gap-1">
              <DollarSign className="h-4 w-4" />
              <span>~{formatBudget(template.estimatedBudget, template.currency)}</span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-4 flex gap-2">
          {showCloneButton && onClone && (
            <Button
              variant="outline"
              size="sm"
              className="flex-1"
              onClick={() => onClone(template)}
            >
              <Copy className="mr-1 h-4 w-4" />
              Clone
            </Button>
          )}
          <Button size="sm" className="flex-1" onClick={() => onUseTemplate(template)}>
            Use Template
          </Button>
        </div>
      </div>
    </div>
  );
}
