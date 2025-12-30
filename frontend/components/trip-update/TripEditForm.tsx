'use client';

import { useState, useCallback, useMemo } from 'react';
import { Pencil, X, Save, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { TripData, TripUpdateData, EditFormState, EditFormErrors } from '@/types/trip-update';

interface TripEditFormProps {
  trip: TripData;
  onSave: (updates: TripUpdateData) => Promise<void>;
  onPreview: (updates: TripUpdateData) => void;
  disabled?: boolean;
}

const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
];

const TRIP_PURPOSES = ['Tourism', 'Business', 'Education', 'Family Visit', 'Medical', 'Other'];

const TRAVEL_STYLES = [
  { value: 'Relaxed', label: 'Relaxed', description: 'Slow-paced, plenty of rest' },
  { value: 'Balanced', label: 'Balanced', description: 'Mix of activities and relaxation' },
  { value: 'Packed', label: 'Packed', description: 'Action-packed, maximum experiences' },
  { value: 'Budget-Focused', label: 'Budget-Focused', description: 'Cost-effective choices' },
];

/**
 * TripEditForm - Form for editing trip details
 * Supports inline editing with validation and change preview
 */
export function TripEditForm({ trip, onSave, onPreview, disabled = false }: TripEditFormProps) {
  const [formState, setFormState] = useState<EditFormState>('viewing');
  const [formData, setFormData] = useState<TripUpdateData>({});
  const [errors, setErrors] = useState<EditFormErrors>({});
  const [saving, setSaving] = useState(false);

  // Merge trip data with form updates for display
  const currentData = useMemo(
    () => ({
      ...trip,
      ...formData,
    }),
    [trip, formData],
  );

  // Check if form has changes
  const hasChanges = useMemo(() => {
    return Object.keys(formData).length > 0;
  }, [formData]);

  const handleEdit = useCallback(() => {
    setFormState('editing');
    setFormData({});
    setErrors({});
  }, []);

  const handleCancel = useCallback(() => {
    setFormState('viewing');
    setFormData({});
    setErrors({});
  }, []);

  const updateField = useCallback(
    <K extends keyof TripUpdateData>(field: K, value: TripUpdateData[K]) => {
      setFormData((prev) => {
        const newData = { ...prev, [field]: value };
        // Remove field if value matches original
        if (JSON.stringify(value) === JSON.stringify(trip[field as keyof TripData])) {
          delete newData[field];
        }
        return newData;
      });
      // Clear error for this field
      if (errors[field]) {
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[field];
          return newErrors;
        });
      }
    },
    [trip, errors],
  );

  const validateForm = useCallback((): boolean => {
    const newErrors: EditFormErrors = {};

    // Validate dates
    const departure = currentData.departureDate ? new Date(currentData.departureDate) : null;
    const returnDate = currentData.returnDate ? new Date(currentData.returnDate) : null;

    if (!currentData.title?.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!currentData.destinationCity?.trim()) {
      newErrors.destinationCity = 'Destination city is required';
    }

    if (!currentData.destinationCountry?.trim()) {
      newErrors.destinationCountry = 'Destination country is required';
    }

    if (!departure) {
      newErrors.departureDate = 'Departure date is required';
    }

    if (!returnDate) {
      newErrors.returnDate = 'Return date is required';
    }

    if (departure && returnDate && returnDate <= departure) {
      newErrors.returnDate = 'Return date must be after departure date';
    }

    if (currentData.budget !== undefined && currentData.budget < 0) {
      newErrors.budget = 'Budget must be a positive number';
    }

    if (currentData.partySize !== undefined && currentData.partySize < 1) {
      newErrors.partySize = 'Party size must be at least 1';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [currentData]);

  const handlePreview = useCallback(() => {
    if (!validateForm()) return;
    onPreview(formData);
    setFormState('previewing');
  }, [validateForm, onPreview, formData]);

  const handleSave = useCallback(async () => {
    if (!validateForm()) return;
    setSaving(true);
    try {
      await onSave(formData);
      setFormState('viewing');
      setFormData({});
    } finally {
      setSaving(false);
    }
  }, [validateForm, onSave, formData]);

  const isEditing = formState === 'editing' || formState === 'previewing';

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Trip Details</h2>
        {!isEditing ? (
          <Button variant="outline" size="sm" onClick={handleEdit} disabled={disabled}>
            <Pencil className="h-4 w-4 mr-2" />
            Edit
          </Button>
        ) : (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleCancel} disabled={saving}>
              <X className="h-4 w-4 mr-1" />
              Cancel
            </Button>
            {hasChanges && (
              <>
                <Button variant="outline" size="sm" onClick={handlePreview} disabled={saving}>
                  <AlertTriangle className="h-4 w-4 mr-1" />
                  Preview Changes
                </Button>
                <Button size="sm" onClick={handleSave} disabled={saving}>
                  <Save className="h-4 w-4 mr-1" />
                  {saving ? 'Saving...' : 'Save'}
                </Button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Form Content */}
      <div className="p-6 space-y-6">
        {/* Title */}
        <div>
          <Label htmlFor="title">Trip Title</Label>
          {isEditing ? (
            <>
              <Input
                id="title"
                value={currentData.title || ''}
                onChange={(e) => updateField('title', e.target.value)}
                className={errors.title ? 'border-red-500' : ''}
              />
              {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
            </>
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.title || 'Untitled Trip'}
            </p>
          )}
        </div>

        {/* Destination */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="destinationCity">Destination City</Label>
            {isEditing ? (
              <>
                <Input
                  id="destinationCity"
                  value={currentData.destinationCity || ''}
                  onChange={(e) => updateField('destinationCity', e.target.value)}
                  className={errors.destinationCity ? 'border-red-500' : ''}
                />
                {errors.destinationCity && (
                  <p className="mt-1 text-sm text-red-600">{errors.destinationCity}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">{trip.destinationCity}</p>
            )}
          </div>
          <div>
            <Label htmlFor="destinationCountry">Destination Country</Label>
            {isEditing ? (
              <>
                <Input
                  id="destinationCountry"
                  value={currentData.destinationCountry || ''}
                  onChange={(e) => updateField('destinationCountry', e.target.value)}
                  className={errors.destinationCountry ? 'border-red-500' : ''}
                />
                {errors.destinationCountry && (
                  <p className="mt-1 text-sm text-red-600">{errors.destinationCountry}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">{trip.destinationCountry}</p>
            )}
          </div>
        </div>

        {/* Origin City */}
        <div>
          <Label htmlFor="originCity">Origin City</Label>
          {isEditing ? (
            <Input
              id="originCity"
              value={currentData.originCity || ''}
              onChange={(e) => updateField('originCity', e.target.value)}
            />
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.originCity || 'Not specified'}
            </p>
          )}
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="departureDate">Departure Date</Label>
            {isEditing ? (
              <>
                <Input
                  id="departureDate"
                  type="date"
                  value={currentData.departureDate || ''}
                  onChange={(e) => updateField('departureDate', e.target.value)}
                  className={errors.departureDate ? 'border-red-500' : ''}
                />
                {errors.departureDate && (
                  <p className="mt-1 text-sm text-red-600">{errors.departureDate}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">
                {trip.departureDate ? new Date(trip.departureDate).toLocaleDateString() : 'Not set'}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="returnDate">Return Date</Label>
            {isEditing ? (
              <>
                <Input
                  id="returnDate"
                  type="date"
                  value={currentData.returnDate || ''}
                  onChange={(e) => updateField('returnDate', e.target.value)}
                  min={currentData.departureDate || undefined}
                  className={errors.returnDate ? 'border-red-500' : ''}
                />
                {errors.returnDate && (
                  <p className="mt-1 text-sm text-red-600">{errors.returnDate}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">
                {trip.returnDate ? new Date(trip.returnDate).toLocaleDateString() : 'Not set'}
              </p>
            )}
          </div>
        </div>

        {/* Budget */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="budget">Budget</Label>
            {isEditing ? (
              <>
                <Input
                  id="budget"
                  type="number"
                  min="0"
                  step="100"
                  value={currentData.budget ?? ''}
                  onChange={(e) => updateField('budget', parseFloat(e.target.value) || 0)}
                  className={errors.budget ? 'border-red-500' : ''}
                />
                {errors.budget && <p className="mt-1 text-sm text-red-600">{errors.budget}</p>}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">
                {trip.budget?.toLocaleString() || 'Not set'}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="currency">Currency</Label>
            {isEditing ? (
              <select
                id="currency"
                value={currentData.currency || 'USD'}
                onChange={(e) => updateField('currency', e.target.value)}
                className="w-full h-10 px-3 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
              >
                {CURRENCIES.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.symbol} {c.code}
                  </option>
                ))}
              </select>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">{trip.currency || 'USD'}</p>
            )}
          </div>
        </div>

        {/* Trip Purpose */}
        <div>
          <Label htmlFor="tripPurpose">Trip Purpose</Label>
          {isEditing ? (
            <select
              id="tripPurpose"
              value={currentData.tripPurpose || ''}
              onChange={(e) => updateField('tripPurpose', e.target.value)}
              className="w-full h-10 px-3 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
            >
              <option value="">Select purpose</option>
              {TRIP_PURPOSES.map((purpose) => (
                <option key={purpose} value={purpose}>
                  {purpose}
                </option>
              ))}
            </select>
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.tripPurpose || 'Not specified'}
            </p>
          )}
        </div>

        {/* Party Size */}
        <div>
          <Label htmlFor="partySize">Party Size</Label>
          {isEditing ? (
            <>
              <Input
                id="partySize"
                type="number"
                min="1"
                max="50"
                value={currentData.partySize ?? 1}
                onChange={(e) => updateField('partySize', parseInt(e.target.value) || 1)}
                className={errors.partySize ? 'border-red-500' : ''}
              />
              {errors.partySize && <p className="mt-1 text-sm text-red-600">{errors.partySize}</p>}
            </>
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.partySize || 1} {(trip.partySize || 1) === 1 ? 'person' : 'people'}
            </p>
          )}
        </div>

        {/* Travel Style */}
        <div>
          <Label htmlFor="travelStyle">Travel Style</Label>
          {isEditing ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
              {TRAVEL_STYLES.map((style) => (
                <button
                  key={style.value}
                  type="button"
                  onClick={() => updateField('travelStyle', style.value)}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    currentData.travelStyle === style.value
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/30'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <div className="font-medium text-sm text-slate-900 dark:text-slate-100">
                    {style.label}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {style.description}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.travelStyle || 'Not specified'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default TripEditForm;
