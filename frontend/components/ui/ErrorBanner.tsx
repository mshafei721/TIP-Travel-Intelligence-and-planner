'use client';

import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';
import { useState } from 'react';

type ErrorBannerVariant = 'error' | 'warning' | 'info' | 'success';

interface ErrorBannerProps {
  variant?: ErrorBannerVariant;
  title?: string;
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const variantConfig = {
  error: {
    icon: AlertCircle,
    bgClass: 'bg-red-50 dark:bg-red-950',
    borderClass: 'border-red-200 dark:border-red-800',
    iconClass: 'text-red-600 dark:text-red-400',
    titleClass: 'text-red-900 dark:text-red-100',
    messageClass: 'text-red-700 dark:text-red-300',
    buttonClass: 'text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200',
  },
  warning: {
    icon: AlertTriangle,
    bgClass: 'bg-amber-50 dark:bg-amber-950',
    borderClass: 'border-amber-200 dark:border-amber-800',
    iconClass: 'text-amber-600 dark:text-amber-400',
    titleClass: 'text-amber-900 dark:text-amber-100',
    messageClass: 'text-amber-700 dark:text-amber-300',
    buttonClass:
      'text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-200',
  },
  info: {
    icon: Info,
    bgClass: 'bg-blue-50 dark:bg-blue-950',
    borderClass: 'border-blue-200 dark:border-blue-800',
    iconClass: 'text-blue-600 dark:text-blue-400',
    titleClass: 'text-blue-900 dark:text-blue-100',
    messageClass: 'text-blue-700 dark:text-blue-300',
    buttonClass: 'text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200',
  },
  success: {
    icon: CheckCircle2,
    bgClass: 'bg-green-50 dark:bg-green-950',
    borderClass: 'border-green-200 dark:border-green-800',
    iconClass: 'text-green-600 dark:text-green-400',
    titleClass: 'text-green-900 dark:text-green-100',
    messageClass: 'text-green-700 dark:text-green-300',
    buttonClass:
      'text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-200',
  },
};

export function ErrorBanner({
  variant = 'error',
  title,
  message,
  dismissible = false,
  onDismiss,
  className = '',
}: ErrorBannerProps) {
  const [isVisible, setIsVisible] = useState(true);

  const config = variantConfig[variant];
  const IconComponent = config.icon;

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible) return null;

  return (
    <div
      className={`rounded-lg border p-4 ${config.bgClass} ${config.borderClass} ${className}`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <IconComponent className={`h-5 w-5 flex-shrink-0 ${config.iconClass}`} />
        <div className="flex-1">
          {title && <h3 className={`font-semibold ${config.titleClass}`}>{title}</h3>}
          <p className={`${title ? 'mt-1' : ''} text-sm ${config.messageClass}`}>{message}</p>
        </div>
        {dismissible && (
          <button
            type="button"
            onClick={handleDismiss}
            className={`flex-shrink-0 rounded-md p-1 transition-colors ${config.buttonClass}`}
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
