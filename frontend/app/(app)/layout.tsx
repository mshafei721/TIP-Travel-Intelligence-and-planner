'use client';

import { AppShell } from '@/components/shell';
import { ToastProvider, ToastContainer } from '@/components/ui/toast';
import { OfflineDetector } from '@/components/ui/OfflineDetector';

const navigationItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'My Trips', href: '/trips' },
  { label: 'Templates', href: '/templates' },
  { label: 'History', href: '/history' },
  { label: 'Create Trip', href: '/trips/create' },
  { label: 'Analytics', href: '/analytics' },
  { label: 'Profile', href: '/profile' },
  { label: 'Settings', href: '/settings' },
];

// Mock user - will be replaced with real auth in Milestone 2
const mockUser = {
  name: 'Demo User',
  // avatarUrl: undefined, // Will show initials
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const handleLogout = () => {
    // TODO: Implement logout logic in Milestone 2
    console.log('Logout clicked');
  };

  return (
    <ToastProvider>
      <OfflineDetector />
      <AppShell navigationItems={navigationItems} user={mockUser} onLogout={handleLogout}>
        {children}
      </AppShell>
      <ToastContainer />
    </ToastProvider>
  );
}
