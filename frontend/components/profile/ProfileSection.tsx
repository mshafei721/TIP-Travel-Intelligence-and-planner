'use client';

import { useState, useEffect } from 'react';
import { User, Chrome, Mail } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { SectionCard } from './SectionCard';
import { ProfilePhotoUpload } from './ProfilePhotoUpload';
import { useDebounce } from '@/hooks/useDebounce';
import type { LegacyUserProfile, SaveState } from '@/types/profile';

export interface ProfileSectionProps {
  profile: LegacyUserProfile;
  onProfileUpdate: (data: Partial<LegacyUserProfile>) => Promise<void>;
  onPhotoUpload: (file: File) => Promise<string>;
  onChangePassword?: () => void;
}

/**
 * ProfileSection - Main profile information management
 *
 * Handles:
 * - Name editing with auto-save
 * - Email display (read-only with provider icon)
 * - Profile photo upload
 * - Change password link (email/password auth only)
 */
export function ProfileSection({
  profile,
  onProfileUpdate,
  onPhotoUpload,
  onChangePassword,
}: ProfileSectionProps) {
  const [name, setName] = useState(profile.name);
  const [saveState, setSaveState] = useState<SaveState>('idle');

  const debouncedName = useDebounce(name, 1500);

  // Auto-save name changes
  useEffect(() => {
    if (debouncedName !== profile.name && debouncedName.trim() !== '') {
      const saveName = async () => {
        setSaveState('saving');
        try {
          await onProfileUpdate({ name: debouncedName });
          setSaveState('saved');
        } catch {
          setSaveState('error');
        }
      };
      saveName();
    }
  }, [debouncedName, profile.name, onProfileUpdate]);

  const showChangePassword = profile.authProvider === 'email' && onChangePassword;

  return (
    <SectionCard
      title="Profile Information"
      description="Manage your personal details and photo"
      icon={User}
      saveState={saveState}
    >
      <div className="grid gap-6 md:grid-cols-[auto,1fr]">
        {/* Photo Upload */}
        <div>
          <ProfilePhotoUpload
            currentPhotoUrl={profile.photoUrl}
            onUpload={onPhotoUpload}
            maxSizeMB={5}
          />
        </div>

        {/* Profile Fields */}
        <div className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="profile-name">Name</Label>
            <Input
              id="profile-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your full name"
              disabled={saveState === 'saving'}
            />
          </div>

          {/* Email (read-only with provider icon) */}
          <div className="space-y-2">
            <Label htmlFor="profile-email">Email</Label>
            <div className="relative">
              <Input id="profile-email" value={profile.email} disabled readOnly className="pr-10" />
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                {profile.authProvider === 'google' ? (
                  <Chrome className="h-4 w-4 text-slate-400" aria-label="Google account" />
                ) : (
                  <Mail className="h-4 w-4 text-slate-400" aria-label="Email account" />
                )}
              </div>
            </div>
            {profile.authProvider === 'google' && (
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Managed by Google account
              </p>
            )}
          </div>

          {/* Change Password (email/password only) */}
          {showChangePassword && (
            <div>
              <Button variant="outline" size="sm" onClick={onChangePassword} className="mt-2">
                Change Password
              </Button>
            </div>
          )}
        </div>
      </div>
    </SectionCard>
  );
}
