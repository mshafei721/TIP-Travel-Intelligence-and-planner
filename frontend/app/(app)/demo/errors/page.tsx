'use client';

import { ErrorBanner } from '@/components/ui/ErrorBanner';
import { useToast } from '@/components/ui/toast';
import { useState } from 'react';

export default function ErrorsDemoPage() {
  const toast = useToast();
  const [showBanners, setShowBanners] = useState({
    error: true,
    warning: true,
    info: true,
    success: true,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <h1 className="mb-2 text-3xl font-bold text-slate-900 dark:text-slate-50">
          Error Banners & Toast Notifications
        </h1>
        <p className="mb-8 text-slate-600 dark:text-slate-400">
          Demo of inline error banners and toast notification system
        </p>

        {/* Inline Error Banners */}
        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-semibold text-slate-900 dark:text-slate-50">
            Inline Error Banners
          </h2>
          <div className="space-y-4">
            {/* Error Banner */}
            {showBanners.error && (
              <ErrorBanner
                variant="error"
                title="Payment Failed"
                message="Your payment could not be processed. Please check your card details and try again."
                dismissible
                onDismiss={() => setShowBanners({ ...showBanners, error: false })}
              />
            )}

            {/* Warning Banner */}
            {showBanners.warning && (
              <ErrorBanner
                variant="warning"
                title="Incomplete Profile"
                message="Please complete your traveler profile to generate accurate trip reports."
                dismissible
                onDismiss={() => setShowBanners({ ...showBanners, warning: false })}
              />
            )}

            {/* Info Banner */}
            {showBanners.info && (
              <ErrorBanner
                variant="info"
                title="Report Generation"
                message="Your trip report is being generated. This usually takes 2-3 minutes."
                dismissible
                onDismiss={() => setShowBanners({ ...showBanners, info: false })}
              />
            )}

            {/* Success Banner */}
            {showBanners.success && (
              <ErrorBanner
                variant="success"
                title="Trip Created"
                message="Your trip has been successfully created and saved as a draft."
                dismissible
                onDismiss={() => setShowBanners({ ...showBanners, success: false })}
              />
            )}

            {/* Simple Error (no title) */}
            <ErrorBanner
              variant="error"
              message="This is a simple error message without a title."
            />

            {/* Non-dismissible Warning */}
            <ErrorBanner
              variant="warning"
              message="This warning cannot be dismissed and will remain visible."
              dismissible={false}
            />
          </div>

          <button
            type="button"
            onClick={() =>
              setShowBanners({
                error: true,
                warning: true,
                info: true,
                success: true,
              })
            }
            className="mt-4 rounded-lg bg-slate-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-700"
          >
            Reset Banners
          </button>
        </section>

        {/* Toast Notifications */}
        <section>
          <h2 className="mb-4 text-2xl font-semibold text-slate-900 dark:text-slate-50">
            Toast Notifications
          </h2>
          <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
            Click buttons below to trigger toast notifications. Toasts auto-dismiss after 5 seconds.
          </p>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {/* Success Toast */}
            <button
              type="button"
              onClick={() => toast.success('Trip saved successfully!', 'Success')}
              className="rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-green-700"
            >
              Success Toast
            </button>

            {/* Error Toast */}
            <button
              type="button"
              onClick={() =>
                toast.error('Failed to connect to server. Please try again.', 'Connection Error')
              }
              className="rounded-lg bg-red-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-700"
            >
              Error Toast
            </button>

            {/* Warning Toast */}
            <button
              type="button"
              onClick={() =>
                toast.warning('Some features may not work offline.', 'Limited Connectivity')
              }
              className="rounded-lg bg-amber-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-amber-700"
            >
              Warning Toast
            </button>

            {/* Info Toast */}
            <button
              type="button"
              onClick={() =>
                toast.info('New features are available. Check the changelog.', 'Update Available')
              }
              className="rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700"
            >
              Info Toast
            </button>
          </div>

          <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
            <h3 className="mb-2 font-semibold text-slate-900 dark:text-slate-50">
              Advanced Options
            </h3>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => toast.success('This toast has no title.')}
                className="rounded bg-green-700 px-3 py-2 text-xs font-medium text-white hover:bg-green-800"
              >
                No Title
              </button>
              <button
                type="button"
                onClick={() => toast.error('This toast will not auto-dismiss.', 'Persistent', 0)}
                className="rounded bg-red-700 px-3 py-2 text-xs font-medium text-white hover:bg-red-800"
              >
                No Auto-Dismiss
              </button>
              <button
                type="button"
                onClick={() => toast.info('This toast dismisses in 2 seconds.', 'Quick', 2000)}
                className="rounded bg-blue-700 px-3 py-2 text-xs font-medium text-white hover:bg-blue-800"
              >
                Custom Duration (2s)
              </button>
              <button
                type="button"
                onClick={() => {
                  toast.success('First toast');
                  setTimeout(() => toast.info('Second toast'), 300);
                  setTimeout(() => toast.warning('Third toast'), 600);
                  setTimeout(() => toast.error('Fourth toast'), 900);
                }}
                className="rounded bg-purple-700 px-3 py-2 text-xs font-medium text-white hover:bg-purple-800"
              >
                Multiple Toasts
              </button>
            </div>
          </div>
        </section>

        {/* Usage Examples */}
        <section className="mt-12">
          <h2 className="mb-4 text-2xl font-semibold text-slate-900 dark:text-slate-50">
            Usage Examples
          </h2>
          <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
            <div>
              <h3 className="mb-2 font-mono text-sm font-semibold text-slate-900 dark:text-slate-50">
                ErrorBanner Component
              </h3>
              <pre className="overflow-x-auto rounded bg-slate-100 p-3 text-xs dark:bg-slate-950">
                {`<ErrorBanner
  variant="error"
  title="Payment Failed"
  message="Your payment could not be processed."
  dismissible
  onDismiss={() => console.log('Dismissed')}
/>`}
              </pre>
            </div>

            <div>
              <h3 className="mb-2 font-mono text-sm font-semibold text-slate-900 dark:text-slate-50">
                Toast Hook
              </h3>
              <pre className="overflow-x-auto rounded bg-slate-100 p-3 text-xs dark:bg-slate-950">
                {`const toast = useToast();

// Simple toast
toast.success('Operation completed!');

// With title
toast.error('Failed to save', 'Error');

// Custom duration (ms, 0 for persistent)
toast.warning('Check your internet', 'Warning', 3000);`}
              </pre>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
