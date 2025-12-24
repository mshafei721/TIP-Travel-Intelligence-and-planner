'use client'

import type { TripFormData } from './TripCreationWizard'

interface TripSummaryProps {
  formData: TripFormData
  onEdit: (step: number) => void
  onSubmit: () => void
  isSubmitting: boolean
}

export default function TripSummary({ formData, onEdit, onSubmit, isSubmitting }: TripSummaryProps) {
  const { travelerDetails, destinations, tripDetails, preferences } = formData

  // Calculate trip duration
  const getDuration = () => {
    if (tripDetails.departureDate && tripDetails.returnDate) {
      const departure = new Date(tripDetails.departureDate)
      const returnDate = new Date(tripDetails.returnDate)
      const diffTime = Math.abs(returnDate.getTime() - departure.getTime())
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays
    }
    return 0
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center py-8 bg-gradient-to-br from-blue-50 to-amber-50/30 dark:from-slate-800 dark:to-slate-800/50
                    rounded-2xl border border-slate-200 dark:border-slate-700">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-50 mb-2">
          Almost There!
        </h2>
        <p className="text-slate-600 dark:text-slate-400">
          Review your trip details before we generate your personalized travel intelligence
        </p>
      </div>

      {/* Summary sections */}
      <div className="space-y-4">
        {/* Traveler Details */}
        <SummaryCard
          title="Traveler Details"
          icon="👤"
          stepNumber={1}
          onEdit={() => onEdit(1)}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SummaryItem label="Name" value={travelerDetails.name} />
            <SummaryItem label="Email" value={travelerDetails.email} />
            <SummaryItem label="Nationality" value={travelerDetails.nationality} />
            <SummaryItem label="Residence" value={travelerDetails.residenceCountry} />
            <SummaryItem label="Origin City" value={travelerDetails.originCity} />
            <SummaryItem label="Status" value={travelerDetails.residencyStatus} />
            <SummaryItem label="Party Size" value={`${travelerDetails.partySize} ${travelerDetails.partySize === 1 ? 'person' : 'people'}`} />
            {travelerDetails.contactPreferences.length > 0 && (
              <SummaryItem label="Contact" value={travelerDetails.contactPreferences.join(', ')} />
            )}
          </div>
        </SummaryCard>

        {/* Destinations */}
        <SummaryCard
          title="Destinations"
          icon="📍"
          stepNumber={2}
          onEdit={() => onEdit(2)}
        >
          <div className="space-y-3">
            {destinations.map((dest, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-sm">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-slate-900 dark:text-slate-100">
                    {dest.city}, {dest.country}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SummaryCard>

        {/* Trip Details */}
        <SummaryCard
          title="Trip Details"
          icon="🗓️"
          stepNumber={3}
          onEdit={() => onEdit(3)}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SummaryItem
              label="Departure"
              value={new Date(tripDetails.departureDate).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            />
            <SummaryItem
              label="Return"
              value={new Date(tripDetails.returnDate).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            />
            <SummaryItem label="Duration" value={`${getDuration()} days`} />
            <SummaryItem label="Budget" value={`${tripDetails.currency} ${tripDetails.budget.toLocaleString()}`} />
            <SummaryItem label="Purpose" value={tripDetails.tripPurpose} />
          </div>
        </SummaryCard>

        {/* Preferences */}
        <SummaryCard
          title="Preferences"
          icon="⭐"
          stepNumber={4}
          onEdit={() => onEdit(4)}
        >
          <div className="space-y-4">
            <SummaryItem label="Travel Style" value={preferences.travelStyle} />
            {preferences.interests.length > 0 && (
              <SummaryItem label="Interests" value={preferences.interests.join(', ')} />
            )}
            {preferences.dietaryRestrictions.length > 0 && (
              <SummaryItem label="Dietary" value={preferences.dietaryRestrictions.join(', ')} />
            )}
            {preferences.accessibilityNeeds && (
              <SummaryItem label="Accessibility" value={preferences.accessibilityNeeds} />
            )}
          </div>
        </SummaryCard>
      </div>

      {/* Submit note */}
      <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <div className="text-2xl">ℹ️</div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
              What happens next?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Once you submit, our AI agents will analyze visa requirements, destination intelligence, weather forecasts, and more to create your comprehensive travel report. This typically takes 2-5 minutes.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

interface SummaryCardProps {
  title: string
  icon: string
  stepNumber: number
  onEdit: () => void
  children: React.ReactNode
}

function SummaryCard({ title, icon, stepNumber, onEdit, children }: SummaryCardProps) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-50">{title}</h3>
        </div>
        <button
          onClick={onEdit}
          className="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400
                   hover:bg-blue-50 dark:hover:bg-blue-950/30 rounded-lg transition-colors
                   flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </button>
      </div>
      <div>{children}</div>
    </div>
  )
}

interface SummaryItemProps {
  label: string
  value: string
}

function SummaryItem({ label, value }: SummaryItemProps) {
  return (
    <div>
      <div className="text-xs font-medium text-slate-500 dark:text-slate-500 mb-1">
        {label}
      </div>
      <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
        {value}
      </div>
    </div>
  )
}
