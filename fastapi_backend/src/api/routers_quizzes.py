from typing import List

from fastapi import APIRouter, HTTPException

from .schemas import Quiz, QuizCreate, QuizUpdate
from .supabase_client import get_supabase_client

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List quizzes",
    description="Retrieve all quizzes.",
    response_model=List[Quiz],
)
def list_quizzes() -> List[Quiz]:
    """List all quizzes."""
    sb = get_supabase_client()
    res = sb.table("quizzes").select("*").order("created_at", desc=False).execute()
    data = res.data or []
    return [Quiz(id=r["id"], lesson_id=r["lesson_id"], title=r["title"], questions=r["questions"]) for r in data]


# PUBLIC_INTERFACE
@router.post(
    "",
    summary="Create quiz",
    description="Create a quiz.",
    response_model=Quiz,
)
def create_quiz(payload: QuizCreate) -> Quiz:
    """Create a quiz."""
    sb = get_supabase_client()
    res = sb.table("quizzes").insert(payload.model_dump()).select("*").single().execute()
    row = res.data
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create quiz")
    return Quiz(id=row["id"], lesson_id=row["lesson_id"], title=row["title"], questions=row["questions"])


# PUBLIC_INTERFACE
@router.put(
    "/{quiz_id}",
    summary="Update quiz",
    description="Update a quiz by ID.",
    response_model=Quiz,
)
def update_quiz(quiz_id: str, payload: QuizUpdate) -> Quiz:
    """Update a quiz by ID."""
    sb = get_supabase_client()
    update_dict = {k: v for k, v in payload.model_dump().items() if v is not None}
    res = sb.table("quizzes").update(update_dict).eq("id", quiz_id).select("*").single().execute()
    row = res.data
    if not row:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return Quiz(id=row["id"], lesson_id=row["lesson_id"], title=row["title"], questions=row["questions"])


# PUBLIC_INTERFACE
@router.delete(
    "/{quiz_id}",
    summary="Delete quiz",
    description="Delete a quiz by ID.",
)
def delete_quiz(quiz_id: str) -> dict:
    """Delete a quiz by ID."""
    sb = get_supabase_client()
    check = sb.table("quizzes").select("id").eq("id", quiz_id).single().execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    sb.table("quizzes").delete().eq("id", quiz_id).execute()
    return {"deleted": True, "id": quiz_id}
