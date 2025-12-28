/**
 * Server-side Authentication Utilities
 * For use in Server Components, Server Actions, and Route Handlers only
 */

import { createClient } from '@/lib/supabase/server';

/**
 * Get authentication token on the server side
 */
export async function getServerAuthToken(): Promise<string | null> {
  try {
    const supabase = await createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      return null;
    }

    return session.access_token;
  } catch (error) {
    console.error('Error getting server auth token:', error);
    return null;
  }
}
