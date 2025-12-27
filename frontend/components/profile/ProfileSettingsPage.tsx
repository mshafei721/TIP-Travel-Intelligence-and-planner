'use client';

import { useRouter } from 'next/navigation';
import { ProfileSection } from './ProfileSection';
import { TravelerDetailsSection } from './TravelerDetailsSection';
import { TravelPreferencesSection } from './TravelPreferencesSection';
import { SavedTemplatesSection } from './SavedTemplatesSection';
import { NotificationsSection } from './NotificationsSection';
import { PrivacySection } from './PrivacySection';
import { AccountSection } from './AccountSection';
import { useToast } from '@/components/ui/toast';
import type {
  ProfileSettings,
  LegacyUserProfile,
  TravelerDetails,
  TravelPreferences,
  NotificationSettings,
  TripTemplateCreate,
  TripTemplateUpdate,
} from '@/types/profile';
import * as profileApi from '@/lib/api/profile';
import * as templatesApi from '@/lib/api/templates';

export interface ProfileSettingsPageProps {
  initialSettings: ProfileSettings;
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
  const router = useRouter();
  const toast = useToast();

  // Profile update handlers
  const handleProfileUpdate = async (data: Partial<LegacyUserProfile>) => {
    try {
      await profileApi.updateProfile({
        display_name: data.name || undefined,
        avatar_url: data.photoUrl || undefined,
      });
      toast.success('Profile updated successfully');
      router.refresh();
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile. Please try again.');
      throw error;
    }
  };

  const handlePhotoUpload = async (file: File): Promise<string> => {
    try {
      // Upload to Supabase Storage
      const { createClient } = await import('@/lib/supabase/client');
      const supabase = createClient();

      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`;
      const filePath = `avatars/${fileName}`;

      const { error: uploadError } = await supabase.storage
        .from('profile-photos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false,
        });

      if (uploadError) {
        throw new Error(`Upload failed: ${uploadError.message}`);
      }

      // Get public URL
      const {
        data: { publicUrl },
      } = supabase.storage.from('profile-photos').getPublicUrl(filePath);

      // Update profile with new photo URL
      await profileApi.updateProfile({ avatar_url: publicUrl });

      toast.success('Photo uploaded successfully');
      router.refresh();
      return publicUrl;
    } catch (error) {
      console.error('Photo upload failed:', error);
      toast.error('Failed to upload photo. Please try again.');
      throw error;
    }
  };

  const handleTravelerDetailsUpdate = async (data: TravelerDetails) => {
    try {
      await profileApi.updateTravelerProfile({
        nationality: data.nationality,
        residency_country: data.residenceCountry,
        residency_status: data.residencyStatus,
        date_of_birth: data.dateOfBirth || null,
      });
      toast.success('Traveler details updated');
      router.refresh();
    } catch (error) {
      console.error('Failed to update traveler details:', error);
      toast.error('Failed to update traveler details. Please try again.');
      throw error;
    }
  };

  const handlePreferencesUpdate = async (data: TravelPreferences) => {
    try {
      // Update traveler profile with travel preferences
      await profileApi.updateTravelerProfile({
        travel_style: data.travelStyle,
        dietary_restrictions: data.dietaryRestrictions,
        accessibility_needs: data.accessibilityNeeds || null,
      });
      toast.success('Travel preferences updated');
      router.refresh();
    } catch (error) {
      console.error('Failed to update preferences:', error);
      toast.error('Failed to update preferences. Please try again.');
      throw error;
    }
  };

  const handleTemplateCreate = async (template: TripTemplateCreate) => {
    try {
      await templatesApi.createTemplate(template);
      toast.success('Template created successfully');
      router.refresh();
    } catch (error) {
      console.error('Failed to create template:', error);
      toast.error('Failed to create template. Please try again.');
      throw error;
    }
  };

  const handleTemplateEdit = async (id: string, template: TripTemplateUpdate) => {
    try {
      await templatesApi.updateTemplate(id, template);
      toast.success('Template updated successfully');
      router.refresh();
    } catch (error) {
      console.error('Failed to edit template:', error);
      toast.error('Failed to update template. Please try again.');
      throw error;
    }
  };

  const handleTemplateDelete = async (id: string) => {
    try {
      await templatesApi.deleteTemplate(id);
      toast.success('Template deleted');
      router.refresh();
    } catch (error) {
      console.error('Failed to delete template:', error);
      toast.error('Failed to delete template. Please try again.');
      throw error;
    }
  };

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
      });
      toast.success('Notification settings updated');
      router.refresh();
    } catch (error) {
      console.error('Failed to update notifications:', error);
      toast.error('Failed to update notifications. Please try again.');
      throw error;
    }
  };

  const handleAccountDelete = async () => {
    try {
      await profileApi.deleteAccount({
        confirmation: 'DELETE MY ACCOUNT',
      });

      toast.info('Account deleted. Redirecting...');

      // Logout from Supabase
      const { createClient } = await import('@/lib/supabase/client');
      const supabase = createClient();
      await supabase.auth.signOut();

      // Redirect to signup
      router.push('/signup');
    } catch (error) {
      console.error('Failed to delete account:', error);
      toast.error('Failed to delete account. Please try again.');
      throw error;
    }
  };

  const handleChangePassword = () => {
    router.push('/change-password');
  };

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
  );
}
