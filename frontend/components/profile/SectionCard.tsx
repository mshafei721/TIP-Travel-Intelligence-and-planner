import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AutoSaveIndicator } from './AutoSaveIndicator';
import type { SaveState } from '@/types/profile';

export interface SectionCardProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  saveState?: SaveState;
  children: ReactNode;
  className?: string;
}

/**
 * SectionCard - Reusable card wrapper for profile settings sections
 *
 * Provides consistent styling with:
 * - Card background with shadow
 * - Section header with icon and title
 * - Optional auto-save indicator
 * - Proper spacing and borders
 *
 * @example
 * ```tsx
 * <SectionCard
 *   title="Profile Information"
 *   description="Update your personal details"
 *   icon={User}
 *   saveState={saveState}
 * >
 *   <Input label="Name" value={name} onChange={setName} />
 * </SectionCard>
 * ```
 */
export function SectionCard({
  title,
  description,
  icon: Icon,
  saveState,
  children,
  className,
}: SectionCardProps) {
  return (
    <div
      className={cn(
        'group rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-200 hover:shadow-lg hover:shadow-slate-200/50',
        'dark:border-slate-800 dark:bg-slate-900 dark:hover:shadow-slate-900/50',
        className,
      )}
    >
      {/* Header */}
      <div className="mb-8 flex items-start justify-between border-b border-slate-100 pb-6 dark:border-slate-800">
        <div className="flex items-start gap-4">
          {Icon && (
            <div className="rounded-xl bg-gradient-to-br from-blue-50 to-blue-100/50 p-3 shadow-sm transition-transform group-hover:scale-105 dark:from-blue-950/40 dark:to-blue-950/20">
              <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            </div>
          )}
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              {title}
            </h2>
            {description && (
              <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                {description}
              </p>
            )}
          </div>
        </div>

        {/* Auto-save indicator */}
        {saveState && saveState !== 'idle' && <AutoSaveIndicator saveState={saveState} />}
      </div>

      {/* Content */}
      <div>{children}</div>
    </div>
  );
}
