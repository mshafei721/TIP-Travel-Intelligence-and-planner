'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { ProfileSection } from './ProfileSection'
import { TravelerDetailsSection } from './TravelerDetailsSection'
import { TravelPreferencesSection } from './TravelPreferencesSection'
import { SavedTemplatesSection } from './SavedTemplatesSection'
import { NotificationsSection } from './NotificationsSection'
import { PrivacySection } from './PrivacySection'
import { AccountSection } from './AccountSection'
import type { ProfileSettings, UserProfile, TravelerDetails, TravelPreferences, NotificationSettings, TripTemplate } from '@/types/profile'
import * as profileApi from '@/lib/api/profile'

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
  const [isUploading, setIsUploading] = useState(false)

  // Profile update handlers
  const handleProfileUpdate = async (data: Partial<UserProfile>) => {
    try {
      await profileApi.updateProfile({
        display_name: data.name || undefined,
        avatar_url: data.photoUrl || undefined,
      })
      router.refresh()
    } catch (error) {
      console.error('Failed to update profile:', error)
      throw error
    }
  }

  const handlePhotoUpload = async (file: File): Promise<string> => {
    setIsUploading(true)
    try {
      // Upload to Supabase Storage
      const { createClient } = await import('@/lib/supabase/client')
      const supabase = createClient()

      const fileExt = file.name.split('.').pop()
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`
      const filePath = `avatars/${fileName}`

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('profile-photos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
        })

      if (uploadError) {
        throw new Error(`Upload failed: ${uploadError.message}`)
      }

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('profile-photos')
        .getPublicUrl(filePath)

      // Update profile with new photo URL
      await profileApi.updateProfile({ avatar_url: publicUrl })

      router.refresh()
      return publicUrl
    } catch (error) {
      console.error('Photo upload failed:', error)
      throw error
    } finally {
      setIsUploading(false)
    }
  }

  const handleTravelerDetailsUpdate = async (data: TravelerDetails) => {
    try {
      await profileApi.updateTravelerProfile({
        nationality: data.nationality,
        residency_country: data.residenceCountry,
        residency_status: data.residencyStatus,
        date_of_birth: data.dateOfBirth || null,
      })
      router.refresh()
    } catch (error) {
      console.error('Failed to update traveler details:', error)
      throw error
    }
  }

  const handlePreferencesUpdate = async (data: TravelPreferences) => {
    try {
      // Update traveler profile with travel preferences
      await profileApi.updateTravelerProfile({
        travel_style: data.travelStyle,
        dietary_restrictions: data.dietaryRestrictions,
        accessibility_needs: data.accessibilityNeeds || null,
      })
      router.refresh()
    } catch (error) {
      console.error('Failed to update preferences:', error)
      throw error
    }
  }

  const handleTemplateCreate = async (template: Omit<TripTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    // TODO: Implement template API endpoints in backend
    throw new Error('Templates feature coming soon')
  }

  const handleTemplateEdit = async (id: string, template: Omit<TripTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    // TODO: Implement template API endpoints in backend
    throw new Error('Templates feature coming soon')
  }

  const handleTemplateDelete = async (id: string) => {
    // TODO: Implement template API endpoints in backend
    throw new Error('Templates feature coming soon')
  }

  const handleNotificationsUpdate = async (notifications: NotificationSettings) => {
    try {
      // Update user preferences with notification settings
      await profileApi.updatePreferences({
        email_notifications: notifications.reportCompletion,
        push_notifications: false, // Not implemented yet
        marketing_emails: notifications.productUpdates,
        language: 'en', // Keep existing
        currency: 'USD', // Keep existing
        units: 'metric', // Keep existing
      })
      router.refresh()
    } catch (error) {
      console.error('Failed to update notifications:', error)
      throw error
    }
  }

  const handleAccountDelete = async () => {
    try {
      await profileApi.deleteAccount({
        confirmation: 'DELETE MY ACCOUNT',
      })

      // Logout from Supabase
      const { createClient } = await import('@/lib/supabase/client')
      const supabase = createClient()
      await supabase.auth.signOut()

      // Redirect to signup
      router.push('/signup')
    } catch (error) {
      console.error('Failed to delete account:', error)
      throw error
    }
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
