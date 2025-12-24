'use client'

import { useState, useEffect } from 'react'
import { Clock, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

export interface SessionExpiryBannerProps {
  expiresAt: string
  onExtendSession: () => Promise<void>
  onDismiss: () => void
}

export function SessionExpiryBanner({
  expiresAt,
  onExtendSession,
  onDismiss,
}: SessionExpiryBannerProps) {
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [isExtending, setIsExtending] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().getTime()
      const expiry = new Date(expiresAt).getTime()
      const remaining = Math.max(0, Math.floor((expiry - now) / 1000))

      setTimeRemaining(remaining)

      if (remaining <= 0) {
        clearInterval(interval)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [expiresAt])

  const handleExtend = async () => {
    setIsExtending(true)
    try {
      await onExtendSession()
      onDismiss()
    } finally {
      setIsExtending(false)
    }
  }

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  // Don't show banner if more than 5 minutes remaining
  if (timeRemaining > 5 * 60 || timeRemaining <= 0) {
    return null
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <Alert
        variant="warning"
        className="rounded-none border-x-0 border-t-0 flex items-center justify-between gap-4"
      >
        <div className="flex items-center gap-3 flex-1">
          <Clock className="h-4 w-4" />
          <AlertDescription className="flex-1">
            Your session will expire in <strong>{formatTime(timeRemaining)}</strong>. Would you
            like to extend it?
          </AlertDescription>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="default"
            onClick={handleExtend}
            disabled={isExtending}
          >
            {isExtending ? 'Extending...' : 'Extend Session'}
          </Button>
          <button
            type="button"
            onClick={onDismiss}
            className="text-slate-400 hover:text-slate-600"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </Alert>
    </div>
  )
}
