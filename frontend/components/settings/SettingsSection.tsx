'use client';

import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface SettingsSectionProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}

export function SettingsSection({
  title,
  description,
  icon: Icon,
  children,
  className,
}: SettingsSectionProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900',
        className
      )}
    >
      <div className="mb-6 flex items-start gap-3">
        {Icon && (
          <div className="rounded-lg bg-slate-100 p-2 dark:bg-slate-800">
            <Icon className="h-5 w-5 text-slate-600 dark:text-slate-400" />
          </div>
        )}
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
          {description && (
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>
          )}
        </div>
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}
