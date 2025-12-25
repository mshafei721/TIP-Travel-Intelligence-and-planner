'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchDestinationReport } from '@/lib/api/destination';
import { sampleDestinationData } from '@/lib/mock-data/destination-sample';
import DestinationIntelligencePage from '@/components/destination/DestinationIntelligencePage';
import LoadingState from '@/components/destination/LoadingState';
import type { DestinationIntelligence, CountryOverview } from '@/types/destination';

export default function TripDestinationPage() {
  const params = useParams();
  const tripId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [destinationData, setDestinationData] = useState<DestinationIntelligence | null>(null);

  useEffect(() => {
    async function loadDestinationReport() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchDestinationReport(tripId);

        if ('error' in result) {
          // Handle different error types
          if (result.error.type === 'REPORT_NOT_FOUND') {
            // Fallback to mock data if report not found
            console.warn('Destination report not found, using sample data');
            setDestinationData(sampleDestinationData);
          } else {
            setError(result.error.message);
          }
        } else {
          // Got real data from API
          const countryData = result.data;

          // Merge with mock data for sections not yet implemented
          // (Weather, Currency, Culture, Laws, Safety, News)
          const fullData: DestinationIntelligence = {
            countryOverview: countryData,
            weather: sampleDestinationData.weather,
            currency: sampleDestinationData.currency,
            culture: sampleDestinationData.culture,
            laws: sampleDestinationData.laws,
            safety: sampleDestinationData.safety,
            news: sampleDestinationData.news,
          };

          setDestinationData(fullData);
        }
      } catch (err) {
        console.error('Error loading destination report:', err);
        setError('Failed to load destination report');
        // Fallback to mock data on error
        setDestinationData(sampleDestinationData);
      } finally {
        setLoading(false);
      }
    }

    if (tripId) {
      loadDestinationReport();
    }
  }, [tripId]);

  if (loading) {
    return <LoadingState />;
  }

  if (error && !destinationData) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
            Error Loading Destination Report
          </h2>
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      </div>
    );
  }

  if (!destinationData) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-amber-900 dark:text-amber-200 mb-2">
            No Destination Data Available
          </h2>
          <p className="text-sm text-amber-700 dark:text-amber-300">
            Please generate a trip report first to see destination intelligence.
          </p>
        </div>
      </div>
    );
  }

  return (
    <DestinationIntelligencePage
      data={destinationData}
      callbacks={{
        onCardExpand: (cardId) => console.log('Card expanded:', cardId),
        onCardCollapse: (cardId) => console.log('Card collapsed:', cardId),
        onExternalLinkClick: (url, title) => {
          console.log('External link clicked:', title, url);
          window.open(url, '_blank', 'noopener,noreferrer');
        },
      }}
      allowMultipleExpanded={true}
    />
  );
}
