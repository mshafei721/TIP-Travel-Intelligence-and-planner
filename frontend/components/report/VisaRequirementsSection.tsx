'use client';

import { FileText, Clock, DollarSign, CheckCircle, XCircle, Plane } from 'lucide-react';
import { ConfidenceBadge } from './ConfidenceBadge';
import { SourceAttribution } from './SourceAttribution';
import { InlineWarning } from './WarningBanner';
import type { VisaIntelligence } from '@/types/visa';

interface VisaRequirementsSectionProps {
  data: VisaIntelligence;
  className?: string;
}

export function VisaRequirementsSection({ data, className = '' }: VisaRequirementsSectionProps) {
  const { visaRequirement, applicationProcess, sources } = data;

  const formatCurrency = (amount?: number, currency?: string) => {
    if (!amount) return 'Free';
    if (currency && currency !== 'USD') {
      return `${amount} ${currency}`;
    }
    return `$${amount} USD`;
  };

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
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-950 flex items-center justify-center">
            <FileText className="text-blue-600 dark:text-blue-400" size={20} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              Visa Requirements
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {data.userNationality} → {data.destinationCountry} · {data.tripPurpose}
            </p>
          </div>
        </div>
        <ConfidenceBadge level={visaRequirement.confidenceLevel} score={data.confidenceScore} />
      </div>

      {/* Visa Status - Hero section */}
      <div
        className={`
          p-6 rounded-lg border-2
          ${visaRequirement.visaRequired
            ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800'
            : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800'
          }
        `}
      >
        <div className="flex items-start gap-4">
          <div
            className={`
              w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
              ${visaRequirement.visaRequired
                ? 'bg-amber-100 dark:bg-amber-900'
                : 'bg-green-100 dark:bg-green-900'
              }
            `}
          >
            {visaRequirement.visaRequired ? (
              <XCircle className="text-amber-600 dark:text-amber-400" size={24} />
            ) : (
              <CheckCircle className="text-green-600 dark:text-green-400" size={24} />
            )}
          </div>
          <div className="flex-1">
            <h3
              className={`
                text-lg font-bold mb-1
                ${visaRequirement.visaRequired
                  ? 'text-amber-900 dark:text-amber-100'
                  : 'text-green-900 dark:text-green-100'
                }
              `}
            >
              {visaRequirement.visaRequired ? 'Visa Required' : 'No Visa Required'}
            </h3>
            <p
              className={`
                text-sm
                ${visaRequirement.visaRequired
                  ? 'text-amber-800 dark:text-amber-200'
                  : 'text-green-800 dark:text-green-200'
                }
              `}
            >
              {visaRequirement.visaType}
              {visaRequirement.maxStayDays && ` · ${visaRequirement.maxStayDays} days maximum stay`}
              {visaRequirement.maxStayDuration && ` · ${visaRequirement.maxStayDuration}`}
            </p>
          </div>
        </div>
      </div>

      {/* Application Details */}
      {visaRequirement.visaRequired && (
        <div className="grid md:grid-cols-2 gap-4">
          {/* Processing Time */}
          {applicationProcess.processingTime && (
            <div className="flex items-start gap-3 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
              <Clock className="text-slate-600 dark:text-slate-400 flex-shrink-0 mt-0.5" size={18} />
              <div>
                <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">
                  Processing Time
                </div>
                <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {applicationProcess.processingTime}
                </div>
              </div>
            </div>
          )}

          {/* Cost */}
          <div className="flex items-start gap-3 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
            <DollarSign className="text-slate-600 dark:text-slate-400 flex-shrink-0 mt-0.5" size={18} />
            <div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">
                Visa Cost
              </div>
              <div className="text-sm font-medium text-slate-900 dark:text-slate-100">
                {formatCurrency(
                  applicationProcess.costLocal?.amount || applicationProcess.costUsd,
                  applicationProcess.costLocal?.currency
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Application Process */}
      {applicationProcess.applicationMethod !== 'not_required' && (
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
            <Plane size={16} className="text-blue-600 dark:text-blue-400" />
            Application Process
          </h3>
          <div className="space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Method:</span>
              <span className="text-sm text-slate-900 dark:text-slate-100 capitalize">
                {applicationProcess.applicationMethod.replace('_', ' ')}
              </span>
            </div>
            {applicationProcess.applicationUrl && (
              <div>
                <a
                  href={applicationProcess.applicationUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Apply Online →
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Required Documents */}
      {applicationProcess.requiredDocuments && applicationProcess.requiredDocuments.length > 0 && (
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Required Documents
          </h3>
          <ul className="space-y-2">
            {applicationProcess.requiredDocuments.map((doc, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                <CheckCircle size={16} className="text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <span>{doc}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Application Steps */}
      {applicationProcess.steps && applicationProcess.steps.length > 0 && (
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Application Steps
          </h3>
          <ol className="space-y-3">
            {applicationProcess.steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-bold flex items-center justify-center">
                  {index + 1}
                </span>
                <span className="text-sm text-slate-700 dark:text-slate-300 mt-0.5">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Warnings */}
      {data.warnings && data.warnings.length > 0 && (
        <div className="space-y-2">
          {data.warnings.map((warning, index) => (
            <InlineWarning key={index} variant="warning" message={warning} />
          ))}
        </div>
      )}

      {/* Sources */}
      <SourceAttribution sources={sources} variant="compact" />
    </section>
  );
}
