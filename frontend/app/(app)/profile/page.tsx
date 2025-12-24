import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { ProfileSettingsPage } from '@/components/profile/ProfileSettingsPage'
import type { ProfileSettings } from '@/types/profile'

/**
 * Profile Settings Page (Server Component)
 *
 * Features:
 * - Server-side authentication check
 * - Fetches user profile and settings from Supabase
 * - Renders profile settings UI with all sections
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

  // Fetch user profile
  const { data: profileData, error: profileError } = await (supabase
    .from('user_profiles')
    .select('*')
    .eq('id', user.id)
    .single() as any)

  if (profileError) {
    console.error('Error fetching profile:', profileError)
    throw new Error('Failed to load profile')
  }

  // Fetch traveler profile (if exists)
  const { data: travelerData } = await (supabase
    .from('traveler_profiles')
    .select('*')
    .eq('user_id', user.id)
    .single() as any)

  // Fetch trip templates
  const { data: templatesData } = await (supabase
    .from('trip_templates')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false }) as any)

  // Construct profile settings
  const profileSettings: ProfileSettings = {
    profile: {
      id: profileData.id,
      name: profileData.name || '',
      email: user.email || '',
      photoUrl: profileData.photo_url,
      authProvider: user.app_metadata?.provider === 'google' ? 'google' : 'email',
      createdAt: profileData.created_at,
      updatedAt: profileData.updated_at,
    },
    travelerDetails: {
      nationality: travelerData?.nationality || '',
      residenceCountry: travelerData?.residence_country || '',
      residencyStatus: travelerData?.residency_status || 'citizen',
      dateOfBirth: travelerData?.date_of_birth || '',
    },
    travelPreferences: {
      travelStyle: travelerData?.travel_style || 'balanced',
      dietaryRestrictions: travelerData?.dietary_restrictions || [],
      accessibilityNeeds: travelerData?.accessibility_needs,
    },
    notifications: {
      deletionReminders: profileData.notification_deletion_reminders ?? true,
      reportCompletion: profileData.notification_report_completion ?? true,
      productUpdates: profileData.notification_product_updates ?? false,
    },
    privacy: {
      dataRetentionAcknowledged: profileData.data_retention_acknowledged ?? false,
      allowAnalytics: profileData.allow_analytics ?? true,
    },
    templates: (templatesData || []).map((t: any) => ({
      id: t.id,
      name: t.name,
      destinations: t.destinations,
      datePattern: t.date_pattern,
      preferences: {
        travelStyle: t.travel_style,
        dietaryRestrictions: t.dietary_restrictions || [],
      },
      createdAt: t.created_at,
      updatedAt: t.updated_at,
    })),
  }

  return <ProfileSettingsPage initialSettings={profileSettings} />
}
