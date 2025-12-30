'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { Loader2, Settings, History } from 'lucide-react';
import { TripReportLayout } from '@/components/report/TripReportLayout';
import {
  TripEditForm,
  RecalculationStatus,
  VersionHistory,
  DiffView,
  ChangeConfirmDialog,
  RestoreDialog,
} from '@/components/trip-update';
import { Button } from '@/components/ui/button';
import {
  getTrip,
  updateTrip,
  getVersionHistory,
  restoreVersion as restoreVersionApi,
  getRecalculationStatus,
  startRecalculation,
  cancelRecalculation,
  calculateLocalChanges,
} from '@/lib/api/trips';
import type {
  TripData,
  TripUpdateData,
  TripVersion,
  RecalculationProgress,
  ChangePreviewData,
} from '@/types/trip-update';
import { FIELD_IMPACT_MAP, REPORT_SECTIONS } from '@/types/trip-update';

type ViewMode = 'edit' | 'history';

export default function TripOverviewPage() {
  const params = useParams();
  const tripId = params.id as string;

  // Data state
  const [trip, setTrip] = useState<TripData | null>(null);
  const [versions, setVersions] = useState<TripVersion[]>([]);
  const [currentVersion, setCurrentVersion] = useState(1);
  const [recalcProgress, setRecalcProgress] = useState<RecalculationProgress>({
    status: 'idle',
    currentAgent: null,
    completedAgents: [],
    failedAgents: [],
    progress: 0,
    startedAt: null,
    completedAt: null,
    estimatedTimeRemaining: null,
    error: null,
  });

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('edit');
  const [pendingPreview, setPendingPreview] = useState<ChangePreviewData | null>(null);

  // Dialog state
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [showRestoreDialog, setShowRestoreDialog] = useState(false);
  const [showDiffView, setShowDiffView] = useState(false);
  const [selectedRestoreVersion, setSelectedRestoreVersion] = useState<TripVersion | null>(null);
  const [compareVersions, setCompareVersions] = useState<{
    a: number;
    b: number;
    dataA?: TripData;
    dataB?: TripData;
  } | null>(null);

  // Load trip data
  const loadTripData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [tripData, versionData] = await Promise.all([
        getTrip(tripId),
        getVersionHistory(tripId).catch(() => ({
          versions: [],
          totalCount: 0,
          currentVersion: 1,
        })),
      ]);

      setTrip(tripData);
      setVersions(versionData.versions);
      setCurrentVersion(versionData.currentVersion);

      // Check for ongoing recalculation
      try {
        const recalcStatus = await getRecalculationStatus(tripId);
        setRecalcProgress(recalcStatus);
      } catch {
        // No active recalculation
      }
    } catch (err) {
      console.error('Error loading trip:', err);
      setError(err instanceof Error ? err.message : 'Failed to load trip');
    } finally {
      setIsLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    loadTripData();
  }, [loadTripData]);

  // Poll recalculation status when processing
  useEffect(() => {
    if (recalcProgress.status !== 'processing' && recalcProgress.status !== 'queued') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const status = await getRecalculationStatus(tripId);
        setRecalcProgress(status);

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          // Refresh trip data after recalculation
          if (status.status === 'completed') {
            await loadTripData();
          }
        }
      } catch (err) {
        console.error('Error polling recalc status:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [tripId, recalcProgress.status, loadTripData]);

  // Build preview data from pending changes
  const buildPreviewData = useCallback(
    (updates: TripUpdateData): ChangePreviewData | null => {
      if (!trip) return null;

      const changes = calculateLocalChanges(trip, updates, FIELD_IMPACT_MAP);
      if (changes.length === 0) return null;

      // Calculate affected sections
      const affectedSectionsSet = new Set<string>();
      const impactLevels = { low: 1, medium: 2, high: 3 };
      let maxImpactScore = 1;

      changes.forEach((change) => {
        const fieldInfo = FIELD_IMPACT_MAP[change.field];
        if (fieldInfo) {
          fieldInfo.affectedSections.forEach((s) => affectedSectionsSet.add(s));
          const score = impactLevels[fieldInfo.impactLevel];
          if (score > maxImpactScore) {
            maxImpactScore = score;
          }
        }
      });

      const highestImpact = maxImpactScore === 3 ? 'high' : maxImpactScore === 2 ? 'medium' : 'low';

      const affectedSections = Array.from(affectedSectionsSet);
      const requiresRecalculation = affectedSections.length > 0;

      return {
        changes,
        impact: {
          affectedSections,
          requiresRecalculation,
          estimatedRecalcTime: affectedSections.length * 15,
          impactSummary:
            highestImpact === 'high'
              ? 'Major changes - full recalculation recommended'
              : highestImpact === 'medium'
                ? 'Moderate changes - partial recalculation needed'
                : 'Minor changes - minimal impact',
        },
        canApply: true,
        warnings: [],
      };
    },
    [trip],
  );

  // Handlers
  const handleSave = async (updates: TripUpdateData) => {
    const preview = buildPreviewData(updates);
    if (preview) {
      setPendingPreview(preview);
      setShowConfirmDialog(true);
    }
  };

  const handlePreview = (updates: TripUpdateData) => {
    const preview = buildPreviewData(updates);
    if (preview) {
      setPendingPreview(preview);
      setShowConfirmDialog(true);
    }
  };

  const handleConfirmChanges = async (options: { triggerRecalculation: boolean }) => {
    if (!pendingPreview || !trip) return;

    // Extract updates from changes
    const updates: TripUpdateData = {};
    pendingPreview.changes.forEach((change) => {
      (updates as Record<string, unknown>)[change.field] = change.newValue;
    });

    const result = await updateTrip(tripId, updates);

    setTrip(result.trip);
    if (result.version) {
      setVersions((prev) => [result.version, ...prev]);
      setCurrentVersion(result.version.versionNumber);
    }

    if (options.triggerRecalculation && result.recalculation) {
      setRecalcProgress(result.recalculation);
    } else if (options.triggerRecalculation && pendingPreview.impact.affectedSections.length) {
      const recalc = await startRecalculation(tripId, pendingPreview.impact.affectedSections);
      setRecalcProgress(recalc);
    }

    setPendingPreview(null);
  };

  const handleCancelRecalculation = async () => {
    try {
      await cancelRecalculation(tripId);
      setRecalcProgress((prev) => ({ ...prev, status: 'cancelled' }));
    } catch (err) {
      console.error('Error cancelling recalculation:', err);
    }
  };

  const handleRetryRecalculation = async () => {
    try {
      const recalc = await startRecalculation(tripId);
      setRecalcProgress(recalc);
    } catch (err) {
      console.error('Error retrying recalculation:', err);
    }
  };

  const handleViewVersion = (version: TripVersion) => {
    console.log('View version:', version);
  };

  const handleRestoreVersion = (version: TripVersion) => {
    setSelectedRestoreVersion(version);
    setShowRestoreDialog(true);
  };

  const handleConfirmRestore = async () => {
    if (!selectedRestoreVersion) return;

    const result = await restoreVersionApi(tripId, selectedRestoreVersion.versionNumber);

    if (result.success) {
      await loadTripData();
      setShowRestoreDialog(false);
      setSelectedRestoreVersion(null);
    }
  };

  const handleCompareVersions = async (versionA: number, versionB: number) => {
    const versionAData = versions.find((v) => v.versionNumber === versionA)?.snapshot;
    const versionBData = versions.find((v) => v.versionNumber === versionB)?.snapshot;

    if (versionAData && versionBData) {
      setCompareVersions({
        a: versionA,
        b: versionB,
        dataA: versionAData,
        dataB: versionBData,
      });
      setShowDiffView(true);
    }
  };

  if (isLoading) {
    return (
      <TripReportLayout tripId={tripId} tripName="Loading..." currentSection="overview">
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </TripReportLayout>
    );
  }

  if (error || !trip) {
    return (
      <TripReportLayout tripId={tripId} tripName="Error" currentSection="overview">
        <div className="rounded-lg border-2 border-red-200 bg-red-50 p-8 text-center dark:border-red-800 dark:bg-red-950/30">
          <p className="text-red-600 dark:text-red-400">{error || 'Trip not found'}</p>
          <Button onClick={loadTripData} className="mt-4" variant="outline">
            Retry
          </Button>
        </div>
      </TripReportLayout>
    );
  }

  const tripName = `${trip.destinationCity}, ${trip.destinationCountry}`;

  return (
    <TripReportLayout tripId={tripId} tripName={tripName} currentSection="overview">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Page Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">Trip Overview</h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              Manage trip details and view version history
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
            <button
              onClick={() => setViewMode('edit')}
              className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors ${
                viewMode === 'edit'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            >
              <Settings className="h-4 w-4" />
              Edit
            </button>
            <button
              onClick={() => setViewMode('history')}
              className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors ${
                viewMode === 'history'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            >
              <History className="h-4 w-4" />
              History
            </button>
          </div>
        </div>

        {/* Recalculation Status */}
        {recalcProgress.status !== 'idle' && (
          <RecalculationStatus
            progress={recalcProgress}
            onCancel={handleCancelRecalculation}
            onRetry={handleRetryRecalculation}
          />
        )}

        {/* Main Content */}
        {viewMode === 'edit' ? (
          <div className="space-y-6">
            {/* Edit Form */}
            <TripEditForm trip={trip} onSave={handleSave} onPreview={handlePreview} />

            {/* Report Sections Info */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                Report Sections
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                Available report sections that can be recalculated when trip details change
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {REPORT_SECTIONS.map((section) => (
                  <div
                    key={section.id}
                    className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700"
                  >
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      {section.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Version History View */
          <VersionHistory
            versions={versions}
            currentVersion={currentVersion}
            onViewVersion={handleViewVersion}
            onRestoreVersion={handleRestoreVersion}
            onCompareVersions={handleCompareVersions}
          />
        )}
      </div>

      {/* Confirm Changes Dialog */}
      {pendingPreview && (
        <ChangeConfirmDialog
          open={showConfirmDialog}
          onOpenChange={setShowConfirmDialog}
          preview={pendingPreview}
          onConfirm={handleConfirmChanges}
          tripName={tripName}
        />
      )}

      {/* Restore Version Dialog */}
      {selectedRestoreVersion && (
        <RestoreDialog
          open={showRestoreDialog}
          onOpenChange={setShowRestoreDialog}
          version={selectedRestoreVersion}
          currentVersion={currentVersion}
          onConfirm={handleConfirmRestore}
        />
      )}

      {/* Diff View Modal */}
      {showDiffView && compareVersions?.dataA && compareVersions?.dataB && (
        <DiffView
          versionA={{ number: compareVersions.a, data: compareVersions.dataA }}
          versionB={{ number: compareVersions.b, data: compareVersions.dataB }}
          onClose={() => {
            setShowDiffView(false);
            setCompareVersions(null);
          }}
        />
      )}
    </TripReportLayout>
  );
}
