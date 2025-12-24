'use client';

import { Lightbulb, AlertTriangle } from 'lucide-react';
import type { VisaIntelligence } from '@/types/visa';

interface TipsAndWarningsSectionProps {
  data: VisaIntelligence;
  className?: string;
}

export function TipsAndWarningsSection({ data, className = '' }: TipsAndWarningsSectionProps) {
  const { tips, warnings } = data;

  const hasTips = tips && tips.length > 0;
  const hasWarnings = warnings && warnings.length > 0;

  if (!hasTips && !hasWarnings) {
    return null;
  }

  return (
    <section
      className={`
        bg-white dark:bg-slate-900
        rounded-xl border-2 border-slate-200 dark:border-slate-800
        p-6 space-y-6
        shadow-sm hover:shadow-md transition-shadow duration-200
        ${className}
      `}
    >
      {/* Tips */}
      {hasTips && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-950 flex items-center justify-center">
              <Lightbulb className="text-blue-600 dark:text-blue-400" size={16} />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
              Helpful Tips
            </h3>
          </div>
          <div className="space-y-3">
            {tips.map((tip, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800"
              >
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 dark:bg-blue-500 text-white text-xs font-bold flex items-center justify-center mt-0.5">
                  {index + 1}
                </div>
                <p className="text-sm text-blue-900 dark:text-blue-100 leading-relaxed">
                  {tip}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {hasWarnings && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-950 flex items-center justify-center">
              <AlertTriangle className="text-amber-600 dark:text-amber-400" size={16} />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
              Important Warnings
            </h3>
          </div>
          <div className="space-y-3">
            {warnings.map((warning, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-4 rounded-lg bg-amber-50 dark:bg-amber-950/20 border-2 border-amber-300 dark:border-amber-700"
              >
                <AlertTriangle className="text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" size={18} />
                <p className="text-sm text-amber-900 dark:text-amber-100 font-medium leading-relaxed">
                  {warning}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
