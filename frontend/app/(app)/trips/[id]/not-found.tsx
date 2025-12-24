import Link from 'next/link';
import { FileQuestion } from 'lucide-react';

export default function TripNotFound() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center space-y-6">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-20 h-20 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
            <FileQuestion className="text-slate-400 dark:text-slate-600" size={40} />
          </div>
        </div>

        {/* Content */}
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Trip Not Found
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            The trip report you're looking for doesn't exist or has been deleted.
          </p>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/dashboard"
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/trips/new"
            className="px-6 py-2 border-2 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg font-semibold transition-colors"
          >
            Create New Trip
          </Link>
        </div>
      </div>
    </div>
  );
}
