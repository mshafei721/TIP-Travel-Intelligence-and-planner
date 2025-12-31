'use client';

import * as React from 'react';
import { useState, useCallback } from 'react';
import { Bug, Lightbulb, Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { trackFeedbackSubmitted } from '@/lib/analytics';
import * as Sentry from '@sentry/nextjs';

type FeedbackType = 'bug' | 'feature';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultType?: FeedbackType;
  // Optional context from error screens
  errorContext?: {
    sentryEventId?: string;
    errorMessage?: string;
  };
}

interface FeedbackFormData {
  type: FeedbackType;
  title: string;
  description: string;
  email: string;
}

type SubmitStatus = 'idle' | 'loading' | 'success' | 'error';

export function FeedbackModal({
  isOpen,
  onClose,
  defaultType = 'bug',
  errorContext,
}: FeedbackModalProps) {
  const [formData, setFormData] = useState<FeedbackFormData>({
    type: defaultType,
    title: '',
    description: errorContext?.errorMessage
      ? `Error: ${errorContext.errorMessage}\n\nSteps to reproduce:\n1. `
      : '',
    email: '',
  });
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleTypeChange = (type: FeedbackType) => {
    setFormData((prev) => ({ ...prev, type }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const resetForm = useCallback(() => {
    setFormData({
      type: defaultType,
      title: '',
      description: '',
      email: '',
    });
    setSubmitStatus('idle');
    setErrorMessage('');
  }, [defaultType]);

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!formData.title.trim()) {
      setErrorMessage('Please provide a title');
      return;
    }
    if (!formData.description.trim()) {
      setErrorMessage('Please provide a description');
      return;
    }

    setSubmitStatus('loading');
    setErrorMessage('');

    try {
      // Get current route
      const route = typeof window !== 'undefined' ? window.location.pathname : '';

      // Get app context
      const appContext = {
        route,
        app_release: process.env.NEXT_PUBLIC_SENTRY_RELEASE || 'unknown',
        browser: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
        posthog_id:
          typeof window !== 'undefined'
            ? (
                window as unknown as { posthog?: { get_distinct_id: () => string } }
              ).posthog?.get_distinct_id?.()
            : undefined,
        sentry_event_id: errorContext?.sentryEventId,
      };

      // Submit to backend API
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: formData.type,
          title: formData.title,
          description: formData.description,
          email: formData.email || undefined,
          ...appContext,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }

      // Track in PostHog
      trackFeedbackSubmitted({
        type: formData.type,
        has_attachment: false,
        route,
      });

      // Also send to Sentry as user feedback
      if (errorContext?.sentryEventId) {
        Sentry.captureFeedback({
          name: formData.email || 'Anonymous',
          message: `${formData.title}\n\n${formData.description}`,
          associatedEventId: errorContext.sentryEventId,
        });
      }

      setSubmitStatus('success');

      // Auto-close after success
      setTimeout(() => {
        handleClose();
      }, 2000);
    } catch (error) {
      console.error('Feedback submission failed:', error);
      setErrorMessage('Failed to submit feedback. Please try again.');
      setSubmitStatus('error');

      // Capture error in Sentry
      Sentry.captureException(error, {
        tags: { component: 'FeedbackModal' },
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Send Feedback</DialogTitle>
          <DialogDescription>
            Help us improve TIP by reporting bugs or suggesting features.
          </DialogDescription>
        </DialogHeader>

        {submitStatus === 'success' ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              Thank you for your feedback!
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
              We appreciate you taking the time to help us improve.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Type Selection */}
            <div className="space-y-2">
              <Label>What type of feedback is this?</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant={formData.type === 'bug' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => handleTypeChange('bug')}
                >
                  <Bug className="h-4 w-4 mr-2" />
                  Bug Report
                </Button>
                <Button
                  type="button"
                  variant={formData.type === 'feature' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => handleTypeChange('feature')}
                >
                  <Lightbulb className="h-4 w-4 mr-2" />
                  Feature Request
                </Button>
              </div>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">
                Title <span className="text-red-500">*</span>
              </Label>
              <Input
                id="title"
                name="title"
                placeholder={
                  formData.type === 'bug'
                    ? 'Brief description of the issue'
                    : 'Brief description of your idea'
                }
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">
                Description <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="description"
                name="description"
                placeholder={
                  formData.type === 'bug'
                    ? 'Steps to reproduce:\n1. Go to...\n2. Click on...\n3. See error...\n\nExpected behavior:\n\nActual behavior:'
                    : 'Describe the feature you would like to see and how it would help you...'
                }
                value={formData.description}
                onChange={handleInputChange}
                className="min-h-[150px]"
                required
              />
            </div>

            {/* Email (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="email">Email (optional)</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleInputChange}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400">
                If you&apos;d like us to follow up with you about this feedback
              </p>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="flex items-center gap-2 text-red-500 text-sm">
                <AlertCircle className="h-4 w-4" />
                {errorMessage}
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitStatus === 'loading'}>
                {submitStatus === 'loading' ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Submit Feedback
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

// Helper hook for using the feedback modal
export function useFeedbackModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [defaultType, setDefaultType] = useState<FeedbackType>('bug');
  const [errorContext, setErrorContext] = useState<{
    sentryEventId?: string;
    errorMessage?: string;
  }>();

  const openFeedback = useCallback(
    (options?: {
      type?: FeedbackType;
      errorContext?: { sentryEventId?: string; errorMessage?: string };
    }) => {
      if (options?.type) setDefaultType(options.type);
      if (options?.errorContext) setErrorContext(options.errorContext);
      setIsOpen(true);
    },
    [],
  );

  const closeFeedback = useCallback(() => {
    setIsOpen(false);
    setErrorContext(undefined);
  }, []);

  return {
    isOpen,
    openFeedback,
    closeFeedback,
    defaultType,
    errorContext,
  };
}
