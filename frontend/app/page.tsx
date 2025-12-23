import { redirect } from 'next/navigation'

export default function HomePage() {
  // Redirect to dashboard (will be protected by auth middleware later)
  redirect('/dashboard')
}
