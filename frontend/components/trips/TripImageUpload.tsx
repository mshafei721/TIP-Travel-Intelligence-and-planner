'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import { Plus, X, Loader2, ImageIcon } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { updateTrip } from '@/lib/api/trips';

interface TripImageUploadProps {
  tripId: string;
  currentImageUrl?: string | null;
  onImageUploaded: (url: string) => void;
  onImageRemoved?: () => void;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-24 w-24',
  md: 'h-32 w-32',
  lg: 'h-48 w-full',
};

export function TripImageUpload({
  tripId,
  currentImageUrl,
  onImageUploaded,
  onImageRemoved,
  size = 'md',
}: TripImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentImageUrl || null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid image (JPEG, PNG, WebP, or GIF)');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be less than 5MB');
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const supabase = createClient();

      // Create unique filename
      const fileExt = file.name.split('.').pop();
      const fileName = `${tripId}/${Date.now()}.${fileExt}`;

      // Upload to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from('trip-images')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: true,
        });

      if (uploadError) {
        throw uploadError;
      }

      // Get public URL
      const { data: urlData } = supabase.storage.from('trip-images').getPublicUrl(fileName);

      const publicUrl = urlData.publicUrl;

      // Update trip via backend API
      await updateTrip(tripId, { coverImageUrl: publicUrl });

      // Update preview and notify parent
      setPreviewUrl(publicUrl);
      onImageUploaded(publicUrl);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload image. Please try again.');
    } finally {
      setIsUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemoveImage = async () => {
    if (!previewUrl) return;

    setIsUploading(true);
    try {
      const supabase = createClient();

      // Extract file path from URL
      const urlParts = previewUrl.split('/trip-images/');
      if (urlParts.length > 1) {
        const filePath = urlParts[1];
        await supabase.storage.from('trip-images').remove([filePath]);
      }

      // Update trip via backend API
      await updateTrip(tripId, { coverImageUrl: null });

      setPreviewUrl(null);
      onImageRemoved?.();
    } catch (err) {
      console.error('Remove error:', err);
      setError('Failed to remove image');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClick = () => {
    if (!isUploading && !previewUrl) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className="space-y-2">
      <div
        onClick={handleClick}
        className={`
          relative ${sizeClasses[size]} rounded-lg overflow-hidden
          border-2 border-dashed transition-all
          ${
            previewUrl
              ? 'border-transparent'
              : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500 cursor-pointer'
          }
          ${isUploading ? 'opacity-50' : ''}
        `}
      >
        {previewUrl ? (
          <>
            <Image
              src={previewUrl}
              alt="Trip cover"
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 300px"
            />
            {/* Remove button */}
            {!isUploading && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveImage();
                }}
                className="absolute top-2 right-2 p-1.5 rounded-full bg-black/50 hover:bg-black/70 text-white transition-colors"
                aria-label="Remove image"
              >
                <X size={16} />
              </button>
            )}
            {/* Change image overlay */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="absolute inset-0 bg-black/0 hover:bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-all cursor-pointer"
            >
              <span className="text-white text-sm font-medium">Change Image</span>
            </div>
          </>
        ) : (
          <div className="h-full w-full flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-800/50">
            {isUploading ? (
              <Loader2 className="h-8 w-8 text-slate-400 animate-spin" />
            ) : (
              <>
                <div className="p-3 rounded-full bg-slate-100 dark:bg-slate-700 mb-2">
                  <Plus className="h-6 w-6 text-slate-500 dark:text-slate-400" />
                </div>
                <span className="text-sm text-slate-500 dark:text-slate-400">Add Cover Image</span>
              </>
            )}
          </div>
        )}

        {/* Loading overlay */}
        {isUploading && previewUrl && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <Loader2 className="h-8 w-8 text-white animate-spin" />
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Error message */}
      {error && <p className="text-sm text-red-500 dark:text-red-400">{error}</p>}

      {/* Helper text */}
      {!previewUrl && !error && (
        <p className="text-xs text-slate-400 dark:text-slate-500">
          JPEG, PNG, WebP or GIF. Max 5MB.
        </p>
      )}
    </div>
  );
}

/**
 * Compact version for inline use (e.g., in cards)
 */
export function TripImageUploadCompact({
  tripId,
  currentImageUrl,
  onImageUploaded,
}: Omit<TripImageUploadProps, 'size' | 'onImageRemoved'>) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!validTypes.includes(file.type) || file.size > 5 * 1024 * 1024) return;

    setIsUploading(true);
    try {
      const supabase = createClient();
      const fileExt = file.name.split('.').pop();
      const fileName = `${tripId}/${Date.now()}.${fileExt}`;

      const { error: uploadError } = await supabase.storage
        .from('trip-images')
        .upload(fileName, file, { cacheControl: '3600', upsert: true });

      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from('trip-images').getPublicUrl(fileName);

      // Update trip via backend API
      await updateTrip(tripId, { coverImageUrl: urlData.publicUrl });

      onImageUploaded(urlData.publicUrl);
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <>
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        className="p-2 rounded-full bg-white/80 dark:bg-slate-800/80 hover:bg-white dark:hover:bg-slate-700 shadow-md transition-all disabled:opacity-50"
        aria-label="Upload cover image"
      >
        {isUploading ? (
          <Loader2 size={20} className="text-slate-600 dark:text-slate-300 animate-spin" />
        ) : currentImageUrl ? (
          <ImageIcon size={20} className="text-slate-600 dark:text-slate-300" />
        ) : (
          <Plus size={20} className="text-slate-600 dark:text-slate-300" />
        )}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleFileSelect}
        className="hidden"
      />
    </>
  );
}
