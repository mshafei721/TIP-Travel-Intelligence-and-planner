'use client';

import { useMemo, useState } from 'react';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps';
import type { CountryVisit } from '@/types/profile';

// Use natural earth world atlas
const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// ISO Alpha-2 to Alpha-3 mapping for common countries
const ALPHA2_TO_ALPHA3: Record<string, string> = {
  US: 'USA',
  CA: 'CAN',
  MX: 'MEX',
  BR: 'BRA',
  AR: 'ARG',
  GB: 'GBR',
  FR: 'FRA',
  DE: 'DEU',
  IT: 'ITA',
  ES: 'ESP',
  PT: 'PRT',
  NL: 'NLD',
  BE: 'BEL',
  CH: 'CHE',
  AT: 'AUT',
  PL: 'POL',
  CZ: 'CZE',
  GR: 'GRC',
  TR: 'TUR',
  RU: 'RUS',
  CN: 'CHN',
  JP: 'JPN',
  KR: 'KOR',
  IN: 'IND',
  TH: 'THA',
  VN: 'VNM',
  ID: 'IDN',
  MY: 'MYS',
  SG: 'SGP',
  PH: 'PHL',
  AU: 'AUS',
  NZ: 'NZL',
  ZA: 'ZAF',
  EG: 'EGY',
  MA: 'MAR',
  KE: 'KEN',
  NG: 'NGA',
  AE: 'ARE',
  SA: 'SAU',
  IL: 'ISR',
  SE: 'SWE',
  NO: 'NOR',
  DK: 'DNK',
  FI: 'FIN',
  IE: 'IRL',
};

export interface WorldMapVizProps {
  countries: CountryVisit[];
  className?: string;
}

/**
 * WorldMapViz - Interactive world map showing visited countries
 */
export function WorldMapViz({ countries, className = '' }: WorldMapVizProps) {
  const [tooltipContent, setTooltipContent] = useState<string>('');
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Create a lookup map for visited countries (by Alpha-3 code)
  const visitedCountries = useMemo(() => {
    const map = new Map<string, CountryVisit>();
    countries.forEach((c) => {
      // Convert Alpha-2 to Alpha-3 for matching with geography data
      const alpha3 = ALPHA2_TO_ALPHA3[c.countryCode] || c.countryCode;
      map.set(alpha3, c);
    });
    return map;
  }, [countries]);

  // Get color based on visit count
  const getCountryColor = (alpha3Code: string): string => {
    const visit = visitedCountries.get(alpha3Code);
    if (!visit) return '#e2e8f0'; // Not visited - slate-200

    if (visit.visitCount >= 5) return '#1e40af'; // 5+ visits - blue-800
    if (visit.visitCount >= 3) return '#3b82f6'; // 3-4 visits - blue-500
    if (visit.visitCount >= 2) return '#60a5fa'; // 2 visits - blue-400
    return '#93c5fd'; // 1 visit - blue-300
  };

  const visitedCount = countries.length;
  const percentage = Math.round((visitedCount / 195) * 100); // 195 recognized countries

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Stats Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Countries Visited
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {visitedCount} of 195 countries ({percentage}%)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <div className="h-3 w-3 rounded bg-slate-200" />
            <span>Not visited</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <div className="h-3 w-3 rounded bg-blue-300" />
            <span>1x</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <div className="h-3 w-3 rounded bg-blue-500" />
            <span>3+</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <div className="h-3 w-3 rounded bg-blue-800" />
            <span>5+</span>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-sky-50 dark:border-slate-700 dark:bg-slate-800">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 120,
            center: [10, 30],
          }}
          style={{ width: '100%', height: 'auto' }}
        >
          <ZoomableGroup>
            <Geographies geography={GEO_URL}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const alpha3 = (geo.properties.ISO_A3 as string | undefined) || geo.id || '';
                  const visit = alpha3 ? visitedCountries.get(alpha3) : undefined;
                  const countryName = geo.properties.NAME || geo.properties.name || 'Unknown';

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={getCountryColor(alpha3)}
                      stroke="#94a3b8"
                      strokeWidth={0.5}
                      style={{
                        default: { outline: 'none' },
                        hover: { outline: 'none', fill: visit ? '#2563eb' : '#cbd5e1' },
                        pressed: { outline: 'none' },
                      }}
                      onMouseEnter={(evt) => {
                        const tooltip = visit
                          ? `${countryName}: ${visit.visitCount} visit${visit.visitCount !== 1 ? 's' : ''}`
                          : countryName;
                        setTooltipContent(tooltip);
                        setTooltipPosition({ x: evt.clientX, y: evt.clientY });
                      }}
                      onMouseLeave={() => {
                        setTooltipContent('');
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

        {/* Tooltip */}
        {tooltipContent && (
          <div
            className="pointer-events-none fixed z-50 rounded bg-slate-900 px-2 py-1 text-xs text-white shadow-lg"
            style={{
              left: tooltipPosition.x + 10,
              top: tooltipPosition.y - 30,
            }}
          >
            {tooltipContent}
          </div>
        )}
      </div>

      {/* Empty state */}
      {countries.length === 0 && (
        <p className="text-center text-sm text-slate-500 dark:text-slate-400">
          Complete your first trip to see visited countries on the map!
        </p>
      )}
    </div>
  );
}
