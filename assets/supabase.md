# Supabase Integration - Employees Table

This backend uses Supabase for data storage. For employee profile gating we use a minimal `employees` table.

Table: employees
- employee_id: text (PRIMARY KEY, unique, not null)
- name: text (nullable)

SQL:
CREATE TABLE IF NOT EXISTS public.employees (
  employee_id text PRIMARY KEY,
  name text
);

RLS:
You can keep RLS disabled for this prototype or add permissive policies for service role key. The backend uses the service key via environment variables.

Environment variables required (set via orchestrator; do not hardcode):
- SUPABASE_URL
- SUPABASE_KEY
- (Optional) EMPLOYEES_TABLE_NAME (defaults to "employees")
- (Optional) ALLOWED_ORIGINS for CORS (comma-separated list)

Endpoints added:
- GET /employees/{employee_id}
  - 200: { "exists": true, "employee": { "employee_id", "name" } }
  - 404: { "detail": "Employee not found" }
- POST /employees
  - Request: { "employee_id": "emp-001", "name": "Alice" }
  - Response: { "employee_id": "emp-001", "name": "Alice" }

These endpoints are used by the React frontend to:
- HR/Admin: create employee profiles
- Employee: verify profile exists before accessing dashboard
