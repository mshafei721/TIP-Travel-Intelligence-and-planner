'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { SignupForm } from '@/components/auth'
import { signUp } from '@/lib/auth/actions'
import { createClient } from '@/lib/supabase/client'
import type { SignupCredentials } from '@/types/auth'

export default function SignupPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | undefined>()

  const handleSignup = async (credentials: SignupCredentials) => {
    setError(undefined)
    setIsLoading(true)

    try {
      const result = await signUp(credentials)

      if (result.error) {
        setError(result.error)
      } else {
        // Auto-login successful, redirect to dashboard
        router.push('/')
      }
    } catch {
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleAuth = async () => {
    setError(undefined)
    setIsLoading(true)

    try {
      const supabase = createClient()
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (error) {
        setError(error.message)
        setIsLoading(false)
      }
    } catch {
      setError('An unexpected error occurred. Please try again.')
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900">Create Your Account</h1>
          <p className="mt-2 text-sm text-slate-600">
            Get started with personalized travel intelligence
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <SignupForm onSignup={handleSignup} onGoogleAuth={handleGoogleAuth} isLoading={isLoading} error={error} />
        </div>
      </div>
    </div>
  )
}
