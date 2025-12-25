import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { ProfileSettingsPage } from '@/components/profile/ProfileSettingsPage'
import { getProfile, getStatistics } from '@/lib/api/profile'
import type { ProfileSettings } from '@/types/profile'

/**
 * Profile Settings Page (Server Component)
 *
 * Features:
 * - Server-side authentication check
 * - Fetches user profile from FastAPI backend
 * - Renders profile settings UI with all sections
 *
 * Note: This page uses the legacy ProfileSettings type for backwards compatibility
 * with existing components. New pages should use the ProfileResponse type.
 */
export default async function ProfilePage() {
  const supabase = await createClient()

  // Check authentication
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser()

  if (authError || !user) {
    redirect('/login')
  }

  try {
    // Fetch profile from backend API
    const profileResponse = await getProfile()
    const statistics = await getStatistics()

    // Map new API response to legacy ProfileSettings type for existing components
    const profileSettings: ProfileSettings = {
      profile: {
        id: profileResponse.user.id,
        name: profileResponse.user.display_name || '',
        email: user.email || '',
        photoUrl: profileResponse.user.avatar_url,
        authProvider: user.app_metadata?.provider === 'google' ? 'google' : 'email',
        createdAt: profileResponse.user.created_at,
        updatedAt: profileResponse.user.updated_at,
      },
      travelerDetails: {
        nationality: profileResponse.travelerProfile?.nationality || '',
        residenceCountry: profileResponse.travelerProfile?.residency_country || '',
        residencyStatus: (profileResponse.travelerProfile?.residency_status as any) || 'citizen',
        dateOfBirth: profileResponse.travelerProfile?.date_of_birth || '',
      },
      travelPreferences: {
        travelStyle: profileResponse.travelerProfile?.travel_style || 'balanced',
        dietaryRestrictions: profileResponse.travelerProfile?.dietary_restrictions || [],
        accessibilityNeeds: profileResponse.travelerProfile?.accessibility_needs || undefined,
      },
      notifications: {
        deletionReminders: true, // Default until backend supports this
        reportCompletion: profileResponse.user.preferences?.email_notifications ?? true,
        productUpdates: profileResponse.user.preferences?.marketing_emails ?? false,
      },
      privacy: {
        dataRetentionAcknowledged: false, // TODO: Add to backend
        allowAnalytics: true, // TODO: Add to backend
      },
      templates: [], // TODO: Fetch from backend when template API is ready
    }

    return <ProfileSettingsPage initialSettings={profileSettings} />
  } catch (error) {
    console.error('Error fetching profile:', error)
    throw new Error('Failed to load profile. Please try again later.')
  }
}
