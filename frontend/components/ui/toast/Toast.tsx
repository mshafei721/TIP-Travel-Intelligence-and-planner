'use client';

import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { type Toast as ToastType } from './ToastContext';

interface ToastProps {
  toast: ToastType;
  onDismiss: (id: string) => void;
}

const variantConfig = {
  success: {
    icon: CheckCircle2,
    bgClass: 'bg-green-600 dark:bg-green-700',
    iconClass: 'text-white',
    titleClass: 'text-white',
    messageClass: 'text-green-50',
  },
  error: {
    icon: AlertCircle,
    bgClass: 'bg-red-600 dark:bg-red-700',
    iconClass: 'text-white',
    titleClass: 'text-white',
    messageClass: 'text-red-50',
  },
  warning: {
    icon: AlertTriangle,
    bgClass: 'bg-amber-600 dark:bg-amber-700',
    iconClass: 'text-white',
    titleClass: 'text-white',
    messageClass: 'text-amber-50',
  },
  info: {
    icon: Info,
    bgClass: 'bg-blue-600 dark:bg-blue-700',
    iconClass: 'text-white',
    titleClass: 'text-white',
    messageClass: 'text-blue-50',
  },
};

export function Toast({ toast, onDismiss }: ToastProps) {
  const [isExiting, setIsExiting] = useState(false);

  const config = variantConfig[toast.variant];
  const IconComponent = config.icon;

  useEffect(() => {
    // Add enter animation
    const timer = setTimeout(() => {
      setIsExiting(false);
    }, 10);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss(toast.id);
    }, 300); // Match animation duration
  };

  return (
    <div
      className={`pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg shadow-lg transition-all duration-300 ${
        config.bgClass
      } ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}`}
      role="alert"
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <IconComponent className={`h-5 w-5 flex-shrink-0 ${config.iconClass}`} />
          <div className="flex-1">
            {toast.title && <h3 className={`font-semibold ${config.titleClass}`}>{toast.title}</h3>}
            <p className={`${toast.title ? 'mt-1' : ''} text-sm ${config.messageClass}`}>
              {toast.message}
            </p>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className="flex-shrink-0 rounded-md p-1 text-white transition-opacity hover:opacity-80"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
