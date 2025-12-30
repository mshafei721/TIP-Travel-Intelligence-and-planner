'use client';

import { Globe } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { CountryVisit } from '@/types/profile';

export interface CountryBadgesProps {
  countries: CountryVisit[];
  maxDisplay?: number;
}

/**
 * CountryBadges - Display visited countries as badges
 *
 * Shows country names with visit counts
 */
export function CountryBadges({ countries, maxDisplay = 12 }: CountryBadgesProps) {
  const displayCountries = countries.slice(0, maxDisplay);
  const remainingCount = countries.length - maxDisplay;

  if (countries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Globe className="mb-2 h-8 w-8 text-slate-300 dark:text-slate-600" />
        <p className="text-sm text-slate-500 dark:text-slate-400">No countries visited yet</p>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Complete a trip to see your visited countries here
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {displayCountries.map((country) => (
        <Badge
          key={country.countryCode}
          variant="secondary"
          className="cursor-default px-3 py-1.5 text-sm"
          title={`Visited ${country.visitCount} time${country.visitCount !== 1 ? 's' : ''}`}
        >
          <span className="mr-1.5 text-base">{getFlagEmoji(country.countryCode)}</span>
          {country.countryName}
          {country.visitCount > 1 && (
            <span className="ml-1.5 rounded-full bg-slate-200 px-1.5 py-0.5 text-xs dark:bg-slate-700">
              {country.visitCount}
            </span>
          )}
        </Badge>
      ))}
      {remainingCount > 0 && (
        <Badge variant="outline" className="px-3 py-1.5 text-sm">
          +{remainingCount} more
        </Badge>
      )}
    </div>
  );
}

/**
 * Convert ISO 3166-1 alpha-2 country code to flag emoji
 */
function getFlagEmoji(countryCode: string): string {
  if (!countryCode || countryCode.length !== 2) return '';

  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map((char) => 127397 + char.charCodeAt(0));

  return String.fromCodePoint(...codePoints);
}
