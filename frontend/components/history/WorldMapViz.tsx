'use client';

import { useMemo } from 'react';
import type { CountryVisit } from '@/types/profile';

// Simplified world map SVG paths for major countries
// Using ISO 3166-1 alpha-2 codes
const COUNTRY_PATHS: Record<string, string> = {
  US: 'M 169 120 L 185 120 L 185 135 L 169 135 Z',
  CA: 'M 165 90 L 195 90 L 195 115 L 165 115 Z',
  MX: 'M 155 135 L 175 135 L 175 155 L 155 155 Z',
  BR: 'M 230 170 L 265 170 L 265 220 L 230 220 Z',
  AR: 'M 235 220 L 255 220 L 255 270 L 235 270 Z',
  GB: 'M 350 95 L 360 95 L 360 110 L 350 110 Z',
  FR: 'M 350 110 L 365 110 L 365 125 L 350 125 Z',
  DE: 'M 365 100 L 380 100 L 380 115 L 365 115 Z',
  IT: 'M 370 115 L 380 115 L 380 135 L 370 135 Z',
  ES: 'M 340 115 L 355 115 L 355 130 L 340 130 Z',
  PT: 'M 335 115 L 345 115 L 345 130 L 335 130 Z',
  NL: 'M 360 95 L 370 95 L 370 105 L 360 105 Z',
  BE: 'M 355 100 L 365 100 L 365 110 L 355 110 Z',
  CH: 'M 365 110 L 375 110 L 375 120 L 365 120 Z',
  AT: 'M 375 105 L 390 105 L 390 115 L 375 115 Z',
  PL: 'M 385 95 L 400 95 L 400 110 L 385 110 Z',
  CZ: 'M 380 100 L 390 100 L 390 110 L 380 110 Z',
  GR: 'M 395 120 L 408 120 L 408 135 L 395 135 Z',
  TR: 'M 410 110 L 440 110 L 440 125 L 410 125 Z',
  RU: 'M 420 60 L 520 60 L 520 100 L 420 100 Z',
  CN: 'M 480 100 L 530 100 L 530 145 L 480 145 Z',
  JP: 'M 540 105 L 555 105 L 555 130 L 540 130 Z',
  KR: 'M 530 110 L 540 110 L 540 125 L 530 125 Z',
  IN: 'M 445 130 L 480 130 L 480 175 L 445 175 Z',
  TH: 'M 490 145 L 505 145 L 505 170 L 490 170 Z',
  VN: 'M 505 140 L 515 140 L 515 170 L 505 170 Z',
  ID: 'M 495 180 L 540 180 L 540 200 L 495 200 Z',
  MY: 'M 495 165 L 515 165 L 515 180 L 495 180 Z',
  SG: 'M 502 175 L 508 175 L 508 180 L 502 180 Z',
  PH: 'M 525 150 L 540 150 L 540 170 L 525 170 Z',
  AU: 'M 505 210 L 560 210 L 560 260 L 505 260 Z',
  NZ: 'M 575 250 L 590 250 L 590 270 L 575 270 Z',
  ZA: 'M 390 220 L 415 220 L 415 250 L 390 250 Z',
  EG: 'M 400 130 L 420 130 L 420 150 L 400 150 Z',
  MA: 'M 345 130 L 360 130 L 360 145 L 345 145 Z',
  KE: 'M 420 175 L 435 175 L 435 195 L 420 195 Z',
  NG: 'M 375 165 L 395 165 L 395 185 L 375 185 Z',
  AE: 'M 445 135 L 460 135 L 460 145 L 445 145 Z',
  SA: 'M 425 135 L 450 135 L 450 160 L 425 160 Z',
  IL: 'M 415 125 L 422 125 L 422 138 L 415 138 Z',
  SE: 'M 375 60 L 385 60 L 385 85 L 375 85 Z',
  NO: 'M 365 55 L 380 55 L 380 80 L 365 80 Z',
  DK: 'M 370 85 L 380 85 L 380 95 L 370 95 Z',
  FI: 'M 395 55 L 410 55 L 410 80 L 395 80 Z',
  IE: 'M 340 95 L 350 95 L 350 105 L 340 105 Z',
};

export interface WorldMapVizProps {
  countries: CountryVisit[];
  className?: string;
}

/**
 * WorldMapViz - Interactive world map showing visited countries
 */
export function WorldMapViz({ countries, className = '' }: WorldMapVizProps) {
  // Create a lookup map for visited countries
  const visitedCountries = useMemo(() => {
    const map = new Map<string, CountryVisit>();
    countries.forEach((c) => {
      map.set(c.country_code, c);
    });
    return map;
  }, [countries]);

  // Get color based on visit count
  const getCountryColor = (countryCode: string): string => {
    const visit = visitedCountries.get(countryCode);
    if (!visit) return '#e2e8f0'; // Not visited - slate-200

    if (visit.visit_count >= 5) return '#1e40af'; // 5+ visits - blue-800
    if (visit.visit_count >= 3) return '#3b82f6'; // 3-4 visits - blue-500
    if (visit.visit_count >= 2) return '#60a5fa'; // 2 visits - blue-400
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
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
        <svg
          viewBox="100 40 500 250"
          className="h-auto w-full"
          role="img"
          aria-label="World map showing visited countries"
        >
          {/* Background */}
          <rect
            x="100"
            y="40"
            width="500"
            height="250"
            fill="#f8fafc"
            className="dark:fill-slate-900"
          />

          {/* Ocean */}
          <rect
            x="100"
            y="40"
            width="500"
            height="250"
            fill="#e0f2fe"
            className="dark:fill-slate-800"
          />

          {/* Country shapes */}
          {Object.entries(COUNTRY_PATHS).map(([code, path]) => {
            const visit = visitedCountries.get(code);
            return (
              <g key={code}>
                <path
                  d={path}
                  fill={getCountryColor(code)}
                  stroke="#94a3b8"
                  strokeWidth="0.5"
                  className="transition-colors hover:brightness-110"
                >
                  {visit && (
                    <title>
                      {visit.country_name}: {visit.visit_count} visit
                      {visit.visit_count !== 1 ? 's' : ''}
                    </title>
                  )}
                </path>
              </g>
            );
          })}
        </svg>
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
