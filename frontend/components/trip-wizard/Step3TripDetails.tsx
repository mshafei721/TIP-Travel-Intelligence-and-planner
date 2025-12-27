'use client';

import { useState } from 'react';
import type { TripDetails, TripPurposeType } from './TripCreationWizard';

interface Step3Props {
  data: TripDetails;
  onChange: (data: TripDetails) => void;
}

const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
];

const TRIP_PURPOSES = [
  { value: 'Tourism', icon: '🏖️', desc: 'Leisure and sightseeing' },
  { value: 'Business', icon: '💼', desc: 'Work-related travel' },
  { value: 'Education', icon: '📚', desc: 'Study or research' },
  { value: 'Family Visit', icon: '👨‍👩‍👧', desc: 'Visiting relatives' },
  { value: 'Medical', icon: '🏥', desc: 'Healthcare purposes' },
  { value: 'Other', icon: '✈️', desc: 'Other purposes' },
];

export default function Step3TripDetails({ data, onChange }: Step3Props) {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateField = <K extends keyof TripDetails>(field: K, value: TripDetails[K]) => {
    onChange({ ...data, [field]: value });

    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const togglePurpose = (purpose: TripPurposeType) => {
    const current = data.tripPurposes || [];
    const isSelected = current.includes(purpose);
    const newPurposes = isSelected ? current.filter((p) => p !== purpose) : [...current, purpose];
    updateField('tripPurposes', newPurposes);
  };

  // Validate dates
  const validateDates = () => {
    const newErrors: Record<string, string> = {};

    if (data.departureDate && data.returnDate) {
      const departure = new Date(data.departureDate);
      const returnDate = new Date(data.returnDate);

      if (returnDate <= departure) {
        newErrors.returnDate = 'Return date must be after departure date';
      }
    }

    setErrors(newErrors);
  };

  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];

  // Calculate trip duration
  const calculateDuration = () => {
    if (data.departureDate && data.returnDate) {
      const departure = new Date(data.departureDate);
      const returnDate = new Date(data.returnDate);
      const diffTime = Math.abs(returnDate.getTime() - departure.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays;
    }
    return null;
  };

  const duration = calculateDuration();

  return (
    <div className="space-y-8">
      {/* Page title */}
      <div className="border-l-4 border-blue-600 pl-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-1">Trip Details</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          When and how much you plan to spend
        </p>
      </div>

      <div className="space-y-6">
        {/* Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-slideInUp">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Departure Date <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              min={today}
              value={data.departureDate}
              onChange={(e) => {
                updateField('departureDate', e.target.value);
                setTimeout(validateDates, 100);
              }}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Return Date <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              min={data.departureDate || today}
              value={data.returnDate}
              onChange={(e) => {
                updateField('returnDate', e.target.value);
                setTimeout(validateDates, 100);
              }}
              className={`w-full px-4 py-3 rounded-lg border ${errors.returnDate ? 'border-red-500' : 'border-slate-300 dark:border-slate-700'} bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200`}
            />
            {errors.returnDate && <p className="mt-1 text-sm text-red-600">{errors.returnDate}</p>}
          </div>
        </div>

        {/* Duration display */}
        {duration && (
          <div
            className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900 rounded-lg p-4 flex items-center gap-3 animate-slideInUp"
            style={{ animationDelay: '50ms' }}
          >
            <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white text-xl">
              📅
            </div>
            <div>
              <div className="font-semibold text-slate-900 dark:text-slate-100">
                {duration} {duration === 1 ? 'day' : 'days'}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Total trip duration</div>
            </div>
          </div>
        )}

        {/* Budget */}
        <div className="animate-slideInUp" style={{ animationDelay: '100ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Budget <span className="text-red-600">*</span>
          </label>
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                type="number"
                min="0"
                step="100"
                value={data.budget || ''}
                onChange={(e) => updateField('budget', parseFloat(e.target.value) || 0)}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                placeholder="5000"
              />
            </div>
            <div className="w-32">
              <select
                value={data.currency}
                onChange={(e) => updateField('currency', e.target.value as TripDetails['currency'])}
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              >
                {CURRENCIES.map((currency) => (
                  <option key={currency.code} value={currency.code}>
                    {currency.symbol} {currency.code}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
            Estimated total budget for the entire trip
          </p>
        </div>

        {/* Budget breakdown (if budget is set) */}
        {data.budget > 0 && duration && (
          <div
            className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 grid grid-cols-3 gap-4 animate-slideInUp"
            style={{ animationDelay: '150ms' }}
          >
            <div className="text-center">
              <div className="text-xs text-slate-500 dark:text-slate-500 mb-1">Per Day</div>
              <div className="font-mono font-semibold text-slate-900 dark:text-slate-100">
                {CURRENCIES.find((c) => c.code === data.currency)?.symbol}
                {Math.round(data.budget / duration)}
              </div>
            </div>
            <div className="text-center border-x border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 dark:text-slate-500 mb-1">Total</div>
              <div className="font-mono font-semibold text-slate-900 dark:text-slate-100">
                {CURRENCIES.find((c) => c.code === data.currency)?.symbol}
                {data.budget.toLocaleString()}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-slate-500 dark:text-slate-500 mb-1">Currency</div>
              <div className="font-mono font-semibold text-slate-900 dark:text-slate-100">
                {data.currency}
              </div>
            </div>
          </div>
        )}

        {/* Trip Purpose - Multi-select */}
        <div className="animate-slideInUp" style={{ animationDelay: '200ms' }}>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Trip Purpose <span className="text-red-600">*</span>
          </label>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">Select all that apply</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {TRIP_PURPOSES.map((purpose) => {
              const isSelected = data.tripPurposes?.includes(purpose.value as TripPurposeType);
              return (
                <button
                  key={purpose.value}
                  type="button"
                  onClick={() => togglePurpose(purpose.value as TripPurposeType)}
                  className={`p-4 rounded-xl border-2 transition-all duration-200 text-left hover:shadow-md ${isSelected ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/30 shadow-md' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="text-2xl mb-2">{purpose.icon}</div>
                    {isSelected && (
                      <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center">
                        <svg
                          className="w-3 h-3 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="font-semibold text-slate-900 dark:text-slate-100 mb-0.5">
                    {purpose.value}
                  </div>
                  <div className="text-xs text-slate-600 dark:text-slate-400">{purpose.desc}</div>
                </button>
              );
            })}
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
  );
}
