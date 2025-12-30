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

    const residencyStatus = profileResponse.travelerProfile?.residencyStatus;
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
        name: profileResponse.user.displayName || '',
        email: user.email || '',
        photoUrl: profileResponse.user.avatarUrl ?? undefined,
        authProvider: user.app_metadata?.provider === 'google' ? 'google' : 'email',
        createdAt: profileResponse.user.createdAt,
        updatedAt: profileResponse.user.updatedAt,
      },
      travelerDetails: {
        nationality: profileResponse.travelerProfile?.nationality || '',
        residenceCountry: profileResponse.travelerProfile?.residencyCountry || '',
        residencyStatus: normalizedResidencyStatus,
        dateOfBirth: profileResponse.travelerProfile?.dateOfBirth || '',
      },
      travelPreferences: {
        travelStyle: profileResponse.travelerProfile?.travelStyle || 'balanced',
        dietaryRestrictions: profileResponse.travelerProfile?.dietaryRestrictions || [],
        accessibilityNeeds: profileResponse.travelerProfile?.accessibilityNeeds || undefined,
      },
      notifications: {
        deletionReminders: true, // Default until backend supports this
        reportCompletion: profileResponse.user.preferences?.emailNotifications ?? true,
        productUpdates: profileResponse.user.preferences?.marketingEmails ?? false,
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
