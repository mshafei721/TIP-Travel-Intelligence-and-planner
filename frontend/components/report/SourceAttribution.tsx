'use client';

import { ExternalLink, Globe, Building2, Link as LinkIcon } from 'lucide-react';
import type { SourceReference } from '@/types/visa';

interface SourceAttributionProps {
  sources: SourceReference[];
  title?: string;
  variant?: 'compact' | 'detailed';
  className?: string;
}

const SOURCE_TYPE_CONFIG = {
  government: {
    label: 'Government',
    icon: Globe,
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-200 dark:border-blue-800',
  },
  embassy: {
    label: 'Embassy',
    icon: Building2,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-50 dark:bg-green-950/30',
    border: 'border-green-200 dark:border-green-800',
  },
  'third-party': {
    label: 'Third-Party',
    icon: LinkIcon,
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-50 dark:bg-amber-950/30',
    border: 'border-amber-200 dark:border-amber-800',
  },
} as const;

// Default config for unknown source types
const DEFAULT_SOURCE_CONFIG = SOURCE_TYPE_CONFIG['third-party'];

// Helper function to safely get source config
function getSourceConfig(sourceType: string | undefined | null) {
  if (!sourceType) return DEFAULT_SOURCE_CONFIG;
  return SOURCE_TYPE_CONFIG[sourceType as keyof typeof SOURCE_TYPE_CONFIG] || DEFAULT_SOURCE_CONFIG;
}

export function SourceAttribution({
  sources,
  title = 'Sources',
  variant = 'detailed',
  className = '',
}: SourceAttributionProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }).format(date);
    } catch {
      return dateString;
    }
  };

  if (variant === 'compact') {
    return (
      <div className={`flex flex-wrap items-center gap-2 ${className}`}>
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}:</span>
        {sources.map((source, index) => {
          const config = getSourceConfig(source.type);
          const Icon = config.icon;

          return (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`
                inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium
                ${config.bg} ${config.color} ${config.border} border
                hover:shadow-sm transition-all duration-200
                group
              `}
              title={`${source.name} (verified ${formatDate(source.lastVerified)})`}
            >
              <Icon size={12} />
              <span className="max-w-[120px] truncate">{source.name}</span>
              <ExternalLink
                size={10}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              />
            </a>
          );
        })}
      </div>
    );
  }

  // Detailed variant
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        <LinkIcon className="text-slate-400" size={16} />
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          ({sources.length} {sources.length === 1 ? 'source' : 'sources'})
        </span>
      </div>

      {/* Source cards */}
      <div className="space-y-2">
        {sources.map((source, index) => {
          const config = getSourceConfig(source.type);
          const Icon = config.icon;

          return (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`
                block p-3 rounded-lg border
                bg-white dark:bg-slate-900
                border-slate-200 dark:border-slate-800
                hover:border-blue-300 dark:hover:border-blue-700
                hover:shadow-md
                transition-all duration-200
                group
              `}
            >
              <div className="flex items-start justify-between gap-3">
                {/* Left: Icon and content */}
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  {/* Type icon */}
                  <div
                    className={`
                    flex-shrink-0 w-8 h-8 rounded-md
                    ${config.bg} ${config.border} border
                    flex items-center justify-center
                  `}
                  >
                    <Icon className={config.color} size={16} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {source.name}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {config.label} · Verified {formatDate(source.lastVerified)}
                    </div>
                    <div className="text-xs text-slate-400 dark:text-slate-500 mt-1 truncate font-mono">
                      {source.url}
                    </div>
                  </div>
                </div>

                {/* Right: External link icon */}
                <ExternalLink
                  size={16}
                  className="flex-shrink-0 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors"
                />
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Inline source link (for embedding within text)
 */
interface SourceLinkProps {
  source: SourceReference;
  showIcon?: boolean;
}

export function SourceLink({ source, showIcon = true }: SourceLinkProps) {
  const config = getSourceConfig(source.type);

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`
        inline-flex items-center gap-1
        ${config.color} hover:underline
        transition-colors
      `}
      title={`${source.name} (${config.label})`}
    >
      {showIcon && <ExternalLink size={12} />}
      <span className="font-medium">{source.name}</span>
    </a>
  );
}
