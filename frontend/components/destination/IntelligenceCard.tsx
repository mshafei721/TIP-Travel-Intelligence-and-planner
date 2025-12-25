'use client';

import { ReactNode, useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface IntelligenceCardProps {
  id: string;
  title: string;
  icon: ReactNode;
  iconColor?: string;
  isExpanded?: boolean;
  isLoading?: boolean;
  children: ReactNode;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
  badge?: ReactNode;
}

export default function IntelligenceCard({
  id,
  title,
  icon,
  iconColor = 'text-blue-600 dark:text-blue-400',
  isExpanded: controlledExpanded,
  isLoading = false,
  children,
  onExpand,
  onCollapse,
  badge,
}: IntelligenceCardProps) {
  const [internalExpanded, setInternalExpanded] = useState(false);

  // Use controlled state if provided, otherwise use internal state
  const isExpanded = controlledExpanded ?? internalExpanded;
  const setExpanded =
    controlledExpanded !== undefined
      ? (value: boolean) => (value ? onExpand?.(id) : onCollapse?.(id))
      : setInternalExpanded;

  const handleToggle = () => {
    const newState = !isExpanded;
    setExpanded(newState);

    if (newState) {
      onExpand?.(id);
    } else {
      onCollapse?.(id);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div
      className={`
        group relative
        bg-white dark:bg-slate-900
        border border-slate-200 dark:border-slate-800
        rounded-xl
        overflow-hidden
        transition-all duration-300 ease-out
        hover:shadow-lg hover:shadow-blue-500/10 dark:hover:shadow-blue-500/20
        hover:-translate-y-1
        ${isExpanded ? 'shadow-xl shadow-blue-500/10 dark:shadow-blue-500/20' : 'shadow-md'}
      `}
      role="region"
      aria-labelledby={`${id}-title`}
    >
      {/* Gradient accent border on hover */}
      <div
        className="
        absolute inset-0
        bg-gradient-to-br from-blue-500/0 via-amber-500/0 to-blue-500/0
        group-hover:from-blue-500/10 group-hover:via-amber-500/5 group-hover:to-blue-500/10
        dark:group-hover:from-blue-500/20 dark:group-hover:via-amber-500/10 dark:group-hover:to-blue-500/20
        transition-all duration-500
        pointer-events-none
        rounded-xl
      "
      />

      {/* Card header - clickable */}
      <button
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        className="
          w-full px-6 py-5
          flex items-center gap-4
          cursor-pointer
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          dark:focus:ring-offset-slate-900
          transition-colors
          hover:bg-slate-50 dark:hover:bg-slate-800/50
        "
        aria-expanded={isExpanded}
        aria-controls={`${id}-content`}
        id={`${id}-title`}
      >
        {/* Icon */}
        <div
          className={`
          flex-shrink-0
          w-12 h-12
          flex items-center justify-center
          rounded-lg
          bg-gradient-to-br from-slate-100 to-slate-50
          dark:from-slate-800 dark:to-slate-900
          transition-transform duration-300
          ${isExpanded ? 'scale-110' : 'group-hover:scale-105'}
          ${iconColor}
        `}
        >
          {icon}
        </div>

        {/* Title */}
        <div className="flex-1 text-left">
          <h3
            className="
            text-xl font-semibold
            text-slate-900 dark:text-slate-50
            transition-colors
          "
          >
            {title}
          </h3>
          {badge && <div className="mt-1">{badge}</div>}
        </div>

        {/* Expand indicator */}
        <ChevronDown
          className={`
            w-6 h-6
            text-slate-400 dark:text-slate-500
            transition-transform duration-300
            ${isExpanded ? 'rotate-180' : ''}
          `}
        />
      </button>

      {/* Card content - expandable */}
      <div
        id={`${id}-content`}
        className={`
          overflow-hidden
          transition-all duration-300 ease-in-out
          ${isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'}
        `}
        aria-hidden={!isExpanded}
      >
        <div
          className="
          px-6 pb-6
          border-t border-slate-100 dark:border-slate-800
        "
        >
          {isLoading ? (
            <div className="py-8 flex items-center justify-center">
              <div className="flex flex-col items-center gap-3">
                <div
                  className="
                  w-10 h-10
                  border-4 border-blue-200 dark:border-blue-900
                  border-t-blue-600 dark:border-t-blue-400
                  rounded-full
                  animate-spin
                "
                />
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Loading intelligence...
                </p>
              </div>
            </div>
          ) : (
            <div className="pt-4">{children}</div>
          )}
        </div>
      </div>
    </div>
  );
}
