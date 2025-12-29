import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { ProfileSettingsPage } from '@/components/profile/ProfileSettingsPage';
import { ProfileError } from '@/components/profile/ProfileError';
import { serverApiRequest } from '@/lib/api/auth-utils.server';
import type {
  ProfileSettings,
  TravelerDetails,
  ProfileResponse,
  TripTemplate,
} from '@/types/profile';

/**
 * Profile Settings Page (Server Component)
 *
 * Features:
 * - Server-side authentication check
 * - Fetches user profile from FastAPI backend
 * - Renders profile settings UI with all sections
 *
 * Note: This page uses the ProfileSettings adapter for backwards compatibility.
 * New pages should use the ProfileResponse type directly.
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
    // Fetch profile and templates from backend API using server-side auth
    const [profileResponse, templatesResponse] = await Promise.all([
      serverApiRequest<ProfileResponse>('/api/profile'),
      serverApiRequest<{ templates: TripTemplate[] }>('/api/templates'),
    ]);
    const templates = templatesResponse.templates;

    const residencyStatus = profileResponse.travelerProfile?.residency_status;
    const normalizedResidencyStatus: TravelerDetails['residencyStatus'] =
      residencyStatus === 'citizen' ||
      residencyStatus === 'permanent_resident' ||
      residencyStatus === 'temporary_resident' ||
      residencyStatus === 'visitor'
        ? residencyStatus
        : 'citizen';

    // Map API response to ProfileSettings type for existing components
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
        residencyStatus: normalizedResidencyStatus,
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
      templates,
    };

    return <ProfileSettingsPage initialSettings={profileSettings} />;
  } catch (error) {
    console.error('Error fetching profile:', error);
    return <ProfileError />;
  }
}
