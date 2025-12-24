'use client'

interface AutoSaveIndicatorProps {
  show: boolean
}

export default function AutoSaveIndicator({ show }: AutoSaveIndicatorProps) {
  if (!show) return null

  return (
    <div className="fixed bottom-8 right-8 z-50 animate-slideInRight">
      <div className="bg-green-600 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-3 border border-green-500">
        <svg
          className="w-5 h-5 animate-checkmark"
          fill="none"
          strokeWidth="2.5"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <span className="font-medium text-sm">Draft saved</span>
      </div>
    </div>
  )
}

// Add these styles globally or in a separate CSS file
const styles = `
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes checkmark {
    0% {
      transform: scale(0);
      opacity: 0;
    }
    50% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }

  .animate-slideInRight {
    animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .animate-checkmark {
    animation: checkmark 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
`

// Inject styles (only needed if not using global CSS)
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = styles
  document.head.appendChild(styleSheet)
}
