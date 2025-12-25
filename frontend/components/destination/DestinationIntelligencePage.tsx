'use client';

import { useState } from 'react';
import CountryOverviewCard from './CountryOverviewCard';
import WeatherCard from './WeatherCard';
import CurrencyCard from './CurrencyCard';
import CultureCard from './CultureCard';
import UnusualLawsCard from './UnusualLawsCard';
import SafetyCard from './SafetyCard';
import NewsCard from './NewsCard';
import type { DestinationIntelligence, DestinationCallbacks } from '@/types/destination';

interface DestinationIntelligencePageProps {
  data: DestinationIntelligence;
  isLoading?: boolean;
  callbacks?: DestinationCallbacks;
  allowMultipleExpanded?: boolean;
}

export default function DestinationIntelligencePage({
  data,
  isLoading = false,
  callbacks,
  allowMultipleExpanded = false,
}: DestinationIntelligencePageProps) {
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  const handleCardExpand = (cardId: string) => {
    if (!allowMultipleExpanded) {
      setExpandedCard(cardId);
    }
    callbacks?.onCardExpand?.(cardId);
  };

  const handleCardCollapse = (cardId: string) => {
    if (!allowMultipleExpanded) {
      setExpandedCard(null);
    }
    callbacks?.onCardCollapse?.(cardId);
  };

  const handleLinkClick = (url: string, title: string) => {
    callbacks?.onExternalLinkClick?.(url, title);
  };

  const isCardExpanded = (cardId: string): boolean => {
    return allowMultipleExpanded ? false : expandedCard === cardId;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-3">
          Destination Intelligence
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400">
          Everything you need to know about {data.countryOverview.name}
        </p>
      </div>

      {/* Cards grid - Masonry layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 auto-rows-max">
        {/* Country Overview - spans 2 columns on xl */}
        <div className="xl:col-span-2">
          <CountryOverviewCard
            data={data.countryOverview}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('country-overview')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
            onLinkClick={handleLinkClick}
          />
        </div>

        {/* Weather Card */}
        <div>
          <WeatherCard
            data={data.weather}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('weather')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
          />
        </div>

        {/* Currency Card */}
        <div>
          <CurrencyCard
            data={data.currency}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('currency')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
          />
        </div>

        {/* Culture Card */}
        <div>
          <CultureCard
            data={data.culture}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('culture')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
            onLinkClick={handleLinkClick}
          />
        </div>

        {/* Unusual Laws Card */}
        <div>
          <UnusualLawsCard
            data={data.laws}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('unusual-laws')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
            onLinkClick={handleLinkClick}
          />
        </div>

        {/* Safety Card - spans 2 columns on xl */}
        <div className="xl:col-span-2">
          <SafetyCard
            data={data.safety}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('safety')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
            onLinkClick={handleLinkClick}
          />
        </div>

        {/* News Card */}
        <div>
          <NewsCard
            data={data.news}
            isExpanded={allowMultipleExpanded ? undefined : isCardExpanded('news')}
            isLoading={isLoading}
            onExpand={handleCardExpand}
            onCollapse={handleCardCollapse}
            onLinkClick={handleLinkClick}
          />
        </div>
      </div>

      {/* Footer note */}
      <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-sm text-blue-900 dark:text-blue-200 text-center">
          💡 <strong>Travel Intelligence Note:</strong> This information is compiled from official
          sources and updated regularly. Always verify critical details (especially visa
          requirements and safety alerts) with official government sources before traveling.
        </p>
      </div>
    </div>
  );
}
