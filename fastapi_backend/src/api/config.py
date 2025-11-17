import logging
import os
from functools import lru_cache

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

logger = logging.getLogger("lms.config")


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        # Core Supabase config
        self.supabase_url = (os.getenv("SUPABASE_URL") or "").strip()
        self.supabase_service_role_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
        anon = (os.getenv("SUPABASE_ANON_KEY") or "").strip()
        # Optional anon key for future use
        self.supabase_anon_key = anon if anon else None
        self.supabase_storage_bucket = (os.getenv("SUPABASE_STORAGE_BUCKET") or "lms-files").strip()

        # CORS configuration
        cors = (os.getenv("CORS_ALLOW_ORIGINS") or "").strip()
        self.cors_allow_origins = [o.strip() for o in cors.split(",") if o.strip()] or ["*"]

        # API port
        self.api_port = int(os.getenv("API_PORT") or "3001")

    def supabase_configured(self) -> bool:
        """Return True if required Supabase env variables are present."""
        return bool(self.supabase_url and self.supabase_service_role_key)

    def missing_supabase_vars(self) -> list[str]:
        """List missing required Supabase env vars."""
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        return missing


@lru_cache()
def get_settings():
    """Return cached settings instance."""
    settings = Settings()
    if not settings.supabase_configured():
        logger.warning(
            "Supabase not fully configured. Missing: %s. "
            "The API will start but DB/storage operations will return 500 until configured.",
            ", ".join(settings.missing_supabase_vars()) or "none",
        )
    return settings
