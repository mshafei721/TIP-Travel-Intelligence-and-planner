interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div data-testid="dashboard-layout" className="space-y-6">
      {children}
    </div>
  )
}

/**
 * Grid-based dashboard layout for arranging cards
 *
 * Desktop Layout (2 columns):
 * [ Quick Actions ]    [ Statistics Summary ]
 * [ Recent Trips  ]    [ Upcoming Trips     ]
 * [ Recommendations (full width)           ]
 *
 * Mobile Layout (1 column):
 * [ Quick Actions      ]
 * [ Statistics Summary ]
 * [ Recent Trips       ]
 * [ Upcoming Trips     ]
 * [ Recommendations    ]
 */
export function DashboardGrid({ children }: DashboardLayoutProps) {
  return (
    <div
      data-testid="dashboard-layout"
      className="grid grid-cols-1 gap-6 lg:grid-cols-2"
    >
      {children}
    </div>
  )
}

/**
 * Section wrapper for dashboard cards
 * Use for full-width sections like recommendations
 */
export function DashboardSection({ children }: DashboardLayoutProps) {
  return <div className="lg:col-span-2">{children}</div>
}
