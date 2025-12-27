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
    const departure = currentData.departure_date ? new Date(currentData.departure_date) : null;
    const returnDate = currentData.return_date ? new Date(currentData.return_date) : null;

    if (!currentData.title?.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!currentData.destination_city?.trim()) {
      newErrors.destination_city = 'Destination city is required';
    }

    if (!currentData.destination_country?.trim()) {
      newErrors.destination_country = 'Destination country is required';
    }

    if (!departure) {
      newErrors.departure_date = 'Departure date is required';
    }

    if (!returnDate) {
      newErrors.return_date = 'Return date is required';
    }

    if (departure && returnDate && returnDate <= departure) {
      newErrors.return_date = 'Return date must be after departure date';
    }

    if (currentData.budget !== undefined && currentData.budget < 0) {
      newErrors.budget = 'Budget must be a positive number';
    }

    if (currentData.party_size !== undefined && currentData.party_size < 1) {
      newErrors.party_size = 'Party size must be at least 1';
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
            <Label htmlFor="destination_city">Destination City</Label>
            {isEditing ? (
              <>
                <Input
                  id="destination_city"
                  value={currentData.destination_city || ''}
                  onChange={(e) => updateField('destination_city', e.target.value)}
                  className={errors.destination_city ? 'border-red-500' : ''}
                />
                {errors.destination_city && (
                  <p className="mt-1 text-sm text-red-600">{errors.destination_city}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">{trip.destination_city}</p>
            )}
          </div>
          <div>
            <Label htmlFor="destination_country">Destination Country</Label>
            {isEditing ? (
              <>
                <Input
                  id="destination_country"
                  value={currentData.destination_country || ''}
                  onChange={(e) => updateField('destination_country', e.target.value)}
                  className={errors.destination_country ? 'border-red-500' : ''}
                />
                {errors.destination_country && (
                  <p className="mt-1 text-sm text-red-600">{errors.destination_country}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">{trip.destination_country}</p>
            )}
          </div>
        </div>

        {/* Origin City */}
        <div>
          <Label htmlFor="origin_city">Origin City</Label>
          {isEditing ? (
            <Input
              id="origin_city"
              value={currentData.origin_city || ''}
              onChange={(e) => updateField('origin_city', e.target.value)}
            />
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.origin_city || 'Not specified'}
            </p>
          )}
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="departure_date">Departure Date</Label>
            {isEditing ? (
              <>
                <Input
                  id="departure_date"
                  type="date"
                  value={currentData.departure_date || ''}
                  onChange={(e) => updateField('departure_date', e.target.value)}
                  className={errors.departure_date ? 'border-red-500' : ''}
                />
                {errors.departure_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.departure_date}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">
                {trip.departure_date
                  ? new Date(trip.departure_date).toLocaleDateString()
                  : 'Not set'}
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="return_date">Return Date</Label>
            {isEditing ? (
              <>
                <Input
                  id="return_date"
                  type="date"
                  value={currentData.return_date || ''}
                  onChange={(e) => updateField('return_date', e.target.value)}
                  min={currentData.departure_date || undefined}
                  className={errors.return_date ? 'border-red-500' : ''}
                />
                {errors.return_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.return_date}</p>
                )}
              </>
            ) : (
              <p className="mt-1 text-slate-700 dark:text-slate-300">
                {trip.return_date ? new Date(trip.return_date).toLocaleDateString() : 'Not set'}
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
          <Label htmlFor="trip_purpose">Trip Purpose</Label>
          {isEditing ? (
            <select
              id="trip_purpose"
              value={currentData.trip_purpose || ''}
              onChange={(e) => updateField('trip_purpose', e.target.value)}
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
              {trip.trip_purpose || 'Not specified'}
            </p>
          )}
        </div>

        {/* Party Size */}
        <div>
          <Label htmlFor="party_size">Party Size</Label>
          {isEditing ? (
            <>
              <Input
                id="party_size"
                type="number"
                min="1"
                max="50"
                value={currentData.party_size ?? 1}
                onChange={(e) => updateField('party_size', parseInt(e.target.value) || 1)}
                className={errors.party_size ? 'border-red-500' : ''}
              />
              {errors.party_size && (
                <p className="mt-1 text-sm text-red-600">{errors.party_size}</p>
              )}
            </>
          ) : (
            <p className="mt-1 text-slate-700 dark:text-slate-300">
              {trip.party_size || 1} {(trip.party_size || 1) === 1 ? 'person' : 'people'}
            </p>
          )}
        </div>

        {/* Travel Style */}
        <div>
          <Label htmlFor="travel_style">Travel Style</Label>
          {isEditing ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
              {TRAVEL_STYLES.map((style) => (
                <button
                  key={style.value}
                  type="button"
                  onClick={() => updateField('travel_style', style.value)}
                  className={`p-3 rounded-lg border-2 text-left transition-all ${
                    currentData.travel_style === style.value
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
              {trip.travel_style || 'Not specified'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default TripEditForm;
