# Supabase Storage Setup for Profile Photos

## Required Storage Bucket

The profile photo upload feature requires a Supabase Storage bucket named `profile-photos`.

### Setup Instructions

1. **Go to Supabase Dashboard**
   - Navigate to your project: https://supabase.com/dashboard
   - Go to **Storage** in the left sidebar

2. **Create the Bucket**
   - Click "New bucket"
   - Bucket name: `profile-photos`
   - Public bucket: **Yes** (photos need to be publicly accessible)
   - File size limit: 5 MB (enforced in frontend)
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`

3. **Set Up Storage Policies**

   Run these SQL commands in the SQL Editor:

   ```sql
   -- Policy: Allow authenticated users to upload their own photos
   CREATE POLICY "Users can upload their own profile photos"
   ON storage.objects FOR INSERT
   TO authenticated
   WITH CHECK (
     bucket_id = 'profile-photos' AND
     (storage.foldername(name))[1] = 'avatars'
   );

   -- Policy: Allow public read access to all photos
   CREATE POLICY "Profile photos are publicly accessible"
   ON storage.objects FOR SELECT
   TO public
   USING (bucket_id = 'profile-photos');

   -- Policy: Allow users to update their own photos
   CREATE POLICY "Users can update their own profile photos"
   ON storage.objects FOR UPDATE
   TO authenticated
   USING (bucket_id = 'profile-photos')
   WITH CHECK (bucket_id = 'profile-photos');

   -- Policy: Allow users to delete their own photos
   CREATE POLICY "Users can delete their own profile photos"
   ON storage.objects FOR DELETE
   TO authenticated
   USING (bucket_id = 'profile-photos');
   ```

4. **Bucket Structure**

   Photos will be stored in the following structure:
   ```
   profile-photos/
   └── avatars/
       ├── 1234567890-abc123.jpg
       ├── 1234567891-def456.png
       └── ...
   ```

   Each file is named with:
   - Timestamp (milliseconds)
   - Random string (for uniqueness)
   - Original file extension

5. **File Size and Type Restrictions**

   Frontend enforces:
   - Maximum file size: 5 MB
   - Accepted formats: JPG, PNG, WebP, GIF
   - Files are validated before upload

6. **Public URL Format**

   After upload, photos are accessible at:
   ```
   https://[project-ref].supabase.co/storage/v1/object/public/profile-photos/avatars/[filename]
   ```

## Testing

1. Login to the app
2. Go to Profile Settings
3. Click on the profile photo upload area
4. Select an image file (< 5 MB)
5. Photo should upload and display immediately
6. URL should be saved to `user_profiles.avatar_url`

## Troubleshooting

### Upload Fails with "Bucket not found"
- Verify the bucket `profile-photos` exists in Supabase Storage
- Check that the bucket is set to "Public"

### Upload Fails with "Permission denied"
- Check that storage policies are correctly configured
- Verify user is authenticated (has valid Supabase session)

### Photo doesn't display after upload
- Check that the bucket is set to "Public"
- Verify the public access policy is enabled
- Check browser console for CORS errors

## Security Considerations

- Photos are publicly accessible (required for display)
- Users can only upload to their own folder structure
- File size limits prevent storage abuse
- RLS policies prevent unauthorized uploads
- Original filenames are replaced with timestamps for privacy
