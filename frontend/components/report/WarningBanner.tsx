'use client';

import { AlertTriangle, Info, AlertCircle, CheckCircle, X } from 'lucide-react';
import { useState } from 'react';

type WarningVariant = 'error' | 'warning' | 'info' | 'success';

interface WarningBannerProps {
  variant?: WarningVariant;
  title: string;
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  dismissible?: boolean;
  className?: string;
}

const VARIANT_CONFIG = {
  error: {
    icon: AlertCircle,
    colors: {
      bg: 'bg-red-50 dark:bg-red-950/30',
      border: 'border-red-200 dark:border-red-800',
      text: 'text-red-900 dark:text-red-100',
      icon: 'text-red-600 dark:text-red-400',
      button: 'bg-red-600 hover:bg-red-700 text-white',
    },
  },
  warning: {
    icon: AlertTriangle,
    colors: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-800',
      text: 'text-amber-900 dark:text-amber-100',
      icon: 'text-amber-600 dark:text-amber-400',
      button: 'bg-amber-600 hover:bg-amber-700 text-white',
    },
  },
  info: {
    icon: Info,
    colors: {
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-800',
      text: 'text-blue-900 dark:text-blue-100',
      icon: 'text-blue-600 dark:text-blue-400',
      button: 'bg-blue-600 hover:bg-blue-700 text-white',
    },
  },
  success: {
    icon: CheckCircle,
    colors: {
      bg: 'bg-green-50 dark:bg-green-950/30',
      border: 'border-green-200 dark:border-green-800',
      text: 'text-green-900 dark:text-green-100',
      icon: 'text-green-600 dark:text-green-400',
      button: 'bg-green-600 hover:bg-green-700 text-white',
    },
  },
} as const;

export function WarningBanner({
  variant = 'warning',
  title,
  message,
  action,
  dismissible = false,
  className = '',
}: WarningBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const config = VARIANT_CONFIG[variant];
  const Icon = config.icon;

  if (isDismissed) {
    return null;
  }

  return (
    <div
      className={`
        rounded-lg border-2 p-4
        ${config.colors.bg} ${config.colors.border}
        ${className}
        animate-in fade-in slide-in-from-top-2 duration-300
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0">
          <Icon className={config.colors.icon} size={24} strokeWidth={2} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className={`font-bold text-base ${config.colors.text} mb-1`}>
            {title}
          </h3>
          <p className={`text-sm ${config.colors.text} opacity-90 leading-relaxed`}>
            {message}
          </p>

          {/* Action button */}
          {action && (
            <button
              onClick={action.onClick}
              className={`
                mt-3 px-4 py-2 rounded-lg text-sm font-semibold
                ${config.colors.button}
                transition-all duration-200
                hover:shadow-md
                focus:outline-none focus:ring-2 focus:ring-offset-2
              `}
            >
              {action.label}
            </button>
          )}
        </div>

        {/* Dismiss button */}
        {dismissible && (
          <button
            onClick={() => setIsDismissed(true)}
            className={`
              flex-shrink-0 p-1 rounded
              ${config.colors.text} opacity-50 hover:opacity-100
              transition-opacity
            `}
            aria-label="Dismiss"
          >
            <X size={18} />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Compact inline warning
 */
interface InlineWarningProps {
  variant?: WarningVariant;
  message: string;
  className?: string;
}

export function InlineWarning({ variant = 'warning', message, className = '' }: InlineWarningProps) {
  const config = VARIANT_CONFIG[variant];
  const Icon = config.icon;

  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-md
        ${config.colors.bg} ${config.colors.border} border
        ${className}
      `}
    >
      <Icon className={config.colors.icon} size={14} />
      <span className={`text-xs font-medium ${config.colors.text}`}>
        {message}
      </span>
    </div>
  );
}
