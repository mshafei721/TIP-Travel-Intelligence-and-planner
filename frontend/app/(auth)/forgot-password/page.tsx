'use client'

import { useState } from 'react'
import { PasswordResetRequestForm } from '@/components/auth'
import { requestPasswordReset } from '@/lib/auth/actions'

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

  const handleRequestReset = async (email: string) => {
    setIsLoading(true)

    try {
      const result = await requestPasswordReset(email)

      if (!result.error) {
        setEmailSent(true)
      }
    } catch {
      // Even on error, show success message for security
      // (don't reveal whether email exists)
      setEmailSent(true)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <PasswordResetRequestForm
            onRequestReset={handleRequestReset}
            isLoading={isLoading}
            emailSent={emailSent}
          />
        </div>
      </div>
    </div>
  )
}
