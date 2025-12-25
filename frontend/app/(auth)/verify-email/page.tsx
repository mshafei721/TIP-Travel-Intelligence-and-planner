'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { EmailVerificationPage } from '@/components/auth';
import { createClient } from '@/lib/supabase/client';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';

  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const handleVerify = async () => {
    setIsLoading(true);

    try {
      const supabase = createClient();

      // Verify the email using the token from the URL
      // Supabase handles this automatically when the user clicks the link
      const { error: verifyError } = await supabase.auth.verifyOtp({
        token_hash: token,
        type: 'email',
      });

      if (verifyError) {
        setError(verifyError.message);
      } else {
        setSuccess(true);
      }
    } catch {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
        <div className="w-full max-w-md space-y-8">
          <div className="rounded-lg border border-red-200 bg-red-50 p-8 shadow-sm">
            <p className="text-center text-red-600">
              Invalid verification link. Please check your email for the correct link.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
          <EmailVerificationPage
            onVerify={handleVerify}
            isLoading={isLoading}
            success={success}
            error={error}
          />
        </div>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
