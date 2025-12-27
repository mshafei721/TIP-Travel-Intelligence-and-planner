'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ReportSectionNav, ReportBreadcrumb } from './ReportSectionNav';
import { DeleteTripDialog } from './DeleteTripDialog';
import { exportTripReportPDF, deleteTrip, shareTripReport } from '@/lib/api/reports';
import { Loader2, CheckCircle2, XCircle, Share2, Copy } from 'lucide-react';

interface TripReportLayoutProps {
  tripId: string;
  tripName: string;
  currentSection: 'overview' | 'visa' | 'destination' | 'itinerary';
  children: React.ReactNode;
}

export function TripReportLayout({
  tripId,
  tripName,
  currentSection,
  children,
}: TripReportLayoutProps) {
  const router = useRouter();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [exportMessage, setExportMessage] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  const handleExportPDF = async () => {
    setIsExporting(true);
    setExportMessage(null);

    try {
      const result = await exportTripReportPDF(tripId);

      if (result.success && result.url) {
        // Download the PDF
        const link = document.createElement('a');
        link.href = result.url;
        link.download = `trip-report-${tripId.slice(0, 8)}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up object URL if it was created
        if (result.url.startsWith('blob:')) {
          setTimeout(() => URL.revokeObjectURL(result.url!), 1000);
        }

        setExportMessage({
          type: 'success',
          message: 'PDF exported successfully!',
        });
      } else {
        setExportMessage({
          type: 'error',
          message: result.error || 'Failed to export PDF',
        });
      }
    } catch (error) {
      console.error('Export error:', error);
      setExportMessage({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to export PDF',
      });
    } finally {
      setIsExporting(false);
      // Clear message after 5 seconds
      setTimeout(() => setExportMessage(null), 5000);
    }
  };

  const handleShare = async () => {
    setIsSharing(true);
    setShareUrl(null);

    try {
      const result = await shareTripReport(tripId);

      if (result.success && result.shareUrl) {
        setShareUrl(result.shareUrl);
      } else {
        setExportMessage({
          type: 'error',
          message: result.error || 'Failed to generate share link',
        });
        setTimeout(() => setExportMessage(null), 5000);
      }
    } catch (err) {
      console.error('Share error:', err);
      setExportMessage({
        type: 'error',
        message: err instanceof Error ? err.message : 'Failed to share trip',
      });
      setTimeout(() => setExportMessage(null), 5000);
    } finally {
      setIsSharing(false);
    }
  };

  const handleCopyShareUrl = async () => {
    if (!shareUrl) return;

    try {
      await navigator.clipboard.writeText(shareUrl);
      setExportMessage({
        type: 'success',
        message: 'Share link copied to clipboard!',
      });
      setTimeout(() => setExportMessage(null), 3000);
    } catch {
      setExportMessage({
        type: 'error',
        message: 'Failed to copy link',
      });
      setTimeout(() => setExportMessage(null), 3000);
    }
  };

  const handleDelete = async () => {
    const result = await deleteTrip(tripId);

    if (result.success) {
      // Redirect to trips list after successful deletion
      router.push('/trips?deleted=true');
    } else {
      throw new Error(result.error || 'Failed to delete trip');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Section Navigation */}
      <ReportSectionNav
        tripId={tripId}
        currentSection={currentSection}
        onExportPDF={handleExportPDF}
        onShare={handleShare}
        onDelete={() => setIsDeleteDialogOpen(true)}
        showActions={true}
      />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Breadcrumb */}
        <ReportBreadcrumb tripId={tripId} tripName={tripName} currentSection={currentSection} />

        {/* Status Messages */}
        {exportMessage && (
          <div
            className={`mb-4 p-4 rounded-lg border ${
              exportMessage.type === 'success'
                ? 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800'
            }`}
          >
            <div className="flex items-center gap-2">
              {exportMessage.type === 'success' ? (
                <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
              )}
              <p
                className={`text-sm font-medium ${
                  exportMessage.type === 'success'
                    ? 'text-green-900 dark:text-green-200'
                    : 'text-red-900 dark:text-red-200'
                }`}
              >
                {exportMessage.message}
              </p>
            </div>
          </div>
        )}

        {/* Share URL Dialog */}
        {shareUrl && (
          <div className="mb-4 p-4 rounded-lg border bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-3">
              <Share2 className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
                  Share this trip report
                </p>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={shareUrl}
                    readOnly
                    className="flex-1 px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-blue-300 dark:border-blue-700 rounded-lg text-slate-900 dark:text-slate-100"
                  />
                  <button
                    onClick={handleCopyShareUrl}
                    className="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors inline-flex items-center gap-1.5"
                  >
                    <Copy className="h-4 w-4" />
                    Copy
                  </button>
                </div>
              </div>
              <button
                onClick={() => setShareUrl(null)}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Loading Indicators */}
        {(isExporting || isSharing) && (
          <div className="mb-4 p-4 rounded-lg border bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin text-blue-600 dark:text-blue-400" />
              <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                {isExporting ? 'Generating PDF...' : 'Generating share link...'}
              </p>
            </div>
          </div>
        )}

        {/* Page Content */}
        {children}
      </div>

      {/* Delete Confirmation Dialog */}
      <DeleteTripDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDelete}
        tripName={tripName}
        tripId={tripId}
      />
    </div>
  );
}
