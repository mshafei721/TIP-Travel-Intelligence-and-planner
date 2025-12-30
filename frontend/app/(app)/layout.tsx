'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '@/components/shell';
import { ToastProvider, ToastContainer } from '@/components/ui/toast';
import { OfflineDetector } from '@/components/ui/OfflineDetector';
import { createClient } from '@/lib/supabase/client';
import { GenerationProgressProvider } from '@/contexts/GenerationProgressContext';
import { GenerationProgressModal, GenerationProgressBadge } from '@/components/reports';

const navigationItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'My Trips', href: '/trips' },
  { label: 'Templates', href: '/templates' },
  { label: 'History', href: '/history' },
  { label: 'Create Trip', href: '/trips/create' },
  { label: 'Profile', href: '/profile' },
  { label: 'Settings', href: '/settings' },
];

interface UserInfo {
  name: string;
  avatarUrl?: string;
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const supabase = createClient();

    const getUser = async () => {
      try {
        const {
          data: { user: authUser },
        } = await supabase.auth.getUser();
        if (authUser) {
          setUser({
            name:
              authUser.user_metadata?.display_name ||
              authUser.user_metadata?.full_name ||
              authUser.email?.split('@')[0] ||
              'User',
            avatarUrl: authUser.user_metadata?.avatar_url,
          });
        }
      } catch (error) {
        console.error('Failed to get user:', error);
      } finally {
        setIsLoading(false);
      }
    };

    getUser();

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser({
          name:
            session.user.user_metadata?.display_name ||
            session.user.user_metadata?.full_name ||
            session.user.email?.split('@')[0] ||
            'User',
          avatarUrl: session.user.user_metadata?.avatar_url,
        });
      } else {
        setUser(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push('/login');
  };

  return (
    <ToastProvider>
      <GenerationProgressProvider>
        <OfflineDetector />
        <AppShell
          navigationItems={navigationItems}
          user={isLoading ? { name: 'Loading...' } : user || undefined}
          onLogout={handleLogout}
        >
          {children}
        </AppShell>
        <GenerationProgressModal />
        <GenerationProgressBadge />
        <ToastContainer />
      </GenerationProgressProvider>
    </ToastProvider>
  );
}
