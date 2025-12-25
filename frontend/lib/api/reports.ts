import { createClient } from '@/lib/supabase/client';

/**
 * Export trip report as PDF
 * Note: This requires backend implementation of PDF generation
 */
export async function exportTripReportPDF(
  tripId: string,
): Promise<{ success: boolean; url?: string; error?: string }> {
  try {
    const supabase = createClient();

    // Get the auth token
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) {
      return { success: false, error: 'Not authenticated' };
    }

    // Call backend PDF generation endpoint
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/trips/${tripId}/report/pdf`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      },
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'PDF generation failed' }));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();

    // If backend returns a URL to download the PDF
    if (data.pdf_url) {
      return {
        success: true,
        url: data.pdf_url,
      };
    }

    // If backend returns PDF blob directly
    if (response.headers.get('content-type')?.includes('application/pdf')) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      return {
        success: true,
        url,
      };
    }

    return {
      success: false,
      error: 'Invalid response from server',
    };
  } catch (error) {
    console.error('Error exporting PDF:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to export PDF',
    };
  }
}

/**
 * Delete a trip and all associated data
 */
export async function deleteTrip(tripId: string): Promise<{
  success: boolean;
  error?: string;
}> {
  try {
    const supabase = createClient();

    // Delete trip from database (cascade will delete related data)
    const { error } = await supabase.from('trips').delete().eq('id', tripId);

    if (error) {
      console.error('Error deleting trip:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete trip',
      };
    }

    // Also call backend to clean up report sections and any cached data
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (session) {
      try {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/trips/${tripId}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });
      } catch (backendError) {
        // Log but don't fail if backend cleanup fails
        console.warn('Backend cleanup failed:', backendError);
      }
    }

    return { success: true };
  } catch (error) {
    console.error('Error deleting trip:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to delete trip',
    };
  }
}

/**
 * Share trip report via shareable link
 * Note: This requires backend implementation
 */
export async function shareTripReport(tripId: string): Promise<{
  success: boolean;
  shareUrl?: string;
  error?: string;
}> {
  try {
    const supabase = createClient();

    // Get the auth token
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) {
      return { success: false, error: 'Not authenticated' };
    }

    // Call backend to generate shareable link
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/trips/${tripId}/share`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Share failed' }));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();

    if (data.share_url) {
      return {
        success: true,
        shareUrl: data.share_url,
      };
    }

    return {
      success: false,
      error: 'Invalid response from server',
    };
  } catch (error) {
    console.error('Error sharing trip:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to share trip',
    };
  }
}
