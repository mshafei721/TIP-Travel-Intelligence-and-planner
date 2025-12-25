'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-slate-900 dark:text-slate-100">500</h1>
        <h2 className="mt-4 text-2xl font-semibold text-slate-700 dark:text-slate-300">
          Something went wrong
        </h2>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          An unexpected error occurred. Please try again.
        </p>
        <button
          onClick={reset}
          className="mt-6 inline-block rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
