import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AutoSaveIndicator } from './AutoSaveIndicator'
import type { SaveState } from '@/types/profile'

export interface SectionCardProps {
  title: string
  description?: string
  icon?: LucideIcon
  saveState?: SaveState
  children: ReactNode
  className?: string
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
        'rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md',
        'dark:border-slate-800 dark:bg-slate-900',
        className
      )}
    >
      {/* Header */}
      <div className="mb-6 flex items-start justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className="rounded-lg bg-blue-50 p-2 dark:bg-blue-950/20">
              <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            </div>
          )}
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              {title}
            </h2>
            {description && (
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                {description}
              </p>
            )}
          </div>
        </div>

        {/* Auto-save indicator */}
        {saveState && saveState !== 'idle' && (
          <AutoSaveIndicator saveState={saveState} />
        )}
      </div>

      {/* Content */}
      <div className="space-y-4">{children}</div>
    </div>
  )
}
