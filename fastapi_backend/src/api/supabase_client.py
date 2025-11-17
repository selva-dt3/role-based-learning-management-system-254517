from typing import Optional

# Prefer the official 'supabase' v2 client, which exposes:
#   from supabase import create_client, Client
# If environment falls back to legacy 'supabase-py', this import would fail.
# In such a case, update requirements to use 'supabase==2.6.*'.
from supabase import Client, create_client

from .config import get_settings

_client: Optional[Client] = None


# PUBLIC_INTERFACE
def get_supabase_client() -> Client:
    """Get a singleton Supabase client authenticated with service role.

    Returns:
        Client: Supabase Python client instance created via create_client.

    Notes:
        - Uses SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from environment.
        - This module expects the 'supabase' package v2.x to be installed.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client
