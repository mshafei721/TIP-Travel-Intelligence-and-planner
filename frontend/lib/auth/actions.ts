/**
 * Server Actions for Authentication
 * All auth operations use Supabase Auth
 */

'use server'

import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'
import type { SupabaseClient } from '@supabase/supabase-js'
import type { Database } from '@/types/database'
import type { SignupCredentials, LoginCredentials, ChangePasswordData } from '@/types/auth'

type UserProfilesTable = Database['public']['Tables']['user_profiles']
type UserProfilesInsert = UserProfilesTable['Insert']

const userProfilesTable = (supabase: SupabaseClient<Database, 'public'>) =>
  supabase.from('user_profiles') as unknown as {
    insert: (values: UserProfilesInsert) => Promise<{ error: { message: string } | null }>
    delete: () => {
      eq: (
        column: keyof UserProfilesTable['Row'],
        value: string
      ) => Promise<{ error: { message: string } | null }>
    }
  }

/**
 * Sign up with email and password
 */
export async function signUp(credentials: SignupCredentials) {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const { data, error } = await supabase.auth.signUp({
    email: credentials.email,
    password: credentials.password,
    options: {
      data: {
        display_name: credentials.name,
      },
      emailRedirectTo: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/auth/callback`,
    },
  })

  if (error) {
    return { error: error.message }
  }

  // Create user profile
  if (data.user) {
    const { error: profileError } = await userProfilesTable(supabase).insert({
      id: data.user.id,
      display_name: credentials.name,
      preferences: {},
    })

    if (profileError) {
      console.error('Failed to create user profile:', profileError)
    }
  }

  return { data, error: null }
}

/**
 * Sign in with email and password
 */
export async function signIn(credentials: LoginCredentials) {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const { data, error } = await supabase.auth.signInWithPassword({
    email: credentials.email,
    password: credentials.password,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  return { data, error: null }
}

/**
 * Sign out
 */
export async function signOut() {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>
  await supabase.auth.signOut()
  revalidatePath('/', 'layout')
  redirect('/login')
}

/**
 * Request password reset
 */
export async function requestPasswordReset(email: string) {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/reset-password`,
  })

  if (error) {
    return { error: error.message }
  }

  return { error: null }
}

/**
 * Update password
 */
export async function updatePassword(newPassword: string) {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const { error } = await supabase.auth.updateUser({
    password: newPassword,
  })

  if (error) {
    return { error: error.message }
  }

  return { error: null }
}

/**
 * Change password (requires current password)
 */
export async function changePassword(data: ChangePasswordData) {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  // Verify current password by attempting sign in
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user?.email) {
    return { error: 'Not authenticated' }
  }

  // Re-authenticate with current password
  const { error: reAuthError } = await supabase.auth.signInWithPassword({
    email: user.email,
    password: data.currentPassword,
  })

  if (reAuthError) {
    return { error: 'Current password is incorrect' }
  }

  // Update to new password
  const { error } = await supabase.auth.updateUser({
    password: data.newPassword,
  })

  if (error) {
    return { error: error.message }
  }

  return { error: null }
}

/**
 * Delete account
 */
export async function deleteAccount() {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return { error: 'Not authenticated' }
  }

  // Delete user profile (cascade will handle related data)
  const { error: profileError } = await userProfilesTable(supabase).delete().eq('id', user.id)

  if (profileError) {
    return { error: 'Failed to delete profile' }
  }

  // Sign out
  await supabase.auth.signOut()

  redirect('/signup')
}

/**
 * Resend verification email
 */
export async function resendVerificationEmail() {
  const supabase = (await createClient()) as SupabaseClient<Database, 'public'>

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user?.email) {
    return { error: 'Not authenticated' }
  }

  const { error } = await supabase.auth.resend({
    type: 'signup',
    email: user.email,
    options: {
      emailRedirectTo: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/auth/callback`,
    },
  })

  if (error) {
    return { error: error.message }
  }

  return { error: null }
}
