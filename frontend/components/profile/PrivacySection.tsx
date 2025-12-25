import { Shield, ExternalLink } from 'lucide-react';
import { SectionCard } from './SectionCard';

/**
 * PrivacySection - Privacy policy and data retention information
 *
 * Displays:
 * - Data deletion policy (7-day auto-deletion)
 * - Link to full privacy policy
 */
export function PrivacySection() {
  return (
    <SectionCard
      title="Privacy & Data"
      description="How we handle your personal information"
      icon={Shield}
    >
      <div className="space-y-4">
        {/* Auto-Deletion Policy */}
        <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-950/20">
          <h3 className="font-medium text-blue-900 dark:text-blue-100">Automatic Data Deletion</h3>
          <p className="mt-2 text-sm text-blue-800 dark:text-blue-200">
            Your trip data is automatically deleted <strong>7 days after your trip end date</strong>{' '}
            to protect your privacy. You&apos;ll receive email reminders before deletion if enabled
            in notification settings.
          </p>
        </div>

        {/* Privacy Policy Link */}
        <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4 dark:border-slate-800">
          <div>
            <h3 className="font-medium text-slate-900 dark:text-slate-50">Full Privacy Policy</h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Read our complete privacy policy and data handling practices
            </p>
          </div>
          <a
            href="/privacy-policy"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            View Policy
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </SectionCard>
  );
}
