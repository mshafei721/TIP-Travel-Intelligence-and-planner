'use client';

import { createContext, useCallback, useContext, useState } from 'react';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  variant: ToastVariant;
  title?: string;
  message: string;
  duration?: number; // milliseconds, 0 for no auto-dismiss
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (message: string, title?: string, duration?: number) => void;
  error: (message: string, title?: string, duration?: number) => void;
  warning: (message: string, title?: string, duration?: number) => void;
  info: (message: string, title?: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Define removeToast first so it can be used in addToast
  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newToast: Toast = { id, ...toast };
      setToasts((prev) => [...prev, newToast]);

      // Auto-dismiss if duration is set
      if (toast.duration !== 0) {
        setTimeout(() => {
          removeToast(id);
        }, toast.duration || 5000);
      }
    },
    [removeToast],
  );

  const success = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast({ variant: 'success', message, title, duration });
    },
    [addToast],
  );

  const error = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast({ variant: 'error', message, title, duration });
    },
    [addToast],
  );

  const warning = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast({ variant: 'warning', message, title, duration });
    },
    [addToast],
  );

  const info = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast({ variant: 'info', message, title, duration });
    },
    [addToast],
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, warning, info }}>
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
