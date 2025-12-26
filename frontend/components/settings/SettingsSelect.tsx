'use client';

import { memo, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface Option {
  value: string;
  label: string;
  description?: string;
}

interface SettingsSelectProps {
  label: string;
  description?: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const SettingsSelect = memo(function SettingsSelect({
  label,
  description,
  value,
  options,
  onChange,
  disabled,
}: SettingsSelectProps) {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange(e.target.value);
    },
    [onChange],
  );

  return (
    <div
      className={cn(
        'flex flex-col gap-2 rounded-lg border border-slate-200 p-4 dark:border-slate-700',
        disabled && 'opacity-50',
      )}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <p className="font-medium text-slate-900 dark:text-slate-100">{label}</p>
          {description && (
            <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{description}</p>
          )}
        </div>
        <select
          value={value}
          onChange={handleChange}
          disabled={disabled}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
});
