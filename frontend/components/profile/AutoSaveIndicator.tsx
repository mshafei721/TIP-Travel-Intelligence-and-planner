'use client'

import { useEffect, useState } from 'react'
import { Check, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { SaveState } from '@/types/profile'

export interface AutoSaveIndicatorProps {
  saveState: SaveState
  className?: string
  /**
   * Duration in ms to show "Saved" state before fading out
   * @default 2500
   */
  savedDuration?: number
  /**
   * Optional error message to display
   */
  errorMessage?: string
}

/**
 * AutoSaveIndicator - Smooth animated save status indicator
 *
 * Displays different states:
 * - idle: Hidden
 * - saving: Spinner with "Saving..."
 * - saved: Check icon with "Saved" (fades out after savedDuration)
 * - error: Alert icon with "Failed to save"
 *
 * Features smooth fade-in/out animations and auto-hide after success.
 *
 * @example
 * ```tsx
 * const [saveState, setSaveState] = useState<SaveState>('idle')
 *
 * const handleSave = async () => {
 *   setSaveState('saving')
 *   try {
 *     await updateProfile(data)
 *     setSaveState('saved')
 *   } catch (error) {
 *     setSaveState('error')
 *   }
 * }
 *
 * <AutoSaveIndicator saveState={saveState} />
 * ```
 */
export function AutoSaveIndicator({
  saveState,
  className,
  savedDuration = 2500,
  errorMessage,
}: AutoSaveIndicatorProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [shouldRender, setShouldRender] = useState(false)

  useEffect(() => {
    let fadeInTimer: ReturnType<typeof setTimeout> | undefined
    let hideTimer: ReturnType<typeof setTimeout> | undefined
    let unmountTimer: ReturnType<typeof setTimeout> | undefined

    if (saveState === 'idle') {
      // Fade out
      fadeInTimer = setTimeout(() => setIsVisible(false), 0)
      // Remove from DOM after animation
      unmountTimer = setTimeout(() => setShouldRender(false), 300)

      return () => {
        if (fadeInTimer) clearTimeout(fadeInTimer)
        if (unmountTimer) clearTimeout(unmountTimer)
      }
    }

    // Show indicator
    const showTimer = setTimeout(() => setShouldRender(true), 0)
    // Trigger fade-in after render
    fadeInTimer = setTimeout(() => setIsVisible(true), 10)

    // Auto-hide after success
    if (saveState === 'saved') {
      hideTimer = setTimeout(() => {
        setIsVisible(false)
        unmountTimer = setTimeout(() => setShouldRender(false), 300)
      }, savedDuration)
    }

    return () => {
      clearTimeout(showTimer)
      if (fadeInTimer) clearTimeout(fadeInTimer)
      if (hideTimer) clearTimeout(hideTimer)
      if (unmountTimer) clearTimeout(unmountTimer)
    }
  }, [saveState, savedDuration])

  if (!shouldRender) return null

  return (
    <div
      data-testid="auto-save-indicator"
      className={cn(
        'inline-flex items-center gap-1.5 text-sm font-medium transition-opacity duration-300',
        isVisible ? 'opacity-100' : 'opacity-0',
        className
      )}
      role="status"
      aria-live="polite"
    >
      {saveState === 'saving' && (
        <>
          <Loader2
            className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400"
            aria-hidden="true"
          />
          <span className="text-slate-600 dark:text-slate-400">Saving...</span>
        </>
      )}

      {saveState === 'saved' && (
        <>
          <Check
            className="h-4 w-4 text-green-600 dark:text-green-400"
            aria-hidden="true"
          />
          <span className="text-green-600 dark:text-green-400">Saved</span>
        </>
      )}

      {saveState === 'error' && (
        <>
          <AlertCircle
            className="h-4 w-4 text-red-600 dark:text-red-400"
            aria-hidden="true"
          />
          <span className="text-red-600 dark:text-red-400">
            {errorMessage || 'Failed to save'}
          </span>
        </>
      )}
    </div>
  )
}
