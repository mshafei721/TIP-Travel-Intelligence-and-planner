'use client';

import { Shield, AlertTriangle, Phone, Heart, ExternalLink } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { SafetyInfo } from '@/types/destination';

interface SafetyCardProps {
  data: SafetyInfo;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

const ratingColors = [
  'from-red-500 to-rose-500',
  'from-orange-500 to-red-500',
  'from-amber-500 to-orange-500',
  'from-blue-500 to-cyan-500',
  'from-green-500 to-emerald-500',
];

const severityStyles = {
  info: {
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-900 dark:text-blue-200',
    icon: 'text-blue-600',
  },
  caution: {
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    border: 'border-amber-200 dark:border-amber-800',
    text: 'text-amber-900 dark:text-amber-200',
    icon: 'text-amber-600',
  },
  warning: {
    bg: 'bg-orange-50 dark:bg-orange-950/30',
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-900 dark:text-orange-200',
    icon: 'text-orange-600',
  },
  danger: {
    bg: 'bg-red-50 dark:bg-red-950/30',
    border: 'border-red-200 dark:border-red-800',
    text: 'text-red-900 dark:text-red-200',
    icon: 'text-red-600',
  },
};

export default function SafetyCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: SafetyCardProps) {
  return (
    <IntelligenceCard
      id="safety"
      title="Safety & Security"
      icon={<Shield className="w-6 h-6" />}
      iconColor="text-green-600 dark:text-green-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full ${
                i < data.overallSafetyRating ? 'bg-green-500' : 'bg-slate-300 dark:bg-slate-700'
              }`}
            />
          ))}
        </div>
      }
    >
      <div className="space-y-5">
        {/* Safety rating */}
        <div className="p-5 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-green-700 dark:text-green-300">
              Overall Safety Rating
            </span>
            <span className="text-3xl font-bold text-green-900 dark:text-green-100">
              {data.overallSafetyRating}/5
            </span>
          </div>
          <div className="h-3 bg-white dark:bg-slate-900 rounded-full overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${ratingColors[data.overallSafetyRating - 1]} transition-all duration-500`}
              style={{ width: `${(data.overallSafetyRating / 5) * 100}%` }}
            />
          </div>
        </div>

        {/* Safety alerts */}
        {data.safetyAlerts.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
              Safety Alerts
            </h4>
            {data.safetyAlerts.map((alert, idx) => {
              const style = severityStyles[alert.severity];
              return (
                <div key={idx} className={`p-4 ${style.bg} border ${style.border} rounded-lg`}>
                  <div className="flex items-start gap-3">
                    <AlertTriangle className={`w-5 h-5 ${style.icon} flex-shrink-0 mt-0.5`} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h5 className={`text-sm font-semibold ${style.text}`}>{alert.title}</h5>
                        <span
                          className={`text-xs px-2 py-0.5 ${style.bg} border ${style.border} rounded-full font-medium ${style.text}`}
                        >
                          {alert.type.replace('-', ' ')}
                        </span>
                      </div>
                      <p className={`text-sm ${style.text}`}>{alert.description}</p>
                      {alert.date && (
                        <p className={`text-xs ${style.text} mt-1 opacity-75`}>
                          Updated: {new Date(alert.date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Crime rates */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
              Overall Crime
            </p>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50 capitalize">
              {data.crimeRates.overall.replace('-', ' ')}
            </p>
          </div>
          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
              Petty Theft
            </p>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50 capitalize">
              {data.crimeRates.pettyTheft.replace('-', ' ')}
            </p>
          </div>
          <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2">
              Violent Crime
            </p>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50 capitalize">
              {data.crimeRates.violentCrime.replace('-', ' ')}
            </p>
          </div>
        </div>

        {/* Emergency numbers */}
        {data.emergencyNumbers.length > 0 && (
          <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <Phone className="w-5 h-5 text-red-600 dark:text-red-400" />
              <p className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase tracking-wide">
                Emergency Contacts
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {data.emergencyNumbers.map((contact, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-white dark:bg-slate-900 rounded-lg"
                >
                  <span className="text-sm text-slate-700 dark:text-slate-300">
                    {contact.service}
                  </span>
                  <span className="text-lg font-bold text-red-600 dark:text-red-400 font-mono">
                    {contact.number}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Health risks */}
        {data.healthRisks.length > 0 && (
          <div className="p-4 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <Heart className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <p className="text-xs font-semibold text-purple-700 dark:text-purple-400 uppercase tracking-wide">
                Health Risks
              </p>
            </div>
            <div className="space-y-3">
              {data.healthRisks.map((risk, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 bg-white dark:bg-slate-900 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="text-sm font-semibold text-purple-900 dark:text-purple-200">
                        {risk.risk}
                      </h5>
                      {risk.vaccinationRequired && (
                        <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full font-medium">
                          Vaccine required
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-purple-800 dark:text-purple-300">
                      {risk.prevention}
                    </p>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${
                      risk.severity === 'high'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : risk.severity === 'moderate'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    }`}
                  >
                    {risk.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Travel advisories */}
        {data.travelAdvisories && data.travelAdvisories.length > 0 && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Official Travel Advisories
            </p>
            <div className="flex flex-wrap gap-2">
              {data.travelAdvisories.map((link, idx) => (
                <a
                  key={idx}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onLinkClick?.(link.url, link.title)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300 text-sm font-medium rounded-lg hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors"
                >
                  <span>{link.title}</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </IntelligenceCard>
  );
}
