'use client';

import { useState } from 'react';
import { AlertTriangle, Loader2, X } from 'lucide-react';

interface DeleteTripDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  tripName: string;
  tripId: string;
}

export function DeleteTripDialog({
  isOpen,
  onClose,
  onConfirm,
  tripName,
  tripId,
}: DeleteTripDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [error, setError] = useState<string | null>(null);

  const isConfirmValid = confirmText.toLowerCase() === 'delete';

  const handleConfirm = async () => {
    if (!isConfirmValid || isDeleting) return;

    try {
      setIsDeleting(true);
      setError(null);
      await onConfirm();
      // Dialog will close via onClose after successful deletion
    } catch (err) {
      console.error('Failed to delete trip:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete trip');
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    if (isDeleting) return; // Prevent closing while deleting
    setConfirmText('');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div
        className="bg-white dark:bg-slate-900 rounded-xl shadow-2xl max-w-md w-full border-2 border-red-200 dark:border-red-800"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-950/50 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Delete Trip
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                This action cannot be undone
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isDeleting}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Close dialog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Warning Message */}
          <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-sm text-red-900 dark:text-red-200">
              <strong>Warning:</strong> Deleting this trip will permanently remove all associated
              data, including:
            </p>
            <ul className="mt-2 text-sm text-red-800 dark:text-red-300 list-disc list-inside space-y-1">
              <li>Visa intelligence reports</li>
              <li>Destination intelligence data</li>
              <li>Travel itinerary and activities</li>
              <li>Flight information</li>
              <li>All generated PDFs and exports</li>
            </ul>
          </div>

          {/* Trip Info */}
          <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
            <div className="text-xs text-slate-600 dark:text-slate-400 mb-1">Trip to delete:</div>
            <div className="font-medium text-slate-900 dark:text-slate-100">{tripName}</div>
            <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">
              ID: {tripId.slice(0, 8)}
            </div>
          </div>

          {/* Confirmation Input */}
          <div>
            <label
              htmlFor="confirm-delete"
              className="block text-sm font-medium text-slate-900 dark:text-slate-100 mb-2"
            >
              Type{' '}
              <span className="font-mono font-semibold text-red-600 dark:text-red-400">DELETE</span>{' '}
              to confirm:
            </label>
            <input
              id="confirm-delete"
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              disabled={isDeleting}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Type DELETE"
              autoComplete="off"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 rounded-b-xl">
          <button
            onClick={handleClose}
            disabled={isDeleting}
            className="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isConfirmValid || isDeleting}
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-red-600 hover:bg-red-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:cursor-not-allowed transition-colors inline-flex items-center gap-2"
          >
            {isDeleting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <AlertTriangle className="h-4 w-4" />
                Delete Trip
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
