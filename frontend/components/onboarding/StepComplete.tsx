'use client';

import { CheckCircle, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface StepCompleteProps {
  onComplete: () => void;
  isLoading?: boolean;
}

export function StepComplete({ onComplete, isLoading }: StepCompleteProps) {
  return (
    <div className="flex flex-col items-center text-center">
      {/* Success Icon */}
      <div className="relative mb-6">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
          <CheckCircle className="h-10 w-10 text-green-600 dark:text-green-400" />
        </div>
        <div className="absolute -right-1 -top-1 flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/30">
          <Sparkles className="h-4 w-4 text-amber-600 dark:text-amber-400" />
        </div>
      </div>

      {/* Success Message */}
      <h2 className="mb-3 text-2xl font-bold text-slate-900 dark:text-white">
        You&apos;re All Set!
      </h2>
      <p className="mb-8 max-w-md text-lg text-slate-600 dark:text-slate-400">
        Your travel profile is complete. You can now create trips with personalized visa
        requirements and recommendations.
      </p>

      {/* What's Next */}
      <div className="mb-8 w-full max-w-md rounded-lg border border-slate-200 bg-slate-50 p-6 dark:border-slate-700 dark:bg-slate-800/50">
        <h3 className="mb-4 font-semibold text-slate-900 dark:text-white">What you can do now:</h3>
        <ul className="space-y-3 text-left">
          <li className="flex items-start gap-3">
            <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400">1</span>
            </div>
            <span className="text-slate-600 dark:text-slate-400">
              Create your first trip with AI-powered planning
            </span>
          </li>
          <li className="flex items-start gap-3">
            <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400">2</span>
            </div>
            <span className="text-slate-600 dark:text-slate-400">
              Get accurate visa requirements for any destination
            </span>
          </li>
          <li className="flex items-start gap-3">
            <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400">3</span>
            </div>
            <span className="text-slate-600 dark:text-slate-400">
              Receive personalized destination recommendations
            </span>
          </li>
        </ul>
      </div>

      {/* CTA */}
      <Button
        onClick={onComplete}
        disabled={isLoading}
        size="lg"
        className="w-full max-w-md bg-blue-600 hover:bg-blue-700"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Saving...
          </span>
        ) : (
          <>
            Start Exploring
            <ArrowRight className="ml-2 h-4 w-4" />
          </>
        )}
      </Button>

      <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
        You can update these settings anytime in your profile
      </p>
    </div>
  );
}
