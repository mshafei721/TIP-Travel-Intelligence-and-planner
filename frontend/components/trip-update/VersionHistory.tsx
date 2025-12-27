'use client';

import { useState } from 'react';
import {
  History,
  User,
  Bot,
  Settings,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Eye,
  GitCompare,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { TripVersion } from '@/types/trip-update';

interface VersionHistoryProps {
  versions: TripVersion[];
  currentVersion: number;
  onViewVersion: (version: TripVersion) => void;
  onRestoreVersion: (version: TripVersion) => void;
  onCompareVersions: (versionA: number, versionB: number) => void;
}

const CREATOR_ICONS: Record<string, React.ElementType> = {
  user: User,
  system: Settings,
  ai: Bot,
};

const CREATOR_LABELS: Record<string, string> = {
  user: 'Manual Edit',
  system: 'System Update',
  ai: 'AI Recalculation',
};

/**
 * VersionHistory - Shows version history with restore capability
 */
export function VersionHistory({
  versions,
  currentVersion,
  onViewVersion,
  onRestoreVersion,
  onCompareVersions,
}: VersionHistoryProps) {
  const [expandedVersions, setExpandedVersions] = useState<Set<string>>(new Set());
  const [compareMode, setCompareMode] = useState(false);
  const [compareSelection, setCompareSelection] = useState<number[]>([]);

  const toggleExpand = (versionId: string) => {
    setExpandedVersions((prev) => {
      const next = new Set(prev);
      if (next.has(versionId)) {
        next.delete(versionId);
      } else {
        next.add(versionId);
      }
      return next;
    });
  };

  const handleCompareClick = (versionNumber: number) => {
    if (!compareMode) return;

    setCompareSelection((prev) => {
      if (prev.includes(versionNumber)) {
        return prev.filter((v) => v !== versionNumber);
      }
      if (prev.length < 2) {
        return [...prev, versionNumber];
      }
      // Replace oldest selection
      return [prev[1], versionNumber];
    });
  };

  const handleStartCompare = () => {
    if (compareSelection.length === 2) {
      onCompareVersions(Math.min(...compareSelection), Math.max(...compareSelection));
      setCompareMode(false);
      setCompareSelection([]);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (versions.length === 0) {
    return (
      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-6 text-center">
        <History className="h-8 w-8 text-slate-400 mx-auto mb-2" />
        <p className="text-slate-600 dark:text-slate-400">No version history available</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-slate-500" />
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">Version History</h3>
          <Badge variant="secondary" className="text-xs">
            {versions.length} versions
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {compareMode ? (
            <>
              <span className="text-sm text-slate-500">{compareSelection.length}/2 selected</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setCompareMode(false);
                  setCompareSelection([]);
                }}
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleStartCompare}
                disabled={compareSelection.length !== 2}
              >
                <GitCompare className="h-4 w-4 mr-1" />
                Compare
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCompareMode(true)}
              disabled={versions.length < 2}
            >
              <GitCompare className="h-4 w-4 mr-1" />
              Compare Versions
            </Button>
          )}
        </div>
      </div>

      {/* Version List */}
      <div className="divide-y divide-slate-200 dark:divide-slate-800 max-h-[400px] overflow-y-auto">
        {versions.map((version) => {
          const isExpanded = expandedVersions.has(version.id);
          const isCurrent = version.version_number === currentVersion;
          const isSelected = compareSelection.includes(version.version_number);
          const CreatorIcon = CREATOR_ICONS[version.created_by] || User;

          return (
            <div
              key={version.id}
              className={`${
                compareMode
                  ? isSelected
                    ? 'bg-blue-50 dark:bg-blue-950/30'
                    : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer'
                  : ''
              }`}
              onClick={compareMode ? () => handleCompareClick(version.version_number) : undefined}
            >
              {/* Version Header */}
              <div className="flex items-center gap-3 p-4">
                {/* Compare Selection Indicator */}
                {compareMode && (
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                      isSelected
                        ? 'bg-blue-600 border-blue-600'
                        : 'border-slate-300 dark:border-slate-600'
                    }`}
                  >
                    {isSelected && <CheckCircle className="h-3 w-3 text-white" />}
                  </div>
                )}

                {/* Version Number */}
                <div className="flex-shrink-0">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      isCurrent
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    v{version.version_number}
                  </div>
                </div>

                {/* Version Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900 dark:text-slate-100">
                      {version.change_summary || 'Changes saved'}
                    </span>
                    {isCurrent && (
                      <Badge className="bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400">
                        Current
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-sm text-slate-500 dark:text-slate-400">
                    <span className="flex items-center gap-1">
                      <CreatorIcon className="h-3 w-3" />
                      {CREATOR_LABELS[version.created_by]}
                    </span>
                    <span>{formatDate(version.created_at)}</span>
                    {version.changed_fields.length > 0 && (
                      <span>
                        {version.changed_fields.length} field
                        {version.changed_fields.length !== 1 ? 's' : ''} changed
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                {!compareMode && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewVersion(version);
                      }}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    {!isCurrent && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRestoreVersion(version);
                        }}
                      >
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpand(version.id);
                      }}
                    >
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                )}
              </div>

              {/* Expanded Details */}
              {isExpanded && !compareMode && (
                <div className="px-4 pb-4 pl-16">
                  <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-3">
                    <h5 className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">
                      Changed Fields
                    </h5>
                    {version.changed_fields.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {version.changed_fields.map((field) => (
                          <Badge key={field} variant="secondary" className="text-xs">
                            {field.replace(/_/g, ' ')}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500">No fields changed (initial version)</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default VersionHistory;
