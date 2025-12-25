'use client';

import { Scale, AlertTriangle, Info, AlertOctagon, ExternalLink } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { UnusualLaws } from '@/types/destination';

interface UnusualLawsCardProps {
  data: UnusualLaws;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  onLinkClick?: (url: string, title: string) => void;
}

const severityStyles = {
  info: {
    icon: Info,
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-900 dark:text-blue-200',
    iconColor: 'text-blue-600 dark:text-blue-400',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    border: 'border-amber-200 dark:border-amber-800',
    text: 'text-amber-900 dark:text-amber-200',
    iconColor: 'text-amber-600 dark:text-amber-400',
  },
  critical: {
    icon: AlertOctagon,
    bg: 'bg-red-50 dark:bg-red-950/30',
    border: 'border-red-200 dark:border-red-800',
    text: 'text-red-900 dark:text-red-200',
    iconColor: 'text-red-600 dark:text-red-400',
  },
};

export default function UnusualLawsCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
  onLinkClick,
}: UnusualLawsCardProps) {
  const criticalCount = data.restrictions.filter((r) => r.severity === 'critical').length;

  return (
    <IntelligenceCard
      id="unusual-laws"
      title="Unusual Laws & Restrictions"
      icon={<Scale className="w-6 h-6" />}
      iconColor="text-red-600 dark:text-red-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        criticalCount > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs font-medium rounded-full">
            <AlertOctagon className="w-3 h-3" />
            {criticalCount} critical
          </span>
        )
      }
    >
      <div className="space-y-4">
        {/* Restrictions */}
        {data.restrictions.length > 0 && (
          <div className="space-y-3">
            {data.restrictions.map((restriction, idx) => {
              const style = severityStyles[restriction.severity];
              const Icon = style.icon;

              return (
                <div key={idx} className={`p-4 ${style.bg} border ${style.border} rounded-lg`}>
                  <div className="flex items-start gap-3">
                    <Icon className={`w-5 h-5 ${style.iconColor} flex-shrink-0 mt-0.5`} />
                    <div className="flex-1">
                      <h4 className={`text-sm font-semibold ${style.text} mb-1`}>
                        {restriction.title}
                      </h4>
                      <p className={`text-sm ${style.text}`}>{restriction.description}</p>
                      {restriction.penalty && (
                        <p className={`text-xs ${style.text} mt-2 font-medium`}>
                          Penalty: {restriction.penalty}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Import restrictions */}
        {data.importRestrictions && data.importRestrictions.length > 0 && (
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-3">
              Import Restrictions
            </p>
            <ul className="space-y-2">
              {data.importRestrictions.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-slate-500 rounded-full mt-2" />
                  <span className="text-sm text-slate-700 dark:text-slate-300">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Photography restrictions */}
        {data.photographyRestrictions && data.photographyRestrictions.length > 0 && (
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-3">
              Photography Restrictions
            </p>
            <ul className="space-y-2">
              {data.photographyRestrictions.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-slate-500 rounded-full mt-2" />
                  <span className="text-sm text-slate-700 dark:text-slate-300">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Internet restrictions */}
        {data.internetRestrictions && data.internetRestrictions.length > 0 && (
          <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-3">
              Internet Restrictions
            </p>
            <ul className="space-y-2">
              {data.internetRestrictions.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-slate-500 rounded-full mt-2" />
                  <span className="text-sm text-slate-700 dark:text-slate-300">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Legal resources */}
        {data.legalResources && data.legalResources.length > 0 && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Legal Resources
            </p>
            <div className="flex flex-wrap gap-2">
              {data.legalResources.map((link, idx) => (
                <a
                  key={idx}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onLinkClick?.(link.url, link.title)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm font-medium rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 transition-colors"
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
