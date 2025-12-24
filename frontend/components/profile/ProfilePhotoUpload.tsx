'use client'

import { useState, useRef, DragEvent, ChangeEvent } from 'react'
import { Upload, User, Loader2, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import type { SaveState } from '@/types/profile'

export interface ProfilePhotoUploadProps {
  currentPhotoUrl?: string
  onUpload: (file: File) => Promise<string>
  maxSizeMB?: number
  className?: string
}

/**
 * ProfilePhotoUpload - Photo upload with preview and drag-and-drop
 *
 * Features:
 * - Click to upload or drag-and-drop
 * - Image preview
 * - Loading state during upload
 * - File size validation
 * - Remove photo option
 *
 * @example
 * ```tsx
 * <ProfilePhotoUpload
 *   currentPhotoUrl={user.photoUrl}
 *   onUpload={async (file) => {
 *     const url = await uploadPhotoToStorage(file)
 *     return url
 *   }}
 *   maxSizeMB={5}
 * />
 * ```
 */
export function ProfilePhotoUpload({
  currentPhotoUrl,
  onUpload,
  maxSizeMB = 5,
  className,
}: ProfilePhotoUploadProps) {
  const [preview, setPreview] = useState<string | undefined>(currentPhotoUrl)
  const [isDragging, setIsDragging] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [error, setError] = useState<string>()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!file.type.startsWith('image/')) {
      return 'Please upload an image file (JPG, PNG, GIF)'
    }

    // Check file size
    const sizeMB = file.size / (1024 * 1024)
    if (sizeMB > maxSizeMB) {
      return `Image size must be less than ${maxSizeMB}MB`
    }

    return null
  }

  const handleFile = async (file: File) => {
    setError(undefined)

    // Validate
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    // Show preview immediately
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Upload
    setSaveState('saving')
    try {
      const url = await onUpload(file)
      setPreview(url)
      setSaveState('saved')
      setTimeout(() => setSaveState('idle'), 2500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setSaveState('error')
      setPreview(currentPhotoUrl) // Revert to original
    }
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleRemove = () => {
    setPreview(undefined)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Upload Area */}
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative flex h-32 w-32 cursor-pointer items-center justify-center rounded-full border-2 border-dashed transition-all duration-200',
          isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
            : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50 dark:border-slate-700 dark:hover:border-blue-500 dark:hover:bg-slate-800/50',
          saveState === 'saving' && 'pointer-events-none opacity-75'
        )}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            handleClick()
          }
        }}
        aria-label="Upload profile photo"
      >
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="hidden"
          aria-label="Photo file input"
        />

        {saveState === 'saving' ? (
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        ) : preview ? (
          <img
            src={preview}
            alt="Profile"
            className="h-full w-full rounded-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 text-slate-400">
            <User className="h-12 w-12" />
            <Upload className="h-5 w-5" />
          </div>
        )}

        {/* Remove button (when photo exists) */}
        {preview && saveState !== 'saving' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleRemove()
            }}
            className="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-white shadow-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            aria-label="Remove photo"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Help text */}
      <p className="text-xs text-slate-500 dark:text-slate-400">
        Click or drag to upload • Max {maxSizeMB}MB
      </p>

      {/* Save state indicator */}
      {saveState === 'saved' && (
        <p className="text-sm font-medium text-green-600 dark:text-green-400">
          Photo updated
        </p>
      )}

      {/* Error message */}
      {error && (
        <p className="text-sm font-medium text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
    </div>
  )
}
