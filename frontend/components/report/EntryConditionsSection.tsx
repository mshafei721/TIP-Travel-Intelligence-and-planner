'use client';

import { Shield, Syringe, Ticket, Home, Wallet, FileCheck } from 'lucide-react';
import type { VisaIntelligence } from '@/types/visa';

interface EntryConditionsSectionProps {
  data: VisaIntelligence;
  className?: string;
}

export function EntryConditionsSection({ data, className = '' }: EntryConditionsSectionProps) {
  const { entryRequirements } = data;

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
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-950 flex items-center justify-center">
          <Shield className="text-green-600 dark:text-green-400" size={20} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
            Entry Conditions
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Requirements for entering {data.destinationCountry}
          </p>
        </div>
      </div>

      {/* Passport Validity */}
      <div className="flex items-start gap-4 p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-800">
        <FileCheck className="text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" size={20} />
        <div className="flex-1">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
            Passport Validity
          </h3>
          <p className="text-sm text-blue-800 dark:text-blue-200">
            {entryRequirements.passportValidity}
          </p>
          {entryRequirements.blankPagesRequired !== undefined && (
            <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
              Blank pages required: {entryRequirements.blankPagesRequired}
            </p>
          )}
        </div>
      </div>

      {/* Grid of additional requirements */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Return Ticket */}
        {entryRequirements.returnTicket !== undefined && (
          <RequirementCard
            icon={Ticket}
            label="Return Ticket"
            required={entryRequirements.returnTicket}
          />
        )}

        {/* Proof of Accommodation */}
        {entryRequirements.proofOfAccommodation !== undefined && (
          <RequirementCard
            icon={Home}
            label="Proof of Accommodation"
            required={entryRequirements.proofOfAccommodation}
          />
        )}

        {/* Proof of Funds */}
        {entryRequirements.proofOfFunds !== undefined && (
          <RequirementCard
            icon={Wallet}
            label="Proof of Funds"
            required={entryRequirements.proofOfFunds}
          />
        )}
      </div>

      {/* Vaccinations */}
      {entryRequirements.vaccinations && entryRequirements.vaccinations.length > 0 ? (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Syringe className="text-amber-600 dark:text-amber-400" size={18} />
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
              Required Vaccinations
            </h3>
          </div>
          <div className="space-y-2">
            {entryRequirements.vaccinations.map((vaccination, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800"
              >
                <Syringe size={14} className="text-amber-600 dark:text-amber-400 flex-shrink-0" />
                <span className="text-sm text-amber-900 dark:text-amber-100 font-medium">
                  {vaccination}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
          <Syringe size={16} className="text-green-600 dark:text-green-400" />
          <span className="text-sm text-green-800 dark:text-green-200 font-medium">
            No vaccinations required
          </span>
        </div>
      )}

      {/* Other Requirements */}
      {entryRequirements.otherRequirements && entryRequirements.otherRequirements.length > 0 && (
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-3">
            Additional Requirements
          </h3>
          <ul className="space-y-2">
            {entryRequirements.otherRequirements.map((req, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300 p-2 rounded bg-slate-50 dark:bg-slate-800/50"
              >
                <span className="text-blue-600 dark:text-blue-400">•</span>
                <span>{req}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

/**
 * Requirement card for boolean requirements
 */
interface RequirementCardProps {
  icon: React.ElementType;
  label: string;
  required: boolean;
}

function RequirementCard({ icon: Icon, label, required }: RequirementCardProps) {
  return (
    <div
      className={`
        flex items-center gap-3 p-4 rounded-lg border-2
        ${required
          ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800'
          : 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800'
        }
      `}
    >
      <Icon
        className={required ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'}
        size={18}
      />
      <div className="flex-1">
        <div
          className={`text-sm font-semibold ${
            required
              ? 'text-amber-900 dark:text-amber-100'
              : 'text-green-900 dark:text-green-100'
          }`}
        >
          {label}
        </div>
        <div
          className={`text-xs ${
            required
              ? 'text-amber-700 dark:text-amber-300'
              : 'text-green-700 dark:text-green-300'
          }`}
        >
          {required ? 'Required' : 'Not Required'}
        </div>
      </div>
    </div>
  );
}
