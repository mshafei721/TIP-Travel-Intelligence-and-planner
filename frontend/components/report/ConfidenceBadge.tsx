'use client';

import { Shield, AlertTriangle, HelpCircle } from 'lucide-react';
import type { ConfidenceLevel } from '@/types/visa';

interface ConfidenceBadgeProps {
  level: ConfidenceLevel;
  score?: number; // 0.0 - 1.0
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const CONFIDENCE_CONFIG = {
  official: {
    label: 'Official Source',
    description: 'Verified from government or embassy sources',
    icon: Shield,
    colors: {
      bg: 'bg-green-50 dark:bg-green-950/30',
      border: 'border-green-200 dark:border-green-800',
      text: 'text-green-800 dark:text-green-200',
      icon: 'text-green-600 dark:text-green-400',
      stamp: 'from-green-600 to-green-700',
    },
  },
  'third-party': {
    label: 'Third-Party Source',
    description: 'Data from trusted third-party providers',
    icon: AlertTriangle,
    colors: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-800',
      text: 'text-amber-800 dark:text-amber-200',
      icon: 'text-amber-600 dark:text-amber-400',
      stamp: 'from-amber-600 to-amber-700',
    },
  },
  uncertain: {
    label: 'Uncertain',
    description: 'Information may be incomplete or unverified',
    icon: HelpCircle,
    colors: {
      bg: 'bg-slate-50 dark:bg-slate-900/50',
      border: 'border-slate-300 dark:border-slate-700',
      text: 'text-slate-700 dark:text-slate-300',
      icon: 'text-slate-500 dark:text-slate-400',
      stamp: 'from-slate-500 to-slate-600',
    },
  },
} as const;

const SIZE_CONFIG = {
  sm: {
    padding: 'px-2 py-0.5',
    text: 'text-xs',
    icon: 12,
    stamp: 'w-4 h-4',
  },
  md: {
    padding: 'px-3 py-1',
    text: 'text-sm',
    icon: 14,
    stamp: 'w-5 h-5',
  },
  lg: {
    padding: 'px-4 py-1.5',
    text: 'text-base',
    icon: 16,
    stamp: 'w-6 h-6',
  },
} as const;

export function ConfidenceBadge({
  level,
  score,
  size = 'md',
  showLabel = true,
  className = '',
}: ConfidenceBadgeProps) {
  const config = CONFIDENCE_CONFIG[level];
  const sizeConfig = SIZE_CONFIG[size];
  const Icon = config.icon;

  const formatScore = (s: number) => {
    return `${Math.round(s * 100)}% confidence`;
  };

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 rounded-md border font-medium
        ${config.colors.bg} ${config.colors.border} ${config.colors.text}
        ${sizeConfig.padding} ${sizeConfig.text}
        transition-all duration-200 hover:shadow-sm
        ${className}
      `}
      title={`${config.description}${score ? ` (${formatScore(score)})` : ''}`}
    >
      {/* Icon with subtle stamp effect */}
      <div className="relative">
        <Icon size={sizeConfig.icon} className={config.colors.icon} strokeWidth={2.5} />
        <div
          className={`
            absolute inset-0 rounded-full opacity-0 group-hover:opacity-10
            bg-gradient-to-br ${config.colors.stamp}
          `}
        />
      </div>

      {/* Label */}
      {showLabel && <span className="font-semibold">{config.label}</span>}

      {/* Optional confidence score */}
      {score !== undefined && (
        <span className="opacity-75 font-mono text-xs ml-0.5">{Math.round(score * 100)}%</span>
      )}
    </div>
  );
}

/**
 * Stamp-style confidence badge (for decorative use)
 */
interface ConfidenceStampProps {
  level: ConfidenceLevel;
  score?: number;
  size?: 'md' | 'lg' | 'xl';
}

export function ConfidenceStamp({ level, score, size = 'lg' }: ConfidenceStampProps) {
  const config = CONFIDENCE_CONFIG[level];
  const Icon = config.icon;

  const sizeClasses = {
    md: 'w-16 h-16 text-xs',
    lg: 'w-20 h-20 text-sm',
    xl: 'w-24 h-24 text-base',
  };

  return (
    <div
      className={`
        relative ${sizeClasses[size]} flex-shrink-0
        rounded-full border-2 ${config.colors.border}
        ${config.colors.bg}
        flex flex-col items-center justify-center gap-0.5
        transform rotate-12 transition-transform hover:rotate-0
        shadow-sm hover:shadow-md
      `}
      title={config.description}
    >
      {/* Icon */}
      <Icon className={config.colors.icon} size={size === 'xl' ? 20 : size === 'lg' ? 16 : 14} />

      {/* Label */}
      <span
        className={`${config.colors.text} font-bold uppercase tracking-tight text-center leading-tight`}
      >
        {level === 'official' ? 'Official' : level === 'third-party' ? 'Verified' : 'Review'}
      </span>

      {/* Score */}
      {score !== undefined && (
        <span className={`${config.colors.text} font-mono text-xs opacity-75`}>
          {Math.round(score * 100)}%
        </span>
      )}

      {/* Border ring effect */}
      <div
        className={`
          absolute inset-0 rounded-full border-2 ${config.colors.border}
          opacity-30 scale-110
        `}
      />
    </div>
  );
}
