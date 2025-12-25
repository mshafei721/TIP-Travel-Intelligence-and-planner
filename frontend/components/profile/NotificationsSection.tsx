'use client'

import { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { SectionCard } from './SectionCard'
import { useDebounce } from '@/hooks/useDebounce'
import type { NotificationSettings, SaveState } from '@/types/profile'

const NOTIFICATION_OPTIONS = [
  {
    key: 'deletionReminders' as keyof NotificationSettings,
    label: 'Deletion Reminders',
    description: 'Email notifications before your trip data is automatically deleted (7 days after trip end date)',
  },
  {
    key: 'reportCompletion' as keyof NotificationSettings,
    label: 'Report Completion',
    description: 'Email when your travel intelligence report is ready to view',
  },
  {
    key: 'productUpdates' as keyof NotificationSettings,
    label: 'Product Updates',
    description: 'Occasional emails about new features and product improvements',
  },
]

export interface NotificationsSectionProps {
  notifications: NotificationSettings
  onUpdate: (notifications: NotificationSettings) => Promise<void>
}

/**
 * NotificationsSection - Email notification preferences
 *
 * Three toggles:
 * - Deletion reminders (default: ON)
 * - Report completion (default: ON)
 * - Product updates (default: OFF)
 */
export function NotificationsSection({ notifications, onUpdate }: NotificationsSectionProps) {
  const [settings, setSettings] = useState<NotificationSettings>(notifications)
  const [saveState, setSaveState] = useState<SaveState>('idle')

  const debouncedSettings = useDebounce(settings, 1000)

  // Auto-save when settings change
  useEffect(() => {
    if (JSON.stringify(debouncedSettings) !== JSON.stringify(notifications)) {
      const saveSettings = async () => {
        setSaveState('saving')
        try {
          await onUpdate(debouncedSettings)
          setSaveState('saved')
        } catch {
          setSaveState('error')
        }
      }
      saveSettings()
    }
  }, [debouncedSettings, notifications, onUpdate])

  const toggleNotification = (key: keyof NotificationSettings) => {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <SectionCard
      title="Email Notifications"
      description="Choose which emails you'd like to receive"
      icon={Bell}
      saveState={saveState}
    >
      <div className="space-y-4">
        {NOTIFICATION_OPTIONS.map((option) => (
          <div
            key={option.key}
            className="flex items-start space-x-3 rounded-lg border border-slate-200 p-4 dark:border-slate-800"
          >
            <Checkbox
              id={option.key}
              checked={settings[option.key]}
              onChange={() => toggleNotification(option.key)}
              disabled={saveState === 'saving'}
              className="mt-1"
            />
            <div className="flex-1">
              <Label htmlFor={option.key} className="cursor-pointer font-medium">
                {option.label}
              </Label>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {option.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  )
}
