'use client'

import { useState, useEffect } from 'react'
import { MapPin, Calendar } from 'lucide-react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { SectionCard } from './SectionCard'
import { useDebounce } from '@/hooks/useDebounce'
import type { TravelerDetails, SaveState } from '@/types/profile'

// Note: In production, use a comprehensive country list library
const COUNTRIES = [
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'CA', name: 'Canada' },
  { code: 'IN', name: 'India' },
  { code: 'AU', name: 'Australia' },
  { code: 'FR', name: 'France' },
  { code: 'DE', name: 'Germany' },
  { code: 'JP', name: 'Japan' },
  // Add more countries as needed
]

const RESIDENCY_STATUS_OPTIONS = [
  { value: 'citizen', label: 'Citizen' },
  { value: 'permanent_resident', label: 'Permanent Resident' },
  { value: 'temporary_resident', label: 'Temporary Resident' },
  { value: 'visitor', label: 'Visitor' },
] as const

export interface TravelerDetailsSectionProps {
  travelerDetails: TravelerDetails
  onUpdate: (data: TravelerDetails) => Promise<void>
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
export function TravelerDetailsSection({
  travelerDetails,
  onUpdate,
}: TravelerDetailsSectionProps) {
  const [details, setDetails] = useState<TravelerDetails>(travelerDetails)
  const [saveState, setSaveState] = useState<SaveState>('idle')

  const debouncedDetails = useDebounce(details, 1500)

  // Auto-save when details change
  useEffect(() => {
    if (JSON.stringify(debouncedDetails) !== JSON.stringify(travelerDetails)) {
      const saveDetails = async () => {
        setSaveState('saving')
        try {
          await onUpdate(debouncedDetails)
          setSaveState('saved')
        } catch {
          setSaveState('error')
        }
      }
      saveDetails()
    }
  }, [debouncedDetails, travelerDetails, onUpdate])

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
          <Label htmlFor="nationality">Nationality</Label>
          <select
            id="nationality"
            value={details.nationality}
            onChange={(e) => setDetails({ ...details, nationality: e.target.value })}
            className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900"
            disabled={saveState === 'saving'}
          >
            <option value="">Select nationality</option>
            {COUNTRIES.map((country) => (
              <option key={country.code} value={country.code}>
                {country.name}
              </option>
            ))}
          </select>
        </div>

        {/* Residence Country */}
        <div className="space-y-2">
          <Label htmlFor="residence-country">Residence Country</Label>
          <select
            id="residence-country"
            value={details.residenceCountry}
            onChange={(e) => setDetails({ ...details, residenceCountry: e.target.value })}
            className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900"
            disabled={saveState === 'saving'}
          >
            <option value="">Select residence country</option>
            {COUNTRIES.map((country) => (
              <option key={country.code} value={country.code}>
                {country.name}
              </option>
            ))}
          </select>
        </div>

        {/* Residency Status */}
        <div className="space-y-2">
          <Label htmlFor="residency-status">Residency Status</Label>
          <select
            id="residency-status"
            value={details.residencyStatus}
            onChange={(e) =>
              setDetails({
                ...details,
                residencyStatus: e.target.value as TravelerDetails['residencyStatus'],
              })
            }
            className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900"
            disabled={saveState === 'saving'}
          >
            <option value="">Select status</option>
            {RESIDENCY_STATUS_OPTIONS.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Date of Birth */}
        <div className="space-y-2">
          <Label htmlFor="date-of-birth">Date of Birth</Label>
          <div className="relative">
            <Input
              id="date-of-birth"
              type="date"
              value={details.dateOfBirth}
              onChange={(e) => setDetails({ ...details, dateOfBirth: e.target.value })}
              disabled={saveState === 'saving'}
              className="pr-10"
            />
            <Calendar className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          </div>
        </div>
      </div>
    </SectionCard>
  )
}
