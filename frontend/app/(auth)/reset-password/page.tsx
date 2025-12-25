'use client'

import { useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { PasswordResetForm } from '@/components/auth'
import { updatePassword } from '@/lib/auth/actions'

function ResetPasswordContent() {
  const searchParams = useSearchParams()
  const token = searchParams.get('token') || ''

  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | undefined>()

  const handleResetPassword = async (newPassword: string) => {
    setError(undefined)
    setIsLoading(true)

    try {
      const result = await updatePassword(newPassword)

      if (result.error) {
        setError(result.error)
      } else {
        setSuccess(true)
      }
    } catch {
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
        <div className="w-full max-w-md space-y-8">
          <div className="rounded-lg border border-red-200 bg-red-50 p-8 shadow-sm">
            <p className="text-center text-red-600">
              Invalid reset link. Please request a new password reset.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <PasswordResetForm
            onResetPassword={handleResetPassword}
            isLoading={isLoading}
            success={success}
            error={error}
          />
        </div>
      </div>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ResetPasswordContent />
    </Suspense>
  )
}
