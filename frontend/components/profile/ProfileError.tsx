'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';

export function ProfileError() {
  const router = useRouter();

  const handleRetry = () => {
    router.refresh();
  };

  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center dark:border-red-900 dark:bg-red-950/30">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/50">
          <svg
            className="h-6 w-6 text-red-600 dark:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h2 className="mb-2 text-lg font-semibold text-red-900 dark:text-red-100">
          Failed to load profile
        </h2>
        <p className="mb-4 text-sm text-red-700 dark:text-red-300">
          We couldn&apos;t load your profile settings. Please check your connection and try again.
        </p>
        <Button
          onClick={handleRetry}
          variant="outline"
          className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-900/50"
        >
          Try Again
        </Button>
      </div>
    </div>
  );
}
