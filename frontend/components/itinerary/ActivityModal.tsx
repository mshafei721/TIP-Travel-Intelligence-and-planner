'use client';

import React, { useState, useEffect } from 'react';
import type {
  Activity,
  ActivityCategory,
  TimeOfDay,
  ActivityLocation,
  ActivityCost,
  BookingInfo,
  AccessibilityInfo,
} from '@/types/itinerary';
import { X, Check, AlertCircle, Clock, MapPin, DollarSign, Info } from 'lucide-react';

interface ActivityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (activity: Partial<Activity>) => void;
  activity?: Activity; // If editing
  dayNumber: number;
  timeOfDay: TimeOfDay;
  existingActivities?: Activity[]; // For conflict detection
}

// Category options with icons (matching ActivityCard)
const categoryOptions: Array<{
  value: ActivityCategory;
  label: string;
  icon: string;
  description: string;
}> = [
  {
    value: 'culture',
    label: 'Culture',
    icon: '🎭',
    description: 'Museums, theaters, cultural sites',
  },
  {
    value: 'food',
    label: 'Food',
    icon: '🍽️',
    description: 'Restaurants, cafes, food tours',
  },
  {
    value: 'nature',
    label: 'Nature',
    icon: '🏞️',
    description: 'Parks, beaches, hiking',
  },
  {
    value: 'shopping',
    label: 'Shopping',
    icon: '🛍️',
    description: 'Markets, malls, boutiques',
  },
  {
    value: 'accommodation',
    label: 'Accommodation',
    icon: '🏨',
    description: 'Hotels, check-in/out',
  },
  {
    value: 'transport',
    label: 'Transport',
    icon: '🚇',
    description: 'Trains, buses, transfers',
  },
  {
    value: 'entertainment',
    label: 'Entertainment',
    icon: '🎪',
    description: 'Shows, concerts, nightlife',
  },
  {
    value: 'relaxation',
    label: 'Relaxation',
    icon: '🧘',
    description: 'Spa, leisure',
  },
  {
    value: 'adventure',
    label: 'Adventure',
    icon: '⛰️',
    description: 'Sports, activities',
  },
  {
    value: 'other',
    label: 'Other',
    icon: '📍',
    description: 'Miscellaneous',
  },
];

const priorityOptions = [
  { value: 'must-see', label: 'Must See', color: 'amber' },
  { value: 'recommended', label: 'Recommended', color: 'blue' },
  { value: 'optional', label: 'Optional', color: 'slate' },
];

export function ActivityModal({
  isOpen,
  onClose,
  onSave,
  activity,
  dayNumber,
  timeOfDay,
  existingActivities = [],
}: ActivityModalProps) {
  const isEditing = !!activity;

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    category: 'culture' as ActivityCategory,
    startTime: '09:00',
    endTime: '10:00',
    locationName: '',
    locationAddress: '',
    locationNeighborhood: '',
    locationTransportInfo: '',
    description: '',
    costAmount: 0,
    costCurrency: '¥',
    costPerPerson: true,
    costNotes: '',
    bookingRequired: false,
    bookingWebsite: '',
    bookingPhone: '',
    bookingStatus: 'pending' as 'pending' | 'confirmed' | 'cancelled',
    notes: '',
    priority: 'recommended' as 'must-see' | 'recommended' | 'optional' | undefined,
    wheelchairAccessible: false,
    accessibilityNotes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [timeConflict, setTimeConflict] = useState<string | null>(null);

  // Initialize form with activity data when editing
  useEffect(() => {
    if (activity) {
      setFormData({
        name: activity.name,
        category: activity.category,
        startTime: activity.startTime,
        endTime: activity.endTime,
        locationName: activity.location.name,
        locationAddress: activity.location.address || '',
        locationNeighborhood: activity.location.neighborhood || '',
        locationTransportInfo: activity.location.transportInfo || '',
        description: activity.description || '',
        costAmount: activity.cost?.amount || 0,
        costCurrency: activity.cost?.currency || '¥',
        costPerPerson: activity.cost?.perPerson ?? true,
        costNotes: activity.cost?.notes || '',
        bookingRequired: activity.bookingInfo?.required || false,
        bookingWebsite: activity.bookingInfo?.website || '',
        bookingPhone: activity.bookingInfo?.phone || '',
        bookingStatus: activity.bookingInfo?.bookingStatus || 'pending',
        notes: activity.notes || '',
        priority: activity.priority,
        wheelchairAccessible: activity.accessibility?.wheelchairAccessible || false,
        accessibilityNotes: activity.accessibility?.notes || '',
      });
    }
  }, [activity]);

  // Check for time conflicts
  useEffect(() => {
    const activitiesToCheck = isEditing && activity
      ? existingActivities.filter((a) => a.id !== activity.id)
      : existingActivities;

    const conflict = detectTimeConflict(
      formData.startTime,
      formData.endTime,
      activitiesToCheck
    );
    setTimeConflict(conflict);
  }, [formData.startTime, formData.endTime, existingActivities, isEditing, activity]);

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Activity name is required';
    }

    if (!formData.locationName.trim()) {
      newErrors.locationName = 'Location name is required';
    }

    const [startHour, startMin] = formData.startTime.split(':').map(Number);
    const [endHour, endMin] = formData.endTime.split(':').map(Number);
    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;

    if (endMinutes <= startMinutes) {
      newErrors.endTime = 'End time must be after start time';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle save
  const handleSave = () => {
    if (!validateForm()) return;

    const [startHour, startMin] = formData.startTime.split(':').map(Number);
    const [endHour, endMin] = formData.endTime.split(':').map(Number);
    const duration = (endHour * 60 + endMin) - (startHour * 60 + startMin);

    const activityData: Partial<Activity> = {
      id: activity?.id || `activity-${Date.now()}`,
      name: formData.name,
      category: formData.category,
      startTime: formData.startTime,
      endTime: formData.endTime,
      duration,
      location: {
        name: formData.locationName,
        address: formData.locationAddress || undefined,
        neighborhood: formData.locationNeighborhood || undefined,
        transportInfo: formData.locationTransportInfo || undefined,
      },
      description: formData.description || undefined,
      cost: formData.costAmount > 0 || formData.costNotes
        ? {
            amount: formData.costAmount,
            currency: formData.costCurrency,
            perPerson: formData.costPerPerson,
            notes: formData.costNotes || undefined,
          }
        : undefined,
      bookingInfo: formData.bookingRequired
        ? {
            required: formData.bookingRequired,
            website: formData.bookingWebsite || undefined,
            phone: formData.bookingPhone || undefined,
            bookingStatus: formData.bookingStatus,
          }
        : undefined,
      notes: formData.notes || undefined,
      priority: formData.priority,
      accessibility: {
        wheelchairAccessible: formData.wheelchairAccessible,
        notes: formData.accessibilityNotes || undefined,
      },
    };

    onSave(activityData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div
        className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-xl border-2 border-slate-300 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
        style={{
          // Travel document aesthetic with subtle stamp pattern
          backgroundImage: `
            radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(251, 191, 36, 0.03) 0%, transparent 50%)
          `,
        }}
      >
        {/* Header - Passport stamp style */}
        <div className="sticky top-0 z-10 border-b-2 border-dashed border-slate-300 bg-gradient-to-r from-blue-50 to-amber-50 p-6 dark:border-slate-700 dark:from-slate-800 dark:to-slate-800">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                {isEditing ? '✏️ Edit Activity' : '➕ Add New Activity'}
              </h2>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Day {dayNumber} • {timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)}
              </p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-300"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Form content */}
        <div className="p-6 space-y-6">
          {/* Time Conflict Warning */}
          {timeConflict && (
            <div className="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4 dark:border-amber-700 dark:bg-amber-950/30">
              <AlertCircle className="h-5 w-5 flex-shrink-0 text-amber-600 dark:text-amber-500" />
              <div className="flex-1">
                <h4 className="font-semibold text-amber-900 dark:text-amber-200">
                  Time Conflict Detected
                </h4>
                <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">
                  {timeConflict}
                </p>
              </div>
            </div>
          )}

          {/* Basic Information Section */}
          <section className="space-y-4">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
              <Info className="h-5 w-5" />
              Basic Information
            </h3>

            {/* Activity Name */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Activity Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={`w-full rounded-lg border px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 dark:bg-slate-800 dark:text-slate-50 ${
                  errors.name
                    ? 'border-red-300 focus:ring-red-500'
                    : 'border-slate-300 focus:ring-blue-500 dark:border-slate-700'
                }`}
                placeholder="e.g., Visit Senso-ji Temple"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
              )}
            </div>

            {/* Category Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Category *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {categoryOptions.map((cat) => (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, category: cat.value })}
                    className={`flex flex-col items-center gap-1 rounded-lg border-2 p-3 transition-all ${
                      formData.category === cat.value
                        ? 'border-blue-500 bg-blue-50 shadow-sm dark:border-blue-400 dark:bg-blue-950/30'
                        : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-600'
                    }`}
                  >
                    <span className="text-2xl">{cat.icon}</span>
                    <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                      {cat.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                placeholder="Brief description of the activity..."
              />
            </div>
          </section>

          {/* Time Section */}
          <section className="space-y-4">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
              <Clock className="h-5 w-5" />
              Time
            </h3>

            <div className="grid grid-cols-2 gap-4">
              {/* Start Time */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Start Time *
                </label>
                <input
                  type="time"
                  value={formData.startTime}
                  onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                />
              </div>

              {/* End Time */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  End Time *
                </label>
                <input
                  type="time"
                  value={formData.endTime}
                  onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                  className={`w-full rounded-lg border px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 dark:bg-slate-800 dark:text-slate-50 ${
                    errors.endTime
                      ? 'border-red-300 focus:ring-red-500'
                      : 'border-slate-300 focus:ring-blue-500 dark:border-slate-700'
                  }`}
                />
                {errors.endTime && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.endTime}</p>
                )}
              </div>
            </div>
          </section>

          {/* Location Section */}
          <section className="space-y-4">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
              <MapPin className="h-5 w-5" />
              Location
            </h3>

            <div className="grid gap-4">
              {/* Location Name */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Location Name *
                </label>
                <input
                  type="text"
                  value={formData.locationName}
                  onChange={(e) => setFormData({ ...formData, locationName: e.target.value })}
                  className={`w-full rounded-lg border px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 dark:bg-slate-800 dark:text-slate-50 ${
                    errors.locationName
                      ? 'border-red-300 focus:ring-red-500'
                      : 'border-slate-300 focus:ring-blue-500 dark:border-slate-700'
                  }`}
                  placeholder="e.g., Senso-ji Temple"
                />
                {errors.locationName && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.locationName}
                  </p>
                )}
              </div>

              {/* Address & Neighborhood */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                    Address
                  </label>
                  <input
                    type="text"
                    value={formData.locationAddress}
                    onChange={(e) =>
                      setFormData({ ...formData, locationAddress: e.target.value })
                    }
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                    placeholder="Street address"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                    Neighborhood
                  </label>
                  <input
                    type="text"
                    value={formData.locationNeighborhood}
                    onChange={(e) =>
                      setFormData({ ...formData, locationNeighborhood: e.target.value })
                    }
                    className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                    placeholder="e.g., Asakusa"
                  />
                </div>
              </div>

              {/* Transport Info */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  How to Get There
                </label>
                <input
                  type="text"
                  value={formData.locationTransportInfo}
                  onChange={(e) =>
                    setFormData({ ...formData, locationTransportInfo: e.target.value })
                  }
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                  placeholder="e.g., Asakusa Station (Ginza Line)"
                />
              </div>
            </div>
          </section>

          {/* Cost Section */}
          <section className="space-y-4">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
              <DollarSign className="h-5 w-5" />
              Cost
            </h3>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Amount (0 for free)
                </label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.costAmount}
                  onChange={(e) =>
                    setFormData({ ...formData, costAmount: Number(e.target.value) })
                  }
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Cost Notes
                </label>
                <input
                  type="text"
                  value={formData.costNotes}
                  onChange={(e) => setFormData({ ...formData, costNotes: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                  placeholder="e.g., Entrance fee included"
                />
              </div>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.costPerPerson}
                onChange={(e) => setFormData({ ...formData, costPerPerson: e.target.checked })}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-slate-700 dark:text-slate-300">Cost is per person</span>
            </label>
          </section>

          {/* Additional Options */}
          <section className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
              Additional Options
            </h3>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Priority
              </label>
              <div className="flex gap-2">
                {priorityOptions.map((priority) => (
                  <button
                    key={priority.value}
                    type="button"
                    onClick={() =>
                      setFormData({
                        ...formData,
                        priority: priority.value as typeof formData.priority,
                      })
                    }
                    className={`flex-1 rounded-lg border-2 px-4 py-2 text-sm font-medium transition-all ${
                      formData.priority === priority.value
                        ? `border-${priority.color}-500 bg-${priority.color}-50 text-${priority.color}-700 dark:bg-${priority.color}-950/30 dark:text-${priority.color}-400`
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
                    }`}
                  >
                    {priority.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Booking Required */}
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.bookingRequired}
                onChange={(e) =>
                  setFormData({ ...formData, bookingRequired: e.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-slate-700 dark:text-slate-300">
                Booking required in advance
              </span>
            </label>

            {/* Wheelchair Accessible */}
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.wheelchairAccessible}
                onChange={(e) =>
                  setFormData({ ...formData, wheelchairAccessible: e.target.checked })
                }
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-slate-700 dark:text-slate-300">
                Wheelchair accessible
              </span>
            </label>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-50"
                placeholder="Additional notes or reminders..."
              />
            </div>
          </section>
        </div>

        {/* Footer - Action buttons */}
        <div className="sticky bottom-0 border-t-2 border-dashed border-slate-300 bg-gradient-to-r from-slate-50 to-blue-50 p-6 dark:border-slate-700 dark:from-slate-800 dark:to-slate-800">
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="rounded-lg border border-slate-300 bg-white px-6 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-2 rounded-lg bg-amber-500 px-6 py-2.5 font-semibold text-white shadow-sm transition-all hover:bg-amber-600 hover:shadow-md"
            >
              <Check className="h-5 w-5" />
              {isEditing ? 'Save Changes' : 'Add Activity'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper function to detect time conflicts
function detectTimeConflict(
  startTime: string,
  endTime: string,
  activities: Activity[]
): string | null {
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);
  const newStart = startHour * 60 + startMin;
  const newEnd = endHour * 60 + endMin;

  for (const activity of activities) {
    const [actStartHour, actStartMin] = activity.startTime.split(':').map(Number);
    const [actEndHour, actEndMin] = activity.endTime.split(':').map(Number);
    const actStart = actStartHour * 60 + actStartMin;
    const actEnd = actEndHour * 60 + actEndMin;

    // Check for overlap
    if (
      (newStart >= actStart && newStart < actEnd) ||
      (newEnd > actStart && newEnd <= actEnd) ||
      (newStart <= actStart && newEnd >= actEnd)
    ) {
      return `This activity conflicts with "${activity.name}" (${activity.startTime} - ${activity.endTime})`;
    }
  }

  return null;
}
