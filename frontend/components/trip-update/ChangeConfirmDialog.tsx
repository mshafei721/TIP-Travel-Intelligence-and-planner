'use client';

import { useState } from 'react';
import { AlertTriangle, Save, X, Loader2, RefreshCw } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ChangePreview } from './ChangePreview';
import { AffectedSections } from './AffectedSections';
import type { ChangePreviewData, ReportSectionId } from '@/types/trip-update';

interface ChangeConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  preview: ChangePreviewData;
  onConfirm: (options: { triggerRecalculation: boolean }) => Promise<void>;
  tripName?: string;
}

/**
 * ChangeConfirmDialog - Confirmation dialog for applying changes
 */
export function ChangeConfirmDialog({
  open,
  onOpenChange,
  preview,
  onConfirm,
  tripName,
}: ChangeConfirmDialogProps) {
  const [saving, setSaving] = useState(false);
  const [triggerRecalculation, setTriggerRecalculation] = useState(true);

  const hasHighImpactChanges = preview.changes.some((c) => c.impactLevel === 'high');
  const affectedSections = preview.impact.affectedSections as ReportSectionId[];

  const handleConfirm = async () => {
    setSaving(true);
    try {
      await onConfirm({ triggerRecalculation });
      onOpenChange(false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {hasHighImpactChanges && <AlertTriangle className="h-5 w-5 text-amber-500" />}
            Confirm Changes
          </DialogTitle>
          <DialogDescription>
            Review the changes you&apos;re about to make
            {tripName && ` to "${tripName}"`}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Warnings */}
          {preview.warnings.length > 0 && (
            <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-800 dark:text-amber-200">
                    Important Notes
                  </h4>
                  <ul className="mt-1 text-sm text-amber-700 dark:text-amber-300 list-disc list-inside space-y-1">
                    {preview.warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Change Preview */}
          <ChangePreview changes={preview.changes} impact={preview.impact} />

          {/* Affected Sections */}
          {affectedSections.length > 0 && (
            <AffectedSections sections={affectedSections} showRecalculationHint={false} />
          )}

          {/* Recalculation Option */}
          {preview.impact.requiresRecalculation && (
            <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <RefreshCw className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <Checkbox
                      id="recalculate"
                      checked={triggerRecalculation}
                      onChange={(e) => setTriggerRecalculation(e.target.checked)}
                    />
                    <Label
                      htmlFor="recalculate"
                      className="font-medium text-blue-800 dark:text-blue-200"
                    >
                      Trigger AI Recalculation
                    </Label>
                  </div>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-2 ml-6">
                    Your changes affect {affectedSections.length} report section
                    {affectedSections.length !== 1 ? 's' : ''}. The AI will recalculate these
                    sections to reflect your updates.
                    {preview.impact.estimatedRecalcTime > 0 && (
                      <span className="block mt-1 text-xs">
                        Estimated time: ~{Math.ceil(preview.impact.estimatedRecalcTime / 60)}{' '}
                        minutes
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
            <X className="h-4 w-4 mr-1" />
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={saving || !preview.canApply}>
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-1" />
                Save Changes
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default ChangeConfirmDialog;
