'use client';

import {
  MapPin,
  FileText,
  Calendar,
  Wallet,
  Shield,
  Globe,
  Briefcase,
  Plane,
  RefreshCw,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { REPORT_SECTIONS, type ReportSectionId } from '@/types/trip-update';

interface AffectedSectionsProps {
  sections: ReportSectionId[];
  showRecalculationHint?: boolean;
  compact?: boolean;
}

const SECTION_ICONS: Record<string, React.ElementType> = {
  visa: FileText,
  destination: MapPin,
  itinerary: Calendar,
  budget: Wallet,
  safety: Shield,
  culture: Globe,
  packing: Briefcase,
  transportation: Plane,
};

/**
 * AffectedSections - Shows which report sections will be affected by changes
 */
export function AffectedSections({
  sections,
  showRecalculationHint = true,
  compact = false,
}: AffectedSectionsProps) {
  if (sections.length === 0) {
    return null;
  }

  const affectedSectionData = REPORT_SECTIONS.filter((s) => sections.includes(s.id));

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-slate-500 dark:text-slate-500">Affects:</span>
        {affectedSectionData.map((section) => {
          const Icon = SECTION_ICONS[section.id] || RefreshCw;
          return (
            <Badge key={section.id} variant="secondary" className="text-xs gap-1">
              <Icon className="h-3 w-3" />
              {section.label}
            </Badge>
          );
        })}
      </div>
    );
  }

  return (
    <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-slate-900 dark:text-slate-100">
          Affected Report Sections
        </h4>
        <span className="text-xs text-slate-500 dark:text-slate-500">
          {sections.length} of {REPORT_SECTIONS.length} sections
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {REPORT_SECTIONS.map((section) => {
          const Icon = SECTION_ICONS[section.id] || RefreshCw;
          const isAffected = sections.includes(section.id);

          return (
            <div
              key={section.id}
              className={`flex items-center gap-2 p-2 rounded-lg border transition-colors ${
                isAffected
                  ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900'
                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 opacity-50'
              }`}
            >
              <Icon
                className={`h-4 w-4 ${
                  isAffected
                    ? 'text-amber-600 dark:text-amber-400'
                    : 'text-slate-400 dark:text-slate-600'
                }`}
              />
              <span
                className={`text-xs font-medium ${
                  isAffected
                    ? 'text-amber-800 dark:text-amber-200'
                    : 'text-slate-500 dark:text-slate-500'
                }`}
              >
                {section.label}
              </span>
            </div>
          );
        })}
      </div>

      {showRecalculationHint && sections.length > 0 && (
        <div className="mt-3 flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400">
          <RefreshCw className="h-3 w-3" />
          <span>These sections will be recalculated using AI when you save changes.</span>
        </div>
      )}
    </div>
  );
}

export default AffectedSections;
