import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { VisaRequirementsSection } from '@/components/report/VisaRequirementsSection';
import { EntryConditionsSection } from '@/components/report/EntryConditionsSection';
import { TipsAndWarningsSection } from '@/components/report/TipsAndWarningsSection';
import { SourceAttribution } from '@/components/report/SourceAttribution';
import { WarningBanner } from '@/components/report/WarningBanner';
import { VisaReportLoadingSkeleton, VisaErrorState } from '@/components/report/VisaLoadingState';
import { ConfidenceStamp } from '@/components/report/ConfidenceBadge';
import type { VisaIntelligence } from '@/types/visa';

interface TripReportPageProps {
  params: Promise<{ id: string }>;
}

interface TripData {
  id: string;
  destination_city: string;
  destination_country: string;
  [key: string]: unknown; // Allow other properties from the database
}

// Mock data for development (replace with API call)
const getMockVisaData = (tripId: string): VisaIntelligence => {
  return {
    tripId,
    generatedAt: new Date().toISOString(),
    userNationality: 'US',
    destinationCountry: 'FR',
    destinationCity: 'Paris',
    tripPurpose: 'tourism',
    durationDays: 14,
    visaRequirement: {
      visaRequired: false,
      visaType: 'Visa-Free (Schengen)',
      visaCategory: 'visa-free',
      maxStayDays: 90,
      maxStayDuration: '90 days within 180 days',
      multipleEntry: true,
      confidenceLevel: 'official',
    },
    applicationProcess: {
      applicationMethod: 'not_required',
      processingTime: 'N/A',
      costUsd: 0,
    },
    entryRequirements: {
      passportValidity: 'Must be valid for at least 3 months beyond your planned departure date',
      passportValidityMonths: 3,
      blankPagesRequired: 2,
      vaccinations: [],
      returnTicket: true,
      proofOfAccommodation: true,
      proofOfFunds: true,
      otherRequirements: [
        'Travel health insurance with minimum coverage of €30,000',
        'ETIAS authorization required starting 2025',
      ],
    },
    tips: [
      'No visa required for stays up to 90 days for tourism or business',
      'You can travel freely within the Schengen Area during your stay',
      'Ensure your passport has at least 3 months validity beyond your departure date',
      'Keep proof of return travel and accommodation bookings with you',
    ],
    warnings: [
      'ETIAS (European Travel Information and Authorization System) will be required starting 2025 - apply online before travel',
    ],
    confidenceScore: 0.95,
    sources: [
      {
        name: 'U.S. Department of State - France Travel Advisory',
        url: 'https://travel.state.gov/content/travel/en/international-travel/International-Travel-Country-Information-Pages/France.html',
        type: 'government',
        lastVerified: new Date().toISOString(),
      },
      {
        name: 'Embassy of France in the United States',
        url: 'https://fr.usembassy.gov/',
        type: 'embassy',
        lastVerified: new Date().toISOString(),
      },
      {
        name: 'Schengen Visa Info',
        url: 'https://www.schengenvisainfo.com/',
        type: 'third-party',
        lastVerified: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
      },
    ],
    lastVerified: new Date().toISOString(),
    isPartialData: false,
  };
};

async function getTripData(tripId: string): Promise<{ trip: TripData; visaData: VisaIntelligence } | null> {
  const supabase = await createClient();

  // Get trip basic info
  const { data: trip, error: tripError } = await supabase
    .from('trips')
    .select('*')
    .eq('id', tripId)
    .single();

  if (tripError || !trip) {
    return null;
  }

  // TODO: Fetch visa report from backend API
  // For now, return mock data
  const visaData = getMockVisaData(tripId);

  return {
    trip: trip as TripData,
    visaData,
  };
}

export default async function TripReportPage({ params }: TripReportPageProps) {
  const { id } = await params;
  const data = await getTripData(id);

  if (!data) {
    notFound();
  }

  const { trip, visaData } = data;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Page Header */}
        <div className="flex items-start justify-between gap-6">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-2">
              Travel Intelligence Report
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              {trip.destination_city}, {trip.destination_country}
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-500 mt-1">
              Generated {new Date(visaData.generatedAt).toLocaleDateString()} · Trip ID: {trip.id.slice(0, 8)}
            </p>
          </div>

          {/* Confidence Stamp */}
          <ConfidenceStamp
            level={visaData.visaRequirement.confidenceLevel}
            score={visaData.confidenceScore}
            size="xl"
          />
        </div>

        {/* Partial Data Warning */}
        {visaData.isPartialData && (
          <WarningBanner
            variant="warning"
            title="Incomplete Visa Information"
            message="We couldn't find complete visa information for this destination. Please verify requirements with the embassy before traveling."
            action={{
              label: 'Contact Embassy',
              onClick: () => {
                // TODO: Implement embassy contact modal
                console.log('Contact embassy');
              },
            }}
          />
        )}

        {/* Main Content */}
        <Suspense fallback={<VisaReportLoadingSkeleton />}>
          <div className="space-y-6">
            {/* Visa Requirements */}
            <VisaRequirementsSection data={visaData} />

            {/* Entry Conditions */}
            <EntryConditionsSection data={visaData} />

            {/* Tips and Warnings */}
            <TipsAndWarningsSection data={visaData} />

            {/* Detailed Sources */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border-2 border-slate-200 dark:border-slate-800 p-6">
              <SourceAttribution sources={visaData.sources} variant="detailed" />
            </div>

            {/* Metadata */}
            <div className="bg-slate-100 dark:bg-slate-900/50 rounded-lg p-4 border border-slate-200 dark:border-slate-800">
              <div className="flex flex-wrap items-center gap-6 text-xs text-slate-600 dark:text-slate-400">
                <div>
                  <span className="font-semibold">Last Verified:</span>{' '}
                  {new Date(visaData.lastVerified).toLocaleString()}
                </div>
                <div>
                  <span className="font-semibold">Confidence Score:</span>{' '}
                  {Math.round(visaData.confidenceScore * 100)}%
                </div>
                <div>
                  <span className="font-semibold">Sources:</span> {visaData.sources.length} official
                </div>
              </div>
            </div>
          </div>
        </Suspense>
      </div>
    </div>
  );
}
