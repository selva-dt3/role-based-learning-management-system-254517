from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers_lessons import router as lessons_router
from .routers_quizzes import router as quizzes_router
from .routers_assignments import router as assignments_router
from .routers_upload import router as upload_router

openapi_tags = [
    {"name": "Health", "description": "Service health and metadata"},
    {"name": "Lessons", "description": "CRUD operations for lessons"},
    {"name": "Quizzes", "description": "CRUD operations for quizzes"},
    {"name": "Assignments & Progress", "description": "Assign lessons and check employee progress"},
    {"name": "Files", "description": "Upload files to Supabase Storage"},
]

app = FastAPI(
    title="LMS Backend API",
    description="FastAPI backend for Role-Based LMS using Supabase for data and storage.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Configure CORS from env
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check", description="Return service health status.")
def health_check():
    """Health check endpoint for service liveness."""
    return {"message": "Healthy"}


# Include routers
app.include_router(lessons_router)
app.include_router(quizzes_router)
app.include_router(assignments_router)
app.include_router(upload_router)
