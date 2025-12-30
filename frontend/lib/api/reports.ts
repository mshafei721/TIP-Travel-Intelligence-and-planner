import { createClient } from '@/lib/supabase/client';

/**
 * Trip generation status response
 */
export interface TripGenerationStatus {
  status: 'draft' | 'pending' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  current_agent: string | null;
  agents_completed: string[];
  agents_failed: string[];
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

/**
 * Start AI report generation for a trip
 */
export async function generateTripReport(tripId: string): Promise<{
  success: boolean;
  task_id?: string;
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

    // Call backend to start report generation
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/generate`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      },
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Generation failed' }));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();

    return {
      success: true,
      task_id: data.task_id,
    };
  } catch (error) {
    console.error('Error starting report generation:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to start generation',
    };
  }
}

/**
 * Get current report generation status for a trip
 */
export async function getTripGenerationStatus(
  tripId: string,
): Promise<{ success: boolean; status?: TripGenerationStatus; error?: string }> {
  try {
    const supabase = createClient();

    // Get the auth token
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) {
      return { success: false, error: 'Not authenticated' };
    }

    // Call backend status endpoint
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/status`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      },
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to get status' }));
      return {
        success: false,
        error: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();

    return {
      success: true,
      status: data,
    };
  } catch (error) {
    console.error('Error getting generation status:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get status',
    };
  }
}

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
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/report/pdf`,
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
 * @deprecated Use deleteTrip from '@/lib/api/trips' instead
 */
export { deleteTrip } from './trips';

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
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/trips/${tripId}/share`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      },
    );

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
