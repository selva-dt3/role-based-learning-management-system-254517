from typing import Optional

from supabase import Client, create_client

from .config import get_settings

_client: Optional[Client] = None


# PUBLIC_INTERFACE
def get_supabase_client() -> Client:
    """Get a singleton Supabase client authenticated with service role.

    Returns:
        Client: Supabase Python client instance.

    Notes:
        Uses SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from environment.
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client
