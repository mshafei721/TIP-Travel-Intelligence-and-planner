'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Eye, EyeOff, AlertCircle, Chrome } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { validateEmail } from '@/lib/auth/validation'
import { getLockoutTimeRemaining, formatLockoutTime } from '@/lib/auth/rate-limit'
import type { LoginCredentials } from '@/types/auth'

export interface LoginFormProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>
  onGoogleAuth: () => Promise<void>
  isLoading?: boolean
  error?: string
  rateLimited?: boolean
  lockoutEndsAt?: string
}

export function LoginForm({
  onLogin,
  onGoogleAuth,
  isLoading = false,
  error,
  rateLimited = false,
  lockoutEndsAt,
}: LoginFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  })

  const [showPassword, setShowPassword] = useState(false)
  const [touched, setTouched] = useState({
    email: false,
    password: false,
  })

  const [lockoutRemaining, setLockoutRemaining] = useState(0)

  // Update lockout timer
  useState(() => {
    if (rateLimited && lockoutEndsAt) {
      const interval = setInterval(() => {
        const remaining = getLockoutTimeRemaining(new Date(lockoutEndsAt))
        setLockoutRemaining(remaining)
        if (remaining <= 0) {
          clearInterval(interval)
        }
      }, 1000)

      return () => clearInterval(interval)
    }
  })

  // Validation
  const emailValid = validateEmail(formData.email)
  const passwordValid = formData.password.length > 0

  const formValid = emailValid && passwordValid && !rateLimited

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (field === 'rememberMe') {
      setFormData((prev) => ({ ...prev, [field]: e.target.checked }))
    } else {
      setFormData((prev) => ({ ...prev, [field]: e.target.value }))
    }
  }

  const handleBlur = (field: keyof typeof touched) => () => {
    setTouched((prev) => ({ ...prev, [field]: true }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Mark all fields as touched
    setTouched({
      email: true,
      password: true,
    })

    if (!formValid) return

    await onLogin({
      email: formData.email.trim(),
      password: formData.password,
      rememberMe: formData.rememberMe,
    })
  }

  return (
    <div className="w-full max-w-md space-y-6">
      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Rate Limit Alert */}
      {rateLimited && (
        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Too many failed attempts. Try again in {formatLockoutTime(lockoutRemaining)} or{' '}
            <Link href="/forgot-password" className="font-medium underline">
              reset your password
            </Link>
            .
          </AlertDescription>
        </Alert>
      )}

      {/* Google OAuth Button */}
      <Button
        type="button"
        variant="outline"
        className="w-full h-11 text-base"
        onClick={onGoogleAuth}
        disabled={isLoading || rateLimited}
      >
        <Chrome className="h-5 w-5" />
        Continue with Google
      </Button>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-slate-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-slate-500">Or</span>
        </div>
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={handleChange('email')}
            onBlur={handleBlur('email')}
            aria-invalid={touched.email && !emailValid}
            disabled={isLoading || rateLimited}
            autoFocus
            required
          />
          {touched.email && !emailValid && formData.email.trim() !== '' && (
            <p className="text-sm text-red-600">Invalid email address</p>
          )}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link
              href="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-700"
              tabIndex={-1}
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange('password')}
              onBlur={handleBlur('password')}
              aria-invalid={touched.password && !passwordValid}
              disabled={isLoading || rateLimited}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* Remember Me */}
        <div className="flex items-center space-x-2">
          <Checkbox
            id="rememberMe"
            checked={formData.rememberMe}
            onChange={handleChange('rememberMe')}
            disabled={isLoading || rateLimited}
          />
          <Label htmlFor="rememberMe" className="cursor-pointer">
            Remember me
          </Label>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full h-11 text-base"
          disabled={!formValid || isLoading}
        >
          {isLoading ? 'Logging in...' : 'Log In'}
        </Button>
      </form>

      {/* Signup Link */}
      <p className="text-center text-sm text-slate-600">
        Don't have an account?{' '}
        <Link href="/signup" className="font-medium text-blue-600 hover:text-blue-700">
          Sign up
        </Link>
      </p>
    </div>
  )
}
