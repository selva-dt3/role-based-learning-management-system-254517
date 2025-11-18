# FastAPI Backend - Supabase Setup

This backend uses Supabase (Postgres + Storage) for data and file storage.

Project details:
- Project Name: my-lms-app
- Region: us-east-1
- Project ID: fcrzmnafjvclnvyuquau
- Supabase URL: https://fcrzmnafjvclnvyuquau.supabase.co
- Storage Bucket (public): lms-files

IMPORTANT
- This setup enables permissive Row Level Security (RLS) policies suitable for local development only. Replace with least-privilege policies before production.

Prerequisites
- Supabase project created and accessible
- Access to Supabase SQL Editor and Storage
- Service Role Key (keep secret)

Environment Variables
Create role-based-learning-management-system-254517/fastapi_backend/.env (copy from .env.example):
- SUPABASE_URL: https://fcrzmnafjvclnvyuquau.supabase.co
- SUPABASE_SERVICE_ROLE_KEY: Service role key from Supabase (Settings -> API)
- SUPABASE_STORAGE_BUCKET: lms-files
- CORS_ALLOW_ORIGINS: Comma-separated origins (e.g., http://localhost:3000)
- API_PORT: Backend port (default: 3001)
- Optional: SUPABASE_ANON_KEY for client operations if needed later

Local Development Quick Start
1) Copy .env.example to .env and populate values (the API will still start even if SUPABASE_* are missing; DB endpoints will return 500 until configured).
2) Ensure bucket lms-files exists (see Storage section)
3) Install dependencies: pip install -r requirements.txt
4) Run the FastAPI app (binds to 0.0.0.0:3001): uvicorn src.api.main:app --host 0.0.0.0 --port 3001
5) Generate OpenAPI file (optional for interfaces dir): python -m src.api.generate_openapi

Running Tests (pytest + coverage)
- From fastapi_backend/, run:
    pytest --maxfail=1 --disable-warnings --cov=src.api --cov-report=term-missing
- Tests mock Supabase client; no real Supabase credentials are required.

Available APIs (summary)
- Lessons:
  - GET /lessons
  - POST /lessons
  - PUT /lessons/{id}
  - DELETE /lessons/{id}
- Quizzes:
  - GET /quizzes
  - POST /quizzes
  - PUT /quizzes/{id}
  - DELETE /quizzes/{id}
- Assignments & Progress:
  - POST /assign
  - GET /assignments/{employee_id}
  - POST /complete
  - GET /progress/{employee_id}
- Files:
  - POST /upload (multipart/form-data)

Notes
- File uploads go to bucket lms-files; endpoint returns a public URL. Ensure bucket is public or switch to signed URLs if required.
- Service role key is used server-side; never expose this key to clients.

Troubleshooting
- Missing pgcrypto:
  - Ensure "CREATE EXTENSION IF NOT EXISTS pgcrypto;" runs successfully.
- Permission denied on policies:
  - Run the SQL as a user with sufficient privileges in Supabase SQL editor.
- Bucket access errors:
  - Confirm bucket exists and is public (or adjust code to use signed URLs).
- CORS issues:
  - Ensure CORS_ALLOW_ORIGINS includes your frontend URL(s), e.g., http://localhost:3000.
- Startup issues:
  - If the app fails to access Supabase, it will now log a warning and still start; DB endpoints will return HTTP 500 with a clear error about missing configuration or missing package.

Security Notes
- Replace permissive development policies with least-privilege RLS policies for production.
- Rotate and secure SUPABASE_SERVICE_ROLE_KEY; do not log it or commit it.

