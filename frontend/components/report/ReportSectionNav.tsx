'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText, Globe, MapPin, Download, Share2, Trash2, ChevronRight } from 'lucide-react';

interface ReportSection {
  id: string;
  name: string;
  href: string;
  icon: React.ElementType;
  description: string;
}

interface ReportSectionNavProps {
  tripId: string;
  currentSection?: 'visa' | 'destination' | 'itinerary';
  onExportPDF?: () => void;
  onShare?: () => void;
  onDelete?: () => void;
  showActions?: boolean;
}

export function ReportSectionNav({
  tripId,
  currentSection,
  onExportPDF,
  onShare,
  onDelete,
  showActions = true,
}: ReportSectionNavProps) {
  const pathname = usePathname();

  const sections: ReportSection[] = [
    {
      id: 'visa',
      name: 'Visa Intelligence',
      href: `/trips/${tripId}`,
      icon: FileText,
      description: 'Entry requirements & visa information',
    },
    {
      id: 'destination',
      name: 'Destination Intelligence',
      href: `/trips/${tripId}/destination`,
      icon: Globe,
      description: 'Country info, weather, culture & food',
    },
    {
      id: 'itinerary',
      name: 'Travel Itinerary',
      href: `/trips/${tripId}/itinerary`,
      icon: MapPin,
      description: 'Day-by-day plan & activities',
    },
  ];

  // Determine active section from pathname if not explicitly provided
  const activeSection =
    currentSection ||
    (pathname === `/trips/${tripId}`
      ? 'visa'
      : pathname.includes('/destination')
        ? 'destination'
        : pathname.includes('/itinerary')
          ? 'itinerary'
          : 'visa');

  return (
    <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Section Tabs */}
          <nav className="flex -mb-px space-x-8 overflow-x-auto py-4" aria-label="Report sections">
            {sections.map((section) => {
              const isActive = activeSection === section.id;
              const Icon = section.icon;

              return (
                <Link
                  key={section.id}
                  href={section.href}
                  className={`group inline-flex items-center gap-2 py-2 px-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                    isActive
                      ? 'border-blue-600 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-300 dark:hover:border-slate-700'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon
                    className={`h-5 w-5 ${
                      isActive
                        ? 'text-blue-600 dark:text-blue-400'
                        : 'text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300'
                    }`}
                  />
                  <span className="hidden sm:inline">{section.name}</span>
                  <span className="sm:hidden">{section.name.split(' ')[0]}</span>
                </Link>
              );
            })}
          </nav>

          {/* Action Buttons */}
          {showActions && (
            <div className="flex items-center gap-2 pl-4 border-l border-slate-200 dark:border-slate-800">
              {/* Export PDF */}
              {onExportPDF && (
                <button
                  onClick={onExportPDF}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  title="Export to PDF"
                >
                  <Download className="h-4 w-4" />
                  <span className="hidden md:inline">Export</span>
                </button>
              )}

              {/* Share */}
              {onShare && (
                <button
                  onClick={onShare}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  title="Share report"
                >
                  <Share2 className="h-4 w-4" />
                  <span className="hidden md:inline">Share</span>
                </button>
              )}

              {/* Delete */}
              {onDelete && (
                <button
                  onClick={onDelete}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                  title="Delete trip"
                >
                  <Trash2 className="h-4 w-4" />
                  <span className="hidden md:inline">Delete</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Active Section Description (Mobile) */}
        <div className="sm:hidden pb-3 text-xs text-slate-600 dark:text-slate-400">
          {sections.find((s) => s.id === activeSection)?.description}
        </div>
      </div>
    </div>
  );
}

// Breadcrumb navigation for report pages
interface ReportBreadcrumbProps {
  tripId: string;
  tripName?: string;
  currentSection: 'visa' | 'destination' | 'itinerary';
}

export function ReportBreadcrumb({ tripId, tripName, currentSection }: ReportBreadcrumbProps) {
  const sectionNames = {
    visa: 'Visa Intelligence',
    destination: 'Destination Intelligence',
    itinerary: 'Travel Itinerary',
  };

  return (
    <nav className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400 mb-4">
      <Link
        href="/trips"
        className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
      >
        My Trips
      </Link>
      <ChevronRight className="h-4 w-4" />
      <Link
        href={`/trips/${tripId}`}
        className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors max-w-[200px] truncate"
      >
        {tripName || `Trip ${tripId.slice(0, 8)}`}
      </Link>
      <ChevronRight className="h-4 w-4" />
      <span className="text-slate-900 dark:text-slate-100 font-medium">
        {sectionNames[currentSection]}
      </span>
    </nav>
  );
}
