'use client';

import { useMemo } from 'react';
import { ArrowRight, Plus, Minus, Equal, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { TripData } from '@/types/trip-update';

interface DiffViewProps {
  versionA: {
    number: number;
    data: TripData;
  };
  versionB: {
    number: number;
    data: TripData;
  };
  onClose: () => void;
}

type DiffType = 'added' | 'removed' | 'modified' | 'unchanged';

interface DiffLine {
  field: string;
  label: string;
  valueA: unknown;
  valueB: unknown;
  diffType: DiffType;
}

/**
 * DiffView - Side-by-side comparison of two trip versions
 */
export function DiffView({ versionA, versionB, onClose }: DiffViewProps) {
  // Build diff lines from both versions
  const diffLines = useMemo((): DiffLine[] => {
    const lines: DiffLine[] = [];
    const allFields = new Set([...Object.keys(versionA.data), ...Object.keys(versionB.data)]);

    // Skip internal fields
    const skipFields = ['id', 'user_id', 'created_at', 'updated_at'];

    const fieldLabels: Record<string, string> = {
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
      status: 'Status',
      generation_status: 'Generation Status',
    };

    allFields.forEach((field) => {
      if (skipFields.includes(field)) return;

      const valueA = versionA.data[field as keyof TripData];
      const valueB = versionB.data[field as keyof TripData];

      let diffType: DiffType = 'unchanged';
      if (valueA === undefined || valueA === null || valueA === '') {
        if (valueB !== undefined && valueB !== null && valueB !== '') {
          diffType = 'added';
        }
      } else if (valueB === undefined || valueB === null || valueB === '') {
        diffType = 'removed';
      } else if (JSON.stringify(valueA) !== JSON.stringify(valueB)) {
        diffType = 'modified';
      }

      lines.push({
        field,
        label: fieldLabels[field] || field.replace(/_/g, ' '),
        valueA,
        valueB,
        diffType,
      });
    });

    // Sort: modified first, then added, then removed, then unchanged
    const order: Record<DiffType, number> = {
      modified: 0,
      added: 1,
      removed: 2,
      unchanged: 3,
    };

    return lines.sort((a, b) => order[a.diffType] - order[b.diffType]);
  }, [versionA, versionB]);

  const changedCount = diffLines.filter((l) => l.diffType !== 'unchanged').length;

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined || value === '') {
      return '—';
    }
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : '—';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  const getDiffIcon = (type: DiffType) => {
    switch (type) {
      case 'added':
        return <Plus className="h-4 w-4 text-green-600" />;
      case 'removed':
        return <Minus className="h-4 w-4 text-red-600" />;
      case 'modified':
        return <ArrowRight className="h-4 w-4 text-amber-600" />;
      default:
        return <Equal className="h-4 w-4 text-slate-400" />;
    }
  };

  const getDiffColors = (type: DiffType, side: 'left' | 'right') => {
    switch (type) {
      case 'added':
        return side === 'right'
          ? 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900'
          : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700';
      case 'removed':
        return side === 'left'
          ? 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900'
          : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700';
      case 'modified':
        return side === 'left'
          ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900'
          : 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900';
      default:
        return 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800';
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              Version Comparison
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Comparing version {versionA.number} with version {versionB.number}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{changedCount} changes</Badge>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Legend */}
        <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-green-500" />
            <span className="text-slate-600 dark:text-slate-400">Added</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500" />
            <span className="text-slate-600 dark:text-slate-400">Removed</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-amber-500" />
            <span className="text-slate-600 dark:text-slate-400">Modified</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-slate-300 dark:bg-slate-600" />
            <span className="text-slate-600 dark:text-slate-400">Unchanged</span>
          </div>
        </div>

        {/* Version Headers */}
        <div className="grid grid-cols-[1fr,auto,1fr] gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="font-medium text-slate-700 dark:text-slate-300 text-center">
            Version {versionA.number}
            {versionA.number < versionB.number && (
              <span className="text-xs text-slate-500 ml-1">(older)</span>
            )}
          </div>
          <div className="w-8" />
          <div className="font-medium text-slate-700 dark:text-slate-300 text-center">
            Version {versionB.number}
            {versionB.number > versionA.number && (
              <span className="text-xs text-slate-500 ml-1">(newer)</span>
            )}
          </div>
        </div>

        {/* Diff Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="divide-y divide-slate-200 dark:divide-slate-800">
            {diffLines.map((line) => (
              <div
                key={line.field}
                className={`grid grid-cols-[1fr,auto,1fr] gap-2 p-3 ${
                  line.diffType === 'unchanged' ? 'opacity-50' : ''
                }`}
              >
                {/* Left Value */}
                <div className={`rounded-lg p-3 border ${getDiffColors(line.diffType, 'left')}`}>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {line.label}
                  </div>
                  <div
                    className={`text-sm font-mono ${
                      line.diffType === 'removed'
                        ? 'text-red-700 dark:text-red-300 line-through'
                        : line.diffType === 'modified'
                          ? 'text-amber-700 dark:text-amber-300'
                          : 'text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    {formatValue(line.valueA)}
                  </div>
                </div>

                {/* Diff Indicator */}
                <div className="flex items-center justify-center w-8">
                  {getDiffIcon(line.diffType)}
                </div>

                {/* Right Value */}
                <div className={`rounded-lg p-3 border ${getDiffColors(line.diffType, 'right')}`}>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {line.label}
                  </div>
                  <div
                    className={`text-sm font-mono ${
                      line.diffType === 'added'
                        ? 'text-green-700 dark:text-green-300'
                        : line.diffType === 'modified'
                          ? 'text-green-700 dark:text-green-300'
                          : 'text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    {formatValue(line.valueB)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}

export default DiffView;
