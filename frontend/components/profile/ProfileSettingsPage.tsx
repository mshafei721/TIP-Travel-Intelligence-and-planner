'use client'

import { useRouter } from 'next/navigation'
import { ProfileSection } from './ProfileSection'
import { TravelerDetailsSection } from './TravelerDetailsSection'
import { TravelPreferencesSection } from './TravelPreferencesSection'
import { SavedTemplatesSection } from './SavedTemplatesSection'
import { NotificationsSection } from './NotificationsSection'
import { PrivacySection } from './PrivacySection'
import { AccountSection } from './AccountSection'
import type { ProfileSettings, UserProfile, TravelerDetails, TravelPreferences, NotificationSettings, TripTemplate } from '@/types/profile'

export interface ProfileSettingsPageProps {
  initialSettings: ProfileSettings
}

/**
 * ProfileSettingsPage - Main profile settings container (Client Component)
 *
 * Manages all profile sections:
 * - Profile information
 * - Traveler details
 * - Travel preferences
 * - Saved templates
 * - Notifications
 * - Privacy
 * - Account deletion
 */
export function ProfileSettingsPage({ initialSettings }: ProfileSettingsPageProps) {
  const router = useRouter()

  // Profile update handlers
  const handleProfileUpdate = async (data: Partial<UserProfile>) => {
    const response = await fetch('/api/profile', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error('Failed to update profile')
    }

    router.refresh()
  }

  const handlePhotoUpload = async (file: File): Promise<string> => {
    const formData = new FormData()
    formData.append('photo', file)

    const response = await fetch('/api/profile/photo', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Failed to upload photo')
    }

    const { url } = await response.json()
    router.refresh()
    return url
  }

  const handleTravelerDetailsUpdate = async (data: TravelerDetails) => {
    const response = await fetch('/api/profile/traveler-details', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error('Failed to update traveler details')
    }

    router.refresh()
  }

  const handlePreferencesUpdate = async (data: TravelPreferences) => {
    const response = await fetch('/api/profile/preferences', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error('Failed to update preferences')
    }

    router.refresh()
  }

  const handleTemplateCreate = async (template: Omit<TripTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response = await fetch('/api/templates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(template),
    })

    if (!response.ok) {
      throw new Error('Failed to create template')
    }

    router.refresh()
  }

  const handleTemplateEdit = async (id: string, template: Omit<TripTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response = await fetch(`/api/templates/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(template),
    })

    if (!response.ok) {
      throw new Error('Failed to update template')
    }

    router.refresh()
  }

  const handleTemplateDelete = async (id: string) => {
    const response = await fetch(`/api/templates/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error('Failed to delete template')
    }

    router.refresh()
  }

  const handleNotificationsUpdate = async (notifications: NotificationSettings) => {
    const response = await fetch('/api/profile/notifications', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(notifications),
    })

    if (!response.ok) {
      throw new Error('Failed to update notifications')
    }

    router.refresh()
  }

  const handleAccountDelete = async () => {
    const response = await fetch('/api/profile', {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error('Failed to delete account')
    }

    // Logout and redirect
    router.push('/signup')
  }

  const handleChangePassword = () => {
    router.push('/change-password')
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
          Profile & Settings
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Manage your account, preferences, and trip templates
        </p>
      </div>

      {/* Sections */}
      <div className="space-y-6">
        <ProfileSection
          profile={initialSettings.profile}
          onProfileUpdate={handleProfileUpdate}
          onPhotoUpload={handlePhotoUpload}
          onChangePassword={handleChangePassword}
        />

        <TravelerDetailsSection
          travelerDetails={initialSettings.travelerDetails}
          onUpdate={handleTravelerDetailsUpdate}
        />

        <TravelPreferencesSection
          preferences={initialSettings.travelPreferences}
          onUpdate={handlePreferencesUpdate}
        />

        <SavedTemplatesSection
          templates={initialSettings.templates}
          onTemplateCreate={handleTemplateCreate}
          onTemplateEdit={handleTemplateEdit}
          onTemplateDelete={handleTemplateDelete}
        />

        <NotificationsSection
          notifications={initialSettings.notifications}
          onUpdate={handleNotificationsUpdate}
        />

        <PrivacySection />

        <AccountSection onAccountDelete={handleAccountDelete} />
      </div>
    </div>
  )
}
