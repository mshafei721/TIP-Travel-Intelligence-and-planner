import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { ProfileSettingsPage } from '@/components/profile/ProfileSettingsPage';
import { getProfile } from '@/lib/api/profile';
import { listTemplates } from '@/lib/api/templates';
import type { ProfileSettings, TravelStyle } from '@/types/profile';

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
  const supabase = await createClient();

  // Check authentication
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    redirect('/login');
  }

  try {
    // Fetch profile and templates from backend API
    const [profileResponse, templates] = await Promise.all([getProfile(), listTemplates()]);

    // Map new API response to legacy ProfileSettings type for existing components
    const profileSettings: ProfileSettings = {
      profile: {
        id: profileResponse.user.id,
        name: profileResponse.user.display_name || '',
        email: user.email || '',
        photoUrl: profileResponse.user.avatar_url ?? undefined,
        authProvider: user.app_metadata?.provider === 'google' ? 'google' : 'email',
        createdAt: profileResponse.user.created_at,
        updatedAt: profileResponse.user.updated_at,
      },
      travelerDetails: {
        nationality: profileResponse.travelerProfile?.nationality || '',
        residenceCountry: profileResponse.travelerProfile?.residency_country || '',
        residencyStatus: (profileResponse.travelerProfile?.residency_status as string) || 'citizen',
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
      templates: templates.map((template) => ({
        // Map backend template to legacy frontend format
        id: template.id,
        name: template.name,
        destinations: template.destinations.map((d) =>
          d.city ? `${d.city}, ${d.country}` : d.country,
        ),
        datePattern: template.description || 'Custom trip',
        preferences: {
          travelStyle: (template.preferences?.travel_style || 'balanced') as TravelStyle,
          dietaryRestrictions: template.preferences?.dietary_restrictions || [],
          accessibilityNeeds: template.preferences?.accessibility_needs,
        },
        createdAt: template.created_at,
        updatedAt: template.updated_at,
      })),
    };

    return <ProfileSettingsPage initialSettings={profileSettings} />;
  } catch (error) {
    console.error('Error fetching profile:', error);
    throw new Error('Failed to load profile. Please try again later.');
  }
}
