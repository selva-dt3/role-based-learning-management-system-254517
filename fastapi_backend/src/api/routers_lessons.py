from typing import List

from fastapi import APIRouter, HTTPException

from .schemas import Lesson, LessonCreate, LessonUpdate
from .supabase_client import get_supabase_client

router = APIRouter(prefix="/lessons", tags=["Lessons"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List lessons",
    description="Retrieve all lessons.",
    response_model=List[Lesson],
)
def list_lessons() -> List[Lesson]:
    """List all lessons."""
    sb = get_supabase_client()
    res = sb.table("lessons").select("*").order("created_at", desc=False).execute()
    data = res.data or []
    return [
        Lesson(id=row["id"], title=row["title"], description=row.get("description"), file_url=row.get("file_url"))
        for row in data
    ]


# PUBLIC_INTERFACE
@router.post(
    "",
    summary="Create lesson",
    description="Create a new lesson.",
    response_model=Lesson,
)
def create_lesson(payload: LessonCreate) -> Lesson:
    """Create a new lesson."""
    sb = get_supabase_client()
    res = sb.table("lessons").insert(payload.model_dump()).select("*").single().execute()
    row = res.data
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create lesson")
    return Lesson(id=row["id"], title=row["title"], description=row.get("description"), file_url=row.get("file_url"))


# PUBLIC_INTERFACE
@router.put(
    "/{lesson_id}",
    summary="Update lesson",
    description="Update a lesson by ID.",
    response_model=Lesson,
)
def update_lesson(lesson_id: str, payload: LessonUpdate) -> Lesson:
    """Update an existing lesson by ID."""
    sb = get_supabase_client()
    update_dict = {k: v for k, v in payload.model_dump().items() if v is not None}
    res = sb.table("lessons").update(update_dict).eq("id", lesson_id).select("*").single().execute()
    row = res.data
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(id=row["id"], title=row["title"], description=row.get("description"), file_url=row.get("file_url"))


# PUBLIC_INTERFACE
@router.delete(
    "/{lesson_id}",
    summary="Delete lesson",
    description="Delete a lesson by ID.",
)
def delete_lesson(lesson_id: str) -> dict:
    """Delete a lesson by ID."""
    sb = get_supabase_client()
    # Ensure exists
    check = sb.table("lessons").select("id").eq("id", lesson_id).single().execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="Lesson not found")
    sb.table("lessons").delete().eq("id", lesson_id).execute()
    return {"deleted": True, "id": lesson_id}
