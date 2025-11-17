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
1) Create and populate .env (see .env.example included in this folder)
2) Ensure bucket lms-files exists (see Storage section)
3) Run the FastAPI app (example)
   - Use uvicorn or fastapi CLI
   - Make sure requirements are installed: pip install -r requirements.txt

SQL Setup (run in Supabase SQL editor)
This script will:
- Ensure pgcrypto is enabled (for gen_random_uuid)
- Create lessons, quizzes, assignments, completions tables
- Add trigger to auto-update lessons.updated_at
- Enable RLS on all tables
- Add permissive development policies (allow ALL)

-- Helpers
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION public.set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Tables
CREATE TABLE IF NOT EXISTS public.lessons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  file_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.quizzes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id uuid REFERENCES public.lessons(id) ON DELETE CASCADE,
  title text NOT NULL,
  questions jsonb NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id uuid REFERENCES public.lessons(id) ON DELETE CASCADE,
  employee_id text NOT NULL,
  assigned_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.completions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id uuid REFERENCES public.lessons(id) ON DELETE CASCADE,
  employee_id text NOT NULL,
  completed_at timestamptz DEFAULT now(),
  UNIQUE (lesson_id, employee_id)
);

-- Trigger for lessons.updated_at
DROP TRIGGER IF EXISTS trg_set_updated_at ON public.lessons;
CREATE TRIGGER trg_set_updated_at
BEFORE UPDATE ON public.lessons
FOR EACH ROW EXECUTE PROCEDURE public.set_updated_at();

-- Enable RLS
ALTER TABLE public.lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.completions ENABLE ROW LEVEL SECURITY;

-- Development policies (permissive; replace for production)
CREATE POLICY "lessons_all_dev" ON public.lessons FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "quizzes_all_dev" ON public.quizzes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "assignments_all_dev" ON public.assignments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "completions_all_dev" ON public.completions FOR ALL USING (true) WITH CHECK (true);

Storage Setup
Create a public bucket named lms-files:

Option A: Supabase Dashboard
1) Go to Storage -> Create new bucket
2) Name: lms-files
3) Public: Enabled (Public bucket)
4) Save

Option B: SQL (Dashboard's SQL editor)
Note: As of current Supabase versions, bucket creation is typically done via the Dashboard or via the Storage API. If using SQL, ensure the storage schema functions are available. Example (may vary by version and permissions):

-- Example using storage admin function (requires appropriate role):
-- select storage.create_bucket('lms-files', public => true);

Verify the bucket is accessible and record its name in SUPABASE_STORAGE_BUCKET.

Security Notes
- These RLS policies are permissive for development and testing. For production:
  - Replace FOR ALL policies with explicit per-operation policies (SELECT/INSERT/UPDATE/DELETE).
  - Constrain access by JWT claims (auth.uid(), roles), or other attributes.
  - Set storage bucket policies to restrict read/write as needed.
- Do not expose SUPABASE_SERVICE_ROLE_KEY in the frontend or logs.

Troubleshooting
- Missing pgcrypto:
  - Ensure "CREATE EXTENSION IF NOT EXISTS pgcrypto;" runs successfully.
- Permission denied on policies:
  - Run the SQL as a user with sufficient privileges in Supabase SQL editor.
- Bucket access errors:
  - Confirm bucket exists and is public (or adjust code to use signed URLs).

Next Steps
- Implement FastAPI endpoints to use supabase-py for CRUD and uploads to lms-files.
- Replace permissive policies with restricted RLS when moving beyond local development.
