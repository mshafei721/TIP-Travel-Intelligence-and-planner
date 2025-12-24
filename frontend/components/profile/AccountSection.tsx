'use client'

import { useState } from 'react'
import { AlertTriangle, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { SectionCard } from './SectionCard'

export interface AccountSectionProps {
  onAccountDelete: () => Promise<void>
}

/**
 * AccountSection - Account deletion
 *
 * Features:
 * - Red destructive "Delete Account" button
 * - Warning text about permanence
 * - Confirmation dialog before deletion
 */
export function AccountSection({ onAccountDelete }: AccountSectionProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onAccountDelete()
      // onAccountDelete should handle logout and redirect
    } catch (error) {
      setIsDeleting(false)
      alert('Failed to delete account. Please try again.')
    }
  }

  return (
    <>
      <SectionCard
        title="Danger Zone"
        description="Permanent account actions"
        icon={AlertTriangle}
      >
        <div className="rounded-lg border-2 border-red-200 bg-red-50 p-6 dark:border-red-900/50 dark:bg-red-950/20">
          <div className="flex items-start gap-4">
            <div className="rounded-full bg-red-100 p-2 dark:bg-red-900/30">
              <Trash2 className="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-red-900 dark:text-red-100">
                Delete Your Account
              </h3>
              <p className="mt-2 text-sm text-red-800 dark:text-red-200">
                This action is <strong>permanent and cannot be undone</strong>. All your trips, reports, and personal data will be permanently deleted.
                You will be logged out and redirected to the signup page.
              </p>
              <Button
                variant="destructive"
                onClick={() => setIsDialogOpen(true)}
                className="mt-4"
              >
                <Trash2 className="h-4 w-4" />
                Delete Account
              </Button>
            </div>
          </div>
        </div>
      </SectionCard>

      {/* Confirmation Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Account?</DialogTitle>
            <DialogDescription>
              Are you absolutely sure you want to delete your account? This will:
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2 py-4">
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-600 dark:text-slate-400">
              <li>Permanently delete all your trip data and reports</li>
              <li>Remove all saved templates and preferences</li>
              <li>Cancel any in-progress report generation</li>
              <li>Log you out of all devices</li>
            </ul>
            <p className="mt-4 text-sm font-semibold text-red-600 dark:text-red-400">
              This action cannot be undone.
            </p>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
