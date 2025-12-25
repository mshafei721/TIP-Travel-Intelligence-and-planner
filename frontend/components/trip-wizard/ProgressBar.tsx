'use client';

interface ProgressBarProps {
  progress: number; // 0-100
}

export default function ProgressBar({ progress }: ProgressBarProps) {
  return (
    <div className="w-full">
      {/* Progress bar container */}
      <div className="h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner">
        <div
          className="h-full bg-gradient-to-r from-blue-600 via-blue-500 to-amber-500 transition-all duration-700 ease-out rounded-full shadow-lg shadow-blue-500/20"
          style={{ width: `${progress}%` }}
        >
          {/* Shimmer effect */}
          <div
            className="h-full w-full opacity-30"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
              animation: 'shimmer 2s infinite',
            }}
          />
        </div>
      </div>

      {/* Percentage text */}
      <div className="mt-2 text-right">
        <span className="text-xs font-mono font-medium text-slate-500 dark:text-slate-500">
          {Math.round(progress)}% complete
        </span>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}
