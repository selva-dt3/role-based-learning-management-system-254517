import logging
from typing import Optional, Tuple, Any

from fastapi import HTTPException

try:
    # Import only create_client to avoid type import at module load
    from supabase import create_client  # type: ignore
except Exception as exc:  # pragma: no cover - import guard
    create_client = None  # type: ignore
    _import_error: Optional[Exception] = exc
else:
    _import_error = None

from .config import get_settings

logger = logging.getLogger("lms.supabase")

# Hold the client instance; type as Any to avoid hard import on type
_client: Optional[Any] = None


def _build_client() -> Tuple[Optional[Any], Optional[str]]:
    """Create a Supabase client if configuration and package are available.

    Returns:
        (client, error_message): client if created, else None and a human-friendly error string.
    """
    if _import_error is not None or create_client is None:
        return None, "Supabase package not installed. Ensure requirements include 'supabase==2.6.0'."

    settings = get_settings()
    if not settings.supabase_configured():
        return None, f"Missing env vars: {', '.join(settings.missing_supabase_vars())}"

    try:
        client = create_client(settings.supabase_url, settings.supabase_service_role_key)  # type: ignore[arg-type]
        return client, None
    except Exception as exc:
        return None, f"Failed to initialize Supabase client: {exc}"


# PUBLIC_INTERFACE
def get_supabase_client() -> Any:
    """Get a singleton Supabase client authenticated with service role.

    Returns:
        Client: Supabase Python client instance created via create_client.

    Behavior:
        - Lazy-initializes the client on first call.
        - Raises HTTP 500 with a clear message if environment is missing or package is unavailable,
          so the app keeps running and endpoints fail gracefully.
    """
    global _client
    if _client is None:
        client, err = _build_client()
        if err:
            logger.error("Supabase client unavailable: %s", err)
            raise HTTPException(status_code=500, detail=f"Supabase unavailable: {err}")
        _client = client
    return _client
