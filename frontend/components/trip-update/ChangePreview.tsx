'use client';

import { useMemo } from 'react';
import { ArrowRight, AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { FieldChange, ChangePreviewData } from '@/types/trip-update';

interface ChangePreviewProps {
  changes: FieldChange[];
  impact?: ChangePreviewData['impact'];
  warnings?: string[];
}

/**
 * ChangePreview - Shows a visual diff of changes before applying
 */
export function ChangePreview({ changes, impact, warnings = [] }: ChangePreviewProps) {
  // Group changes by impact level
  const groupedChanges = useMemo(() => {
    const groups = {
      high: [] as FieldChange[],
      medium: [] as FieldChange[],
      low: [] as FieldChange[],
    };
    changes.forEach((change) => {
      groups[change.impactLevel].push(change);
    });
    return groups;
  }, [changes]);

  const impactLevelColors = {
    high: {
      bg: 'bg-red-50 dark:bg-red-950/30',
      border: 'border-red-200 dark:border-red-900',
      text: 'text-red-700 dark:text-red-400',
      badge: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
      icon: AlertCircle,
    },
    medium: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-900',
      text: 'text-amber-700 dark:text-amber-400',
      badge: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
      icon: AlertTriangle,
    },
    low: {
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-900',
      text: 'text-blue-700 dark:text-blue-400',
      badge: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
      icon: Info,
    },
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

  if (changes.length === 0) {
    return (
      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-6 text-center">
        <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
        <p className="text-slate-600 dark:text-slate-400">No changes detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Change Preview</h3>
        <div className="flex items-center gap-2">
          {groupedChanges.high.length > 0 && (
            <Badge className={impactLevelColors.high.badge}>
              {groupedChanges.high.length} High Impact
            </Badge>
          )}
          {groupedChanges.medium.length > 0 && (
            <Badge className={impactLevelColors.medium.badge}>
              {groupedChanges.medium.length} Medium Impact
            </Badge>
          )}
          {groupedChanges.low.length > 0 && (
            <Badge className={impactLevelColors.low.badge}>
              {groupedChanges.low.length} Low Impact
            </Badge>
          )}
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-amber-800 dark:text-amber-200">Warnings</h4>
              <ul className="mt-1 text-sm text-amber-700 dark:text-amber-300 space-y-1">
                {warnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Impact Summary */}
      {impact && (
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Impact Summary
            </span>
            {impact.requiresRecalculation && (
              <Badge variant="secondary" className="text-xs">
                Requires AI Recalculation
              </Badge>
            )}
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400">{impact.impactSummary}</p>
          {impact.estimatedRecalcTime > 0 && (
            <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
              Estimated recalculation time: ~{Math.ceil(impact.estimatedRecalcTime / 60)} min
            </p>
          )}
        </div>
      )}

      {/* Changes List */}
      <div className="space-y-3">
        {(['high', 'medium', 'low'] as const).map((level) => {
          const levelChanges = groupedChanges[level];
          if (levelChanges.length === 0) return null;

          const colors = impactLevelColors[level];
          const Icon = colors.icon;

          return (
            <div
              key={level}
              className={`rounded-lg border ${colors.border} ${colors.bg} overflow-hidden`}
            >
              <div className="px-4 py-2 border-b border-inherit flex items-center gap-2">
                <Icon className={`h-4 w-4 ${colors.text}`} />
                <span className={`text-sm font-medium ${colors.text}`}>
                  {level.charAt(0).toUpperCase() + level.slice(1)} Impact Changes
                </span>
              </div>
              <div className="divide-y divide-inherit">
                {levelChanges.map((change, idx) => (
                  <div key={idx} className="px-4 py-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        {change.fieldLabel}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-sm">
                      <div className="flex-1">
                        <span className="text-slate-500 dark:text-slate-500">From: </span>
                        <span className="text-slate-700 dark:text-slate-300 font-mono bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                          {formatValue(change.oldValue)}
                        </span>
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-400 flex-shrink-0" />
                      <div className="flex-1">
                        <span className="text-slate-500 dark:text-slate-500">To: </span>
                        <span className="text-slate-900 dark:text-slate-100 font-mono bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded">
                          {formatValue(change.newValue)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ChangePreview;
