'use client';

import React from 'react';
import { AlertTriangle, X, Trash2 } from 'lucide-react';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      icon: Trash2,
      iconBg: 'bg-red-100 dark:bg-red-950/30',
      iconColor: 'text-red-600 dark:text-red-400',
      borderColor: 'border-red-200 dark:border-red-800',
      titleColor: 'text-red-900 dark:text-red-100',
      confirmBg: 'bg-red-600 hover:bg-red-700',
      confirmText: 'text-white',
    },
    warning: {
      icon: AlertTriangle,
      iconBg: 'bg-amber-100 dark:bg-amber-950/30',
      iconColor: 'text-amber-600 dark:text-amber-400',
      borderColor: 'border-amber-200 dark:border-amber-800',
      titleColor: 'text-amber-900 dark:text-amber-100',
      confirmBg: 'bg-amber-500 hover:bg-amber-600',
      confirmText: 'text-white',
    },
    info: {
      icon: AlertTriangle,
      iconBg: 'bg-blue-100 dark:bg-blue-950/30',
      iconColor: 'text-blue-600 dark:text-blue-400',
      borderColor: 'border-blue-200 dark:border-blue-800',
      titleColor: 'text-blue-900 dark:text-blue-100',
      confirmBg: 'bg-blue-600 hover:bg-blue-700',
      confirmText: 'text-white',
    },
  };

  const style = variantStyles[variant];
  const Icon = style.icon;

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  // Prevent clicks on backdrop from closing (only buttons should close)
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      onClick={handleBackdropClick}
    >
      <div
        className="relative w-full max-w-md rounded-xl border-2 bg-white shadow-2xl dark:bg-slate-900 animate-in fade-in zoom-in-95 duration-200"
        style={{
          animation: 'slideUp 0.3s ease-out',
        }}
      >
        {/* Header with icon */}
        <div className="p-6 pb-4">
          <div className="flex items-start gap-4">
            <div
              className={`flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full ${style.iconBg}`}
            >
              <Icon className={`h-6 w-6 ${style.iconColor}`} />
            </div>
            <div className="flex-1">
              <h3 className={`text-lg font-bold ${style.titleColor}`}>{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                {message}
              </p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-1 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-300"
              aria-label="Close dialog"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 border-t border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800/50">
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            {cancelText}
          </button>
          <button
            onClick={handleConfirm}
            className={`rounded-lg px-4 py-2 font-semibold shadow-sm transition-all hover:shadow-md ${style.confirmBg} ${style.confirmText}`}
          >
            {confirmText}
          </button>
        </div>
      </div>

      {/* Animation keyframes */}
      <style jsx>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
