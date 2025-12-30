'use client';

import { ChevronLeft, Wallet, Scale, Crown, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { DIETARY_RESTRICTIONS, type TravelStyle } from '@/types/profile';

export interface PreferencesData {
  travelStyle: TravelStyle;
  dietaryRestrictions: string[];
  accessibilityNeeds: string;
}

interface StepPreferencesProps {
  data: PreferencesData;
  onChange: (data: PreferencesData) => void;
  onNext: () => void;
  onBack: () => void;
}

const TRAVEL_STYLE_OPTIONS: {
  value: TravelStyle;
  label: string;
  description: string;
  icon: React.ReactNode;
}[] = [
  {
    value: 'budget',
    label: 'Budget',
    description: 'Hostels, local transport, street food',
    icon: <Wallet className="h-5 w-5" />,
  },
  {
    value: 'balanced',
    label: 'Balanced',
    description: 'Mix of comfort and value',
    icon: <Scale className="h-5 w-5" />,
  },
  {
    value: 'luxury',
    label: 'Luxury',
    description: '4-5 star hotels, premium experiences',
    icon: <Crown className="h-5 w-5" />,
  },
];

export function StepPreferences({ data, onChange, onNext, onBack }: StepPreferencesProps) {
  const isValid = data.travelStyle;

  const toggleDietaryRestriction = (restriction: string) => {
    const current = data.dietaryRestrictions;
    const updated = current.includes(restriction)
      ? current.filter((r) => r !== restriction)
      : [...current, restriction];
    onChange({ ...data, dietaryRestrictions: updated });
  };

  return (
    <div className="w-full max-w-lg">
      {/* Header */}
      <div className="mb-8 text-center">
        <h2 className="mb-2 text-2xl font-bold text-slate-900 dark:text-white">
          Your Travel Preferences
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Help us customize your travel recommendations.
        </p>
      </div>

      {/* Form */}
      <div className="space-y-6">
        {/* Travel Style */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">
            Travel Style <span className="text-red-500">*</span>
          </Label>
          <div className="grid gap-3">
            {TRAVEL_STYLE_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => onChange({ ...data, travelStyle: option.value })}
                className={`flex items-center gap-4 rounded-lg border p-4 text-left transition-all ${
                  data.travelStyle === option.value
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20 dark:border-blue-400 dark:bg-blue-900/20'
                    : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-600'
                }`}
              >
                <div
                  className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg ${
                    data.travelStyle === option.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
                  }`}
                >
                  {option.icon}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-slate-900 dark:text-white">{option.label}</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    {option.description}
                  </div>
                </div>
                {data.travelStyle === option.value && (
                  <Check className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Dietary Restrictions */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">
            Dietary Restrictions <span className="text-slate-400">(Optional)</span>
          </Label>
          <div className="flex flex-wrap gap-2">
            {DIETARY_RESTRICTIONS.map((restriction) => (
              <button
                key={restriction}
                type="button"
                onClick={() => toggleDietaryRestriction(restriction)}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition-all ${
                  data.dietaryRestrictions.includes(restriction)
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
                }`}
              >
                {restriction}
              </button>
            ))}
          </div>
        </div>

        {/* Accessibility Needs */}
        <div className="space-y-2">
          <Label htmlFor="accessibilityNeeds" className="text-sm font-medium">
            Accessibility Needs <span className="text-slate-400">(Optional)</span>
          </Label>
          <Textarea
            id="accessibilityNeeds"
            value={data.accessibilityNeeds}
            onChange={(e) => onChange({ ...data, accessibilityNeeds: e.target.value })}
            placeholder="E.g., wheelchair accessibility, mobility assistance..."
            rows={3}
            className="resize-none rounded-lg border-slate-200 dark:border-slate-700 dark:bg-slate-800"
          />
          <p className="text-xs text-slate-500 dark:text-slate-400">
            We&apos;ll include accessibility information in your trip plans
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
          Complete Setup
        </Button>
      </div>
    </div>
  );
}
