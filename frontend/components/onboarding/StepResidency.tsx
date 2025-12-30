'use client';

import { Calendar, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { COUNTRIES, POPULAR_COUNTRIES } from '@/lib/data/countries';

const RESIDENCY_STATUS_OPTIONS = [
  { value: 'citizen', label: 'Citizen' },
  { value: 'permanent_resident', label: 'Permanent Resident' },
  { value: 'temporary_resident', label: 'Temporary Resident' },
  { value: 'visitor', label: 'Visitor' },
] as const;

export interface ResidencyData {
  nationality: string;
  residencyCountry: string;
  residencyStatus: string;
  dateOfBirth: string;
}

interface StepResidencyProps {
  data: ResidencyData;
  onChange: (data: ResidencyData) => void;
  onNext: () => void;
  onBack: () => void;
}

export function StepResidency({ data, onChange, onNext, onBack }: StepResidencyProps) {
  const isValid = data.nationality && data.residencyCountry && data.residencyStatus;

  const selectClassName = `flex h-11 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm shadow-sm transition-all
    focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20
    dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400/20`;

  return (
    <div className="w-full max-w-lg">
      {/* Header */}
      <div className="mb-8 text-center">
        <h2 className="mb-2 text-2xl font-bold text-slate-900 dark:text-white">
          Where are you from?
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          This helps us provide accurate visa requirements for your trips.
        </p>
      </div>

      {/* Form */}
      <div className="space-y-5">
        {/* Nationality */}
        <div className="space-y-2">
          <Label htmlFor="nationality" className="text-sm font-medium">
            Nationality <span className="text-red-500">*</span>
          </Label>
          <select
            id="nationality"
            value={data.nationality}
            onChange={(e) => onChange({ ...data, nationality: e.target.value })}
            className={selectClassName}
          >
            <option value="">Select your nationality</option>
            <optgroup label="Popular Countries">
              {COUNTRIES.filter((c) => POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
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
          <Label htmlFor="residencyCountry" className="text-sm font-medium">
            Country of Residence <span className="text-red-500">*</span>
          </Label>
          <select
            id="residencyCountry"
            value={data.residencyCountry}
            onChange={(e) => onChange({ ...data, residencyCountry: e.target.value })}
            className={selectClassName}
          >
            <option value="">Select your residence country</option>
            <optgroup label="Popular Countries">
              {COUNTRIES.filter((c) => POPULAR_COUNTRIES.includes(c.code)).map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </optgroup>
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
          <Label htmlFor="residencyStatus" className="text-sm font-medium">
            Residency Status <span className="text-red-500">*</span>
          </Label>
          <select
            id="residencyStatus"
            value={data.residencyStatus}
            onChange={(e) => onChange({ ...data, residencyStatus: e.target.value })}
            className={selectClassName}
          >
            <option value="">Select your status</option>
            {RESIDENCY_STATUS_OPTIONS.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Date of Birth */}
        <div className="space-y-2">
          <Label htmlFor="dateOfBirth" className="text-sm font-medium">
            Date of Birth <span className="text-slate-400">(Optional)</span>
          </Label>
          <div className="relative">
            <Input
              id="dateOfBirth"
              type="date"
              value={data.dateOfBirth}
              onChange={(e) => onChange({ ...data, dateOfBirth: e.target.value })}
              max={new Date().toISOString().split('T')[0]}
              className="h-11 rounded-lg border-slate-200 pr-11 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            />
            <Calendar
              className="absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 pointer-events-none"
              aria-hidden="true"
            />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Some visa requirements depend on age
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="mt-8 flex gap-3">
        <Button type="button" variant="outline" onClick={onBack} className="flex-1">
          <ChevronLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <Button
          onClick={onNext}
          disabled={!isValid}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          Continue
        </Button>
      </div>
    </div>
  );
}
