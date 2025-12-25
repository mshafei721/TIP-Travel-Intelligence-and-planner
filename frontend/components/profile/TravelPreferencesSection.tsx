'use client'

import { useState, useEffect } from 'react'
import { Heart, Utensils } from 'lucide-react'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { SectionCard } from './SectionCard'
import { useDebounce } from '@/hooks/useDebounce'
import type { TravelPreferences, TravelStyle, SaveState } from '@/types/profile'

const TRAVEL_STYLES: { value: TravelStyle; label: string; description: string }[] = [
  {
    value: 'budget',
    label: 'Budget',
    description: 'Cost-effective options, hostels, local transport',
  },
  {
    value: 'balanced',
    label: 'Balanced',
    description: 'Mix of comfort and value, mid-range hotels',
  },
  {
    value: 'luxury',
    label: 'Luxury',
    description: 'Premium experiences, 4-5 star hotels, private transport',
  },
]

const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-free',
  'Dairy-free',
  'Nut allergy',
  'Halal',
  'Kosher',
]

export interface TravelPreferencesSectionProps {
  preferences: TravelPreferences
  onUpdate: (data: TravelPreferences) => Promise<void>
}

/**
 * TravelPreferencesSection - Travel style and dietary preferences
 *
 * Captures:
 * - Travel style (relaxed/balanced/packed/budget-focused)
 * - Dietary restrictions (multiple select)
 * - Accessibility needs (free-form text)
 *
 * Auto-saves changes after user stops editing.
 */
export function TravelPreferencesSection({
  preferences,
  onUpdate,
}: TravelPreferencesSectionProps) {
  const [prefs, setPrefs] = useState<TravelPreferences>(preferences)
  const [saveState, setSaveState] = useState<SaveState>('idle')

  const debouncedPrefs = useDebounce(prefs, 1500)

  // Auto-save when preferences change
  useEffect(() => {
    if (JSON.stringify(debouncedPrefs) !== JSON.stringify(preferences)) {
      const savePrefs = async () => {
        setSaveState('saving')
        try {
          await onUpdate(debouncedPrefs)
          setSaveState('saved')
        } catch (error) {
          setSaveState('error')
        }
      }
      savePrefs()
    }
  }, [debouncedPrefs, preferences, onUpdate])

  const toggleDietaryRestriction = (restriction: string) => {
    setPrefs((prev) => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restriction)
        ? prev.dietaryRestrictions.filter((r) => r !== restriction)
        : [...prev.dietaryRestrictions, restriction],
    }))
  }

  return (
    <SectionCard
      title="Travel Preferences"
      description="Customize your travel style and dietary needs"
      icon={Heart}
      saveState={saveState}
    >
      <div className="space-y-6">
        {/* Travel Style */}
        <div className="space-y-3">
          <Label>Travel Style</Label>
          <div className="space-y-2">
            {TRAVEL_STYLES.map((style) => (
              <div
                key={style.value}
                className={`cursor-pointer rounded-lg border p-4 transition-all ${
                  prefs.travelStyle === style.value
                    ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950/20'
                    : 'border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700'
                }`}
                onClick={() => setPrefs({ ...prefs, travelStyle: style.value })}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border-2">
                    {prefs.travelStyle === style.value && (
                      <div className="h-3 w-3 rounded-full bg-blue-600 dark:bg-blue-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-slate-900 dark:text-slate-50">
                      {style.label}
                    </p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {style.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dietary Restrictions */}
        <div className="space-y-3">
          <Label className="flex items-center gap-2">
            <Utensils className="h-4 w-4" aria-hidden="true" />
            Dietary Restrictions
          </Label>
          <div className="grid gap-3 sm:grid-cols-2">
            {DIETARY_OPTIONS.map((option) => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox
                  id={`dietary-${option}`}
                  checked={prefs.dietaryRestrictions.includes(option)}
                  onCheckedChange={() => toggleDietaryRestriction(option)}
                  disabled={saveState === 'saving'}
                />
                <label
                  htmlFor={`dietary-${option}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {option}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Accessibility Needs */}
        <div className="space-y-2">
          <Label htmlFor="accessibility-needs">Accessibility Needs (Optional)</Label>
          <textarea
            id="accessibility-needs"
            value={prefs.accessibilityNeeds || ''}
            onChange={(e) => setPrefs({ ...prefs, accessibilityNeeds: e.target.value })}
            placeholder="E.g., Wheelchair accessible accommodations, hearing assistance..."
            rows={3}
            disabled={saveState === 'saving'}
            className="flex w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900"
          />
        </div>
      </div>
    </SectionCard>
  )
}
