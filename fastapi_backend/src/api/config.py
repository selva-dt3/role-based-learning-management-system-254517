import os
from functools import lru_cache

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


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

        # Basic validation with actionable messages
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if missing:
            raise ValueError(
                "Missing required environment variables: "
                + ", ".join(missing)
                + ". Create fastapi_backend/.env from .env.example and set these values."
            )


@lru_cache()
def get_settings():
    """Return cached settings instance."""
    return Settings()
