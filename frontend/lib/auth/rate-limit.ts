/**
 * Client-side Rate Limiting
 * Tracks failed login attempts per email
 * Note: This is supplementary to server-side rate limiting
 */

import type { RateLimitState } from '@/types/auth'

const STORAGE_KEY = 'auth_rate_limit'
const MAX_ATTEMPTS = 5
const LOCKOUT_DURATION_MS = 15 * 60 * 1000 // 15 minutes

interface StoredRateLimitData {
  [email: string]: {
    attempts: number
    lockedUntil: string | null
  }
}

/**
 * Get rate limit state for an email
 */
export function getRateLimitState(email: string): RateLimitState {
  if (typeof window === 'undefined') {
    return { attempts: 0, lockedUntil: null, isLocked: false }
  }

  const data = getStoredData()
  const emailData = data[email.toLowerCase()]

  if (!emailData) {
    return { attempts: 0, lockedUntil: null, isLocked: false }
  }

  const lockedUntil = emailData.lockedUntil ? new Date(emailData.lockedUntil) : null
  const isLocked = lockedUntil ? new Date() < lockedUntil : false

  // Clear lockout if expired
  if (lockedUntil && !isLocked) {
    clearRateLimit(email)
    return { attempts: 0, lockedUntil: null, isLocked: false }
  }

  return {
    attempts: emailData.attempts,
    lockedUntil,
    isLocked,
  }
}

/**
 * Record a failed login attempt
 */
export function recordFailedAttempt(email: string): RateLimitState {
  const data = getStoredData()
  const normalizedEmail = email.toLowerCase()
  const current = data[normalizedEmail] || { attempts: 0, lockedUntil: null }

  const newAttempts = current.attempts + 1
  let lockedUntil = current.lockedUntil

  // Lock account if max attempts reached
  if (newAttempts >= MAX_ATTEMPTS) {
    lockedUntil = new Date(Date.now() + LOCKOUT_DURATION_MS).toISOString()
  }

  data[normalizedEmail] = {
    attempts: newAttempts,
    lockedUntil,
  }

  saveStoredData(data)

  return {
    attempts: newAttempts,
    lockedUntil: lockedUntil ? new Date(lockedUntil) : null,
    isLocked: newAttempts >= MAX_ATTEMPTS,
  }
}

/**
 * Clear rate limit for an email (after successful login)
 */
export function clearRateLimit(email: string): void {
  const data = getStoredData()
  delete data[email.toLowerCase()]
  saveStoredData(data)
}

/**
 * Get stored rate limit data
 */
function getStoredData(): StoredRateLimitData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

/**
 * Save rate limit data
 */
function saveStoredData(data: StoredRateLimitData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch {
    // Ignore storage errors
  }
}

/**
 * Get time remaining in lockout
 */
export function getLockoutTimeRemaining(lockedUntil: Date | null): number {
  if (!lockedUntil) return 0
  const remaining = lockedUntil.getTime() - Date.now()
  return Math.max(0, Math.ceil(remaining / 1000)) // seconds
}

/**
 * Format lockout time for display
 */
export function formatLockoutTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}
