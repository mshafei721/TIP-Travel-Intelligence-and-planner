import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Profile Edit Page
 *
 * Allows users to edit their profile information
 */
export default async function ProfileEditPage() {
  const supabase = await createClient()

  // Check authentication
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser()

  if (authError || !user) {
    redirect('/login')
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <div className="space-y-6">
        {/* Header with back button */}
        <div className="flex items-center gap-4">
          <Link href="/profile">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Profile
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
            Edit Profile
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Update your personal information and preferences
          </p>
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
          <p className="text-slate-600 dark:text-slate-400">
            Profile editing UI will be added here. For now, please use the main profile page.
          </p>
          <div className="mt-4">
            <Link href="/profile">
              <Button>Go to Profile Settings</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
