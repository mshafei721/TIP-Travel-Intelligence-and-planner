'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTheme } from 'next-themes';
import {
  Palette,
  Bell,
  Shield,
  Bot,
  Download,
  Loader2,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { SettingsSection, SettingsToggle, SettingsSelect } from '@/components/settings';
import { getAllSettings, updateAllSettings, requestDataExport } from '@/lib/api/settings';
import { useToast } from '@/components/ui/toast';
import type {
  UserSettings,
  AppearanceSettingsUpdate,
  NotificationSettingsUpdate,
  PrivacySettingsUpdate,
  AIPreferencesUpdate,
} from '@/types/settings';
import { THEME_OPTIONS, VISIBILITY_OPTIONS, DETAIL_LEVEL_OPTIONS } from '@/types/settings';

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [exportStatus, setExportStatus] = useState<'idle' | 'exporting' | 'success' | 'error'>(
    'idle',
  );
  const toast = useToast();
  const { setTheme } = useTheme();

  const fetchSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAllSettings();
      setSettings(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const saveSettings = async (updates: {
    appearance?: AppearanceSettingsUpdate;
    notifications?: NotificationSettingsUpdate;
    privacy?: PrivacySettingsUpdate;
    ai_preferences?: AIPreferencesUpdate;
  }) => {
    if (!settings) return;

    // Optimistic update - apply changes immediately
    const previousSettings = settings;
    setSettings((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        appearance: { ...prev.appearance, ...updates.appearance },
        notifications: { ...prev.notifications, ...updates.notifications },
        privacy: { ...prev.privacy, ...updates.privacy },
        ai_preferences: { ...prev.ai_preferences, ...updates.ai_preferences },
      };
    });

    setSaveStatus('saving');
    try {
      const response = await updateAllSettings(updates);
      setSettings(response.data);
      setSaveStatus('saved');
      toast.success('Settings saved successfully');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (err) {
      // Rollback on failure
      setSettings(previousSettings);
      setSaveStatus('error');
      console.error('Failed to save settings:', err);
      toast.error('Failed to save settings. Please try again.');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const handleExportData = async () => {
    setExportStatus('exporting');
    try {
      await requestDataExport('json');
      setExportStatus('success');
      toast.success('Data export initiated! Check your email for the download link.');
      setTimeout(() => setExportStatus('idle'), 3000);
    } catch (err) {
      setExportStatus('error');
      console.error('Failed to export data:', err);
      toast.error('Failed to export data. Please try again.');
      setTimeout(() => setExportStatus('idle'), 3000);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !settings) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-900/20">
        <p className="text-red-700 dark:text-red-400">{error || 'Failed to load settings'}</p>
        <button
          onClick={fetchSettings}
          className="mt-3 rounded-lg bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-400 dark:hover:bg-red-800"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Settings</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Manage your account preferences and customization
          </p>
        </div>

        {/* Save Status Indicator */}
        {saveStatus !== 'idle' && (
          <div className="flex items-center gap-2">
            {saveStatus === 'saving' && (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                <span className="text-sm text-slate-600">Saving...</span>
              </>
            )}
            {saveStatus === 'saved' && (
              <>
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-green-600">Saved</span>
              </>
            )}
            {saveStatus === 'error' && (
              <>
                <AlertCircle className="h-4 w-4 text-red-600" />
                <span className="text-sm text-red-600">Failed to save</span>
              </>
            )}
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Appearance Settings */}
        <SettingsSection
          title="Appearance"
          description="Customize the look and feel of the app"
          icon={Palette}
        >
          <SettingsSelect
            label="Theme"
            description="Choose your preferred color scheme"
            value={settings.appearance.theme}
            options={THEME_OPTIONS}
            onChange={(theme) => {
              setTheme(theme); // Apply theme immediately
              saveSettings({ appearance: { theme: theme as 'light' | 'dark' | 'system' } });
            }}
          />
          <SettingsToggle
            label="Compact Mode"
            description="Use a more condensed layout"
            checked={settings.appearance.compact_mode}
            onChange={(compact_mode) => saveSettings({ appearance: { compact_mode } })}
          />
          <SettingsToggle
            label="Show Animations"
            description="Enable UI animations and transitions"
            checked={settings.appearance.show_animations}
            onChange={(show_animations) => saveSettings({ appearance: { show_animations } })}
          />
          <SettingsSelect
            label="Font Size"
            description="Adjust the text size"
            value={settings.appearance.font_size}
            options={[
              { value: 'small', label: 'Small' },
              { value: 'medium', label: 'Medium' },
              { value: 'large', label: 'Large' },
            ]}
            onChange={(font_size) =>
              saveSettings({ appearance: { font_size: font_size as 'small' | 'medium' | 'large' } })
            }
          />
        </SettingsSection>

        {/* Notification Settings */}
        <SettingsSection
          title="Notifications"
          description="Control how you receive updates"
          icon={Bell}
        >
          <SettingsToggle
            label="Trip Updates"
            description="Get notified about changes to your trips"
            checked={settings.notifications.email_trip_updates}
            onChange={(email_trip_updates) =>
              saveSettings({ notifications: { email_trip_updates } })
            }
          />
          <SettingsToggle
            label="Report Ready"
            description="Notify when AI reports are complete"
            checked={settings.notifications.email_report_ready}
            onChange={(email_report_ready) =>
              saveSettings({ notifications: { email_report_ready } })
            }
          />
          <SettingsToggle
            label="Weekly Digest"
            description="Receive a weekly summary of your activity"
            checked={settings.notifications.email_weekly_digest}
            onChange={(email_weekly_digest) =>
              saveSettings({ notifications: { email_weekly_digest } })
            }
          />
          <SettingsToggle
            label="Marketing Emails"
            description="Receive news, tips, and promotional content"
            checked={settings.notifications.email_marketing}
            onChange={(email_marketing) => saveSettings({ notifications: { email_marketing } })}
          />
          <SettingsToggle
            label="Trip Reminders"
            description="Push notifications for upcoming trips"
            checked={settings.notifications.push_trip_reminders}
            onChange={(push_trip_reminders) =>
              saveSettings({ notifications: { push_trip_reminders } })
            }
          />
          <SettingsToggle
            label="Agent Completion"
            description="Notify when AI agents complete tasks"
            checked={settings.notifications.push_agent_completion}
            onChange={(push_agent_completion) =>
              saveSettings({ notifications: { push_agent_completion } })
            }
          />
        </SettingsSection>

        {/* Privacy Settings */}
        <SettingsSection
          title="Privacy"
          description="Control your data and visibility"
          icon={Shield}
        >
          <SettingsSelect
            label="Profile Visibility"
            description="Who can see your profile"
            value={settings.privacy.profile_visibility}
            options={VISIBILITY_OPTIONS}
            onChange={(profile_visibility) =>
              saveSettings({
                privacy: {
                  profile_visibility: profile_visibility as 'public' | 'private' | 'friends_only',
                },
              })
            }
          />
          <SettingsToggle
            label="Show Travel History"
            description="Display your past trips on your profile"
            checked={settings.privacy.show_travel_history}
            onChange={(show_travel_history) => saveSettings({ privacy: { show_travel_history } })}
          />
          <SettingsToggle
            label="Share Recommendations"
            description="Allow sharing AI recommendations with others"
            checked={settings.privacy.allow_recommendations_sharing}
            onChange={(allow_recommendations_sharing) =>
              saveSettings({ privacy: { allow_recommendations_sharing } })
            }
          />
          <SettingsToggle
            label="Analytics"
            description="Help us improve by sharing usage data"
            checked={settings.privacy.analytics_enabled}
            onChange={(analytics_enabled) => saveSettings({ privacy: { analytics_enabled } })}
          />
        </SettingsSection>

        {/* AI Preferences */}
        <SettingsSection
          title="AI Preferences"
          description="Customize AI recommendations"
          icon={Bot}
        >
          <SettingsSelect
            label="Detail Level"
            description="How detailed should AI responses be"
            value={settings.ai_preferences.detail_level}
            options={DETAIL_LEVEL_OPTIONS}
            onChange={(detail_level) =>
              saveSettings({
                ai_preferences: {
                  detail_level: detail_level as 'minimal' | 'standard' | 'detailed',
                },
              })
            }
          />
          <SettingsToggle
            label="Budget Suggestions"
            description="Include budget recommendations"
            checked={settings.ai_preferences.include_budget_suggestions}
            onChange={(include_budget_suggestions) =>
              saveSettings({ ai_preferences: { include_budget_suggestions } })
            }
          />
          <SettingsToggle
            label="Local Tips"
            description="Include local insider tips and recommendations"
            checked={settings.ai_preferences.include_local_tips}
            onChange={(include_local_tips) =>
              saveSettings({ ai_preferences: { include_local_tips } })
            }
          />
        </SettingsSection>
      </div>

      {/* Data Export Section */}
      <SettingsSection
        title="Data & Privacy"
        description="Download or delete your data"
        icon={Download}
      >
        <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <div>
            <p className="font-medium text-slate-900 dark:text-slate-100">Export Your Data</p>
            <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
              Download a copy of all your data in JSON format
            </p>
          </div>
          <button
            onClick={handleExportData}
            disabled={exportStatus === 'exporting'}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {exportStatus === 'exporting' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Exporting...
              </>
            ) : exportStatus === 'success' ? (
              <>
                <CheckCircle className="h-4 w-4" />
                Requested!
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export Data
              </>
            )}
          </button>
        </div>
      </SettingsSection>
    </div>
  );
}
