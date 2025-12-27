'use client';

import { useState } from 'react';
import {
  RotateCcw,
  AlertTriangle,
  X,
  Loader2,
  History,
  Calendar,
  User,
  Bot,
  Settings,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { TripVersion, TripData } from '@/types/trip-update';

interface RestoreDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  version: TripVersion;
  currentVersion: number;
  onConfirm: () => Promise<void>;
}

const CREATOR_ICONS: Record<string, React.ElementType> = {
  user: User,
  system: Settings,
  ai: Bot,
};

const FIELD_LABELS: Record<string, string> = {
  title: 'Trip Title',
  destination_city: 'Destination City',
  destination_country: 'Destination Country',
  origin_city: 'Origin City',
  departure_date: 'Departure Date',
  return_date: 'Return Date',
  budget: 'Budget',
  currency: 'Currency',
  trip_purpose: 'Trip Purpose',
  party_size: 'Party Size',
  travel_style: 'Travel Style',
  interests: 'Interests',
  dietary_restrictions: 'Dietary Restrictions',
  accessibility_needs: 'Accessibility Needs',
};

/**
 * RestoreDialog - Confirmation dialog for restoring a previous version
 */
export function RestoreDialog({
  open,
  onOpenChange,
  version,
  currentVersion,
  onConfirm,
}: RestoreDialogProps) {
  const [restoring, setRestoring] = useState(false);

  const CreatorIcon = CREATOR_ICONS[version.created_by] || User;

  const handleConfirm = async () => {
    setRestoring(true);
    try {
      await onConfirm();
      onOpenChange(false);
    } finally {
      setRestoring(false);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined || value === '') {
      return 'Not set';
    }
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : 'None';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  // Get key fields to preview
  const previewFields = [
    'title',
    'destination_city',
    'destination_country',
    'departure_date',
    'return_date',
    'budget',
    'trip_purpose',
    'travel_style',
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-blue-600" />
            Restore Version {version.version_number}
          </DialogTitle>
          <DialogDescription>
            This will restore your trip to a previous state. A new version will be created to
            preserve your current changes.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Warning */}
          <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-amber-800 dark:text-amber-200">Important</h4>
                <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                  Restoring to version {version.version_number} will revert all trip details to that
                  point. Your current version (v{currentVersion}) will remain in history if you need
                  to restore it later.
                </p>
              </div>
            </div>
          </div>

          {/* Version Info */}
          <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">Version {version.version_number}</Badge>
                  <span className="text-sm text-slate-500">{version.change_summary}</span>
                </div>
                <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <CreatorIcon className="h-3 w-3" />
                    {version.created_by === 'user'
                      ? 'Manual Edit'
                      : version.created_by === 'ai'
                        ? 'AI Recalculation'
                        : 'System'}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(version.created_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* Changed Fields in This Version */}
            {version.changed_fields.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                <span className="text-xs font-medium text-slate-500">
                  Fields changed in this version:
                </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {version.changed_fields.map((field) => (
                    <Badge key={field} variant="outline" className="text-xs">
                      {field.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Preview of Values */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg divide-y divide-slate-200 dark:divide-slate-800">
            <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800/50">
              <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Values to Restore
              </h4>
            </div>
            {previewFields.map((field) => {
              const value = version.snapshot[field as keyof TripData];
              if (value === undefined) return null;

              return (
                <div key={field} className="px-4 py-2 flex justify-between">
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    {FIELD_LABELS[field] || field}
                  </span>
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {field.includes('date')
                      ? new Date(value as string).toLocaleDateString()
                      : field === 'budget'
                        ? `${version.snapshot.currency} ${Number(value).toLocaleString()}`
                        : formatValue(value)}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Recalculation Notice */}
          <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900 rounded-lg p-3">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              After restoring, you may want to trigger AI recalculation to update your travel report
              with the restored values.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={restoring}>
            <X className="h-4 w-4 mr-1" />
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={restoring}>
            {restoring ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Restoring...
              </>
            ) : (
              <>
                <RotateCcw className="h-4 w-4 mr-1" />
                Restore Version
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default RestoreDialog;
