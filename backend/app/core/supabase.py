"""Supabase client for backend API"""

from typing import Optional

from supabase import Client, create_client

from app.core.config import settings

# Cached client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client with service role key (full access)
    Used for backend API operations that bypass RLS.

    Returns None if Supabase is not configured (e.g., in CI/testing).
    """
    global _supabase_client

    # Return cached client if available
    if _supabase_client is not None:
        return _supabase_client

    # Check if Supabase is configured
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None

    # Create and cache client
    _supabase_client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )
    return _supabase_client


# Lazy-loaded client (use get_supabase_client() for proper error handling)
# This property allows backward compatibility with existing code
class _SupabaseClientProxy:
    """Lazy proxy for Supabase client to avoid import-time errors."""

    def __getattr__(self, name: str):
        client = get_supabase_client()
        if client is None:
            raise RuntimeError(
                "Supabase is not configured. Set SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY environment variables."
            )
        return getattr(client, name)


supabase = _SupabaseClientProxy()
