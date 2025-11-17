import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .config import get_settings
from .supabase_client import get_supabase_client

router = APIRouter(prefix="/upload", tags=["Files"])


# PUBLIC_INTERFACE
@router.post(
    "",
    summary="Upload file to Supabase Storage",
    description="Uploads a file to the configured Supabase Storage bucket and returns a public URL.",
)
async def upload_file(file: UploadFile = File(...), prefix: Optional[str] = Form(default="lessons")) -> dict:
    """Upload a file to Supabase storage.

    Parameters:
        file: File to upload
        prefix: Optional folder prefix in the bucket

    Returns:
        dict with { 'url': 'https://...' }
    """
    settings = get_settings()
    sb = get_supabase_client()

    # Generate storage path
    safe_prefix = prefix.strip("/ ")
    unique = uuid.uuid4().hex
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    filename = file.filename or "file"
    path = f"{safe_prefix}/{timestamp}-{unique}-{filename}"

    # Read file bytes
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    # Upload
    try:
        storage = sb.storage.from_(settings.supabase_storage_bucket)
        storage.upload(path, content)
        public_url = storage.get_public_url(path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc

    return {"url": public_url}
