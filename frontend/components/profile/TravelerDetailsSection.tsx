'use client';

import { useState, useEffect } from 'react';
import { MapPin, Calendar } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { SectionCard } from './SectionCard';
import { useDebounce } from '@/hooks/useDebounce';
import { COUNTRIES, POPULAR_COUNTRIES } from '@/lib/data/countries';
import type { TravelerDetails, SaveState } from '@/types/profile';

const RESIDENCY_STATUS_OPTIONS = [
  { value: 'citizen', label: 'Citizen' },
  { value: 'permanent_resident', label: 'Permanent Resident' },
  { value: 'temporary_resident', label: 'Temporary Resident' },
  { value: 'visitor', label: 'Visitor' },
] as const;

export interface TravelerDetailsSectionProps {
  travelerDetails: TravelerDetails;
  onUpdate: (data: TravelerDetails) => Promise<void>;
}

/**
 * TravelerDetailsSection - Default traveler details management
 *
 * Captures:
 * - Nationality
 * - Residence country
 * - Residency status
 * - Date of birth
 *
 * Auto-saves changes after user stops editing.
 */
export function TravelerDetailsSection({ travelerDetails, onUpdate }: TravelerDetailsSectionProps) {
  const [details, setDetails] = useState<TravelerDetails>(travelerDetails);
  const [saveState, setSaveState] = useState<SaveState>('idle');

  const debouncedDetails = useDebounce(details, 1500);

  // Auto-save when details change
  useEffect(() => {
    if (JSON.stringify(debouncedDetails) !== JSON.stringify(travelerDetails)) {
      const saveDetails = async () => {
        setSaveState('saving');
        try {
          await onUpdate(debouncedDetails);
          setSaveState('saved');
        } catch {
          setSaveState('error');
        }
      };
      saveDetails();
    }
  }, [debouncedDetails, travelerDetails, onUpdate]);

  return (
    <SectionCard
      title="Default Traveler Details"
      description="Pre-fill trip creation with your common details"
      icon={MapPin}
      saveState={saveState}
    >
      <div className="grid gap-4 md:grid-cols-2">
        {/* Nationality */}
        <div className="space-y-2">
          <Label htmlFor="nationality" className="text-sm font-medium">
            Nationality
          </Label>
          <select
            id="nationality"
            value={details.nationality}
            onChange={(e) => setDetails({ ...details, nationality: e.target.value })}
            className="flex h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
            disabled={saveState === 'saving'}
          >
            <option value="" className="text-slate-400">
              Select your nationality
            </option>
            {/* Popular countries first */}
            <optgroup label="Popular Countries">
              {COUNTRIES.filter((c) => POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
            {/* All countries */}
            <optgroup label="All Countries">
              {COUNTRIES.filter((c) => !POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
          </select>
        </div>

        {/* Residence Country */}
        <div className="space-y-2">
          <Label htmlFor="residence-country" className="text-sm font-medium">
            Residence Country
          </Label>
          <select
            id="residence-country"
            value={details.residenceCountry}
            onChange={(e) => setDetails({ ...details, residenceCountry: e.target.value })}
            className="flex h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
            disabled={saveState === 'saving'}
          >
            <option value="" className="text-slate-400">
              Select your residence country
            </option>
            {/* Popular countries first */}
            <optgroup label="Popular Countries">
              {COUNTRIES.filter((c) => POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
            {/* All countries */}
            <optgroup label="All Countries">
              {COUNTRIES.filter((c) => !POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
          </select>
        </div>

        {/* Residency Status */}
        <div className="space-y-2">
          <Label htmlFor="residency-status" className="text-sm font-medium">
            Residency Status
          </Label>
          <select
            id="residency-status"
            value={details.residencyStatus}
            onChange={(e) =>
              setDetails({
                ...details,
                residencyStatus: e.target.value as TravelerDetails['residencyStatus'],
              })
            }
            className="flex h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
            disabled={saveState === 'saving'}
          >
            <option value="" className="text-slate-400">
              Select your status
            </option>
            {RESIDENCY_STATUS_OPTIONS.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Date of Birth */}
        <div className="space-y-2">
          <Label htmlFor="date-of-birth" className="text-sm font-medium">
            Date of Birth
          </Label>
          <div className="relative">
            <Input
              id="date-of-birth"
              type="date"
              value={details.dateOfBirth}
              onChange={(e) => setDetails({ ...details, dateOfBirth: e.target.value })}
              disabled={saveState === 'saving'}
              className="h-11 rounded-lg border-slate-200 pr-11 shadow-sm transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
            />
            <Calendar
              className="absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
