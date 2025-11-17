from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
import os
from supabase import create_client, Client

# App metadata with tags
app = FastAPI(
    title="LMS Backend API",
    description="FastAPI backend for Role-Based LMS using Supabase for data and storage.",
    version="1.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health and metadata"},
        {"name": "Lessons", "description": "CRUD operations for lessons"},
        {"name": "Quizzes", "description": "CRUD operations for quizzes"},
        {"name": "Assignments & Progress", "description": "Assign lessons and check employee progress"},
        {"name": "Files", "description": "Upload files to Supabase Storage"},
        {"name": "Employees", "description": "Create and check employee profiles"},
    ],
)

# CORS
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",")] if ALLOWED_ORIGINS else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client factory
def get_supabase() -> Client:
    """Create supabase client using env vars."""
    url = os.environ.get("SUPABASE_URL") or os.environ.get("REACT_APP_SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or os.environ.get("REACT_APP_SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase configuration missing: SUPABASE_URL and SUPABASE_KEY")
    return create_client(url, key)

EMP_TABLE = os.environ.get("EMPLOYEES_TABLE_NAME", "employees")

class EmployeeCreate(BaseModel):
    """Payload to create or update an employee profile."""
    employee_id: str = Field(..., description="Unique employee identifier")
    name: Optional[str] = Field(None, description="Employee display name")

class EmployeeRecord(BaseModel):
    """Employee record representation."""
    employee_id: str = Field(..., description="Unique employee identifier")
    name: Optional[str] = Field(None, description="Employee display name")

@app.get("/", tags=["Health"], summary="Health Check", description="Return service health status.")
def health_check() -> Dict[str, Any]:
    """Simple health check endpoint."""
    return {"ok": True, "service": "lms-backend", "version": app.version}

# PUBLIC_INTERFACE
@app.get(
    "/employees/{employee_id}",
    tags=["Employees"],
    summary="Check employee profile existence",
    description="Returns the employee record if found; 404 if not found.",
    responses={
        200: {"description": "Employee found"},
        404: {"description": "Employee NOT found"},
    },
)
def get_employee(employee_id: str) -> Dict[str, Any]:
    """Get employee by id."""
    try:
        sb = get_supabase()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase not configured: {e}") from e

    try:
        res = sb.table(EMP_TABLE).select("*").eq("employee_id", employee_id).limit(1).execute()
        data = (res.data or [])
        if not data:
            raise HTTPException(status_code=404, detail="Employee not found")
        # Return one row
        row = data[0]
        return {"exists": True, "employee": {"employee_id": row.get("employee_id"), "name": row.get("name")}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee: {e}") from e

# PUBLIC_INTERFACE
@app.post(
    "/employees",
    tags=["Employees"],
    summary="Create or update employee profile",
    description="Upserts an employee profile by employee_id.",
    response_model=EmployeeRecord,
)
def create_or_update_employee(payload: EmployeeCreate) -> EmployeeRecord:
    """Create or update an employee record using upsert."""
    try:
        sb = get_supabase()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase not configured: {e}") from e

    try:
        upsert_payload = {"employee_id": payload.employee_id, "name": payload.name}
        res = sb.table(EMP_TABLE).upsert(upsert_payload, on_conflict="employee_id").execute()
        data = (res.data or [])
        # Some versions of supabase-py may not return upserted row; fetch to be sure
        if not data:
            res2 = sb.table(EMP_TABLE).select("*").eq("employee_id", payload.employee_id).limit(1).execute()
            data = res2.data or []
        if not data:
            raise HTTPException(status_code=500, detail="Upsert failed")
        row = data[0]
        return EmployeeRecord(employee_id=row.get("employee_id"), name=row.get("name"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upsert employee: {e}") from e
