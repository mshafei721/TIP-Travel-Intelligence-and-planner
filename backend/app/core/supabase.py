"""Supabase client for backend API"""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Get Supabase client with service role key (full access)
    Used for backend API operations that bypass RLS
    """
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
    )


# Global client instance (reused across requests)
supabase: Client = get_supabase_client()
