'use client';

import { useState, useMemo, useCallback } from 'react';
import type { Destination } from './TripCreationWizard';
import { SearchableSelect, type SelectOption } from '@/components/ui/SearchableSelect';
import { getAllCountries, getCitiesForCountry, getCountryCodeByName } from '@/lib/geography';

interface Step2Props {
  data: Destination[];
  onChange: (data: Destination[]) => void;
}

// Popular destinations for quick selection
const POPULAR_DESTINATIONS = [
  { country: 'France', city: 'Paris', countryCode: 'FR' },
  { country: 'Italy', city: 'Rome', countryCode: 'IT' },
  { country: 'Japan', city: 'Tokyo', countryCode: 'JP' },
  { country: 'United Kingdom', city: 'London', countryCode: 'GB' },
  { country: 'United States', city: 'New York', countryCode: 'US' },
  { country: 'Thailand', city: 'Bangkok', countryCode: 'TH' },
];

export default function Step2Destination({ data, onChange }: Step2Props) {
  const [isMultiCity, setIsMultiCity] = useState(data.length > 1);
  // Track country codes for city dropdown filtering
  const [countryCodes, setCountryCodes] = useState<(string | undefined)[]>(
    data.map((d) => (d.country ? getCountryCodeByName(d.country) : undefined)),
  );

  // Memoize country options
  const countryOptions = useMemo(() => getAllCountries(), []);

  // Get city options for a specific destination index
  const getCityOptions = useCallback(
    (index: number): SelectOption[] => {
      const code = countryCodes[index];
      if (!code) return [];
      return getCitiesForCountry(code);
    },
    [countryCodes],
  );

  const updateDestination = (index: number, field: keyof Destination, value: string) => {
    const newDestinations = [...data];
    newDestinations[index] = { ...newDestinations[index], [field]: value };
    onChange(newDestinations);
  };

  const handleCountryChange = (index: number, option: SelectOption | null) => {
    const newDestinations = [...data];
    const newCodes = [...countryCodes];

    if (option) {
      newDestinations[index] = {
        ...newDestinations[index],
        country: option.label,
        city: '', // Clear city when country changes
      };
      newCodes[index] = option.value;
    } else {
      newDestinations[index] = {
        ...newDestinations[index],
        country: '',
        city: '',
      };
      newCodes[index] = undefined;
    }

    setCountryCodes(newCodes);
    onChange(newDestinations);
  };

  const handleCityChange = (index: number, option: SelectOption | null) => {
    updateDestination(index, 'city', option?.value || '');
  };

  const addDestination = () => {
    onChange([...data, { country: '', city: '' }]);
    setCountryCodes([...countryCodes, undefined]);
  };

  const removeDestination = (index: number) => {
    if (data.length > 1) {
      const newDestinations = data.filter((_, i) => i !== index);
      const newCodes = countryCodes.filter((_, i) => i !== index);
      onChange(newDestinations);
      setCountryCodes(newCodes);
      if (newDestinations.length === 1) {
        setIsMultiCity(false);
      }
    }
  };

  const toggleMultiCity = () => {
    if (!isMultiCity) {
      // Enabling multi-city: add second destination
      onChange([...data, { country: '', city: '' }]);
      setCountryCodes([...countryCodes, undefined]);
      setIsMultiCity(true);
    } else {
      // Disabling multi-city: keep only first destination
      onChange([data[0]]);
      setCountryCodes([countryCodes[0]]);
      setIsMultiCity(false);
    }
  };

  const handleQuickSelect = (index: number, dest: (typeof POPULAR_DESTINATIONS)[0]) => {
    const newDestinations = [...data];
    const newCodes = [...countryCodes];
    newDestinations[index] = { country: dest.country, city: dest.city };
    newCodes[index] = dest.countryCode;
    onChange(newDestinations);
    setCountryCodes(newCodes);
  };

  return (
    <div className="space-y-8">
      {/* Page title */}
      <div className="border-l-4 border-blue-600 pl-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-1">Destinations</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Where are you planning to visit?
        </p>
      </div>

      {/* Multi-city toggle */}
      <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 animate-slideInUp">
        <div>
          <h3 className="font-medium text-slate-900 dark:text-slate-100">Multi-City Trip</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
            Visiting multiple destinations
          </p>
        </div>
        <button
          type="button"
          onClick={toggleMultiCity}
          className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors duration-200 ${isMultiCity ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-700'}`}
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-200 ${isMultiCity ? 'translate-x-6' : 'translate-x-1'}`}
          />
        </button>
      </div>

      {/* Destination cards */}
      <div className="space-y-4">
        {data.map((destination, index) => (
          <div
            key={index}
            className="relative bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300 animate-slideInUp"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Destination number badge */}
            <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-sm shadow-lg">
              {index + 1}
            </div>

            {/* Remove button for additional destinations */}
            {index > 0 && (
              <button
                type="button"
                onClick={() => removeDestination(index)}
                className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors"
                title="Remove destination"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  strokeWidth="2.5"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
              {/* Country */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Country <span className="text-red-600">*</span>
                </label>
                <SearchableSelect
                  value={
                    destination.country
                      ? countryOptions.find((c) => c.label === destination.country) || null
                      : null
                  }
                  onChange={(option) => handleCountryChange(index, option)}
                  options={countryOptions}
                  placeholder="Search for a country..."
                  noOptionsMessage="No countries found"
                />
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  City <span className="text-red-600">*</span>
                </label>
                <SearchableSelect
                  value={
                    destination.city ? { value: destination.city, label: destination.city } : null
                  }
                  onChange={(option) => handleCityChange(index, option)}
                  options={getCityOptions(index)}
                  placeholder={
                    countryCodes[index] ? 'Search for a city...' : 'Select a country first'
                  }
                  isDisabled={!countryCodes[index]}
                  noOptionsMessage={
                    countryCodes[index] ? 'No cities found' : 'Please select a country first'
                  }
                />
              </div>
            </div>

            {/* Quick suggestions */}
            {!destination.country && !destination.city && (
              <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                <p className="text-xs text-slate-500 dark:text-slate-500 mb-2">
                  Popular destinations:
                </p>
                <div className="flex flex-wrap gap-2">
                  {POPULAR_DESTINATIONS.map((dest, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleQuickSelect(index, dest)}
                      className="px-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-full hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      {dest.city}, {dest.country}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add destination button (only show if multi-city enabled) */}
      {isMultiCity && data.length < 5 && (
        <button
          type="button"
          onClick={addDestination}
          className="w-full py-4 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl text-slate-600 dark:text-slate-400 hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-200 flex items-center justify-center gap-2 font-medium group"
        >
          <svg
            className="w-5 h-5 group-hover:scale-110 transition-transform"
            fill="none"
            strokeWidth="2"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Add Another Destination
        </button>
      )}

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
  );
}
