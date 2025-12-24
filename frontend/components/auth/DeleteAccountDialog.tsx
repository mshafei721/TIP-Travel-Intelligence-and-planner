'use client'

import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export interface DeleteAccountDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  isLoading?: boolean
}

export function DeleteAccountDialog({
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
}: DeleteAccountDialogProps) {
  if (!isOpen) return null

  const handleConfirm = async () => {
    await onConfirm()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6 space-y-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Delete Account</AlertTitle>
          <AlertDescription>
            This will permanently delete your account and all trip data. This action cannot be
            undone.
          </AlertDescription>
        </Alert>

        <div className="space-y-3">
          <p className="text-sm text-slate-600">
            Are you absolutely sure you want to delete your account? All of your data will be
            permanently removed from our servers forever. This action is irreversible.
          </p>

          <ul className="text-sm text-slate-600 space-y-1 list-disc list-inside">
            <li>All trip plans and reports will be deleted</li>
            <li>All saved templates will be deleted</li>
            <li>Your profile and preferences will be deleted</li>
            <li>You will no longer receive notifications</li>
          </ul>
        </div>

        <div className="flex gap-3">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            className="flex-1"
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Deleting...' : 'Confirm Delete'}
          </Button>
        </div>
      </div>
    </div>
  )
}
