'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export interface EmailVerificationPageProps {
  onVerify: () => Promise<void>
  isLoading?: boolean
  success?: boolean
  error?: string
}

export function EmailVerificationPage({
  onVerify,
  isLoading = false,
  success = false,
  error,
}: EmailVerificationPageProps) {
  // Auto-verify on mount
  useEffect(() => {
    if (!success && !error && !isLoading) {
      onVerify()
    }
  }, [onVerify, success, error, isLoading])

  if (isLoading) {
    return (
      <div className="w-full max-w-md space-y-6">
        <div className="flex flex-col items-center justify-center space-y-4 py-12">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
          <p className="text-lg text-slate-600">Verifying your email...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full max-w-md space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Verification Failed</AlertTitle>
          <AlertDescription>
            {error || 'The verification link is invalid or has expired.'}
          </AlertDescription>
        </Alert>

        <div className="space-y-3">
          <Link href="/login">
            <Button className="w-full">Continue to Login</Button>
          </Link>
          <Link href="/signup">
            <Button variant="outline" className="w-full">
              Create a New Account
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="w-full max-w-md space-y-6">
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>Email Verified Successfully</AlertTitle>
          <AlertDescription>
            Your email address has been verified. You can now log in to your account.
          </AlertDescription>
        </Alert>

        <Link href="/login">
          <Button className="w-full h-11 text-base">Continue to Login</Button>
        </Link>
      </div>
    )
  }

  return null
}
