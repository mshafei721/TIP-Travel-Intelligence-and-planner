'use client';

import { Globe, MapPin, Users, Clock, Car, ExternalLink } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { CountryOverview } from '@/types/destination';

interface CountryOverviewCardProps {
  data: CountryOverview;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

export default function CountryOverviewCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: CountryOverviewCardProps) {
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatArea = (area: number): string => {
    return `${formatNumber(area)} km²`;
  };

  const populationDensity = Math.round(data.population / data.area);

  return (
    <IntelligenceCard
      id="country-overview"
      title="Country Overview"
      icon={<Globe className="w-6 h-6" />}
      iconColor="text-blue-600 dark:text-blue-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {data.region} • {data.subregion}
        </span>
      }
    >
      <div className="space-y-6">
        {/* Flag and basic info */}
        {data.flag && (
          <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <div className="text-6xl">{data.flag}</div>
            <div>
              <h4 className="text-2xl font-bold text-slate-900 dark:text-slate-50">{data.name}</h4>
              <p className="text-sm text-slate-500 dark:text-slate-400">{data.code}</p>
            </div>
          </div>
        )}

        {/* Key facts grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Capital */}
          <div className="flex items-start gap-3 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="mt-1">
              <MapPin className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Capital
              </p>
              <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {data.capital}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {data.coordinates.lat}°N, {data.coordinates.lng}°E
              </p>
            </div>
          </div>

          {/* Population */}
          <div className="flex items-start gap-3 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="mt-1">
              <Users className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Population
              </p>
              <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {formatNumber(data.population)}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Density: {formatNumber(populationDensity)}/km²
              </p>
            </div>
          </div>

          {/* Timezones */}
          <div className="flex items-start gap-3 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="mt-1">
              <Clock className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Time Zone{data.timezones.length > 1 ? 's' : ''}
              </p>
              <div className="mt-1 space-y-1">
                {data.timezones.map((tz, idx) => (
                  <p key={idx} className="text-sm font-medium text-slate-900 dark:text-slate-50">
                    {tz}
                  </p>
                ))}
              </div>
            </div>
          </div>

          {/* Driving */}
          <div className="flex items-start gap-3 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="mt-1">
              <Car className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Driving
              </p>
              <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-50">
                {data.drivingSide === 'left' ? 'Left side' : 'Right side'}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">of the road</p>
            </div>
          </div>
        </div>

        {/* Additional info */}
        <div className="space-y-3">
          {/* Languages */}
          <div className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900 rounded-lg">
            <p className="text-xs font-medium text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-2">
              Languages
            </p>
            <div className="flex flex-wrap gap-2">
              {data.languages.map((lang, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm font-medium rounded-full"
                >
                  {lang}
                </span>
              ))}
            </div>
          </div>

          {/* Area */}
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Total Area
            </span>
            <span className="text-sm font-semibold text-slate-900 dark:text-slate-50">
              {formatArea(data.area)}
            </span>
          </div>

          {/* Currency */}
          {data.currency && (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                Currency
              </span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                {data.currency.name} ({data.currency.code}) {data.currency.symbol}
              </span>
            </div>
          )}

          {/* Political System */}
          {data.politicalSystem && (
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                Political System
              </span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                {data.politicalSystem}
              </span>
            </div>
          )}

          {/* Bordering Countries */}
          {data.borderingCountries.length > 0 && (
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
              <p className="text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-2">
                Bordering Countries
              </p>
              <div className="flex flex-wrap gap-2">
                {data.borderingCountries.map((country, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm rounded-full"
                  >
                    {country}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Official links */}
        {(data.officialWebsite || data.tourismWebsite) && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Official Resources
            </p>
            <div className="flex flex-wrap gap-2">
              {data.officialWebsite && (
                <a
                  href={data.officialWebsite}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() =>
                    onLinkClick?.(data.officialWebsite!, 'Official Government Website')
                  }
                  className="
                    inline-flex items-center gap-2 px-4 py-2
                    bg-blue-50 dark:bg-blue-950/30
                    border border-blue-200 dark:border-blue-800
                    text-blue-700 dark:text-blue-300
                    text-sm font-medium rounded-lg
                    hover:bg-blue-100 dark:hover:bg-blue-900/50
                    transition-colors
                  "
                >
                  <span>Official Website</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
              {data.tourismWebsite && (
                <a
                  href={data.tourismWebsite}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onLinkClick?.(data.tourismWebsite!, 'Tourism Website')}
                  className="
                    inline-flex items-center gap-2 px-4 py-2
                    bg-amber-50 dark:bg-amber-950/30
                    border border-amber-200 dark:border-amber-800
                    text-amber-700 dark:text-amber-300
                    text-sm font-medium rounded-lg
                    hover:bg-amber-100 dark:hover:bg-amber-900/50
                    transition-colors
                  "
                >
                  <span>Tourism Board</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </IntelligenceCard>
  );
}
