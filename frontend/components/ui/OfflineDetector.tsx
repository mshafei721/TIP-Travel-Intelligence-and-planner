'use client';

import { WifiOff, Wifi } from 'lucide-react';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';
import { useEffect, useState, useRef } from 'react';

/**
 * OfflineDetector Component
 * Displays a fixed banner at the top of the screen when the user loses internet connection
 * Automatically hides when connection is restored
 */
export function OfflineDetector() {
  const isOnline = useOnlineStatus();
  const [showReconnected, setShowReconnected] = useState(false);
  const previousOnlineRef = useRef<boolean | null>(null);

  // Track status changes via effect but without direct state updates
  useEffect(() => {
    const wasOffline = previousOnlineRef.current === false;
    const isNowOnline = isOnline === true;

    if (wasOffline && isNowOnline) {
      // User just reconnected - schedule state update asynchronously
      const immediateTimer = setTimeout(() => {
        setShowReconnected(true);
      }, 0);

      // Hide "reconnected" message after 3 seconds
      const hideTimer = setTimeout(() => {
        setShowReconnected(false);
      }, 3000);

      // Update ref after scheduling
      previousOnlineRef.current = isOnline;

      return () => {
        clearTimeout(immediateTimer);
        clearTimeout(hideTimer);
      };
    }

    // Update ref for next comparison
    previousOnlineRef.current = isOnline;
  }, [isOnline]);

  // Don't render anything if online and never was offline
  if (isOnline && !showReconnected) {
    return null;
  }

  return (
    <div
      className={`fixed left-0 right-0 top-0 z-50 transform transition-all duration-500 ease-in-out ${
        !isOnline || showReconnected ? 'translate-y-0' : '-translate-y-full'
      }`}
      role="alert"
      aria-live="assertive"
    >
      {!isOnline ? (
        // Offline banner
        <div className="bg-amber-600 dark:bg-amber-700">
          <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center gap-3">
              <WifiOff className="h-5 w-5 flex-shrink-0 text-white" aria-hidden="true" />
              <div className="flex-1 text-center">
                <p className="text-sm font-medium text-white sm:text-base">
                  You&apos;re offline. Check your internet connection.
                </p>
              </div>
              <div className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            </div>
          </div>
        </div>
      ) : (
        // Reconnected banner (brief confirmation)
        <div className="bg-green-600 dark:bg-green-700">
          <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center gap-3">
              <Wifi className="h-5 w-5 flex-shrink-0 text-white" aria-hidden="true" />
              <div className="flex-1 text-center">
                <p className="text-sm font-medium text-white sm:text-base">
                  Back online! Your connection has been restored.
                </p>
              </div>
              <div className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
