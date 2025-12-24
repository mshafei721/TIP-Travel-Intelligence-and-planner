'use client'

import { useState, useEffect } from 'react'
import type { TravelerDetails } from './TripCreationWizard'

interface Step1Props {
  data: TravelerDetails
  onChange: (data: TravelerDetails) => void
}

// Country list (top 50 most common)
const COUNTRIES = [
  'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 'France',
  'Italy', 'Spain', 'Japan', 'China', 'India', 'Brazil', 'Mexico', 'South Korea',
  'Netherlands', 'Sweden', 'Switzerland', 'Norway', 'Denmark', 'Finland',
  'Belgium', 'Austria', 'Poland', 'Greece', 'Portugal', 'Ireland', 'New Zealand',
  'Singapore', 'UAE', 'Saudi Arabia', 'Turkey', 'Egypt', 'South Africa', 'Nigeria',
  'Argentina', 'Chile', 'Colombia', 'Peru', 'Thailand', 'Vietnam', 'Philippines',
  'Indonesia', 'Malaysia', 'Pakistan', 'Bangladesh', 'Israel', 'Russia', 'Ukraine',
  'Czech Republic', 'Hungary'
].sort()

const RESIDENCY_STATUS = [
  'Citizen',
  'Permanent Resident',
  'Temporary Resident',
  'Student Visa',
  'Work Visa'
]

const CONTACT_PREFERENCES = ['Email', 'SMS', 'WhatsApp']

export default function Step1TravelerDetails({ data, onChange }: Step1Props) {
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Validate email
  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // Update field with validation
  const updateField = <K extends keyof TravelerDetails>(
    field: K,
    value: TravelerDetails[K]
  ) => {
    onChange({ ...data, [field]: value })

    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  // Validate party size and ages
  useEffect(() => {
    if (data.partySize > 1 && data.partyAges.length !== data.partySize - 1) {
      onChange({
        ...data,
        partyAges: Array(data.partySize - 1).fill(0),
      })
    } else if (data.partySize === 1) {
      onChange({ ...data, partyAges: [] })
    }
  }, [data.partySize])

  // Update party age
  const updatePartyAge = (index: number, age: number) => {
    const newAges = [...data.partyAges]
    newAges[index] = age
    onChange({ ...data, partyAges: newAges })
  }

  // Toggle contact preference
  const toggleContactPref = (pref: string) => {
    const isSelected = data.contactPreferences.includes(pref)
    const newPrefs = isSelected
      ? data.contactPreferences.filter((p) => p !== pref)
      : [...data.contactPreferences, pref]
    onChange({ ...data, contactPreferences: newPrefs })
  }

  return (
    <div className="space-y-8">
      {/* Page title */}
      <div className="border-l-4 border-blue-600 pl-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-1">
          Traveler Details
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Tell us about who's traveling
        </p>
      </div>

      {/* Form fields with staggered animation */}
      <div className="space-y-6">
        {/* Name */}
        <div className="animate-slideInUp" style={{ animationDelay: '0ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Full Name <span className="text-red-600">*</span>
          </label>
          <input
            type="text"
            value={data.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     transition-all duration-200"
            placeholder="John Smith"
          />
        </div>

        {/* Email & Age */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-slideInUp" style={{ animationDelay: '50ms' }}>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Email <span className="text-red-600">*</span>
            </label>
            <input
              type="email"
              value={data.email}
              onChange={(e) => updateField('email', e.target.value)}
              onBlur={() => {
                if (data.email && !validateEmail(data.email)) {
                  setErrors((prev) => ({ ...prev, email: 'Invalid email format' }))
                }
              }}
              className={`w-full px-4 py-3 rounded-lg border
                       ${errors.email ? 'border-red-500' : 'border-slate-300 dark:border-slate-700'}
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200`}
              placeholder="john@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Age (Optional)
            </label>
            <input
              type="number"
              min="0"
              max="120"
              value={data.age || ''}
              onChange={(e) => updateField('age', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
              placeholder="30"
            />
          </div>
        </div>

        {/* Nationality & Residence */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-slideInUp" style={{ animationDelay: '100ms' }}>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Nationality <span className="text-red-600">*</span>
            </label>
            <select
              value={data.nationality}
              onChange={(e) => updateField('nationality', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            >
              <option value="">Select country...</option>
              {COUNTRIES.map((country) => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Country of Residence <span className="text-red-600">*</span>
            </label>
            <select
              value={data.residenceCountry}
              onChange={(e) => updateField('residenceCountry', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            >
              <option value="">Select country...</option>
              {COUNTRIES.map((country) => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Origin City & Residency Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-slideInUp" style={{ animationDelay: '150ms' }}>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Origin City <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              value={data.originCity}
              onChange={(e) => updateField('originCity', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
              placeholder="New York"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Residency Status <span className="text-red-600">*</span>
            </label>
            <select
              value={data.residencyStatus}
              onChange={(e) => updateField('residencyStatus', e.target.value as TravelerDetails['residencyStatus'])}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            >
              <option value="">Select status...</option>
              {RESIDENCY_STATUS.map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Party Size */}
        <div className="animate-slideInUp" style={{ animationDelay: '200ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Party Size <span className="text-red-600">*</span>
          </label>
          <input
            type="number"
            min="1"
            max="20"
            value={data.partySize}
            onChange={(e) => updateField('partySize', parseInt(e.target.value) || 1)}
            className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700
                     bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     transition-all duration-200"
          />
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
            Including yourself
          </p>
        </div>

        {/* Party Ages (if party size > 1) */}
        {data.partySize > 1 && (
          <div className="animate-slideInUp bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
              Ages of Other Travelers
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {data.partyAges.map((age, index) => (
                <div key={index}>
                  <input
                    type="number"
                    min="0"
                    max="120"
                    value={age || ''}
                    onChange={(e) => updatePartyAge(index, parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700
                             bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             transition-all duration-200"
                    placeholder={`Person ${index + 2}`}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contact Preferences */}
        <div className="animate-slideInUp" style={{ animationDelay: '250ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
            Preferred Contact Methods
          </label>
          <div className="flex flex-wrap gap-3">
            {CONTACT_PREFERENCES.map((pref) => (
              <button
                key={pref}
                type="button"
                onClick={() => toggleContactPref(pref)}
                className={`px-4 py-2 rounded-lg border-2 font-medium transition-all duration-200
                         ${
                           data.contactPreferences.includes(pref)
                             ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400'
                             : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                         }`}
              >
                {pref}
              </button>
            ))}
          </div>
        </div>
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
