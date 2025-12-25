'use client';

import { DollarSign, CreditCard, Banknote, TrendingUp } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { CurrencyInfo } from '@/types/destination';

interface CurrencyCardProps {
  data: CurrencyInfo;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
}

const availabilityColors = {
  widespread: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  common: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  limited: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  rare: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

const costLevelColors = {
  'very-low': 'from-green-400 to-emerald-400',
  low: 'from-blue-400 to-cyan-400',
  moderate: 'from-amber-400 to-yellow-400',
  high: 'from-orange-400 to-red-400',
  'very-high': 'from-red-500 to-rose-500',
};

export default function CurrencyCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
}: CurrencyCardProps) {
  return (
    <IntelligenceCard
      id="currency"
      title="Currency & Costs"
      icon={<DollarSign className="w-6 h-6" />}
      iconColor="text-green-600 dark:text-green-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {data.localCurrency.code} • 1 USD = {data.exchangeRate.toFixed(2)}{' '}
          {data.localCurrency.code}
        </span>
      }
    >
      <div className="space-y-6">
        {/* Currency info */}
        <div className="p-5 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 bg-green-600 dark:bg-green-500 text-white rounded-lg flex items-center justify-center text-2xl font-bold">
              {data.localCurrency.symbol}
            </div>
            <div>
              <h4 className="text-lg font-bold text-green-900 dark:text-green-100">
                {data.localCurrency.name}
              </h4>
              <p className="text-sm text-green-700 dark:text-green-300">
                {data.localCurrency.code}
              </p>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-green-900 dark:text-green-100">
              {data.exchangeRate.toFixed(4)}
            </span>
            <span className="text-sm text-green-700 dark:text-green-300">
              {data.localCurrency.code} per USD
            </span>
          </div>
        </div>

        {/* Payment methods */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Banknote className="w-5 h-5 text-blue-500" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                ATM Availability
              </span>
            </div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${availabilityColors[data.atmAvailability]}`}
            >
              {data.atmAvailability.charAt(0).toUpperCase() + data.atmAvailability.slice(1)}
            </span>
            <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">{data.atmFees}</p>
          </div>

          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <CreditCard className="w-5 h-5 text-purple-500" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                Card Acceptance
              </span>
            </div>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${availabilityColors[data.creditCardAcceptance]}`}
            >
              {data.creditCardAcceptance.charAt(0).toUpperCase() +
                data.creditCardAcceptance.slice(1)}
            </span>
          </div>
        </div>

        {/* Tipping customs */}
        <div className="p-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg">
          <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wide mb-2">
            Tipping Customs
          </p>
          <p className="text-sm text-amber-900 dark:text-amber-200">{data.tippingCustoms}</p>
        </div>

        {/* Cost of living */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
              Cost of Living
            </h4>
            <div className="relative">
              <div
                className={`h-2 w-32 bg-gradient-to-r ${costLevelColors[data.costOfLiving.level]} rounded-full`}
              />
              <span className="absolute -top-6 right-0 text-xs font-medium text-slate-600 dark:text-slate-400">
                {data.costOfLiving.level
                  .split('-')
                  .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                  .join(' ')}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            {data.costOfLiving.estimates.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
              >
                <span className="text-sm text-slate-700 dark:text-slate-300">{item.category}</span>
                <span className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  {item.cost.min === item.cost.max
                    ? `${item.cost.min} ${item.cost.currency}`
                    : `${item.cost.min}-${item.cost.max} ${item.cost.currency}`}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Exchange tips */}
        {data.currencyExchangeTips.length > 0 && (
          <div className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-start gap-3">
              <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-2">
                  Exchange Tips
                </p>
                <ul className="space-y-1">
                  {data.currencyExchangeTips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="flex-shrink-0 w-1.5 h-1.5 bg-blue-500 rounded-full mt-2" />
                      <span className="text-sm text-blue-900 dark:text-blue-200">{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </IntelligenceCard>
  );
}
