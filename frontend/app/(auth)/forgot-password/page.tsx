export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
      <div className="w-full max-w-md space-y-8 rounded-lg border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
            Reset Password
          </h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Enter your email to receive reset instructions
          </p>
        </div>

        <div className="mt-8">
          <p className="text-center text-sm text-slate-600 dark:text-slate-400">
            Password reset form placeholder - will be implemented in Milestone 2
          </p>
        </div>
      </div>
    </div>
  )
}
