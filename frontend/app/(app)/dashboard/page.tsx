export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
          Dashboard
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Welcome to TIP - Travel Intelligence & Planner
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            My Trips
          </h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            View and manage your travel plans
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Create Trip
          </h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Plan a new trip with AI assistance
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Profile
          </h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Manage your account and preferences
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950">
        <p className="text-sm text-blue-900 dark:text-blue-100">
          <strong>Foundation Milestone (M1):</strong> Application shell and routing structure complete.
          Authentication and trip management features will be implemented in upcoming milestones.
        </p>
      </div>
    </div>
  )
}
