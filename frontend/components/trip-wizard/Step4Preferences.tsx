'use client'

import type { TripPreferences } from './TripCreationWizard'

interface Step4Props {
  data: TripPreferences
  onChange: (data: TripPreferences) => void
}

const TRAVEL_STYLES = [
  {
    value: 'Relaxed',
    icon: '🏖️',
    title: 'Relaxed',
    desc: 'Take it easy, no rush',
  },
  {
    value: 'Balanced',
    icon: '⚖️',
    title: 'Balanced',
    desc: 'Mix of activities and rest',
  },
  {
    value: 'Packed',
    icon: '🚀',
    title: 'Packed',
    desc: 'See and do everything',
  },
  {
    value: 'Budget-Focused',
    icon: '💰',
    title: 'Budget-Focused',
    desc: 'Maximize value, minimize cost',
  },
]

const INTERESTS = [
  { value: 'Food', icon: '🍜' },
  { value: 'Culture', icon: '🎭' },
  { value: 'Museums', icon: '🏛️' },
  { value: 'Adventure', icon: '🧗' },
  { value: 'Nightlife', icon: '🌃' },
  { value: 'Nature', icon: '🌲' },
  { value: 'Shopping', icon: '🛍️' },
  { value: 'History', icon: '📜' },
]

const DIETARY_RESTRICTIONS = [
  'None',
  'Vegetarian',
  'Vegan',
  'Halal',
  'Kosher',
  'Gluten-Free',
  'Lactose-Free',
  'Allergies',
]

export default function Step4Preferences({ data, onChange }: Step4Props) {
  const updateField = <K extends keyof TripPreferences>(
    field: K,
    value: TripPreferences[K]
  ) => {
    onChange({ ...data, [field]: value })
  }

  const toggleInterest = (interest: string) => {
    const isSelected = data.interests.includes(interest)
    const newInterests = isSelected
      ? data.interests.filter((i) => i !== interest)
      : [...data.interests, interest]
    updateField('interests', newInterests)
  }

  const toggleDietary = (restriction: string) => {
    const isSelected = data.dietaryRestrictions.includes(restriction)
    let newRestrictions: string[]

    if (restriction === 'None') {
      // If selecting "None", clear all others
      newRestrictions = isSelected ? [] : ['None']
    } else {
      // If selecting anything else, remove "None" if present
      newRestrictions = data.dietaryRestrictions.filter((r) => r !== 'None')
      if (isSelected) {
        newRestrictions = newRestrictions.filter((r) => r !== restriction)
      } else {
        newRestrictions = [...newRestrictions, restriction]
      }
    }

    updateField('dietaryRestrictions', newRestrictions)
  }

  return (
    <div className="space-y-8">
      {/* Page title */}
      <div className="border-l-4 border-blue-600 pl-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-1">
          Travel Preferences
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Customize your experience
        </p>
      </div>

      <div className="space-y-8">
        {/* Travel Style */}
        <div className="animate-slideInUp">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-4">
            Travel Style <span className="text-red-600">*</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {TRAVEL_STYLES.map((style) => (
              <button
                key={style.value}
                type="button"
                onClick={() => updateField('travelStyle', style.value as TripPreferences['travelStyle'])}
                className={`p-5 rounded-xl border-2 transition-all duration-300
                         hover:shadow-lg hover:scale-105
                         ${
                           data.travelStyle === style.value
                             ? 'border-amber-500 bg-amber-50 dark:bg-amber-950/30 shadow-lg shadow-amber-500/20'
                             : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800'
                         }`}
              >
                <div className="text-3xl mb-2">{style.icon}</div>
                <div className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
                  {style.title}
                </div>
                <div className="text-xs text-slate-600 dark:text-slate-400">
                  {style.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Interests */}
        <div className="animate-slideInUp" style={{ animationDelay: '50ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-4">
            Interests
            <span className="ml-2 text-xs font-normal text-slate-500 dark:text-slate-500">
              (Select all that apply)
            </span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {INTERESTS.map((interest) => (
              <button
                key={interest.value}
                type="button"
                onClick={() => toggleInterest(interest.value)}
                className={`p-4 rounded-xl border-2 transition-all duration-200
                         flex flex-col items-center gap-2
                         ${
                           data.interests.includes(interest.value)
                             ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/30 shadow-md'
                             : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'
                         }`}
              >
                <div className="text-3xl">{interest.icon}</div>
                <div className="font-medium text-sm text-slate-900 dark:text-slate-100">
                  {interest.value}
                </div>
                {data.interests.includes(interest.value) && (
                  <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" strokeWidth="3" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Dietary Restrictions */}
        <div className="animate-slideInUp" style={{ animationDelay: '100ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-4">
            Dietary Restrictions
          </label>
          <div className="flex flex-wrap gap-2">
            {DIETARY_RESTRICTIONS.map((restriction) => (
              <button
                key={restriction}
                type="button"
                onClick={() => toggleDietary(restriction)}
                className={`px-4 py-2 rounded-full border-2 font-medium transition-all duration-200
                         ${
                           data.dietaryRestrictions.includes(restriction)
                             ? 'border-green-600 bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400'
                             : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                         }`}
              >
                {restriction}
                {data.dietaryRestrictions.includes(restriction) && (
                  <span className="ml-1.5">✓</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Accessibility Needs */}
        <div className="animate-slideInUp" style={{ animationDelay: '150ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Accessibility Needs
            <span className="ml-2 text-xs font-normal text-slate-500 dark:text-slate-500">
              (Optional)
            </span>
          </label>
          <textarea
            value={data.accessibilityNeeds}
            onChange={(e) => updateField('accessibilityNeeds', e.target.value)}
            rows={4}
            className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     transition-all duration-200 resize-none"
            placeholder="Please describe any mobility needs, visual/hearing requirements, or other accessibility considerations..."
          />
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
            This helps us recommend appropriate accommodations and activities
          </p>
        </div>

        {/* Summary of selections */}
        {(data.travelStyle || data.interests.length > 0 || data.dietaryRestrictions.length > 0) && (
          <div className="bg-gradient-to-br from-slate-50 to-blue-50/30 dark:from-slate-800/50 dark:to-blue-950/20
                        border border-slate-200 dark:border-slate-700 rounded-xl p-6
                        animate-slideInUp" style={{ animationDelay: '200ms' }}>
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
              <span className="text-lg">✨</span>
              Your Travel Profile
            </h3>
            <div className="space-y-2 text-sm">
              {data.travelStyle && (
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 dark:text-slate-500 min-w-20">Style:</span>
                  <span className="text-slate-900 dark:text-slate-100 font-medium">{data.travelStyle}</span>
                </div>
              )}
              {data.interests.length > 0 && (
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 dark:text-slate-500 min-w-20">Interests:</span>
                  <span className="text-slate-900 dark:text-slate-100 font-medium">
                    {data.interests.join(', ')}
                  </span>
                </div>
              )}
              {data.dietaryRestrictions.length > 0 && (
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 dark:text-slate-500 min-w-20">Dietary:</span>
                  <span className="text-slate-900 dark:text-slate-100 font-medium">
                    {data.dietaryRestrictions.join(', ')}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideInUp {
          animation: slideInUp 0.6s ease-out both;
        }
      `}</style>
    </div>
  )
}
