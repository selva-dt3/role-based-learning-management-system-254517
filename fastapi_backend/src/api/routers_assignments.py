from typing import List

from fastapi import APIRouter, HTTPException

from .schemas import Assignment, AssignmentCreate, Completion, CompletionCreate
from .supabase_client import get_supabase_client

router = APIRouter(prefix="", tags=["Assignments & Progress"])


# PUBLIC_INTERFACE
@router.post(
    "/assign",
    summary="Assign lesson",
    description="Assign a lesson to an employee.",
    response_model=Assignment,
)
def assign_lesson(payload: AssignmentCreate) -> Assignment:
    """Assign a lesson to an employee."""
    sb = get_supabase_client()
    res = sb.table("assignments").insert(payload.model_dump()).select("*").single().execute()
    row = res.data
    if not row:
        raise HTTPException(status_code=500, detail="Failed to assign lesson")
    return Assignment(id=row["id"], lesson_id=row["lesson_id"], employee_id=row["employee_id"])


# PUBLIC_INTERFACE
@router.get(
    "/assignments/{employee_id}",
    summary="List assignments for employee",
    description="Get all assigned lessons for an employee.",
    response_model=List[Assignment],
)
def list_assignments(employee_id: str) -> List[Assignment]:
    """List assignments for an employee."""
    sb = get_supabase_client()
    res = sb.table("assignments").select("*").eq("employee_id", employee_id).order("assigned_at", desc=True).execute()
    data = res.data or []
    return [Assignment(id=r["id"], lesson_id=r["lesson_id"], employee_id=r["employee_id"]) for r in data]


# PUBLIC_INTERFACE
@router.post(
    "/complete",
    summary="Mark lesson complete",
    description="Mark an assignment as completed by the employee.",
    response_model=Completion,
)
def mark_complete(payload: CompletionCreate) -> Completion:
    """Mark a lesson as completed by an employee."""
    sb = get_supabase_client()
    # Upsert unique by (lesson_id, employee_id)
    res = (
        sb.table("completions")
        .upsert(payload.model_dump(), on_conflict="lesson_id,employee_id")
        .select("*")
        .single()
        .execute()
    )
    row = res.data
    if not row:
        raise HTTPException(status_code=500, detail="Failed to mark completion")
    return Completion(id=row["id"], lesson_id=row["lesson_id"], employee_id=row["employee_id"])


# PUBLIC_INTERFACE
@router.get(
    "/progress/{employee_id}",
    summary="Get progress for employee",
    description="Return counts of assigned and completed lessons and percentage progress for an employee.",
)
def get_progress(employee_id: str) -> dict:
    """Return simple progress metrics for an employee."""
    sb = get_supabase_client()
    assignments = sb.table("assignments").select("id,lesson_id").eq("employee_id", employee_id).execute().data or []
    completions = (
        sb.table("completions")
        .select("id,lesson_id")
        .eq("employee_id", employee_id)
        .execute()
        .data
        or []
    )
    assigned_count = len(assignments)
    completed_count = len({c["lesson_id"] for c in completions})
    percent = (completed_count / assigned_count) * 100 if assigned_count else 0.0
    return {
        "employee_id": employee_id,
        "assigned_count": assigned_count,
        "completed_count": completed_count,
        "progress_percent": round(percent, 2),
    }
