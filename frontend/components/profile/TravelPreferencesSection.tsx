'use client';

import { useState, useEffect } from 'react';
import { Heart, Utensils } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { SectionCard } from './SectionCard';
import { useDebounce } from '@/hooks/useDebounce';
import type { TravelPreferences, TravelStyle, SaveState } from '@/types/profile';

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
];

const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Gluten-free',
  'Dairy-free',
  'Nut allergy',
  'Halal',
  'Kosher',
];

export interface TravelPreferencesSectionProps {
  preferences: TravelPreferences;
  onUpdate: (data: TravelPreferences) => Promise<void>;
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
export function TravelPreferencesSection({ preferences, onUpdate }: TravelPreferencesSectionProps) {
  const [prefs, setPrefs] = useState<TravelPreferences>(preferences);
  const [saveState, setSaveState] = useState<SaveState>('idle');

  const debouncedPrefs = useDebounce(prefs, 1500);

  // Auto-save when preferences change
  useEffect(() => {
    if (JSON.stringify(debouncedPrefs) !== JSON.stringify(preferences)) {
      const savePrefs = async () => {
        setSaveState('saving');
        try {
          await onUpdate(debouncedPrefs);
          setSaveState('saved');
        } catch {
          setSaveState('error');
        }
      };
      savePrefs();
    }
  }, [debouncedPrefs, preferences, onUpdate]);

  const toggleDietaryRestriction = (restriction: string) => {
    setPrefs((prev) => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restriction)
        ? prev.dietaryRestrictions.filter((r) => r !== restriction)
        : [...prev.dietaryRestrictions, restriction],
    }));
  };

  return (
    <SectionCard
      title="Travel Preferences"
      description="Customize your travel style and dietary needs"
      icon={Heart}
      saveState={saveState}
    >
      <div className="space-y-8">
        {/* Travel Style */}
        <div className="space-y-4">
          <Label className="text-sm font-medium">Travel Style Preference</Label>
          <div className="grid gap-3 sm:grid-cols-1">
            {TRAVEL_STYLES.map((style) => (
              <div
                key={style.value}
                className={`group cursor-pointer rounded-xl border-2 p-5 transition-all duration-200 ${
                  prefs.travelStyle === style.value
                    ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-blue-50/50 shadow-md shadow-blue-100/50 dark:border-blue-400 dark:from-blue-950/40 dark:to-blue-950/20 dark:shadow-blue-900/20'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900/50 dark:hover:border-slate-700'
                }`}
                onClick={() => setPrefs({ ...prefs, travelStyle: style.value })}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all ${
                      prefs.travelStyle === style.value
                        ? 'border-blue-500 bg-white dark:border-blue-400 dark:bg-slate-900'
                        : 'border-slate-300 dark:border-slate-600'
                    }`}
                  >
                    {prefs.travelStyle === style.value && (
                      <div className="h-3 w-3 rounded-full bg-blue-600 dark:bg-blue-400 animate-in zoom-in duration-200" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p
                      className={`font-semibold transition-colors ${
                        prefs.travelStyle === style.value
                          ? 'text-blue-900 dark:text-blue-100'
                          : 'text-slate-900 dark:text-slate-50'
                      }`}
                    >
                      {style.label}
                    </p>
                    <p
                      className={`mt-1 text-sm leading-relaxed transition-colors ${
                        prefs.travelStyle === style.value
                          ? 'text-blue-700 dark:text-blue-300'
                          : 'text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      {style.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dietary Restrictions */}
        <div className="space-y-4">
          <Label className="flex items-center gap-2 text-sm font-medium">
            <Utensils className="h-4 w-4" aria-hidden="true" />
            Dietary Restrictions
          </Label>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {DIETARY_OPTIONS.map((option) => (
              <div
                key={option}
                className={`flex items-center space-x-3 rounded-lg border-2 p-3 transition-all duration-150 ${
                  prefs.dietaryRestrictions.includes(option)
                    ? 'border-amber-400 bg-amber-50/50 dark:border-amber-500 dark:bg-amber-950/20'
                    : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900/50 dark:hover:border-slate-700'
                }`}
              >
                <Checkbox
                  id={`dietary-${option}`}
                  checked={prefs.dietaryRestrictions.includes(option)}
                  onChange={() => toggleDietaryRestriction(option)}
                  disabled={saveState === 'saving'}
                  className="data-[state=checked]:bg-amber-500 data-[state=checked]:border-amber-500"
                />
                <label
                  htmlFor={`dietary-${option}`}
                  className={`cursor-pointer text-sm font-medium leading-none transition-colors ${
                    prefs.dietaryRestrictions.includes(option)
                      ? 'text-amber-900 dark:text-amber-100'
                      : 'text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {option}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Accessibility Needs */}
        <div className="space-y-3">
          <Label htmlFor="accessibility-needs" className="text-sm font-medium">
            Accessibility Needs <span className="text-slate-400">(Optional)</span>
          </Label>
          <textarea
            id="accessibility-needs"
            value={prefs.accessibilityNeeds || ''}
            onChange={(e) => setPrefs({ ...prefs, accessibilityNeeds: e.target.value })}
            placeholder="E.g., Wheelchair accessible accommodations, hearing assistance, visual aids..."
            rows={4}
            disabled={saveState === 'saving'}
            className="flex w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm leading-relaxed shadow-sm placeholder:text-slate-400 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:focus:border-blue-400 dark:focus:ring-blue-400/20"
          />
        </div>
      </div>
    </SectionCard>
  );
}
